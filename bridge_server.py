"""
JARVIS frontend bridge.

Run this server from the same folder as index.html/style.css/script.js:
    python bridge_server.py

Then open:
    http://127.0.0.1:8765

Your Python JARVIS backend can update the UI by importing jarvis_ui:

    import jarvis_ui
    jarvis_ui.start()

    jarvis_ui.set_state("listening")
    jarvis_ui.set_command("open YouTube")
    jarvis_ui.set_audio_level(0.72)

States:
    standby
    listening
    thinking
    speaking

This bridge is intentionally dependency-free: only the Python standard library.
"""

from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import json
import threading
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
HOST = "127.0.0.1"
PORT = 8765

_state = {
    "state": "standby",
    "command": "",
    "audio_level": 0.03,
}
_lock = threading.Lock()


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def log_message(self, format, *args):
        pass

    def _json(self, payload, status=200):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/state":
            with _lock:
                payload = dict(_state)
            return self._json(payload)
        return super().do_GET()

    def do_POST(self):
        path = urlparse(self.path).path
        if path != "/api/event":
            return self._json({"ok": False, "error": "Not found"}, 404)

        try:
            length = int(self.headers.get("Content-Length", "0"))
            data = json.loads(self.rfile.read(length) or b"{}")
        except (ValueError, json.JSONDecodeError):
            return self._json({"ok": False, "error": "Invalid JSON"}, 400)

        with _lock:
            if "state" in data:
                _state["state"] = str(data["state"])
            if "command" in data:
                _state["command"] = str(data["command"])
            if "audio_level" in data:
                try:
                    _state["audio_level"] = max(0.0, min(1.0, float(data["audio_level"])))
                except (TypeError, ValueError):
                    pass

        return self._json({"ok": True})


def main():
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"JARVIS UI: http://{HOST}:{PORT}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
