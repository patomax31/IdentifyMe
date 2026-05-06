from __future__ import annotations

import socket
import sys
import threading
import time
from contextlib import closing
from dataclasses import dataclass
from typing import Optional
from urllib.request import Request, urlopen

import webview
from webview.errors import WebViewException
from werkzeug.serving import make_server

from flask_server import create_app


HOST = "127.0.0.1"
PORT = 5000


@dataclass
class ServerState:
    server: Optional[object] = None
    thread: Optional[threading.Thread] = None
    startup_error: Optional[str] = None


def is_port_available(host: str, port: int) -> bool:
    """Return True when a TCP port can be bound locally."""
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind((host, port))
            return True
        except OSError:
            return False


def start_flask_server(state: ServerState) -> None:
    """Run Flask in a dedicated thread using a controllable WSGI server."""
    try:
        app = create_app()
        http_server = make_server(HOST, PORT, app)
        state.server = http_server
        http_server.serve_forever()
    except Exception as exc:  # pragma: no cover
        state.startup_error = str(exc)
        print(f"[ERROR] Flask no pudo iniciar: {exc}")


def wait_for_server(timeout_seconds: float = 12.0) -> bool:
    """Poll /status until server is ready or timeout expires."""
    url = f"http://{HOST}:{PORT}/status"
    deadline = time.monotonic() + timeout_seconds

    while time.monotonic() < deadline:
        try:
            req = Request(url, method="GET")
            with urlopen(req, timeout=1.0) as response:
                if response.status == 200:
                    return True
        except Exception:
            time.sleep(0.25)

    return False


def stop_server(state: ServerState) -> None:
    """Gracefully stop Flask server and join thread."""
    if state.server is not None:
        try:
            state.server.shutdown()
        except Exception as exc:
            print(f"[WARN] Error al detener servidor Flask: {exc}")

    if state.thread is not None and state.thread.is_alive():
        state.thread.join(timeout=3)


def run_desktop_app() -> int:
    if not is_port_available(HOST, PORT):
        print(f"[ERROR] El puerto {PORT} no esta disponible. Cierra la app que lo use e intenta de nuevo.")
        return 1

    state = ServerState()
    state.thread = threading.Thread(target=start_flask_server, args=(state,), daemon=True)
    state.thread.start()

    if not wait_for_server():
        detail = state.startup_error or "Tiempo de espera agotado al iniciar Flask"
        print(f"[ERROR] Flask no esta listo: {detail}")
        stop_server(state)
        return 1

    window = webview.create_window(
        title="IdentifyMe",
        url=f"http://{HOST}:{PORT}/",
        width=900,
        height=600,
    )

    try:
        # Debug desactivado para entorno de produccion.
        webview.start(gui="qt", debug=False)
    except WebViewException as exc:
        print("[ERROR] No se pudo iniciar PyWebview con backend Qt.")
        print(f"[ERROR] Detalle: {exc}")
        print("[HINT] Instala dependencias Python: pip install qtpy PyQt6 PyQt6-WebEngine")
        return 1
    finally:
        stop_server(state)

    return 0


if __name__ == "__main__":
    sys.exit(run_desktop_app())
