# Merge regional order files

The workspace has three CSV files: `region_a.csv`, `region_b.csv`, `region_c.csv`.
They carry the same three columns — `order_id`, `customer`, `amount` — but the
column ORDER differs between files, and some `customer` values contain commas and
non-ASCII characters.

Produce a single file `merged.csv` that:

1. Has the header exactly: `order_id,customer,amount`
2. Contains every row from all three input files.
3. Is sorted by `order_id` ascending (numeric).
4. Preserves every value exactly as it appears in the input — no reformatting of
   amounts, no changing of names or their punctuation/accents.

The grader compares the output mechanically after parsing it as CSV, so field
quoting must be correct and values must match exactly.
