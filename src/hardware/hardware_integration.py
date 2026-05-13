"""Orquesta audio, leds y servomotor para eventos del sistema."""

from __future__ import annotations

from typing import Callable

from . import audio, leds, servomotor


class HardwareIntegration:
    """Fachada de hardware para eventos de la app."""

    def __init__(self, enabled: bool = True) -> None:
        self.enabled = enabled

    def startup(self) -> None:
        self._safe_call(audio.start_up)

    def success(self) -> None:
        self._safe_call(audio.access_successful)
        self._safe_call(lambda: leds.leds_turnon(success=True))
        self._safe_call(servomotor.access_successful)

    def error(self) -> None:
        self._safe_call(audio.access_invalid)
        self._safe_call(lambda: leds.leds_turnon(success=False))

    def access_successful(self) -> None:
        self.success()

    def access_invalid(self) -> None:
        self.error()

    def registration(self) -> None:
        self._safe_call(audio.registration)
        self._safe_call(lambda: leds.leds_turnon(success=True))

    def cleanup(self) -> None:
        self._safe_call(audio.cleanup)
        self._safe_call(leds.cleanup)
        self._safe_call(servomotor.cleanup)

    def _safe_call(self, fn: Callable[[], None]) -> None:
        if not self.enabled:
            return
        try:
            fn()
        except Exception as exc:
            print(f"[hardware] Error en evento: {exc}")
