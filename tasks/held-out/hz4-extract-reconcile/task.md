# Reconcile settled transactions against accounts

The workspace has two files:

- `transactions.log` — one transaction per line, in one of two formats, mixed with
  noise lines (separators, comments, blanks, stray log lines) that must be ignored:
  - JSON: `{"txn": ..., "acct": ..., "amount": ..., "status": ...}`
  - Plain: `<txn> | <acct> | <amount> | <status>` (fields separated by ` | `)
- `accounts.csv` — a reference table with columns `acct_id,name`.

Produce `reconciled.csv` that:

1. Has the header exactly: `txn_id,acct_id,name,amount,status`
2. Contains one row for every transaction whose status is exactly `settled`
   (drop `pending`, `failed`, and anything that isn't a valid transaction line).
3. For each settled transaction:
   - `txn_id`, `acct_id`, and `amount` are copied verbatim from the log.
   - `name` is that account's name from `accounts.csv`, or `UNKNOWN` if the
     account id is not present in `accounts.csv`.
   - `status` is `matched` if the account id is in `accounts.csv`, else `unmatched`.
4. Is sorted by `txn_id` ascending (string comparison).

Do not modify `transactions.log` or `accounts.csv`. Preserve `amount` exactly as
written (e.g. `10.0` stays `10.0`, `500.00` stays `500.00`).
