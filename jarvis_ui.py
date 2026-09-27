"""
Small helper the JARVIS Python backend can import.

Add near the top of jarvis.py:
    import jarvis_ui
    jarvis_ui.start()

Then call:
    jarvis_ui.set_state("listening")
    jarvis_ui.set_state("thinking")
    jarvis_ui.set_state("speaking")
    jarvis_ui.set_state("standby")

For the command card:
    jarvis_ui.set_command("open YouTube")

For the visualizer:
    jarvis_ui.set_audio_level(0.0 to 1.0)
"""

from __future__ import annotations
import json
import threading
from urllib.request import Request, urlopen

URL = "http://127.0.0.1:8765/api/event"

_server_started = False
_lock = threading.Lock()


def start() -> None:
    global _server_started
    with _lock:
        if _server_started:
            return
        _server_started = True

    # Start the UI server only once, without blocking Jarvis.
    from bridge_server import main
    threading.Thread(target=main, daemon=True).start()


def _send(payload: dict) -> None:
    try:
        body = json.dumps(payload).encode("utf-8")
        req = Request(
            URL,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(req, timeout=0.15):
            pass
    except Exception:
        # The backend must keep working even if the UI is closed.
        pass


def set_state(state: str) -> None:
    _send({"state": state})


def set_command(command: str) -> None:
    _send({"command": command})


def set_audio_level(level: float) -> None:
    _send({"audio_level": max(0.0, min(1.0, float(level)))})
