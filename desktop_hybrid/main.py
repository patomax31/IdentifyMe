from __future__ import annotations

import socket
import sys
import threading
import time
from contextlib import closing
from dataclasses import dataclass, field
from typing import Optional
from urllib.request import Request, urlopen

import webview
from webview.errors import WebViewException
from werkzeug.serving import make_server

from flask_server import _admin_panel_dist_ready, create_app


# ── Configuración de ventana ──────────────────────────────────────────────
HOST         = "127.0.0.1"
PORT         = 5000
WIN_WIDTH    = 420
WIN_HEIGHT   = 800
WIN_TITLE    = "IdentifyMe"

# ── HTML del splash (logo + texto + barra de progreso) ───────────────────
SPLASH_HTML = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    background: #0D1B2A;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100vh;
    font-family: 'Inter', system-ui, sans-serif;
    color: #fff;
    user-select: none;
  }

  .logo-wrap {
    width: 88px;
    height: 88px;
    border-radius: 24px;
    background: linear-gradient(135deg, #1A56DB, #0EA5E9);
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 22px;
    box-shadow: 0 8px 32px rgba(26,86,219,0.45);
  }

  .logo-wrap svg {
    width: 48px;
    height: 48px;
    fill: none;
    stroke: #fff;
    stroke-width: 2;
    stroke-linecap: round;
    stroke-linejoin: round;
  }

  h1 {
    font-size: 32px;
    font-weight: 800;
    letter-spacing: -0.5px;
    margin-bottom: 6px;
  }

  .subtitle {
    font-size: 13px;
    color: rgba(255,255,255,0.55);
    font-weight: 500;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    margin-bottom: 48px;
  }

  .bar-track {
    width: 240px;
    height: 5px;
    background: rgba(255,255,255,0.12);
    border-radius: 999px;
    overflow: hidden;
    margin-bottom: 14px;
  }

  .bar-fill {
    height: 100%;
    width: 0%;
    background: linear-gradient(90deg, #1A56DB, #0EA5E9);
    border-radius: 999px;
    transition: width 0.3s ease;
  }

  .status-text {
    font-size: 12px;
    color: rgba(255,255,255,0.45);
    font-weight: 500;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    min-height: 18px;
  }
</style>
</head>
<body>
  <div class="logo-wrap">
    <!-- ícono: scan-face estilo Lucide -->
    <svg viewBox="0 0 24 24">
      <path d="M3 7V5a2 2 0 0 1 2-2h2"/>
      <path d="M17 3h2a2 2 0 0 1 2 2v2"/>
      <path d="M21 17v2a2 2 0 0 1-2 2h-2"/>
      <path d="M7 21H5a2 2 0 0 1-2-2v-2"/>
      <circle cx="12" cy="10" r="3"/>
      <path d="M7 16.8A6 6 0 0 1 12 14a6 6 0 0 1 5 2.8"/>
    </svg>
  </div>

  <h1>IdentifyMe</h1>
  <p class="subtitle">Sistema biométrico escolar</p>

  <div class="bar-track">
    <div class="bar-fill" id="bar"></div>
  </div>
  <p class="status-text" id="status">Iniciando...</p>

  <script>
    const steps = [
      [15,  "Cargando módulos..."],
      [35,  "Iniciando servidor..."],
      [60,  "Verificando cámara..."],
      [80,  "Preparando interfaz..."],
      [95,  "Casi listo..."],
    ];
    let i = 0;
    const bar    = document.getElementById('bar');
    const status = document.getElementById('status');

    function advance() {
      if (i < steps.length) {
        const [pct, msg] = steps[i++];
        bar.style.width  = pct + '%';
        status.textContent = msg;
        setTimeout(advance, 600 + Math.random() * 400);
      }
    }
    advance();
  </script>
</body>
</html>"""

# ── HTML de error visual ──────────────────────────────────────────────────
def error_html(title: str, detail: str, hint: str = "") -> str:
    hint_block = f'<p class="hint">{hint}</p>' if hint else ""
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    background: #0D1B2A;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100vh;
    font-family: 'Inter', system-ui, sans-serif;
    color: #fff;
    padding: 32px;
    text-align: center;
  }}
  .icon {{
    width: 72px; height: 72px;
    border-radius: 50%;
    background: rgba(185,28,28,0.18);
    border: 2px solid rgba(185,28,28,0.5);
    display: flex; align-items: center; justify-content: center;
    margin-bottom: 24px;
  }}
  .icon svg {{
    width: 36px; height: 36px;
    stroke: #FCA5A5; stroke-width: 2;
    stroke-linecap: round; stroke-linejoin: round; fill: none;
  }}
  h2 {{
    font-size: 20px; font-weight: 800;
    color: #FCA5A5; margin-bottom: 10px;
  }}
  .detail {{
    font-size: 13px; color: rgba(255,255,255,0.55);
    line-height: 1.6; margin-bottom: 16px;
    max-width: 320px;
  }}
  .hint {{
    font-size: 12px;
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 10px;
    padding: 10px 16px;
    color: rgba(255,255,255,0.45);
    line-height: 1.6;
    max-width: 320px;
  }}
</style>
</head>
<body>
  <div class="icon">
    <svg viewBox="0 0 24 24">
      <circle cx="12" cy="12" r="10"/>
      <line x1="12" y1="8" x2="12" y2="12"/>
      <line x1="12" y1="16" x2="12.01" y2="16"/>
    </svg>
  </div>
  <h2>{title}</h2>
  <p class="detail">{detail}</p>
  {hint_block}
</body>
</html>"""


# ── Estado del servidor ───────────────────────────────────────────────────
@dataclass
class ServerState:
    server:        Optional[object]           = None
    thread:        Optional[threading.Thread] = None
    startup_error: Optional[str]              = None


# ── Utilidades de red ─────────────────────────────────────────────────────
def is_port_available(host: str, port: int) -> bool:
    """Devuelve True si el puerto TCP está libre."""
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind((host, port))
            return True
        except OSError:
            return False


def start_flask_server(state: ServerState) -> None:
    """Ejecuta Flask en hilo dedicado con servidor WSGI controlable."""
    try:
        app = create_app()
        http_server = make_server(HOST, PORT, app)
        state.server = http_server
        http_server.serve_forever()
    except Exception as exc:
        state.startup_error = str(exc)
        print(f"[ERROR] Flask no pudo iniciar: {exc}")


def wait_for_server(timeout_seconds: float = 12.0) -> bool:
    """Hace polling a /status hasta que el servidor responde o expira."""
    url      = f"http://{HOST}:{PORT}/status"
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
    """Detiene Flask y espera a que el hilo termine."""
    if state.server is not None:
        try:
            state.server.shutdown()
        except Exception as exc:
            print(f"[WARN] Error al detener servidor Flask: {exc}")

    if state.thread is not None and state.thread.is_alive():
        state.thread.join(timeout=3)


# ── Punto de entrada principal ────────────────────────────────────────────
def run_desktop_app() -> int:

    # 1. Verificar puerto disponible
    if not is_port_available(HOST, PORT):
        win = webview.create_window(
            title=WIN_TITLE,
            html=error_html(
                title="Puerto ocupado",
                detail=f"El puerto {PORT} ya está en uso. Cierra la aplicación que lo ocupa e intenta de nuevo.",
                hint=f"Puedes identificar el proceso con: lsof -i :{PORT}  (macOS/Linux)  o  netstat -ano | findstr :{PORT}  (Windows)",
            ),
            width=WIN_WIDTH,
            height=WIN_HEIGHT,
            resizable=False,
        )
        webview.start(gui="qt", debug=False)
        return 1

    # 2. Mostrar splash mientras arranca Flask
    splash = webview.create_window(
        title=WIN_TITLE,
        html=SPLASH_HTML,
        width=WIN_WIDTH,
        height=WIN_HEIGHT,
        resizable=False,
    )

    state = ServerState()
    state.thread = threading.Thread(
        target=start_flask_server, args=(state,), daemon=True
    )

    def _on_splash_shown():
        """Se ejecuta cuando el splash ya es visible; inicia Flask en paralelo."""
        state.thread.start()
        ready = wait_for_server()

        if not ready:
            detail = state.startup_error or "Tiempo de espera agotado al iniciar Flask."
            splash.load_html(
                error_html(
                    title="No se pudo iniciar",
                    detail=detail,
                    hint="Revisa la consola para más detalles del error.",
                )
            )
            return

        # 3. Flask listo → cargar la app real en la misma ventana
        target_path = "/admin-panel/" if _admin_panel_dist_ready() else "/"
        splash.load_url(f"http://{HOST}:{PORT}{target_path}")

    # El evento `shown` dispara _on_splash_shown en un hilo separado
    splash.events.shown += _on_splash_shown

    try:
        webview.start(gui="qt", debug=False)
    except WebViewException as exc:
        print("[ERROR] No se pudo iniciar PyWebview con backend Qt.")
        print(f"[ERROR] Detalle: {exc}")
        print("[HINT] Instala dependencias: pip install qtpy PyQt6 PyQt6-WebEngine")
        return 1
    finally:
        stop_server(state)

    return 0


if __name__ == "__main__":
    sys.exit(run_desktop_app())