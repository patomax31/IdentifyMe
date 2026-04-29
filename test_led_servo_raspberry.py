#!/usr/bin/env python3
"""Prueba simple de LED y servomotor para Raspberry Pi.

Hace dos cosas:
- Enciende un LED durante 5 segundos.
- Mueve un servomotor a una posicion de prueba y luego lo regresa.

Pines por defecto:
- LED: GPIO 15
- Servo: GPIO 14

Uso:
    python test_led_servo_raspberry.py
"""

from __future__ import annotations

import os
import time


LED_PIN = int(os.getenv("GPIO_LED_GREEN", "15"))
SERVO_PIN = int(os.getenv("GPIO_SERVO_PIN", "14"))
SERVO_FREQUENCY = float(os.getenv("GPIO_SERVO_FREQUENCY", "50"))


def _load_gpio():
    try:
        import RPi.GPIO as GPIO  # type: ignore

        return GPIO
    except Exception as exc:  # pragma: no cover - depende del hardware
        raise RuntimeError(
            "RPi.GPIO no esta disponible. Ejecuta este script en una Raspberry Pi con GPIO instalado."
        ) from exc


def _servo_duty_cycle(angle: float) -> float:
    angle = max(0.0, min(180.0, angle))
    return 2.5 + (angle / 180.0) * 10.0


def main() -> int:
    GPIO = _load_gpio()

    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(LED_PIN, GPIO.OUT)
    GPIO.setup(SERVO_PIN, GPIO.OUT)

    servo_pwm = GPIO.PWM(SERVO_PIN, SERVO_FREQUENCY)
    servo_pwm.start(0)

    try:
        print(f"Probando LED en GPIO {LED_PIN} durante 5 segundos...")
        GPIO.output(LED_PIN, GPIO.HIGH)

        print(f"Moviendo servomotor en GPIO {SERVO_PIN}...")
        servo_pwm.ChangeDutyCycle(_servo_duty_cycle(90))
        time.sleep(0.8)
        servo_pwm.ChangeDutyCycle(0)

        time.sleep(5)

        print("Apagando LED y regresando servo a posicion inicial...")
        GPIO.output(LED_PIN, GPIO.LOW)
        servo_pwm.ChangeDutyCycle(_servo_duty_cycle(0))
        time.sleep(0.8)
        servo_pwm.ChangeDutyCycle(0)

        print("Prueba completada.")
        return 0
    finally:
        try:
            servo_pwm.stop()
        except Exception:
            pass
        GPIO.output(LED_PIN, GPIO.LOW)
        GPIO.cleanup()


if __name__ == "__main__":
    raise SystemExit(main())