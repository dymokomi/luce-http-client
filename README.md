# luce-http-client

Native Luce Base HTTP/1.1 client. MIT OR Apache-2.0.
First slice: cleartext requests to a numeric IPv4 address. No DNS, redirects or
TLS. Verified HTTPS is `luce-tls` / M3b remaining work.

```sh
python3 tools/bootstrap.py
python3 tests/run.py
python3 tests/sanitize.py
```
