"""Popup flotante para mensajes de posicionamiento facial en Tkinter.

- Animacion fade in / fade out.
- Duracion total configurable (por defecto 5 segundos).
- No bloquea la UI principal.
"""

from __future__ import annotations

import queue
import threading
import tkinter as tk
from dataclasses import dataclass
from typing import Optional


@dataclass
class PopupRequest:
    message: str
    duration_ms: int


class MessagePopup:
    """Gestiona popups efimeros sin bloquear la UI principal."""

    def __init__(
        self,
        root: tk.Misc,
        width: int = 420,
        height: int = 82,
        fade_in_ms: int = 350,
        fade_out_ms: int = 550,
        poll_interval_ms: int = 100,
    ) -> None:
        self.root = root
        self.width = width
        self.height = height
        self.fade_in_ms = max(50, fade_in_ms)
        self.fade_out_ms = max(50, fade_out_ms)
        self.poll_interval_ms = max(30, poll_interval_ms)

        self._queue: "queue.Queue[PopupRequest]" = queue.Queue()
        self._current_popup: Optional[tk.Toplevel] = None
        self._main_thread = threading.main_thread()

        self._schedule_queue_processing()

    def _schedule_queue_processing(self) -> None:
        self.root.after(self.poll_interval_ms, self._process_queue)

    def _process_queue(self) -> None:
        try:
            if self._current_popup is None:
                request = self._queue.get_nowait()
                self._show_popup(request.message, request.duration_ms)
        except queue.Empty:
            pass
        finally:
            self._schedule_queue_processing()

    def show(self, message: str, duration_ms: int = 5000) -> None:
        """API publica para mostrar mensaje sin bloquear.

        Puede invocarse desde la UI principal o desde otro hilo.
        """
        request = PopupRequest(message=message, duration_ms=max(1000, duration_ms))
        self._queue.put(request)

    def _show_popup(self, message: str, duration_ms: int) -> None:
        if self._current_popup is not None:
            try:
                self._current_popup.destroy()
            except Exception:
                pass
            self._current_popup = None

        popup = tk.Toplevel(self.root)
        popup.overrideredirect(True)
        popup.attributes("-topmost", True)
        popup.configure(bg="#111827")

        # Posicion centrada en la ventana principal.
        self.root.update_idletasks()
        x = self.root.winfo_rootx() + (self.root.winfo_width() - self.width) // 2
        y = self.root.winfo_rooty() + int(self.root.winfo_height() * 0.12)
        popup.geometry(f"{self.width}x{self.height}+{x}+{y}")

        frame = tk.Frame(popup, bg="#111827", highlightthickness=2, highlightbackground="#f59e0b")
        frame.pack(fill="both", expand=True)

        tk.Label(
            frame,
            text=message,
            bg="#111827",
            fg="#f9fafb",
            font=("Segoe UI", 11, "bold"),
            wraplength=self.width - 30,
            justify="center",
        ).pack(expand=True, fill="both", padx=14, pady=12)

        self._current_popup = popup

        try:
            popup.attributes("-alpha", 0.0)
        except Exception:
            # Algunas plataformas no soportan alpha en toplevel.
            popup.attributes("-alpha", 1.0)

        self._fade_in(popup, on_done=lambda: self._hold_then_fade_out(popup, duration_ms))

    def _fade_in(self, popup: tk.Toplevel, on_done) -> None:
        steps = 12
        delay = max(10, self.fade_in_ms // steps)

        def step(i: int = 0) -> None:
            if popup != self._current_popup:
                return
            alpha = min(1.0, i / steps)
            try:
                popup.attributes("-alpha", alpha)
            except Exception:
                pass
            if i < steps:
                popup.after(delay, lambda: step(i + 1))
            else:
                on_done()

        step()

    def _hold_then_fade_out(self, popup: tk.Toplevel, duration_ms: int) -> None:
        visible_ms = max(200, duration_ms - self.fade_in_ms - self.fade_out_ms)
        popup.after(visible_ms, lambda: self._fade_out(popup))

    def _fade_out(self, popup: tk.Toplevel) -> None:
        steps = 14
        delay = max(10, self.fade_out_ms // steps)

        def step(i: int = 0) -> None:
            if popup != self._current_popup:
                return
            alpha = max(0.0, 1.0 - (i / steps))
            try:
                popup.attributes("-alpha", alpha)
            except Exception:
                pass
            if i < steps:
                popup.after(delay, lambda: step(i + 1))
            else:
                try:
                    popup.destroy()
                except Exception:
                    pass
                if popup == self._current_popup:
                    self._current_popup = None

        step()


if __name__ == "__main__":
    # Demo rapida local
    root = tk.Tk()
    root.geometry("640x360")
    root.title("Demo MessagePopup")

    popup = MessagePopup(root)

    tk.Button(
        root,
        text="Mostrar mensaje",
        command=lambda: popup.show("Ajusta tu rostro dentro del ovalo para continuar", duration_ms=5000),
    ).pack(pady=24)

    root.mainloop()
