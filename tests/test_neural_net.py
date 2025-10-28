"""
Tests para red neuronal
"""

import pytest
from engine.neural_net import NeuralNetwork


def test_neural_network_creation():
    """Test creación de red neuronal"""
    nn = NeuralNetwork(8, 16, 4)
    
    assert nn.input_size == 8
    assert nn.hidden_size == 16
    assert nn.output_size == 4


def test_neural_network_forward():
    """Test propagación hacia adelante"""
    nn = NeuralNetwork(8, 16, 4)
    inputs = [0.5] * 8
    
    outputs = nn.forward(inputs)
    
    assert len(outputs) == 4
    assert all(0 <= o <= 1 for o in outputs)  # Sigmoid output


def test_neural_network_mutation():
    """Test mutación de pesos"""
    nn = NeuralNetwork(8, 16, 4)
    
    original_weights = nn.weights_ih.copy()
    nn.mutate(rate=1.0)  # 100% mutación
    
    # Verificar que cambió algo
    assert not (nn.weights_ih == original_weights).all()
