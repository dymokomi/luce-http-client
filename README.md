# luce-http-client

Native Luce Base HTTP/1.1 client. MIT OR Apache-2.0.
Cleartext requests use numeric IPv4 addresses. The `https` export uses native
TLS 1.3 with an explicitly supplied P-256 issuer pin; this is **not** general
public-CA trust, and there is no redirect handling or connection pool.

Cleartext `request`, `get` and `post` accept `timeout_ms` (default 30000) and an
optional borrowed `net.Cancellation*`. One absolute deadline covers connection,
request writes and response reads; partial progress does not restart it. Zero
means an immediate deadline; overflowing durations are rejected. Operations use
the pinned standard library's nonblocking connection/deadline stream. Keep any
cancellation object alive until the call returns. Timeout/cancellation closes
the connection and is an error, never partial success; discard the output buffer.
These options do **not** yet apply to the separate HTTPS/TLS path.

Both clients use one bounded incremental response decoder over the standard
library HTTP framing APIs. It handles fixed length, chunked (including validated
trailers), EOF-delimited and up to eight interim responses. Malformed framing,
truncation and output overflow fail instead of returning partial success. Heads
are limited to 32 KiB; cleartext output capacity is capped at 64 MiB, HTTPS at the supplied
output buffer size. Smaller caller buffers remain hard bounds; the client does not
allocate a maximum-size buffer automatically. This is buffered, not streaming
package installation. Discard output after any error. Completion stops at the framed
response boundary; coalesced extra bytes are rejected, but a separate later
response is not read. Upgrades and CONNECT tunnels are unsupported.

HTTPS request headers use the bounded standard encoder; bodies are sent in
16 KiB TLS records. Established connections close on success and failure.
Underlying TLS trust, alerts, timeouts, secret lifecycle and independent-server
interoperability still require further audit before production package downloads.

Tests cover every fixed/chunked fixture truncation, fragmentation sizes, malformed
lengths/chunks/trailers, request injection, and independent Python socket framing.
Cleartext tests also cover silent and continuously dripping peers, zero/overflow
timeouts, pre-request/in-flight cancellation, and successful requests afterward.
Large-transfer fixtures compare every byte of 17 MiB fixed/chunked/EOF responses,
the exact 64 MiB bound, and upload/download of a real tracked compiler bootstrap
source. Oversized output capacity and smaller-buffer overflow are rejected.
The native HTTPS fixture uses ephemeral test credentials; it is not independent
TLS interoperability evidence. All fixtures run in six compiler modes and under
ASan/UBSan. No language sources are changed.

```sh
python3 tools/bootstrap.py
python3 tests/run.py
python3 tests/sanitize.py
```
