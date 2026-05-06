# ⚡ ACCION REQUERIDA AHORA - Reinicia el Raspberry Pi

## Estado Actual

✓ Librerías Python configuradas correctamente  
✓ Picamera2 instalado  
✓ PCIe configurado en /boot/firmware/config.txt  
✗ **PCIe aun no activo** (requiere reinicio)

---

## QUE HACER AHORA

### 1️⃣ OPCIÓN A - Reinicio Seguro (Recomendado)

```bash
# Salir del venv
deactivate

# Reiniciar
sudo reboot
```

El Raspberry se reiniciará. **Esto tardará 30-60 segundos**. Espera a que se reinicie automáticamente.

### 2️⃣ OPCIÓN B - Reinicio Forzado (Si A no funciona)

```bash
sudo reboot -f
```

---

## DESPUES DEL REINICIO

Una vez que el Raspberry haya reiniciado (volverá a conectarse automáticamente):

### Paso 1: Verificar que PCIe está activo

```bash
vcgencmd get_config pcie
# Debe mostrar: pciex1=1 (no "unknown")
```

### Paso 2: Ejecutar el diagnostico

```bash
cd /home/pi/Desktop/identifyme/face-recognition
source venv/bin/activate
python3 test_camera.py
```

Debe mostrar: **[OK] LA CAMARA FUNCIONA CORRECTAMENTE**

### Paso 3: Usar el sistema

```bash
# Registrar usuario
python3 registrar.py

# Iniciar sesion
python3 login.py
```

---

## SI ALGO SIGUE FALLANDO

Si después del reinicio PCIe sigue en estado "unknown":

```bash
# Verificar que la config se escribió correctamente
tail -5 /boot/firmware/config.txt
# Debe mostrar las líneas de PCIe

# Si no está, añade manualmente:
sudo nano /boot/firmware/config.txt
# Ve al final del archivo y añade:
# dtoverlay=pcie-32bit-dma
# dtparam=pciex1=on

# Vuelve a reiniciar
sudo reboot
```

---

## TELEFONOS IMPORTANTES

- **NO apagues el Raspberry sin usar `sudo reboot` o `sudo poweroff`**
- El reinicio tardará un poco, espera con paciencia
- Después del reinicio, todo debería funcionar

---

**Próximo paso:** Ejecuta `sudo reboot` y espera a que se reinicie.
