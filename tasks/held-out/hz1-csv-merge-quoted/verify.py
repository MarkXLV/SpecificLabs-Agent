#!/usr/bin/env python3
"""Verifier: merged.csv must equal the recomputed merge of the pristine inputs,
parsed as CSV (so quoting must be correct), sorted numerically by order_id."""

import csv
import sys
from pathlib import Path

INPUTS = ["region_a.csv", "region_b.csv", "region_c.csv"]
HEADER = ["order_id", "customer", "amount"]


def fail(msg):
    print(msg)
    sys.exit(1)


def main():
    workspace = Path(sys.argv[1])
    pristine = Path(__file__).parent / "workspace"

    expected = []
    for name in INPUTS:
        with open(pristine / name, encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                expected.append((r["order_id"], r["customer"], r["amount"]))
    expected.sort(key=lambda r: int(r[0]))

    out = workspace / "merged.csv"
    if not out.exists():
        fail("merged.csv not found")
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
