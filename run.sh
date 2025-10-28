#!/bin/bash
# Script de inicio rápido para DigiLife

echo "================================"
echo "DigiLife - Simulador de Vida Artificial"
echo "================================"
echo ""

# Verificar si existe el entorno virtual
if [ ! -d "venv" ]; then
    echo "⚠️  No se encontró entorno virtual"
    echo "Ejecuta primero: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activar entorno virtual
source venv/bin/activate

# Verificar instalación
if ! python -c "import pygame" 2>/dev/null; then
    echo "⚠️  Pygame no está instalado"
    echo "Ejecuta: pip install -r requirements.txt"
    exit 1
fi

echo "✅ Entorno verificado"
echo ""

# Ejecutar
python main.py "$@"
