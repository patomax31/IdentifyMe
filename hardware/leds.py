"""Control de LEDs para feedback de acceso.

Soporta Raspberry Pi con RPi.GPIO y fallback simulado en desarrollo.
"""

from __future__ import annotations

import os
import threading
import time
from typing import Optional


class _MockGPIO:
    BCM = "BCM"
    OUT = "OUT"
    LOW = 0
    HIGH = 1

    def setwarnings(self, _state: bool) -> None:
        pass

    def setmode(self, mode) -> None:
        print(f"[leds:MOCK] setmode({mode})")

    def setup(self, pin: int, mode) -> None:
        print(f"[leds:MOCK] setup(pin={pin}, mode={mode})")

    def output(self, pin: int, value: int) -> None:
        state = "ON" if value else "OFF"
        print(f"[leds:MOCK] pin {pin} -> {state}")

    def cleanup(self, pin: Optional[int] = None) -> None:
        print(f"[leds:MOCK] cleanup(pin={pin})")


class LEDController:
    """Controla LEDs de estado (verde/rojo)."""

    def __init__(self) -> None:
        self.green_pin = int(os.getenv("GPIO_LED_GREEN", "23"))
        self.red_pin = int(os.getenv("GPIO_LED_RED", "24"))
        self.enabled = os.getenv("HARDWARE_ENABLED", "1").strip() != "0"
        self._gpio = self._load_gpio_backend()
        self._setup_done = False
        self._lock = threading.Lock()

    def _load_gpio_backend(self):
        if not self.enabled:
            return _MockGPIO()

        try:
            import RPi.GPIO as GPIO  # type: ignore

            return GPIO
        except Exception as exc:
            print(f"[leds] GPIO no disponible, modo simulado: {exc}")
            return _MockGPIO()

    def setup(self) -> None:
        if self._setup_done:
            return

        self._gpio.setwarnings(False)
        self._gpio.setmode(self._gpio.BCM)
        self._gpio.setup(self.green_pin, self._gpio.OUT)
        self._gpio.setup(self.red_pin, self._gpio.OUT)
        self.off_all()
        self._setup_done = True

    def off_all(self) -> None:
        self._gpio.output(self.green_pin, self._gpio.LOW)
        self._gpio.output(self.red_pin, self._gpio.LOW)

    def signal_success(self, duration: float = 1.5) -> None:
        self.setup()
        with self._lock:
            self.off_all()
            self._gpio.output(self.green_pin, self._gpio.HIGH)
            time.sleep(max(0.0, duration))
            self._gpio.output(self.green_pin, self._gpio.LOW)

    def signal_invalid(self, duration: float = 1.5) -> None:
        self.setup()
        with self._lock:
            self.off_all()
            self._gpio.output(self.red_pin, self._gpio.HIGH)
            time.sleep(max(0.0, duration))
            self._gpio.output(self.red_pin, self._gpio.LOW)

    def cleanup(self) -> None:
        try:
            self.off_all()
        except Exception:
            pass
        try:
            self._gpio.cleanup()
        except Exception as exc:
            print(f"[leds] Error en cleanup: {exc}")
        finally:
            self._setup_done = False


_controller = LEDController()


def leds_turnon(success: bool = True, use_red_for_invalid: bool = True, non_blocking: bool = True) -> None:
    """Enciende LED segun resultado de acceso.

    Args:
        success: True para LED verde, False para acceso invalido.
        use_red_for_invalid: Si False, no se usa LED rojo en denegacion.
        non_blocking: Ejecuta en thread para no bloquear UI.
    """

    def _job() -> None:
        try:
            if success:
                _controller.signal_success()
            elif use_red_for_invalid:
                _controller.signal_invalid()
        except Exception as exc:
            print(f"[leds] Error al encender LED: {exc}")

    if non_blocking:
        threading.Thread(target=_job, daemon=True).start()
    else:
        _job()


def cleanup() -> None:
    """Limpia GPIO para salida segura."""
    _controller.cleanup()
