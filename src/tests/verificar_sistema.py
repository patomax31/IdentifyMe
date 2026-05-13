#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
✅ CHECKLIST - Verificación Rápida del Sistema

Este archivo puede ejecutarse para verificar que todo está instalado correctamente.
"""

import sys
from pathlib import Path

def check_python_version():
    """Verifica versión de Python."""
    version = sys.version_info
    print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
    return version.major >= 3 and version.minor >= 7


def check_modules():
    """Verifica módulos de Python instalados."""
    modules = {
        "tkinter": "Tkinter (GUI)",
        "cv2": "OpenCV",
        "numpy": "NumPy",
        "PIL": "Pillow",
        "dlib": "dlib",
        "face_recognition": "face_recognition",
        "sqlite3": "SQLite3",
        "threading": "threading",
        "time": "time",
    }
    
    results = {}
    for module, name in modules.items():
        try:
            __import__(module)
            print(f"  ✓ {name}")
            results[module] = True
        except ImportError:
            print(f"  ✗ {name} - NO INSTALADO")
            results[module] = False
    
    return results


def check_files():
    """Verifica que los archivos necesarios existen."""
    base_path = Path(__file__).parent
    files = {
        "test_setup.py": "Script principal",
        "README_SYSTEM_CHECK.md": "Documentación",
        "GUIA_SYSTEM_CHECK.md": "Guía técnica",
        "ARQUITECTURA.md": "Diagrama de arquitectura",
        "EJEMPLOS_PERSONALIZACION.py": "Ejemplos de código",
    }
    
    results = {}
    for filename, description in files.items():
        filepath = base_path / filename
        if filepath.exists():
            print(f"  ✓ {filename}")
            results[filename] = True
        else:
            print(f"  ✗ {filename} - NO ENCONTRADO")
            results[filename] = False
    
    return results


def check_directories():
    """Verifica que las carpetas necesarias existen."""
    base_path = Path(__file__).parent
    dirs = {
        "database": "Carpeta de base de datos",
        "database/sqlite": "Carpeta SQLite",
        "src": "Código fuente",
    }
    
    results = {}
    for dirname, description in dirs.items():
        dirpath = base_path / dirname
        if dirpath.exists():
            print(f"  ✓ {dirname}/")
            results[dirname] = True
        else:
            print(f"  ⚠ {dirname}/ - No existe (se creará si es necesario)")
            results[dirname] = True  # No es crítico
    
    return results


def print_header(title):
    """Imprime un encabezado con formato."""
    print(f"\n{'='*50}")
    print(f"  {title}")
    print(f"{'='*50}\n")


def main():
    """Ejecuta todas las verificaciones."""
    print("""
    ╔════════════════════════════════════════════════╗
    ║   VERIFICACIÓN DE SISTEMA - Sistema Facial    ║
    ║   Sistema de Verificación de Dependencias     ║
    ╚════════════════════════════════════════════════╝
    """)
    
    results = {
        "python": False,
        "modules": {},
        "files": {},
        "directories": {},
    }
    
    # 1. Verificar Python
    print_header("1. VERSIÓN DE PYTHON")
    results["python"] = check_python_version()
    
    # 2. Verificar módulos
    print_header("2. MÓDULOS INSTALADOS")
    results["modules"] = check_modules()
    
    # 3. Verificar archivos
    print_header("3. ARCHIVOS NECESARIOS")
    results["files"] = check_files()
    
    # 4. Verificar directorios
    print_header("4. DIRECTORIOS")
    results["directories"] = check_directories()
    
    # 5. Resumen
    print_header("📊 RESUMEN")
    
    python_ok = results["python"]
    modules_ok = all(results["modules"].values())
    files_ok = all(results["files"].values())
    dirs_ok = all(results["directories"].values())
    
    print(f"  Python 3.7+:        {'✓ OK' if python_ok else '✗ NECESARIO'}")
    print(f"  Módulos:            {'✓ OK' if modules_ok else '✗ FALTAN MÓDULOS'}")
    print(f"  Archivos:           {'✓ OK' if files_ok else '✗ ARCHIVOS FALTANTES'}")
    print(f"  Directorios:        {'✓ OK' if dirs_ok else '✗ CREAR DIRECTORIOS'}")
    
    # 6. Recomendaciones
    print_header("💡 RECOMENDACIONES")
    
    missing_modules = [m for m, ok in results["modules"].items() if not ok]
    if missing_modules:
        print("  ⚠ Instala los módulos faltantes con:")
        modules_str = " ".join(missing_modules)
        print(f"    pip install {modules_str}")
    else:
        print("  ✓ Todos los módulos están instalados")
    
    # 7. Próximos pasos
    print_header("🚀 PRÓXIMOS PASOS")
    
    if python_ok and modules_ok and files_ok and dirs_ok:
        print("""
  ✓ Sistema verificado correctamente
  
  Ejecuta la verificación de dependencias con:
  
    python test_setup.py
  
  Esto abrirá una interfaz gráfica que validará:
  - Todas las dependencias Python
  - Disponibilidad de hardware (cámara, pantalla)
  - Conexión a base de datos
  
  Si todo está OK, se abrirá la interfaz principal.
        """)
    else:
        print("""
  ⚠ Por favor, completa las acciones anteriores:
  
  1. Instala Python 3.7+
  2. Instala los módulos faltantes
  3. Asegúrate de que todos los archivos estén presentes
  
  Luego ejecuta:
    python test_setup.py
        """)
    
    print_header("📚 DOCUMENTACIÓN")
    print("""
  Para más información, consulta:
  
  • README_SYSTEM_CHECK.md       - Guía rápida
  • GUIA_SYSTEM_CHECK.md         - Documentación técnica
  • ARQUITECTURA.md              - Diagrama de arquitectura
  • EJEMPLOS_PERSONALIZACION.py  - 10 ejemplos de código
  • RESUMEN_EJECUTIVO.md         - Resumen del proyecto
    """)
    
    print_header("✨ ¡LISTO!")
    print("  El sistema está preparado para comenzar.\n")


if __name__ == "__main__":
    main()
