#!/usr/bin/env python3
"""Verifier: each file must equal the pristine file with exactly the manifest's PII
values replaced by their tokens — byte-for-byte. Over- and under-redaction both fail.
The file set must be unchanged."""

import json
import sys
from pathlib import Path


def fail(msg):
    print(msg)
    sys.exit(1)


def main():
    workspace = Path(sys.argv[1])
    here = Path(__file__).parent
    pristine = here / "workspace"
    manifest = json.loads((here / "manifest.json").read_text())["replacements"]

    by_file = {}
    for e in manifest:
        by_file.setdefault(e["file"], []).append(e)

    # file set must match exactly
    def relset(root):
        return {str(p.relative_to(root)) for p in root.rglob("*") if p.is_file()}
    if relset(workspace) != relset(pristine):
        fail(f"file set changed: {sorted(relset(workspace))} vs "
             f"{sorted(relset(pristine))}")

    for rel in sorted(relset(pristine)):
        original = (pristine / rel).read_text(encoding="utf-8")
        expected = original
        # longest value first so no short value corrupts a longer match
        for e in sorted(by_file.get(rel, []), key=lambda x: -len(x["value"])):
            expected = expected.replace(e["value"], e["token"])
        actual = (workspace / rel).read_text(encoding="utf-8")
        # under-redaction: any raw PII value still present
        for e in by_file.get(rel, []):
            if e["value"] in actual:
                fail(f"{rel}: PII not redacted: {e['value']!r}")
        if actual != expected:
            fail(f"{rel}: content differs from expected redaction")

    # JSONL must still parse
    for line in (workspace / "tickets.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            try:
                json.loads(line)
            except json.JSONDecodeError:
                fail("tickets.jsonl is no longer valid JSONL")
    print("ok")


if __name__ == "__main__":
    main()
