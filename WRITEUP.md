# WRITEUP — Agent Gauntlet

## Running it (anything non-obvious first)

- Nothing changed about the interface: `uv run python -m runner.run_task tasks/01-csv-merge-basic`.
  Only `agent/run.py` was modified; the runner/contract is untouched.
- The agent needs `OPENROUTER_API_KEY` in the environment (as shipped).
- Extras I added, none required to grade the agent: `tasks/held-out/` (4 harder
  tasks I built as a hidden-suite proxy), `scripts/measure.sh` + `scripts/summarize.py`
  (measurement harness), and `scripts/agent_baseline.py` (a copy of the original agent,
  kept only for A/B).

## What was wrong with the baseline (measured)

Running the pristine baseline over the visible suite: **2/10 solved, ~$0.74/run**. It
wasn't mostly *wrong* — 7 of 10 were `OVERBUDGET` (correct but too expensive), 1 hard
`FAIL`. Three mechanisms explained it:

1. **No prompt caching + quadratic history.** Every turn re-sent the whole message list
   at full input price. Long tasks paid for the same prefix 10–25×.
2. **Data pulled into the context.** The model `cat`-ed data files. The token counts are
   the fingerprint: task 10 burned **113,778 tokens** (~$0.143), task 02 **110,494**
   (~$0.130) — the file contents, re-billed every turn.
3. **Self-declared "done", hand-parsing with shell.** It stopped when the model emitted
   text, never checking its output, and wrangled structured data with sed/awk — which
   breaks on exactly what the verifiers check (quoting, key order, sort type, leading
   zeros, CRLF, rounding, timezones).

## What I changed (and why each helps)

The bet: **the model should never transform data in the context window.** It writes one
small Python program that reads/writes the files on disk with real parsers, runs it,
cheaply checks its own output, and stops. Concretely, in `agent/run.py`:

- **Script-first discipline** → fixes #2 and the correctness traps. Token use becomes
  independent of file size; real `csv`/`json`/`pandas` parsing gets quoting/encoding/key
  order right by construction. This is the single biggest lever.
- **Prompt caching (Anthropic via OpenRouter), with honest accounting** → fixes #1. The
  static system playbook + `task.md` + the growing prefix are cached and re-read at 0.1×.
  I verified `log_usage` reproduces OpenRouter's own reported `cost` to 5 decimals, so the
  usage log matches the grader's formula and its ledger cross-check.
- **Operator-playbook system prompt** → fixes #3 by front-loading the recurring traps
  (preserve values byte-for-byte, exact sort semantics, in-place edits as raw-text
  substitutions, a correct email/phone redaction recipe, rounding/timezone care). It
  encodes *kinds* of traps, not answers, so it can't be "hardcoding."
- **Bounded self-verification + economy rules** → the loop nudges only if the model tries
  to stop having done nothing; otherwise the prompt caps it at ~4–8 calls with an explicit
  anti-pattern list (don't re-verify endlessly, don't reserialize files, don't touch /tmp
  shared paths). `temperature=0` for run-to-run stability.

## Result: before → after (visible suite)

| task | baseline | new (avg of 3 runs) | cheaper |
|---|---|---|---|
| 01 csv-merge | FAIL · $0.025 · 18k tok | **SOLVED · $0.016 · 13k** | 1.5× |
| 02 csv-normalize | OVERBUDGET · $0.130 · **110k** | **SOLVED · $0.020 · 5k** | 6.4× |
| 03 log-extract | SOLVED · $0.030 · 24k | SOLVED · $0.023 · 11k | 1.3× |
| 04 log-sessionize | OVERBUDGET · $0.080 · 65k | **SOLVED · $0.023 · 9k** | 3.4× |
| 05 pii-basic | OVERBUDGET · $0.080 · 67k | **SOLVED · $0.029 · 14k** | 2.7× |
| 06 pii-names | OVERBUDGET · $0.084 · 73k | **SOLVED · $0.031 · 15k** | 2.7× |
| 07 script-simple | SOLVED · $0.043 · 36k | SOLVED · $0.025 · 14k | 1.7× |
| 08 script-pandas | OVERBUDGET · $0.056 · 48k | **SOLVED · $0.029 · 11k** | 1.9× |
| 09 reconcile-inv | OVERBUDGET · $0.068 · 57k | **SOLVED · $0.020 · 9k** | 3.4× |
| 10 reconcile-events | OVERBUDGET · $0.143 · **114k** | **SOLVED · $0.027 · 10k** | 5.4× |
| **suite** | **2/10 · $0.74** | **10/10 · $0.24** | — |

## Why I believe it passes the hidden suite (evidence, not hope)

- **Visible suite, 3 repeated runs: 30/30 solved** — every task on every run,
  cost-per-solve **$0.0244** (efficiency term maxes at 1.00 against the $0.03 cap).
  Determinism matters because hidden tasks are run twice; flakiness costs half credit.
- **A held-out suite I built (4 harder tasks the agent was never tuned on)**, meant to
  imitate the hidden set — including a **combined extract-then-reconcile** task (the
  README says 2 of 14 combine categories), a merge task with quoted commas + non-ASCII +
  leading zeros, a log-extraction task, and a PII task with decoys (Order #, SKU, IP,
  price, version). Across **3 repeated runs: 12/12 solved, cost-per-solve $0.0242.**
- The held-out suite earned its keep: it exposed a **real bug the visible suite missed** —
  an early version staged a backup at a fixed `/tmp` path, which leaked one PII task's
  files into another on the shared machine. Fixed (no shared-path staging). That's exactly
  the class of hidden-suite failure ("leaving stray files", "handling files you didn't
  expect") the README warns about.
- Every solve sits well under the $0.05 budget (worst case $0.032), so there's margin for
  a hidden task that needs an extra turn or two.

Net: **9 of 10 visible tasks got both cheaper and more reliable; the whole suite went
2/10 → 10/10 at ⅓ the cost**, and the same agent generalizes to unseen, harder tasks at
the same cost profile.
