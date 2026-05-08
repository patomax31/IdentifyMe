#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test agresivo de GPIO - parpadeo intenso para detectar conexión."""

import time
from gpiozero import LED, Device
from gpiozero.pins.lgpio import LGPIOFactory

Device.pin_factory = LGPIOFactory()

LED_PIN = 15  # GPIO 15

print(f"Creando LED en GPIO {LED_PIN}...")
led = LED(LED_PIN)

print(f"\n*** PRUEBA AGRESIVA - Parpadeo intenso por 10 segundos ***")
print("Si no ves una luz intermitente RAPIDA, hay problema de conexion.\n")

try:
    # Parpadeo rápido y agresivo
    for i in range(50):
        led.on()
        time.sleep(0.05)
        led.off()
        time.sleep(0.05)
        print(".", end="", flush=True)
    
    print("\n\n[RESULTADO] Si viste parpadeos rapidisimos = CONEXION OK")
    print("[RESULTADO] Si no viste nada = PROBLEMA DE CONEXION EN PROTOBOARD")
    
except Exception as e:
    print(f"Error: {e}")
finally:
    led.off()
    led.close()
