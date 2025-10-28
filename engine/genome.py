"""
Sistema genético - Genoma digital
"""

import random
from typing import List
import config


class Genome:
    """Genoma que define comportamiento base de la criatura"""
    
    def __init__(self, instructions: List[str] = None):
        if instructions is None:
            # Genoma aleatorio inicial
            self.instructions = self.generate_random()
        else:
            self.instructions = instructions
    
    def generate_random(self, length: int = 20) -> List[str]:
        """Generar genoma aleatorio"""
        instruction_types = [
            'MOVE_FORWARD',
            'TURN_LEFT',
            'TURN_RIGHT',
            'SEEK_FOOD',
            'SEEK_CREATURE',
            'FLEE',
            'REST',
            'REPRODUCE'
        ]
        return [random.choice(instruction_types) for _ in range(length)]
    
    def mutate(self, complexity: float = 0) -> 'Genome':
        """Crear copia mutada del genoma (EVOLUTIVO - CORREGIDO)"""
        new_instructions = self.instructions.copy()
        mutation_rate = config.MUTATION_RATE_BASE
        
        # Criaturas más complejas tienen genomas más largos
        target_length = 20 + int(complexity / 50)  # +1 instrucción cada 50 complejidad
        target_length = min(target_length, 50)  # Máximo 50 instrucciones
        
        instruction_types = [
            'MOVE_FORWARD', 'TURN_LEFT', 'TURN_RIGHT',
            'SEEK_FOOD', 'SEEK_CREATURE', 'FLEE', 'REST', 'REPRODUCE'
        ]
        
        # Iterar sobre índices de forma segura
        i = 0
        while i < len(new_instructions):
            if random.random() < mutation_rate:
                mutation_type = random.random()
                
                if mutation_type < 0.6:  # Mutación puntual
                    new_instructions[i] = random.choice(instruction_types)
                    i += 1
                elif mutation_type < 0.85:  # Inserción
                    if len(new_instructions) < target_length:
                        new_instructions.insert(i, random.choice(instruction_types))
                        i += 1  # Saltar la instrucción insertada
                    i += 1
                elif mutation_type < 0.92:  # Deleción
                    if len(new_instructions) > 10:  # Mínimo 10 instrucciones
                        new_instructions.pop(i)
                        # No incrementar i porque el siguiente elemento ahora está en i
                    else:
                        i += 1
                else:  # Duplicación
                    if len(new_instructions) < target_length:
                        new_instructions.insert(i, new_instructions[i])
                        i += 1  # Saltar la instrucción duplicada
                    i += 1
            else:
                i += 1
        
        # Asegurar crecimiento gradual
        while len(new_instructions) < target_length and random.random() < 0.3:
            new_instructions.append(random.choice(instruction_types))
        
        return Genome(new_instructions)
    
    def crossover(self, other: 'Genome') -> 'Genome':
        """Cruzamiento genético con otro genoma"""
        point = random.randint(1, min(len(self.instructions), len(other.instructions)) - 1)
        new_instructions = self.instructions[:point] + other.instructions[point:]
        return Genome(new_instructions)
    
    def to_dict(self) -> dict:
        """Serializar"""
        return {'instructions': self.instructions}
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Genome':
        """Deserializar"""
        return cls(data['instructions'])
    
    def __len__(self):
        return len(self.instructions)
