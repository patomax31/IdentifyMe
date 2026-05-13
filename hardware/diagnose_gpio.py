#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script de diagnóstico para GPIO en Raspberry Pi 5."""

import os
import sys
import time

print("=" * 60)
print("DIAGNOSTICO DE GPIO - Raspberry Pi 5")
print("=" * 60)

# Test 1: Verificar librerías
print("\n[1] Verificando librerias disponibles...")
try:
    from gpiozero import LED, AngularServo, Device
    from gpiozero.pins.lgpio import LGPIOFactory
    print("  [OK] gpiozero disponible")
    print("  [OK] lgpio backend disponible")
except ImportError as e:
    print(f"  [ERROR] Importando: {e}")
    sys.exit(1)

# Test 2: Configurar GPIO
print("\n[2] Configurando GPIO con lgpio backend...")
try:
    Device.pin_factory = LGPIOFactory()
    print("  [OK] lgpio backend activado")
except Exception as e:
    print(f"  [ERROR] Configurando backend: {e}")
    sys.exit(1)

# Test 3: Pines configurados
LED_PIN = int(os.getenv("GPIO_LED_GREEN", "15"))
SERVO_PIN = int(os.getenv("GPIO_SERVO_PIN", "14"))
print(f"\n[3] Pines configurados:")
print(f"  - LED_PIN: {LED_PIN}")
print(f"  - SERVO_PIN: {SERVO_PIN}")

# Test 4: Crear dispositivos
print("\n[4] Inicializando dispositivos...")
try:
    print(f"  Creando LED en GPIO {LED_PIN}...")
    led = LED(LED_PIN)
    print("  [OK] LED creado")
except Exception as e:
    print(f"  [ERROR] LED: {e}")
    led = None

try:
    print(f"  Creando servo en GPIO {SERVO_PIN}...")
    servo = AngularServo(SERVO_PIN, min_angle=-90, max_angle=90)
    print("  [OK] Servo creado")
except Exception as e:
    print(f"  [ERROR] Servo: {e}")
    servo = None

# Test 5: Prueba del LED
print("\n[5] Probando LED...")
if led:
    try:
        print("  Encendiendo LED...")
        led.on()
        print(f"  LED esta ON: {led.is_lit}")
        time.sleep(1)
        
        print("  Apagando LED...")
        led.off()
        print(f"  LED esta ON: {led.is_lit}")
        print("  [OK] LED funciona")
    except Exception as e:
        print(f"  [ERROR]: {e}")
else:
    print("  [ERROR] LED no inicializado")

# Test 6: Prueba del servo
print("\n[6] Probando servo...")
if servo:
    try:
        print("  Moviendo servo a 0 grados...")
        servo.angle = 0
        time.sleep(0.5)
        print(f"  Angulo actual: {servo.angle} grados")
        
        print("  Moviendo servo a 45 grados...")
        servo.angle = 45
        time.sleep(0.5)
        print(f"  Angulo actual: {servo.angle} grados")
        
        print("  Moviendo servo a -45 grados...")
        servo.angle = -45
        time.sleep(0.5)
        print(f"  Angulo actual: {servo.angle} grados")
        
        print("  Regresando servo a 0 grados...")
        servo.angle = 0
        time.sleep(0.5)
        print("  [OK] Servo funciona")
    except Exception as e:
        print(f"  [ERROR]: {e}")
else:
    print("  [ERROR] Servo no inicializado")

# Limpieza
print("\n[7] Limpiando...")
if led:
    try:
        led.off()
        led.close()
        print("  [OK] LED cerrado")
    except:
        pass

if servo:
    try:
        servo.angle = 0
        servo.close()
        print("  [OK] Servo cerrado")
    except:
        pass

print("\n" + "=" * 60)
print("DIAGNOSTICO COMPLETADO")
print("=" * 60)
