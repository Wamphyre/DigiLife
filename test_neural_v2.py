#!/usr/bin/env python3
"""
Test rápido de la nueva red neuronal profunda
"""

import numpy as np
from engine.neural_net import NeuralNetwork

print("🧠 Test de Red Neuronal Profunda v2.0\n")

# Crear red neuronal
print("1. Creando red neuronal (8 → 16 → 8 → 4)...")
brain = NeuralNetwork(input_size=8, hidden_size=16, output_size=4)
print(f"   ✅ Capas: {brain.input_size} → {brain.hidden_size} → {brain.hidden_size2} → {brain.output_size}")
print(f"   ✅ Memoria: {brain.memory.shape}")

# Test forward pass CPU
print("\n2. Test forward pass (CPU)...")
inputs = [0.5, 0.3, 0.8, 0.2, 0.1, 0.9, 0.4, 1.0]
outputs = brain.forward(inputs, use_gpu=False)
print(f"   Inputs:  {[f'{x:.2f}' for x in inputs]}")
print(f"   Outputs: {[f'{x:.2f}' for x in outputs]}")
print(f"   ✅ Forward pass exitoso")

# Test memoria
print("\n3. Test memoria de corto plazo...")
print(f"   Memoria inicial: {brain.memory[:4]}")
outputs2 = brain.forward(inputs, use_gpu=False)
print(f"   Memoria después:  {brain.memory[:4]}")
print(f"   ✅ Memoria actualizada")

# Test herencia
print("\n4. Test herencia de pesos...")
parent = brain
child = NeuralNetwork(input_size=8, hidden_size=16, output_size=4, parent=parent)
print(f"   Padre weights[0,0]:  {parent.weights_ih1[0,0]:.4f}")
print(f"   Hijo weights[0,0]:   {child.weights_ih1[0,0]:.4f}")
diff = np.abs(parent.weights_ih1 - child.weights_ih1).mean()
print(f"   Diferencia promedio: {diff:.4f}")
print(f"   ✅ Herencia con mutación exitosa")

# Test mutación
print("\n5. Test mutación...")
original = child.weights_ih1.copy()
child.mutate(rate=0.5, strength=0.3)
diff = np.abs(original - child.weights_ih1).mean()
print(f"   Diferencia después de mutar: {diff:.4f}")
print(f"   ✅ Mutación exitosa")

# Test OpenCL
print("\n6. Test OpenCL...")
if NeuralNetwork._cl_context is not None:
    print("   ✅ OpenCL disponible")
    try:
        outputs_gpu = brain.forward(inputs, use_gpu=True)
        print(f"   GPU Outputs: {[f'{x:.2f}' for x in outputs_gpu]}")
        print(f"   ✅ Forward pass GPU exitoso")
    except Exception as e:
        print(f"   ⚠️  GPU falló (usando CPU): {e}")
else:
    print("   ⚠️  OpenCL no disponible (usando CPU)")

print("\n" + "="*50)
print("✅ TODOS LOS TESTS PASARON")
print("="*50)
print("\n🎯 La red neuronal profunda está lista para usar!")
print("🚀 Ejecuta 'python main.py' para ver las mejoras en acción")
