#!/usr/bin/env python3
"""
Script de prueba para el sistema de beeps
"""

import sys
import time

# Probar beeps del sistema
print("🔊 Probando sistema de beeps...")
print()

if sys.platform == 'win32':
    print("Sistema: Windows")
    try:
        import winsound
        print("✅ winsound disponible")
        print("\nProbando beeps:")
        
        # Beep bajo
        print("  - Beep bajo (400 Hz)")
        winsound.Beep(400, 200)
        time.sleep(0.3)
        
        # Beep medio
        print("  - Beep medio (800 Hz)")
        winsound.Beep(800, 200)
        time.sleep(0.3)
        
        # Beep alto
        print("  - Beep alto (1200 Hz)")
        winsound.Beep(1200, 200)
        time.sleep(0.3)
        
        # Secuencia
        print("  - Secuencia de beeps")
        for freq in [600, 700, 800]:
            winsound.Beep(freq, 100)
            time.sleep(0.1)
        
        print("\n✅ Sistema de beeps funcional!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

else:
    print("Sistema: Linux/Mac")
    print("Intentando usar 'beep' del sistema...")
    
    import os
    
    # Probar si beep está instalado
    result = os.system('which beep > /dev/null 2>&1')
    
    if result == 0:
        print("✅ Comando 'beep' disponible")
        print("\nProbando beeps:")
        
        # Beep bajo
        print("  - Beep bajo (400 Hz)")
        os.system('beep -f 400 -l 200 2>/dev/null')
        time.sleep(0.3)
        
        # Beep medio
        print("  - Beep medio (800 Hz)")
        os.system('beep -f 800 -l 200 2>/dev/null')
        time.sleep(0.3)
        
        # Beep alto
        print("  - Beep alto (1200 Hz)")
        os.system('beep -f 1200 -l 200 2>/dev/null')
        time.sleep(0.3)
        
        # Secuencia
        print("  - Secuencia de beeps")
        os.system('beep -f 600 -l 100 -n -f 700 -l 100 -n -f 800 -l 100 2>/dev/null')
        
        print("\n✅ Sistema de beeps funcional!")
        
    else:
        print("⚠️  Comando 'beep' no encontrado")
        print("\nUsando método alternativo (bell character)...")
        
        # Método alternativo: usar el bell character
        print("  - Beep del sistema (\\a)")
        for i in range(3):
            os.system('printf "\\a"')
            time.sleep(0.3)
        
        print("\n✅ Beeps básicos funcionando!")
        print("\nNota: Para beeps con frecuencia variable, instala 'beep':")
        print("  sudo apt-get install beep")
        print("  sudo chmod 4755 /usr/bin/beep")

print("\n" + "="*50)
print("Prueba completada")
print("="*50)
