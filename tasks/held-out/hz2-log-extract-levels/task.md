# Extract alert events from a service log

`service.log` contains lines in two formats, interleaved with noise:

- JSON objects: `{"ts": ..., "level": ..., "svc": ..., "msg": ...}`
- Plain lines: `<ts> <service> <level> <message...>` (space-separated; the message
  is everything after the level and may contain spaces)

Anything else — stack-trace lines, separators, comments, blank lines — is noise
and must be ignored.

Produce `alerts.jsonl` (one JSON object per line) containing only events whose
level is `WARN` or `ERROR`. Each object must have exactly these keys, in this
order:

1. `ts` — copied verbatim
2. `level` — `WARN` or `ERROR`
3. `service` — from `svc` (JSON) or the 2nd field (plain)
4. `message` — from `msg` (JSON) or everything after the level (plain)

Sort the output by `ts` ascending, then by `service` ascending — both as plain
string comparisons. `INFO` and `DEBUG` events must not appear.
