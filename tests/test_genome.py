"""
Tests para sistema genético
"""

import pytest
from engine.genome import Genome


def test_genome_creation():
    """Test creación de genoma"""
    genome = Genome()
    
    assert len(genome.instructions) > 0
    assert all(isinstance(inst, str) for inst in genome.instructions)


def test_genome_mutation():
    """Test mutación"""
    genome = Genome()
    original_length = len(genome)
    
    mutated = genome.mutate()
    
    # Debe ser diferente
    assert mutated.instructions != genome.instructions or len(mutated) != original_length


def test_genome_crossover():
    """Test cruzamiento"""
    genome1 = Genome()
    genome2 = Genome()
    
    child = genome1.crossover(genome2)
    
    assert len(child) > 0
    # Debe contener material de ambos padres
    assert any(inst in genome1.instructions or inst in genome2.instructions 
              for inst in child.instructions)
