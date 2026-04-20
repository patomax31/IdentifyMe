#!/bin/bash
# Script para ejecutar el sistema de acceso facial

# Directorio del proyecto
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# Verificar si el venv existe
if [ ! -d "venv/bin" ]; then
    echo "❌ Virtual environment no encontrado. Creándo..."
    python3 -m venv venv
fi

# Activar venv
source venv/bin/activate

# Ejecutar main.py
echo "🚀 Iniciando Sistema de Acceso Facial..."
python main.py
