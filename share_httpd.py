#!/usr/bin/env python3
"""Minimal shared text board for several AI assistants on one home network.

GET any .txt/.md file in this directory (GET / lists them).
PUT or POST only SHARE_<name>.txt (letters, digits, underscore, hyphen).
BOARD.txt is read-only over HTTP so one seat cannot wipe the instructions.
"""

from __future__ import annotations

import json
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parent
MAX_BYTES = 64_000
HOST = "0.0.0.0"
PORT = 9878
SHARE_NAME = re.compile(r"^SHARE_[A-Za-z0-9_-]{1,40}\.txt$")


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:
        print("%s - %s" % (self.address_string(), fmt % args), flush=True)

    def _rel(self) -> str:
        path = unquote(urlparse(self.path).path)
        name = Path(path).name
        return name if path in ("/" + name, name) else ""

    def _json(self, code: int, payload: dict) -> None:
        data = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:
        rel = self._rel()
        if self.path.rstrip("/") in ("", "/"):
            names = sorted(p.name for p in ROOT.iterdir() if p.is_file() and p.suffix in {".txt", ".md"})
            body = ("\n".join(names) + "\n").encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        path = ROOT / rel
        if not rel or not path.is_file():
            self.send_error(404)
            return
        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_PUT(self) -> None:
        self._write()

    def do_POST(self) -> None:
        self._write()

    def _write(self) -> None:
        name = self._rel()
        if not SHARE_NAME.match(name):
            self._json(403, {"ok": False, "error": "only SHARE_<name>.txt"})
            return
        length = int(self.headers.get("Content-Length", "0") or 0)
        if length <= 0 or length > MAX_BYTES:
            self._json(413, {"ok": False, "error": "empty or too large"})
            return
        data = self.rfile.read(length)
        (ROOT / name).write_bytes(data)
        self._json(200, {"ok": True, "wrote": name, "bytes": len(data), "from": self.client_address[0]})


def main() -> None:
    ThreadingHTTPServer.allow_reuse_address = True
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"share board http://0.0.0.0:{PORT}/", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
