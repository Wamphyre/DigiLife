"""
Red neuronal profunda con soporte OpenCL optimizado
"""

import numpy as np
from typing import List, Optional
import config

# Intentar importar PyOpenCL
try:
    import pyopencl as cl
    import pyopencl.array as cl_array
    OPENCL_AVAILABLE = True
except ImportError:
    OPENCL_AVAILABLE = False
    cl = None
    cl_array = None


class NeuralNetwork:
    """Red neuronal feedforward profunda (3 capas ocultas)"""
    
    # Contexto OpenCL compartido (inicializado una vez)
    _cl_context = None
    _cl_queue = None
    _cl_program = None
    
    def __init__(self, input_size: int, hidden_size: int, output_size: int, parent: Optional['NeuralNetwork'] = None):
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.hidden_size2 = hidden_size // 2  # Segunda capa más pequeña
        self.output_size = output_size
        
        # Si hay padre, heredar pesos con mutación
        if parent:
            self._inherit_from_parent(parent)
        else:
            # Inicializar pesos aleatoriamente (Xavier initialization)
            scale1 = np.sqrt(2.0 / input_size)
            scale2 = np.sqrt(2.0 / hidden_size)
            scale3 = np.sqrt(2.0 / self.hidden_size2)
            
            self.weights_ih1 = np.random.randn(input_size, hidden_size).astype(np.float32) * scale1
            self.weights_h1h2 = np.random.randn(hidden_size, self.hidden_size2).astype(np.float32) * scale2
            self.weights_h2o = np.random.randn(self.hidden_size2, output_size).astype(np.float32) * scale3
            
            self.bias_h1 = np.zeros(hidden_size, dtype=np.float32)
            self.bias_h2 = np.zeros(self.hidden_size2, dtype=np.float32)
            self.bias_o = np.zeros(output_size, dtype=np.float32)
        
        # Memoria de corto plazo (para comportamiento temporal)
        self.memory = np.zeros(self.hidden_size2, dtype=np.float32)
        self.memory_decay = 0.7  # Decaimiento de memoria
        
        # Inicializar OpenCL si está disponible y configurado
        if config.USE_GPU and OPENCL_AVAILABLE and NeuralNetwork._cl_context is None:
            self._init_opencl()
    
    def _inherit_from_parent(self, parent: 'NeuralNetwork'):
        """Heredar pesos del padre con mutación inteligente"""
        mutation_rate = 0.15
        mutation_strength = 0.2
        
        # Copiar pesos del padre
        self.weights_ih1 = parent.weights_ih1.copy()
        self.weights_h1h2 = parent.weights_h1h2.copy()
        self.weights_h2o = parent.weights_h2o.copy()
        self.bias_h1 = parent.bias_h1.copy()
        self.bias_h2 = parent.bias_h2.copy()
        self.bias_o = parent.bias_o.copy()
        
        # Mutar con probabilidad
        for weights in [self.weights_ih1, self.weights_h1h2, self.weights_h2o]:
            mask = np.random.random(weights.shape) < mutation_rate
            weights[mask] += np.random.randn(np.sum(mask)) * mutation_strength
        
        for bias in [self.bias_h1, self.bias_h2, self.bias_o]:
            mask = np.random.random(bias.shape) < mutation_rate
            bias[mask] += np.random.randn(np.sum(mask)) * mutation_strength
    
    @classmethod
    def _init_opencl(cls):
        """Inicializar contexto OpenCL (una sola vez)"""
        try:
            platform = cl.get_platforms()[0]
            device = platform.get_devices()[0]
            cls._cl_context = cl.Context([device])
            cls._cl_queue = cl.CommandQueue(cls._cl_context)
            
            # Kernel optimizado para red neuronal profunda
            kernel_code = """
            // Activación ReLU
            inline float relu(float x) {
                return fmax(0.0f, x);
            }
            
            // Activación Sigmoid
            inline float sigmoid(float x) {
                return 1.0f / (1.0f + exp(-clamp(x, -10.0f, 10.0f)));
            }
            
            // Activación Tanh
            inline float tanh_act(float x) {
                return tanh(clamp(x, -10.0f, 10.0f));
            }
            
            // Forward pass completo de la red neuronal
            __kernel void neural_forward(
                __global const float *input,
                __global const float *w_ih1,
                __global const float *b_h1,
                __global const float *w_h1h2,
                __global const float *b_h2,
                __global const float *w_h2o,
                __global const float *b_o,
                __global const float *memory,
                __global float *output,
                __global float *new_memory,
                const int input_size,
                const int hidden1_size,
                const int hidden2_size,
                const int output_size,
                const float memory_decay)
            {
                int idx = get_global_id(0);
                
                // Capa 1: input -> hidden1
                __local float hidden1[64];  // Ajustar según hidden_size
                if (idx < hidden1_size) {
                    float sum = b_h1[idx];
                    for (int i = 0; i < input_size; i++) {
                        sum += input[i] * w_ih1[i * hidden1_size + idx];
                    }
                    hidden1[idx] = relu(sum);
                }
                barrier(CLK_LOCAL_MEM_FENCE);
                
                // Capa 2: hidden1 -> hidden2 (con memoria)
                __local float hidden2[32];  // Ajustar según hidden2_size
                if (idx < hidden2_size) {
                    float sum = b_h2[idx];
                    for (int i = 0; i < hidden1_size; i++) {
                        sum += hidden1[i] * w_h1h2[i * hidden2_size + idx];
                    }
                    // Agregar memoria de corto plazo
                    sum += memory[idx] * memory_decay;
                    hidden2[idx] = tanh_act(sum);
                    new_memory[idx] = hidden2[idx];  // Actualizar memoria
                }
                barrier(CLK_LOCAL_MEM_FENCE);
                
                // Capa 3: hidden2 -> output
                if (idx < output_size) {
                    float sum = b_o[idx];
                    for (int i = 0; i < hidden2_size; i++) {
                        sum += hidden2[i] * w_h2o[i * output_size + idx];
                    }
                    output[idx] = sigmoid(sum);
                }
            }
            """
            cls._cl_program = cl.Program(cls._cl_context, kernel_code).build()
            print("✅ OpenCL inicializado con red neuronal profunda")
        except Exception as e:
            print(f"⚠️  No se pudo inicializar OpenCL: {e}")
            cls._cl_context = None
    
    def forward(self, inputs: List[float], use_gpu: bool = False) -> List[float]:
        """Propagación hacia adelante (CPU o GPU)"""
        x = np.array(inputs, dtype=np.float32)
        
        # Usar GPU si está disponible y configurado
        if use_gpu and self._cl_context is not None:
            return self._forward_gpu(x)
        else:
            return self._forward_cpu(x)
    
    def _forward_cpu(self, x: np.ndarray) -> List[float]:
        """Forward pass en CPU (3 capas)"""
        # Capa 1: input -> hidden1
        hidden1 = np.dot(x, self.weights_ih1) + self.bias_h1
        hidden1 = self.relu(hidden1)
        
        # Capa 2: hidden1 -> hidden2 (con memoria)
        hidden2 = np.dot(hidden1, self.weights_h1h2) + self.bias_h2
        hidden2 = hidden2 + self.memory * self.memory_decay
        hidden2 = self.tanh(hidden2)
        
        # Actualizar memoria
        self.memory = hidden2.copy()
        
        # Capa 3: hidden2 -> output
        output = np.dot(hidden2, self.weights_h2o) + self.bias_o
        output = self.sigmoid(output)
        
        return output.tolist()
    
    def _forward_gpu(self, x: np.ndarray) -> List[float]:
        """Forward pass en GPU usando OpenCL"""
        try:
            # Crear buffers en GPU
            input_buf = cl.Buffer(self._cl_context, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=x)
            w_ih1_buf = cl.Buffer(self._cl_context, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=self.weights_ih1)
            b_h1_buf = cl.Buffer(self._cl_context, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=self.bias_h1)
            w_h1h2_buf = cl.Buffer(self._cl_context, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=self.weights_h1h2)
            b_h2_buf = cl.Buffer(self._cl_context, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=self.bias_h2)
            w_h2o_buf = cl.Buffer(self._cl_context, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=self.weights_h2o)
            b_o_buf = cl.Buffer(self._cl_context, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=self.bias_o)
            memory_buf = cl.Buffer(self._cl_context, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=self.memory)
            
            output = np.zeros(self.output_size, dtype=np.float32)
            new_memory = np.zeros(self.hidden_size2, dtype=np.float32)
            output_buf = cl.Buffer(self._cl_context, cl.mem_flags.WRITE_ONLY, output.nbytes)
            new_memory_buf = cl.Buffer(self._cl_context, cl.mem_flags.WRITE_ONLY, new_memory.nbytes)
            
            # Ejecutar kernel
            self._cl_program.neural_forward(
                self._cl_queue, (max(self.hidden_size, self.hidden_size2, self.output_size),), None,
                input_buf, w_ih1_buf, b_h1_buf, w_h1h2_buf, b_h2_buf, w_h2o_buf, b_o_buf,
                memory_buf, output_buf, new_memory_buf,
                np.int32(self.input_size), np.int32(self.hidden_size), 
                np.int32(self.hidden_size2), np.int32(self.output_size),
                np.float32(self.memory_decay)
            )
            
            # Leer resultados
            cl.enqueue_copy(self._cl_queue, output, output_buf)
            cl.enqueue_copy(self._cl_queue, new_memory, new_memory_buf)
            self.memory = new_memory
            
            return output.tolist()
        except Exception as e:
            # Fallback a CPU si falla GPU
            return self._forward_cpu(x)
    
    @staticmethod
    def relu(x: np.ndarray) -> np.ndarray:
        """Función de activación ReLU"""
        return np.maximum(0, x)
    
    @staticmethod
    def sigmoid(x: np.ndarray) -> np.ndarray:
        """Función de activación Sigmoid"""
        return 1 / (1 + np.exp(-np.clip(x, -500, 500)))
    
    @staticmethod
    def tanh(x: np.ndarray) -> np.ndarray:
        """Función de activación Tanh"""
        return np.tanh(x)
    
    def mutate(self, rate: float = 0.1, strength: float = 0.2):
        """Mutar pesos de la red con estrategia adaptativa"""
        # Mutación más agresiva en capas tempranas
        for weights, layer_strength in [
            (self.weights_ih1, strength * 1.2),
            (self.weights_h1h2, strength),
            (self.weights_h2o, strength * 0.8)
        ]:
            mask = np.random.random(weights.shape) < rate
            weights[mask] += np.random.randn(np.sum(mask)) * layer_strength
        
        # Mutación de bias
        for bias in [self.bias_h1, self.bias_h2, self.bias_o]:
            mask = np.random.random(bias.shape) < rate
            bias[mask] += np.random.randn(np.sum(mask)) * strength * 0.5
    
    def reset_memory(self):
        """Resetear memoria de corto plazo"""
        self.memory = np.zeros(self.hidden_size2, dtype=np.float32)


class NeuralNetworkBatch:
    """Procesamiento por lotes de múltiples redes neuronales (para GPU)"""
    
    def __init__(self, networks: List[NeuralNetwork]):
        self.networks = networks
    
    def forward_batch(self, inputs_batch: List[List[float]]) -> List[List[float]]:
        """Procesar múltiples inputs en paralelo"""
        # Por ahora, procesamiento secuencial
        # TODO: Implementar procesamiento GPU real con OpenCL
        results = []
        for inputs, network in zip(inputs_batch, self.networks):
            results.append(network.forward(inputs))
        return results
