# luce-http-client

Native Luce Base HTTP/1.1 client. MIT OR Apache-2.0.
Cleartext requests use numeric IPv4 addresses. The `https` export uses native
TLS 1.3 with an explicitly supplied P-256 issuer pin; this is **not** general
public-CA trust, and there is no redirect handling or connection pool.

Both clients use one bounded incremental response decoder over the standard
library HTTP framing APIs. It handles fixed length, chunked (including validated
trailers), EOF-delimited and up to eight interim responses. Malformed framing,
truncation and output overflow fail instead of returning partial success. Heads
are limited to 32 KiB; cleartext output is capped at 1 MiB, HTTPS at the supplied
output buffer size. Discard output after any error. Completion stops at the framed
response boundary; coalesced extra bytes are rejected, but a separate later
response is not read. Upgrades and CONNECT tunnels are unsupported.

HTTPS request headers use the bounded standard encoder; bodies are sent in
16 KiB TLS records. Established connections close on success and failure.
Underlying TLS trust, alerts, timeouts, secret lifecycle and independent-server
interoperability still require further audit before production package downloads.

Tests cover every fixed/chunked fixture truncation, fragmentation sizes, malformed
lengths/chunks/trailers, request injection, and independent Python socket framing.
The native HTTPS fixture uses ephemeral test credentials; it is not independent
TLS interoperability evidence. All fixtures run in six compiler modes and under
ASan/UBSan. No language sources are changed.

```sh
python3 tools/bootstrap.py
python3 tests/run.py
python3 tests/sanitize.py
```
