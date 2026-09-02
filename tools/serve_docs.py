"""Локальный сервер предпросмотра GrafMaster.

Открывает папку docs (макеты, галерея, документы) в браузере:
http://127.0.0.1:8899/UI_MOCKUPS.html
"""
import os
import socketserver
import threading
import webbrowser
from http.server import SimpleHTTPRequestHandler
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "docs"
PORT = 8899

os.chdir(ROOT)


class Handler(SimpleHTTPRequestHandler):
    def log_message(self, fmt, *args):  # noqa: N802
        pass


def main() -> None:
    handler = Handler
    httpd = socketserver.TCPServer(("127.0.0.1", PORT), handler)
    url = f"http://127.0.0.1:{PORT}/UI_MOCKUPS.html"
    print("GrafMaster preview server:", url)
    threading.Timer(0.5, lambda: webbrowser.open(url)).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
