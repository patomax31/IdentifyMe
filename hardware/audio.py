"""Control de audio para eventos del sistema de acceso.

Backends soportados:
1) GPIO buzzer pasivo (PWM) con RPi.GPIO
2) Fallback simulado (log + campana terminal)

Cada evento tiene un patron sonoro distinto.
"""

from __future__ import annotations

import os
import threading
import time
from typing import Dict, List, Optional, Tuple

Tone = Tuple[int, float, float]


class _MockPWM:
    def __init__(self, pin: int, frequency: float) -> None:
        self.pin = pin
        self.frequency = frequency

    def start(self, duty_cycle: float) -> None:
        print(f"[audio:MOCK] PWM start pin={self.pin}, duty={duty_cycle}")

    def ChangeFrequency(self, frequency: float) -> None:
        print(f"[audio:MOCK] freq -> {frequency}Hz")

    def ChangeDutyCycle(self, duty_cycle: float) -> None:
        print(f"[audio:MOCK] duty -> {duty_cycle}")

    def stop(self) -> None:
        print("[audio:MOCK] PWM stop")


class _MockGPIO:
    BCM = "BCM"
    OUT = "OUT"

    def setwarnings(self, _state: bool) -> None:
        pass

    def setmode(self, mode) -> None:
        print(f"[audio:MOCK] setmode({mode})")

    def setup(self, pin: int, mode) -> None:
        print(f"[audio:MOCK] setup(pin={pin}, mode={mode})")

    def PWM(self, pin: int, frequency: float) -> _MockPWM:
        return _MockPWM(pin, frequency)

    def cleanup(self, pin: Optional[int] = None) -> None:
        print(f"[audio:MOCK] cleanup(pin={pin})")


class AudioController:
    """Controlador de audio basado en patrones tonales."""

    PATTERNS: Dict[str, List[Tone]] = {
        "start_up": [(880, 0.09, 0.03), (1175, 0.09, 0.02), (1568, 0.12, 0.00)],
        "shut_down": [(784, 0.09, 0.02), (587, 0.10, 0.03), (392, 0.14, 0.00)],
        "access_successful": [(1000, 0.07, 0.03), (1300, 0.07, 0.00)],
        "access_invalid": [(350, 0.12, 0.05), (280, 0.16, 0.00)],
        "button_select": [(1200, 0.05, 0.00)],
        "registration": [(900, 0.06, 0.03), (1100, 0.06, 0.03), (900, 0.10, 0.00)],
    }

    def __init__(self) -> None:
        self.pin = int(os.getenv("GPIO_BUZZER_PIN", "22"))
        self.base_frequency = float(os.getenv("GPIO_BUZZER_BASE_FREQ", "440"))
        self.enabled = os.getenv("HARDWARE_ENABLED", "1").strip() != "0"
        self._gpio = self._load_gpio_backend()
        self._pwm = None
        self._setup_done = False
        self._lock = threading.Lock()

    def _load_gpio_backend(self):
        if not self.enabled:
            return _MockGPIO()

        try:
            import RPi.GPIO as GPIO  # type: ignore

            return GPIO
        except Exception as exc:
            print(f"[audio] GPIO no disponible, modo simulado: {exc}")
            return _MockGPIO()

    def setup(self) -> None:
        if self._setup_done:
            return

        self._gpio.setwarnings(False)
        self._gpio.setmode(self._gpio.BCM)
        self._gpio.setup(self.pin, self._gpio.OUT)
        self._pwm = self._gpio.PWM(self.pin, self.base_frequency)
        self._pwm.start(0)
        self._setup_done = True

    def _play_pattern_blocking(self, pattern: List[Tone]) -> None:
        self.setup()
        if self._pwm is None:
            return

        with self._lock:
            for freq, duration, pause in pattern:
                self._pwm.ChangeFrequency(max(1, int(freq)))
                self._pwm.ChangeDutyCycle(50)
                time.sleep(max(0.0, duration))
                self._pwm.ChangeDutyCycle(0)
                if pause > 0:
                    time.sleep(pause)

    def play(self, event_name: str, non_blocking: bool = True) -> None:
        pattern = self.PATTERNS.get(event_name)
        if not pattern:
            print(f"[audio] Evento sonoro desconocido: {event_name}")
            return

        if isinstance(self._gpio, _MockGPIO):
            print(f"[audio:MOCK] evento={event_name}")
            # Campana terminal para visualizar actividad en dev.
            print("\a", end="", flush=True)

        if non_blocking:
            threading.Thread(target=self._play_pattern_blocking, args=(pattern,), daemon=True).start()
        else:
            self._play_pattern_blocking(pattern)

    def cleanup(self) -> None:
        try:
            if self._pwm is not None:
                self._pwm.stop()
        except Exception as exc:
            print(f"[audio] Error deteniendo PWM: {exc}")
        finally:
            self._pwm = None

        try:
            self._gpio.cleanup()
        except Exception as exc:
            print(f"[audio] Error en cleanup GPIO: {exc}")
        finally:
            self._setup_done = False


_controller = AudioController()


def start_up(non_blocking: bool = True) -> None:
    _controller.play("start_up", non_blocking=non_blocking)


def shut_down(non_blocking: bool = True) -> None:
    _controller.play("shut_down", non_blocking=non_blocking)


def access_successful(non_blocking: bool = True) -> None:
    _controller.play("access_successful", non_blocking=non_blocking)


def access_invalid(non_blocking: bool = True) -> None:
    _controller.play("access_invalid", non_blocking=non_blocking)


def button_select(non_blocking: bool = True) -> None:
    _controller.play("button_select", non_blocking=non_blocking)


def registration(non_blocking: bool = True) -> None:
    _controller.play("registration", non_blocking=non_blocking)


def cleanup() -> None:
    _controller.cleanup()
