#!/usr/bin/env python3
"""Verifier: alerts.jsonl must equal the recomputed extraction of WARN/ERROR
events from the pristine service.log, keys in fixed order, sorted by (ts, service)."""

import json
import re
import sys
from pathlib import Path

KEYS = ["ts", "level", "service", "message"]
WANT = {"WARN", "ERROR"}
TS_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$")


def fail(msg):
    print(msg)
    sys.exit(1)


def extract(log_text):
    out = []
    for raw in log_text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("{"):
            try:
                o = json.loads(line)
            except json.JSONDecodeError:
                continue
            lvl = o.get("level")
            if lvl in WANT:
                out.append({"ts": o["ts"], "level": lvl,
                            "service": o["svc"], "message": o["msg"]})
            continue
        parts = line.split(" ")
        if len(parts) >= 4 and TS_RE.match(parts[0]) and parts[2] in WANT:
            out.append({"ts": parts[0], "level": parts[2],
                        "service": parts[1], "message": " ".join(parts[3:])})
    out.sort(key=lambda r: (r["ts"], r["service"]))
    return out


def main():
    workspace = Path(sys.argv[1])
    pristine = Path(__file__).parent / "workspace"
    expected = extract((pristine / "service.log").read_text(encoding="utf-8"))

    out = workspace / "alerts.jsonl"
    if not out.exists():
        fail("alerts.jsonl not found")
    got = []
    for i, line in enumerate(out.read_text(encoding="utf-8").splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            fail(f"line {i}: not valid JSON")
        if list(obj.keys()) != KEYS:
            fail(f"line {i}: keys must be {KEYS} in that order, got {list(obj.keys())}")
        got.append(obj)

    if len(got) != len(expected):
        fail(f"expected {len(expected)} events, got {len(got)}")
    for i, (g, e) in enumerate(zip(got, expected), start=1):
        if [g[k] for k in KEYS] != [e[k] for k in KEYS]:
            fail(f"record {i} mismatch: got {[g[k] for k in KEYS]}, "
                 f"expected {[e[k] for k in KEYS]}")
    print("ok")


if __name__ == "__main__":
    main()
