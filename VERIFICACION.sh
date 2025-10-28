#!/bin/bash
# Script de verificación completa de DigiLife

echo "=========================================="
echo "DigiLife - Verificación del Sistema"
echo "=========================================="
echo ""

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Contadores
PASSED=0
FAILED=0
WARNINGS=0

# Función para verificar
check() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $1"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} $1"
        ((FAILED++))
    fi
}

check_warning() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $1"
        ((PASSED++))
    else
        echo -e "${YELLOW}⚠${NC} $1 (opcional)"
        ((WARNINGS++))
    fi
}

echo "1. Verificando Python..."
python3 --version > /dev/null 2>&1
check "Python 3 instalado"

python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" 2>/dev/null
check "Python 3.10 o superior"

echo ""
echo "2. Verificando estructura del proyecto..."
[ -f "main.py" ]
check "main.py existe"

[ -f "config.py" ]
check "config.py existe"

[ -f "requirements.txt" ]
check "requirements.txt existe"

[ -d "engine" ]
check "Directorio engine/ existe"

[ -d "ui" ]
check "Directorio ui/ existe"

[ -d "utils" ]
check "Directorio utils/ existe"

[ -d "tests" ]
check "Directorio tests/ existe"

echo ""
echo "3. Verificando archivos del motor..."
[ -f "engine/world.py" ]
check "engine/world.py existe"

[ -f "engine/creature.py" ]
check "engine/creature.py existe"

[ -f "engine/genome.py" ]
check "engine/genome.py existe"

[ -f "engine/neural_net.py" ]
check "engine/neural_net.py existe"

[ -f "engine/vocal_system.py" ]
check "engine/vocal_system.py existe"

echo ""
echo "4. Verificando entorno virtual..."
if [ -d "venv" ]; then
    echo -e "${GREEN}✓${NC} Entorno virtual existe"
    ((PASSED++))
    
    # Activar y verificar dependencias
    source venv/bin/activate 2>/dev/null
    
    python -c "import pygame" 2>/dev/null
    check "Pygame instalado"
    
    python -c "import numpy" 2>/dev/null
    check "NumPy instalado"
    
    python -c "import pyopencl" 2>/dev/null
    check_warning "PyOpenCL instalado"
    
    python -c "import pyttsx3" 2>/dev/null
    check_warning "pyttsx3 instalado"
    
else
    echo -e "${RED}✗${NC} Entorno virtual no existe"
    echo "  Ejecuta: python3 -m venv venv"
    ((FAILED++))
fi

echo ""
echo "5. Verificando dependencias del sistema..."
which espeak-ng > /dev/null 2>&1
check_warning "espeak-ng instalado"

which clinfo > /dev/null 2>&1
check_warning "clinfo instalado (para GPU)"

echo ""
echo "6. Verificando sintaxis Python..."
if [ -d "venv" ]; then
    source venv/bin/activate 2>/dev/null
    
    python -m py_compile main.py 2>/dev/null
    check "main.py sin errores de sintaxis"
    
    python -m py_compile config.py 2>/dev/null
    check "config.py sin errores de sintaxis"
    
    python -m py_compile engine/world.py 2>/dev/null
    check "engine/world.py sin errores de sintaxis"
    
    python -m py_compile engine/creature.py 2>/dev/null
    check "engine/creature.py sin errores de sintaxis"
fi

echo ""
echo "7. Verificando permisos de ejecución..."
[ -x "main.py" ]
check "main.py es ejecutable"

[ -x "setup_opencl.py" ]
check "setup_opencl.py es ejecutable"

[ -x "run.sh" ]
check "run.sh es ejecutable"

echo ""
echo "8. Verificando documentación..."
[ -f "README.md" ]
check "README.md existe"

[ -f "QUICKSTART.md" ]
check "QUICKSTART.md existe"

[ -f "LEEME.md" ]
check "LEEME.md existe"

[ -f "EXAMPLES.md" ]
check "EXAMPLES.md existe"

echo ""
echo "=========================================="
echo "Resumen de Verificación"
echo "=========================================="
echo -e "${GREEN}Pasadas:${NC} $PASSED"
echo -e "${YELLOW}Advertencias:${NC} $WARNINGS (opcionales)"
echo -e "${RED}Fallidas:${NC} $FAILED"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ DigiLife está listo para ejecutarse!${NC}"
    echo ""
    echo "Ejecuta:"
    echo "  ./run.sh"
    echo ""
    echo "O con opciones:"
    echo "  python main.py --population 20 --data-rate 5"
    exit 0
else
    echo -e "${RED}✗ Hay problemas que resolver${NC}"
    echo ""
    echo "Pasos sugeridos:"
    if [ ! -d "venv" ]; then
        echo "  1. Crear entorno virtual: python3 -m venv venv"
        echo "  2. Activar: source venv/bin/activate"
        echo "  3. Instalar dependencias: pip install -r requirements.txt"
    fi
    echo ""
    echo "Consulta README_INSTALL.md para más detalles"
    exit 1
fi
