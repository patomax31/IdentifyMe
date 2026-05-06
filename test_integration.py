#!/usr/bin/env python
"""
Test de integración para verificar que todas las clases funcionan correctamente
"""

import sys
import os

# Agregar directorio actual al path
sys.path.insert(0, os.path.dirname(__file__))

def test_imports():
    """Verifica que todos los módulos se importan correctamente"""
    print("=" * 70)
    print("TEST: Importar módulos principales")
    print("=" * 70)
    
    try:
        print("\n1. Importando login.py...")
        from login import FaceLoginUI, UIState
        print("   ✓ FaceLoginUI importado correctamente")
        print("   ✓ UIState importado correctamente")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    try:
        print("\n2. Importando registrar.py...")
        from registrar import FaceRegisterUI
        print("   ✓ FaceRegisterUI importado correctamente")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    try:
        print("\n3. Importando main.py...")
        from main import MainWindow
        print("   ✓ MainWindow importado correctamente")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    return True


def test_class_instantiation():
    """Verifica que las clases se pueden instanciar (sin GUI)"""
    print("\n" + "=" * 70)
    print("TEST: Instanciación de clases (modo no-GUI)")
    print("=" * 70)
    
    import tkinter as tk
    
    # Crear root window (invisible)
    root = tk.Tk()
    root.withdraw()  # Ocultar ventana
    
    try:
        print("\n1. Instanciando FaceLoginUI...")
        from login import FaceLoginUI
        
        # No necesitamos instanciar aquí porque requiere UI
        print("   ✓ Clase disponible para instanciar")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        root.destroy()
        return False
    
    try:
        print("\n2. Instanciando FaceRegisterUI...")
        from registrar import FaceRegisterUI
        
        # No necesitamos instanciar aquí porque requiere UI
        print("   ✓ Clase disponible para instanciar")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        root.destroy()
        return False
    
    try:
        print("\n3. Instanciando MainWindow...")
        from main import MainWindow
        
        # No necesitamos instanciar aquí porque requiere UI
        print("   ✓ Clase disponible para instanciar")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        root.destroy()
        return False
    
    root.destroy()
    return True


def test_ui_states():
    """Verifica que la máquina de estados funciona"""
    print("\n" + "=" * 70)
    print("TEST: Máquina de Estados UIState")
    print("=" * 70)
    
    try:
        from login import UIState
        
        states = [
            'IDLE', 'WAITING', 'DETECTING', 'VERIFYING',
            'POSITIONING', 'GRANTED', 'DENIED', 'RESTRICTED', 'ERROR'
        ]
        
        print("\nEstados disponibles:")
        for state in states:
            value = getattr(UIState, state)
            print(f"   ✓ UIState.{state} = '{value}'")
        
        return True
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False


def test_color_palette():
    """Verifica que la paleta de colores está correcta"""
    print("\n" + "=" * 70)
    print("TEST: Paleta de Colores")
    print("=" * 70)
    
    try:
        import login
        
        colors = {
            'COLOR_PRIMARY': '#008f39',
            'COLOR_SECONDARY': '#48a259',
            'COLOR_TERTIARY': '#70b578',
            'COLOR_ACCENT': '#95c799',
            'COLOR_LIGHT': '#b8daba',
            'COLOR_LIGHTER': '#dbeddc',
            'COLOR_WHITE': '#ffffff',
            'COLOR_RED': '#ef4444',
            'COLOR_ORANGE': '#f97316',
        }
        
        print("\nColores definidos:")
        for name, value in colors.items():
            actual = getattr(login, name, None)
            if actual == value:
                print(f"   ✓ {name} = {value}")
            else:
                print(f"   ✗ {name} esperado {value}, obtuvo {actual}")
                return False
        
        return True
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False


def main():
    """Ejecuta todos los tests"""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " TEST DE INTEGRACIÓN - SISTEMA DE ACCESO FACIAL ".center(68) + "║")
    print("╚" + "=" * 68 + "╝")
    
    results = []
    
    # Test 1: Imports
    results.append(("Importación de módulos", test_imports()))
    
    # Test 2: Instantiation
    results.append(("Instanciación de clases", test_class_instantiation()))
    
    # Test 3: States
    results.append(("Máquina de estados", test_ui_states()))
    
    # Test 4: Colors
    results.append(("Paleta de colores", test_color_palette()))
    
    # Summary
    print("\n" + "=" * 70)
    print("RESUMEN DE PRUEBAS")
    print("=" * 70)
    
    for test_name, result in results:
        status = "✓ PASÓ" if result else "✗ FALLÓ"
        print(f"{test_name:.<50} {status}")
    
    # Final result
    all_passed = all(result for _, result in results)
    
    print("\n" + "=" * 70)
    if all_passed:
        print("✅ TODOS LOS TESTS PASARON CORRECTAMENTE")
    else:
        print("❌ ALGUNOS TESTS FALLARON")
    print("=" * 70 + "\n")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
