#!/bin/bash
# Script de configuración automática de beep para DigiLife

echo "🔊 Configurando sistema de beeps para DigiLife..."
echo ""

# Verificar si es Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "⚠️  Este script es solo para Linux"
    echo "En Windows y Mac, los beeps funcionan nativamente"
    exit 0
fi

# Instalar beep
echo "📦 Instalando beep..."
sudo apt-get update -qq
sudo apt-get install -y beep

# Cargar módulo pcspkr
echo "🔌 Cargando módulo pcspkr..."
sudo modprobe pcspkr

# Hacer que el módulo se cargue al inicio
if ! grep -q "pcspkr" /etc/modules; then
    echo "pcspkr" | sudo tee -a /etc/modules > /dev/null
    echo "✅ Módulo pcspkr configurado para carga automática"
fi

# Agregar usuario al grupo input
echo "👤 Agregando usuario al grupo input..."
sudo usermod -a -G input $USER

# Configurar permisos del dispositivo
echo "🔐 Configurando permisos..."
BEEP_DEVICE=$(ls /dev/input/by-path/*pcspkr* 2>/dev/null | head -1)

if [ -n "$BEEP_DEVICE" ]; then
    BEEP_EVENT=$(readlink -f $BEEP_DEVICE)
    sudo chgrp input $BEEP_EVENT
    sudo chmod 660 $BEEP_EVENT
    echo "✅ Permisos configurados para $BEEP_EVENT"
else
    echo "⚠️  No se encontró dispositivo pcspkr"
fi

# Crear regla udev
echo "📝 Creando regla udev..."
echo 'SUBSYSTEM=="input", KERNEL=="event*", ENV{ID_INPUT_KEY}=="1", GROUP="input", MODE="0660"' | sudo tee /etc/udev/rules.d/90-pcspkr.rules > /dev/null

# Recargar reglas udev
echo "🔄 Recargando reglas udev..."
sudo udevadm control --reload-rules
sudo udevadm trigger

echo ""
echo "✅ Configuración completada!"
echo ""
echo "⚠️  IMPORTANTE: Debes cerrar sesión y volver a entrar para que"
echo "   los cambios de grupo surtan efecto."
echo ""
echo "Para probar los beeps después de reiniciar sesión:"
echo "  python3 test_beeps.py"
echo ""
