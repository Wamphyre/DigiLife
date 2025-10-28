"""
Motor evolutivo - Selección natural y especiación
"""

from typing import List
import config


class Evolution:
    """Gestión de procesos evolutivos"""
    
    def __init__(self, world):
        self.world = world
        self.species = {}  # id_especie -> lista de criaturas
    
    def apply_selection_pressure(self):
        """Aplicar presión selectiva"""
        # Las criaturas con menos energía tienen más probabilidad de morir
        if not self.world.creatures:
            return
        
        # Ordenar por energía
        sorted_creatures = sorted(self.world.creatures, key=lambda c: c.energy)
        
        # Eliminar el 10% más débil si hay sobrepoblación
        if len(sorted_creatures) > config.MAX_POPULATION * 0.8:
            to_remove = int(len(sorted_creatures) * 0.1)
            for creature in sorted_creatures[:to_remove]:
                if creature in self.world.creatures:
                    self.world.creatures.remove(creature)
                    self.world.total_deaths += 1
    
    def identify_species(self):
        """Identificar especies por similitud genética"""
        # Simplificado: agrupar por complejidad similar
        self.species.clear()
        
        for creature in self.world.creatures:
            complexity_group = int(creature.complexity / 200)
            if complexity_group not in self.species:
                self.species[complexity_group] = []
            self.species[complexity_group].append(creature)
        
        self.world.species_count = len(self.species)
    
    def get_fitness_stats(self) -> dict:
        """Obtener estadísticas de fitness"""
        if not self.world.creatures:
            return {
                'avg_energy': 0,
                'avg_complexity': 0,
                'avg_age': 0,
                'max_fitness': 0
            }
        
        energies = [c.energy for c in self.world.creatures]
        complexities = [c.complexity for c in self.world.creatures]
        ages = [c.age for c in self.world.creatures]
        
        return {
            'avg_energy': sum(energies) / len(energies),
            'avg_complexity': sum(complexities) / len(complexities),
            'avg_age': sum(ages) / len(ages),
            'max_fitness': max(energies)
        }
