"""
Sistema de procesamiento por lotes para redes neuronales
Optimizado para GPU con OpenCL
"""

import numpy as np
from typing import List, Tuple
import config

try:
    import pyopencl as cl
    import pyopencl.array as cl_array
    OPENCL_AVAILABLE = True
except ImportError:
    OPENCL_AVAILABLE = False
    cl = None


class NeuralBatchProcessor:
    """Procesador por lotes de redes neuronales en GPU"""
    
    def __init__(self):
        self.cl_context = None
        self.cl_queue = None
        self.cl_program = None
        self.initialized = False
        
        # Cachear kernels para evitar recrearlos
        self.kernel_layer1 = None
        self.kernel_layer2 = None
        self.kernel_output = None
        
        if config.USE_GPU and OPENCL_AVAILABLE:
            self._init_opencl()
    
    def _init_opencl(self):
        """Inicializar OpenCL para procesamiento por lotes"""
        try:
            # Seleccionar mejor dispositivo disponible
            platforms = cl.get_platforms()
            device = None
            
            # Preferir GPU sobre CPU
            for platform in platforms:
                gpu_devices = platform.get_devices(device_type=cl.device_type.GPU)
                if gpu_devices:
                    device = gpu_devices[0]
                    break
            
            if device is None:
                # Fallback a CPU
                device = platforms[0].get_devices()[0]
            
            self.cl_context = cl.Context([device])
            self.cl_queue = cl.CommandQueue(self.cl_context)
            
            # Kernel optimizado para procesamiento por lotes
            kernel_code = """
            // Activaciones
            inline float relu(float x) {
                return fmax(0.0f, x);
            }
            
            inline float sigmoid(float x) {
                return 1.0f / (1.0f + exp(-clamp(x, -10.0f, 10.0f)));
            }
            
            inline float tanh_act(float x) {
                return tanh(clamp(x, -10.0f, 10.0f));
            }
            
            // Procesamiento por lotes - Capa 1
            __kernel void batch_layer1(
                __global const float *inputs,      // [batch_size, input_size]
                __global const float *weights,     // [batch_size, input_size, hidden_size]
                __global const float *biases,      // [batch_size, hidden_size]
                __global float *outputs,           // [batch_size, hidden_size]
                const int batch_size,
                const int input_size,
                const int hidden_size)
            {
                int batch_idx = get_global_id(0);
                int hidden_idx = get_global_id(1);
                
                if (batch_idx < batch_size && hidden_idx < hidden_size) {
                    float sum = biases[batch_idx * hidden_size + hidden_idx];
                    
                    for (int i = 0; i < input_size; i++) {
                        int weight_idx = batch_idx * input_size * hidden_size + 
                                       i * hidden_size + hidden_idx;
                        int input_idx = batch_idx * input_size + i;
                        sum += inputs[input_idx] * weights[weight_idx];
                    }
                    
                    outputs[batch_idx * hidden_size + hidden_idx] = relu(sum);
                }
            }
            
            // Procesamiento por lotes - Capa 2
            __kernel void batch_layer2(
                __global const float *inputs,      // [batch_size, hidden1_size]
                __global const float *weights,     // [batch_size, hidden1_size, hidden2_size]
                __global const float *biases,      // [batch_size, hidden2_size]
                __global const float *memory,      // [batch_size, hidden2_size]
                __global float *outputs,           // [batch_size, hidden2_size]
                const int batch_size,
                const int hidden1_size,
                const int hidden2_size,
                const float memory_decay)
            {
                int batch_idx = get_global_id(0);
                int hidden_idx = get_global_id(1);
                
                if (batch_idx < batch_size && hidden_idx < hidden2_size) {
                    float sum = biases[batch_idx * hidden2_size + hidden_idx];
                    
                    for (int i = 0; i < hidden1_size; i++) {
                        int weight_idx = batch_idx * hidden1_size * hidden2_size + 
                                       i * hidden2_size + hidden_idx;
                        int input_idx = batch_idx * hidden1_size + i;
                        sum += inputs[input_idx] * weights[weight_idx];
                    }
                    
                    // Agregar memoria
                    sum += memory[batch_idx * hidden2_size + hidden_idx] * memory_decay;
                    
                    outputs[batch_idx * hidden2_size + hidden_idx] = tanh_act(sum);
                }
            }
            
            // Procesamiento por lotes - Capa de salida
            __kernel void batch_output(
                __global const float *inputs,      // [batch_size, hidden2_size]
                __global const float *weights,     // [batch_size, hidden2_size, output_size]
                __global const float *biases,      // [batch_size, output_size]
                __global float *outputs,           // [batch_size, output_size]
                const int batch_size,
                const int hidden2_size,
                const int output_size)
            {
                int batch_idx = get_global_id(0);
                int output_idx = get_global_id(1);
                
                if (batch_idx < batch_size && output_idx < output_size) {
                    float sum = biases[batch_idx * output_size + output_idx];
                    
                    for (int i = 0; i < hidden2_size; i++) {
                        int weight_idx = batch_idx * hidden2_size * output_size + 
                                       i * output_size + output_idx;
                        int input_idx = batch_idx * hidden2_size + i;
                        sum += inputs[input_idx] * weights[weight_idx];
                    }
                    
                    outputs[batch_idx * output_size + output_idx] = sigmoid(sum);
                }
            }
            """
            
            self.cl_program = cl.Program(self.cl_context, kernel_code).build()
            
            # Cachear kernels (evita warnings y mejora rendimiento)
            self.kernel_layer1 = cl.Kernel(self.cl_program, "batch_layer1")
            self.kernel_layer2 = cl.Kernel(self.cl_program, "batch_layer2")
            self.kernel_output = cl.Kernel(self.cl_program, "batch_output")
            
            self.initialized = True
            
            device_name = device.name
            device_type = "GPU" if device.type == cl.device_type.GPU else "CPU"
            print(f"✅ Procesador por lotes inicializado en {device_type}: {device_name}")
            
        except Exception as e:
            print(f"⚠️  No se pudo inicializar procesador por lotes: {e}")
            self.initialized = False
    
    def process_batch(self, creatures: List, inputs_batch: List[np.ndarray]) -> List[np.ndarray]:
        """Procesar un lote de criaturas en paralelo"""
        if not self.initialized or len(creatures) == 0:
            # Fallback a procesamiento secuencial
            return [c.brain._forward_cpu(inp) for c, inp in zip(creatures, inputs_batch)]
        
        try:
            batch_size = len(creatures)
            
            # Obtener dimensiones de la primera red
            first_brain = creatures[0].brain
            input_size = first_brain.input_size
            hidden_size = first_brain.hidden_size
            hidden2_size = first_brain.hidden_size2
            output_size = first_brain.output_size
            
            # Preparar datos en formato de lote
            inputs_flat = np.concatenate([inp.flatten() for inp in inputs_batch]).astype(np.float32)
            
            # Recopilar pesos y biases de todas las redes
            weights_ih1 = np.concatenate([c.brain.weights_ih1.flatten() for c in creatures]).astype(np.float32)
            weights_h1h2 = np.concatenate([c.brain.weights_h1h2.flatten() for c in creatures]).astype(np.float32)
            weights_h2o = np.concatenate([c.brain.weights_h2o.flatten() for c in creatures]).astype(np.float32)
            
            biases_h1 = np.concatenate([c.brain.bias_h1 for c in creatures]).astype(np.float32)
            biases_h2 = np.concatenate([c.brain.bias_h2 for c in creatures]).astype(np.float32)
            biases_o = np.concatenate([c.brain.bias_o for c in creatures]).astype(np.float32)
            
            memory = np.concatenate([c.brain.memory for c in creatures]).astype(np.float32)
            
            # Crear buffers en GPU
            inputs_buf = cl.Buffer(self.cl_context, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=inputs_flat)
            weights_ih1_buf = cl.Buffer(self.cl_context, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=weights_ih1)
            weights_h1h2_buf = cl.Buffer(self.cl_context, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=weights_h1h2)
            weights_h2o_buf = cl.Buffer(self.cl_context, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=weights_h2o)
            biases_h1_buf = cl.Buffer(self.cl_context, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=biases_h1)
            biases_h2_buf = cl.Buffer(self.cl_context, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=biases_h2)
            biases_o_buf = cl.Buffer(self.cl_context, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=biases_o)
            memory_buf = cl.Buffer(self.cl_context, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=memory)
            
            # Buffers de salida
            hidden1_out = np.zeros(batch_size * hidden_size, dtype=np.float32)
            hidden2_out = np.zeros(batch_size * hidden2_size, dtype=np.float32)
            output_out = np.zeros(batch_size * output_size, dtype=np.float32)
            
            hidden1_buf = cl.Buffer(self.cl_context, cl.mem_flags.READ_WRITE, hidden1_out.nbytes)
            hidden2_buf = cl.Buffer(self.cl_context, cl.mem_flags.READ_WRITE, hidden2_out.nbytes)
            output_buf = cl.Buffer(self.cl_context, cl.mem_flags.WRITE_ONLY, output_out.nbytes)
            
            # Ejecutar kernels en secuencia (usando kernels cacheados)
            # Capa 1
            self.kernel_layer1(
                self.cl_queue, (batch_size, hidden_size), None,
                inputs_buf, weights_ih1_buf, biases_h1_buf, hidden1_buf,
                np.int32(batch_size), np.int32(input_size), np.int32(hidden_size)
            )
            
            # Capa 2
            self.kernel_layer2(
                self.cl_queue, (batch_size, hidden2_size), None,
                hidden1_buf, weights_h1h2_buf, biases_h2_buf, memory_buf, hidden2_buf,
                np.int32(batch_size), np.int32(hidden_size), np.int32(hidden2_size),
                np.float32(first_brain.memory_decay)
            )
            
            # Capa de salida
            self.kernel_output(
                self.cl_queue, (batch_size, output_size), None,
                hidden2_buf, weights_h2o_buf, biases_o_buf, output_buf,
                np.int32(batch_size), np.int32(hidden2_size), np.int32(output_size)
            )
            
            # Leer resultados
            cl.enqueue_copy(self.cl_queue, hidden2_out, hidden2_buf)
            cl.enqueue_copy(self.cl_queue, output_out, output_buf)
            
            # Actualizar memoria de cada criatura
            for i, creature in enumerate(creatures):
                start_idx = i * hidden2_size
                end_idx = start_idx + hidden2_size
                creature.brain.memory = hidden2_out[start_idx:end_idx]
            
            # Dividir resultados por criatura
            results = []
            for i in range(batch_size):
                start_idx = i * output_size
                end_idx = start_idx + output_size
                results.append(output_out[start_idx:end_idx])
            
            return results
            
        except Exception as e:
            # Fallback a CPU si falla
            print(f"⚠️  Error en procesamiento por lotes, usando CPU: {e}")
            return [c.brain._forward_cpu(inp) for c, inp in zip(creatures, inputs_batch)]


# Instancia global del procesador
_batch_processor = None

def get_batch_processor() -> NeuralBatchProcessor:
    """Obtener instancia global del procesador por lotes"""
    global _batch_processor
    if _batch_processor is None:
        _batch_processor = NeuralBatchProcessor()
    return _batch_processor
