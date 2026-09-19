#!/usr/bin/env python3
"""Independent cleartext HTTP origin for the native client."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import sys
import time
from pathlib import Path


class Origin(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        if self.path.startswith('/large-') or self.path == '/bootstrap':
            self.close_connection = True
            try:
                if self.path == '/bootstrap':
                    source = Path(__file__).resolve().parents[2] / 'luce-base/bootstrap/luce-base-arm64-macos.c'
                    body = source.read_bytes()
                    self.wfile.write(b'HTTP/1.1 200 OK\r\nContent-Length: ' + str(len(body)).encode() + b'\r\n\r\n' + body)
                    return
                total = 67108864 if self.path == '/large-max' else 17825795
                chunked = self.path == '/large-chunked'
                head = b'HTTP/1.1 200 OK\r\nConnection: close\r\n'
                if chunked: head += b'Transfer-Encoding: chunked\r\n'
                elif self.path != '/large-eof': head += b'Content-Length: ' + str(total).encode() + b'\r\n'
                self.wfile.write(head + b'\r\n')
                block = bytes(range(251)) * 261
                remaining = total
                while remaining:
                    part = block[:min(remaining, len(block))]
                    if chunked: self.wfile.write(f'{len(part):x}\r\n'.encode())
                    self.wfile.write(part)
                    if chunked: self.wfile.write(b'\r\n')
                    remaining -= len(part)
                if chunked: self.wfile.write(b'0\r\n\r\n')
            except (BrokenPipeError, ConnectionResetError):
                pass
            return
        if self.path in ('/stall', '/drip'):
            self.close_connection = True
            try:
                if self.path == '/stall':
                    time.sleep(1)
                else:
                    # Continuous progress must not reset the request deadline.
                    for byte in b'HTTP/1.1 200 OK\r\nContent-Length: 5\r\n\r\nhello':
                        self.wfile.write(bytes([byte]))
                        self.wfile.flush()
                        time.sleep(.04)
            except (BrokenPipeError, ConnectionResetError):
                pass
            return
        raw = {
            '/chunked': b'HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\n\r\n2\r\nhe\r\n3\r\nllo\r\n0\r\n\r\n',
            '/eof': b'HTTP/1.1 200 OK\r\nConnection: close\r\n\r\nhello',
            '/truncated': b'HTTP/1.1 200 OK\r\nContent-Length: 9\r\n\r\nhello',
            '/bad-chunk': b'HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\n\r\n5\r\nhelloXX',
            '/oversized': b'HTTP/1.1 200 OK\r\nContent-Length: 4097\r\n\r\n',
        }
        if self.path in raw:
            self.close_connection = True
            try:
                for byte in raw[self.path]:
                    self.wfile.write(bytes([byte]))
                    self.wfile.flush()
                    time.sleep(0.001)
            except (BrokenPipeError, ConnectionResetError):
                pass  # Rejection can close the client before the fixture finishes.
            return
        if self.path == "/hello":
            body = b"hello"
        elif self.path == "/headers":
            auth = self.headers.get("Authorization", "")
            forwarded = self.headers.get("X-Forwarded-For", "")
            body = f"Authorization={auth}\nX-Forwarded-For={forwarded}\n".encode()
        else:
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        payload = self.rfile.read(length)
        self.send_response(200)
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(payload)


def main():
    server = ThreadingHTTPServer(("127.0.0.1", 0), Origin)
    print(server.server_address[1], flush=True)
    server.serve_forever()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
