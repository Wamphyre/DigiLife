#!/usr/bin/env python3
"""
Script de verificación de OpenCL para DigiLife
Detecta GPU AMD y verifica configuración
"""

import sys

def check_opencl():
    """Verifica disponibilidad y configuración de OpenCL"""
    print("=" * 60)
    print("DigiLife - Verificación de OpenCL")
    print("=" * 60)
    
    try:
        import pyopencl as cl
        print("✅ PyOpenCL instalado correctamente\n")
    except ImportError:
        print("❌ PyOpenCL no está instalado")
        print("   Instalar con: pip install pyopencl")
        return False
    
    # Obtener plataformas
    try:
        platforms = cl.get_platforms()
        if not platforms:
            print("❌ No se encontraron plataformas OpenCL")
            return False
        
        print(f"✅ Plataformas OpenCL encontradas: {len(platforms)}\n")
        
        total_devices = 0
        for i, platform in enumerate(platforms):
            print(f"Plataforma {i}: {platform.name}")
            print(f"  Vendor: {platform.vendor}")
            print(f"  Version: {platform.version}")
            
            # Obtener dispositivos
            devices = platform.get_devices()
            total_devices += len(devices)
            
            for j, device in enumerate(devices):
                print(f"\n  Dispositivo {j}: {device.name}")
                print(f"    Tipo: {cl.device_type.to_string(device.type)}")
                print(f"    Compute Units: {device.max_compute_units}")
                print(f"    Memoria Global: {device.global_mem_size / (1024**3):.2f} GB")
                print(f"    Memoria Local: {device.local_mem_size / 1024:.2f} KB")
                print(f"    Max Work Group Size: {device.max_work_group_size}")
                print(f"    Max Clock: {device.max_clock_frequency} MHz")
                
                # Verificar si es AMD
                if 'AMD' in device.vendor.upper() or 'AMD' in device.name.upper():
                    print(f"    🎮 GPU AMD detectada!")
        
        print("\n" + "=" * 60)
        if total_devices > 0:
            print(f"✅ Total de dispositivos OpenCL: {total_devices}")
            print("✅ DigiLife puede usar aceleración GPU")
            
            # Test simple
            print("\nRealizando test de cálculo...")
            test_opencl_compute()
            return True
        else:
            print("⚠️  No se encontraron dispositivos OpenCL")
            print("   DigiLife funcionará solo con CPU")
            return False
            
    except Exception as e:
        print(f"❌ Error al verificar OpenCL: {e}")
        return False

def test_opencl_compute():
    """Test simple de cálculo con OpenCL"""
    try:
        import pyopencl as cl
        import numpy as np
        
        # Crear contexto y cola
        platform = cl.get_platforms()[0]
        device = platform.get_devices()[0]
        context = cl.Context([device])
        queue = cl.CommandQueue(context)
        
        # Kernel simple de suma
        kernel_code = """
        __kernel void test_add(__global float *a, __global float *b, __global float *c) {
            int gid = get_global_id(0);
            c[gid] = a[gid] + b[gid];
        }
        """
        
        # Datos de prueba
        n = 1000
        a = np.random.rand(n).astype(np.float32)
        b = np.random.rand(n).astype(np.float32)
        c = np.zeros(n, dtype=np.float32)
        
        # Buffers
        mf = cl.mem_flags
        a_buf = cl.Buffer(context, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=a)
        b_buf = cl.Buffer(context, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=b)
        c_buf = cl.Buffer(context, mf.WRITE_ONLY, c.nbytes)
        
        # Compilar y ejecutar
        program = cl.Program(context, kernel_code).build()
        program.test_add(queue, (n,), None, a_buf, b_buf, c_buf)
        cl.enqueue_copy(queue, c, c_buf)
        
        # Verificar resultado
        expected = a + b
        if np.allclose(c, expected):
            print("✅ Test de cálculo GPU exitoso")
        else:
            print("⚠️  Test de cálculo con diferencias")
            
    except Exception as e:
        print(f"⚠️  Error en test de cálculo: {e}")

def check_audio():
    """Verifica sistema de beeps"""
    print("\n" + "=" * 60)
    print("Verificación de Sistema de Beeps")
    print("=" * 60)
    
    import sys
    import os
    
    if sys.platform == 'win32':
        print("✅ Windows: winsound disponible nativamente")
        return True
    else:
        # Verificar si beep está instalado
        result = os.system('which beep > /dev/null 2>&1')
        
        if result == 0:
            print("✅ Comando 'beep' disponible")
            
            # Verificar permisos
            test_result = os.system('beep -f 800 -l 50 2>/dev/null')
            if test_result == 0:
                print("✅ Beeps funcionando correctamente")
                return True
            else:
                print("⚠️  Beep instalado pero sin permisos")
                print("   Ejecuta: ./setup_beep.sh")
                return False
        else:
            print("⚠️  Comando 'beep' no encontrado")
            print("   Ejecuta: ./setup_beep.sh")
            print("   Fallback: Se usará bell character (\\a)")
            return False

def main():
    """Función principal"""
    opencl_ok = check_opencl()
    audio_ok = check_audio()
    
    print("\n" + "=" * 60)
    print("Resumen de Configuración")
    print("=" * 60)
    
    if opencl_ok:
        print("✅ Aceleración GPU: DISPONIBLE")
    else:
        print("⚠️  Aceleración GPU: NO DISPONIBLE (usará CPU)")
    
    if audio_ok:
        print("✅ Vocalizaciones: DISPONIBLES")
    else:
        print("⚠️  Vocalizaciones: NO DISPONIBLES")
    
    print("\n¡DigiLife está listo para ejecutarse!")
    print("Ejecuta: python main.py")
    print("=" * 60)

if __name__ == "__main__":
    main()
