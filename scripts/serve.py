# -*- coding: utf-8 -*-
"""Servidor local do dist/ — acessível na rede (celular via mDNS).

Uso:  py -3 scripts/serve.py [porta]     (padrão: 8080)
Acesse do celular:  http://<hostname>.local:8080
"""
import socket
import sys
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

DIST = Path(__file__).resolve().parent.parent / "dist"
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8080


class Handler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

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
