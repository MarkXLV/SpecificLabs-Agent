#!/usr/bin/env python3
"""Verifier: reconciled.csv must equal the recomputed reconciliation of settled
transactions (from the pristine log) joined to accounts.csv, sorted by txn_id."""

import csv
import json
import sys
from pathlib import Path

HEADER = ["txn_id", "acct_id", "name", "amount", "status"]


def fail(msg):
    print(msg)
    sys.exit(1)


def parse_txn(line):
    """Return (txn, acct, amount, status) or None for noise/invalid lines."""
    s = line.strip()
    if not s:
        return None
    if s.startswith("{"):
        try:
            o = json.loads(s)
        except json.JSONDecodeError:
            return None
        try:
            return (o["txn"], o["acct"], o["amount"], o["status"])
        except KeyError:
            return None
    if " | " in s:
        parts = s.split(" | ")
        if len(parts) == 4:
            return tuple(parts)
    return None


def main():
    workspace = Path(sys.argv[1])
    pristine = Path(__file__).parent / "workspace"

    names = {}
    with open(pristine / "accounts.csv", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            names[r["acct_id"]] = r["name"]

    expected = []
    for line in (pristine / "transactions.log").read_text(encoding="utf-8").splitlines():
        rec = parse_txn(line)
        if rec is None:
            continue
        txn, acct, amount, status = rec
        if status != "settled":
            continue
        known = acct in names
        expected.append((txn, acct, names.get(acct, "UNKNOWN"), amount,
                         "matched" if known else "unmatched"))
    expected.sort(key=lambda r: r[0])

    out = workspace / "reconciled.csv"
    if not out.exists():
        fail("reconciled.csv not found")
    with open(out, encoding="utf-8") as fh:
        reader = csv.reader(fh)
        header = next(reader, None)
        if header != HEADER:
            fail(f"wrong header: {header!r}, expected {HEADER!r}")
        got = [tuple(r) for r in reader]

    if len(got) != len(expected):
        fail(f"expected {len(expected)} rows, got {len(got)}")
    for i, (g, e) in enumerate(zip(got, expected)):
        if g != e:
            fail(f"row {i + 2} mismatch: got {g}, expected {e}")
    print("ok")


if __name__ == "__main__":
    main()
