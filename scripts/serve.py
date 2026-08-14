# -*- coding: utf-8 -*-
"""Servidor local do dist/ — acessível na rede (celular via mDNS).

Uso:  py -3 scripts/serve.py [porta]     (padrão: 8080)
Acesse do celular:  http://<hostname>.local:8080
"""
import os
import re
import socket
import sys
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

DIST = Path(__file__).resolve().parent.parent / "dist"
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8080


class Handler(SimpleHTTPRequestHandler):
    """SimpleHTTPRequestHandler + HTTP Range (necessário p/ <video>)."""

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        self.send_header("Accept-Ranges", "bytes")
        super().end_headers()

    def send_head(self):
        rng = self.headers.get("Range")
        path = self.translate_path(self.path)
        if os.path.isdir(path):
            path = os.path.join(path, "index.html")
        if not (rng and os.path.isfile(path)):
            return super().send_head()
        m = re.match(r"bytes=(\d*)-(\d*)", rng)
        if not m:
            return super().send_head()
        size = os.path.getsize(path)
        start = int(m.group(1)) if m.group(1) else 0
        end = int(m.group(2)) if m.group(2) else size - 1
        end = min(end, size - 1)
        if start > end:
            self.send_error(416)
            return None
        f = open(path, "rb")
        f.seek(start)
        self.range_len = end - start + 1
        self.send_response(206)
        self.send_header("Content-Type", self.guess_type(path))
        self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.send_header("Content-Length", str(self.range_len))
        self.end_headers()
        return f

    def copyfile(self, source, outputfile):
        if hasattr(self, "range_len"):
            n = self.range_len
            del self.range_len
            while n > 0:
                chunk = source.read(min(65536, n))
                if not chunk:
                    break
                outputfile.write(chunk)
                n -= len(chunk)
        else:
            super().copyfile(source, outputfile)

    def log_message(self, fmt, *args):
        pass  # silencioso


if __name__ == "__main__":
    if not DIST.exists():
        sys.exit("dist/ nao existe — rode antes: py -3 scripts/build.py")
    host = socket.gethostname().lower()
    srv = ThreadingHTTPServer(("0.0.0.0", PORT),
                              partial(Handler, directory=str(DIST)))
    print(f"Servindo {DIST}")
    print(f"  local:   http://localhost:{PORT}")
    print(f"  celular: http://{host}.local:{PORT}")
    srv.serve_forever()
