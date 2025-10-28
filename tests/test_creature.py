"""
Tests para el módulo Creature
"""

import pytest
from engine.creature import Creature
from engine.world import World


def test_creature_creation():
    """Test creación de criatura"""
    world = World(800, 600)
    creature = Creature(100, 100, world)
    
    assert creature.x == 100
    assert creature.y == 100
    assert creature.energy > 0
    assert creature.generation == 0


def test_creature_movement():
    """Test movimiento de criatura"""
    world = World(800, 600)
    creature = Creature(100, 100, world)
    
    initial_x = creature.x
    initial_y = creature.y
    
    creature.vx = 10
    creature.vy = 10
    creature.move(1.0)
    
    assert creature.x != initial_x or creature.y != initial_y


def test_creature_reproduction():
    """Test reproducción"""
    world = World(800, 600)
    creature = Creature(100, 100, world)
    creature.energy = 200
    creature.age = 100
    
    initial_population = world.population
    
    if creature.can_reproduce():
        creature.reproduce()
        assert world.population == initial_population + 1


def test_creature_death():
    """Test muerte por falta de energía"""
    world = World(800, 600)
    creature = Creature(100, 100, world)
    creature.energy = 0
    
    assert creature.is_dead()


def test_creature_phases():
    """Test fases evolutivas"""
    world = World(800, 600)
    creature = Creature(100, 100, world)
    
    creature.complexity = 100
    assert creature.get_phase() == 'primitive'
    
    creature.complexity = 300
    assert creature.get_phase() == 'intermediate'
    
    creature.complexity = 700
    assert creature.get_phase() == 'advanced'
    
    creature.complexity = 1200
    assert creature.get_phase() == 'complex'
