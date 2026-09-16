#!/usr/bin/env python3
"""Independent cleartext HTTP origin for the native client."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import sys


class Origin(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_GET(self):
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
