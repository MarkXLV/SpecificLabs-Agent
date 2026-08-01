# Redact contact PII

The workspace has free-text notes (`notes/*.txt`) and a ticket export
(`tickets.jsonl`). Scattered through them are email addresses and US phone
numbers written with separators (dashes, dots, spaces, a parenthesized area code,
or a leading `+1`).

Edit the files **in place** so that:

1. Every email address becomes exactly `[EMAIL]`.
2. Every phone number becomes exactly `[PHONE]`.
3. Nothing else changes. The following are **not** PII and must stay untouched:
   order numbers (`Order #...`), SKUs, IP addresses, version strings, and prices —
   even when they contain long digit runs that resemble a phone number.
4. The grader compares your files byte-for-byte, so over-redaction fails exactly
   like under-redaction.
5. No files are added, deleted, or renamed.

`tickets.jsonl` must remain valid JSONL after redaction.
