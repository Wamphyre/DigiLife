"""
Gestión del mundo y ecosistema digital
"""

import random
import pickle
import numpy as np
from typing import List, Optional, Tuple
import config
from .creature import Creature
from .disease import DiseaseSystem
from .neural_batch import get_batch_processor
from .knowledge_system import KnowledgeBase
from utils.data_generator import DataGenerator


class World:
    """Mundo donde viven las criaturas digitales"""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.creatures: List[Creature] = []
        self.data_items: List[dict] = []  # Alimento
        self.selected_creature: Optional[Creature] = None
        
        # Estadísticas
        self.cycle = 0
        self.total_births = 0
        self.total_deaths = 0
        self.species_count = 0
        
        # Estadísticas de depredación
        self.predation_kills = 0
        self.active_predators = 0
        
        # Control
        self.speed_multiplier = 1.0
        
        # Generador de datos
        self.data_generator = DataGenerator(self)
        self.data_spawn_timer = 0
        
        # Sistema de enfermedades
        self.disease_system = DiseaseSystem(self)
        
        # Sistema de conocimiento e inteligencia
        self.knowledge_base = KnowledgeBase()
        
        # Procesador por lotes para GPU
        self.batch_processor = get_batch_processor()
        self.batch_size = 32  # Procesar 32 criaturas a la vez
    
    def populate(self, count: int):
        """Poblar mundo con criaturas iniciales"""
        for _ in range(count):
            x = random.uniform(50, self.width - 50)
            y = random.uniform(50, self.height - 50)
            creature = Creature(x, y, self)
            self.creatures.append(creature)
            self.total_births += 1
    
    def update(self, dt: float):
        """Actualizar mundo (OPTIMIZADO + NUEVOS SISTEMAS v2.8)"""
        dt *= self.speed_multiplier
        self.cycle += 1
        
        # Generar datos/alimento
        self.data_spawn_timer += dt
        spawn_interval = 1.0 / config.DATA_SPAWN_RATE
        while self.data_spawn_timer >= spawn_interval:
            self.spawn_data()
            self.data_spawn_timer -= spawn_interval
        
        # Actualizar sistema de enfermedades
        if config.DISEASES_ENABLED:
            self.disease_system.update(dt)
        
        # Actualizar sistema de conocimiento
        self.knowledge_base.update_world_stats(self)
        
        # Actualizar criaturas (OPTIMIZADO v2.9.1: prioridad para complejas)
        dead_creatures = []
        
        # Separar criaturas por complejidad
        if config.USE_GPU and config.GPU_PRIORITY_COMPLEX:
            complex_creatures = [c for c in self.creatures if c.complexity >= config.COMPLEX_THRESHOLD]
            simple_creatures = [c for c in self.creatures if c.complexity < config.COMPLEX_THRESHOLD]
            
            # Procesar complejas SIEMPRE en GPU (son las más costosas)
            if complex_creatures:
                self._update_creatures_batched(dt, dead_creatures, complex_creatures)
            
            # Procesar simples en GPU solo si hay muchas
            if len(simple_creatures) >= config.GPU_THRESHOLD_CREATURES:
                self._update_creatures_batched(dt, dead_creatures, simple_creatures)
            else:
                # Pocas simples: CPU es más eficiente
                for creature in simple_creatures:
                    creature.update(dt)
                    if creature.is_dead():
                        dead_creatures.append(creature)
                    if config.DISEASES_ENABLED and hasattr(creature, 'infection') and creature.infection:
                        nearby = self.get_creatures_near(creature.x, creature.y, 30)
                        self.disease_system.try_spread(creature, nearby)
        elif config.USE_GPU and len(self.creatures) >= config.GPU_THRESHOLD_CREATURES:
            # Procesamiento por lotes estándar
            self._update_creatures_batched(dt, dead_creatures, self.creatures)
        else:
            # Procesamiento secuencial para poblaciones pequeñas
            for creature in self.creatures:
                creature.update(dt)
                if creature.is_dead():
                    dead_creatures.append(creature)
                if config.DISEASES_ENABLED and hasattr(creature, 'infection') and creature.infection:
                    nearby = self.get_creatures_near(creature.x, creature.y, 30)
                    self.disease_system.try_spread(creature, nearby)
        
        # Eliminar criaturas muertas (una sola operación)
        if dead_creatures:
            for creature in dead_creatures:
                self.creatures.remove(creature)
                self.total_deaths += 1
                if config.DEBUG['LOG_DEATHS']:
                    print(f"💀 Criatura {creature.id} murió (edad: {creature.age:.1f})")
        
        # Actualizar conteo de especies (cada 50 ciclos para optimizar)
        if self.cycle % 50 == 0:
            self.update_species_count()
            self.update_predator_count()
        
        # Control de población (OPTIMIZADO: solo si excede significativamente)
        excess = len(self.creatures) - config.MAX_POPULATION
        if excess > 10:  # Solo si hay exceso significativo
            try:
                # Eliminar las más débiles (por fitness, no energía)
                self.creatures.sort(key=lambda c: c.fitness)
                to_remove = self.creatures[:excess]
                for creature in to_remove:
                    if creature in self.creatures:  # Verificar que aún existe
                        self.creatures.remove(creature)
                        self.total_deaths += 1
            except Exception as e:
                # Si hay error, simplemente truncar la lista
                self.creatures = self.creatures[-config.MAX_POPULATION:]
    
    def update_species_count(self):
        """Actualizar conteo de especies únicas"""
        if not self.creatures:
            self.species_count = 0
            return
        
        # Agrupar criaturas por ID de especie
        species_ids = set()
        for creature in self.creatures:
            species_ids.add(creature.get_species_id())
        
        self.species_count = len(species_ids)
    
    def update_predator_count(self):
        """Actualizar conteo de depredadores activos"""
        self.active_predators = sum(
            1 for c in self.creatures 
            if hasattr(c, 'is_predator') and c.is_predator and 
            c.complexity >= config.PREDATION_COMPLEXITY_THRESHOLD
        )
    
    def get_top_predators(self, limit: int = 5) -> List[Tuple]:
        """Obtener top N depredadores por número de kills"""
        predators = [
            (c.id, c.kills, c.complexity) 
            for c in self.creatures 
            if hasattr(c, 'kills') and c.kills > 0
        ]
        # Ordenar por kills (descendente)
        predators.sort(key=lambda x: x[1], reverse=True)
        return predators[:limit]
    
    def _update_creatures_batched(self, dt: float, dead_creatures: List, creatures_to_process: List = None):
        """Actualizar criaturas usando procesamiento por lotes en GPU"""
        if creatures_to_process is None:
            creatures_to_process = self.creatures
        
        # Procesar en lotes de tamaño fijo
        for i in range(0, len(creatures_to_process), self.batch_size):
            batch = creatures_to_process[i:i + self.batch_size]
            
            # Preparar inputs para el lote (solo la parte neural)
            inputs_batch = []
            for creature in batch:
                # Preparar sensores (sin ejecutar la red aún)
                inputs = creature.prepare_neural_inputs()
                inputs_batch.append(np.array(inputs, dtype=np.float32))
            
            # Procesar lote en GPU
            outputs_batch = self.batch_processor.process_batch(batch, inputs_batch)
            
            # Aplicar resultados y actualizar resto de la criatura
            for creature, outputs in zip(batch, outputs_batch):
                # Aplicar outputs de la red neuronal
                creature.apply_neural_outputs(outputs)
                
                # Actualizar resto (física, energía, etc.) - CPU
                creature.update_non_neural(dt)
                
                # Marcar si murió
                if creature.is_dead():
                    dead_creatures.append(creature)
                
                # Propagar enfermedades
                if config.DISEASES_ENABLED and hasattr(creature, 'infection') and creature.infection:
                    nearby = self.get_creatures_near(creature.x, creature.y, 30)
                    self.disease_system.try_spread(creature, nearby)
    
    def spawn_data(self):
        """Generar un dato/alimento en posición aleatoria (MEJORADO - evita bordes)"""
        data_type = self.data_generator.random_type()
        
        # Evitar bordes para mejor distribución (80% en centro, 20% en bordes)
        if random.random() < 0.8:
            # Spawn en zona central (evitar bordes)
            margin = 100
            x = random.uniform(margin, self.width - margin)
            y = random.uniform(margin, self.height - margin)
        else:
            # Spawn ocasional en bordes
            x = random.uniform(10, self.width - 10)
            y = random.uniform(10, self.height - 10)
        
        data_item = {
            'type': data_type,
            'x': x,
            'y': y,
            'size': 5,
            'color': config.DATA_COLORS[data_type]
        }
        self.data_items.append(data_item)
    
    def consume_data(self, creature: Creature, data_item: dict):
        """Criatura consume un dato"""
        if data_item in self.data_items:
            self.data_items.remove(data_item)
            
            # Aplicar nutrición
            nutrition = config.DATA_NUTRITION[data_item['type']]
            creature.energy = min(creature.max_energy, 
                                 creature.energy + nutrition['energy'])
            creature.complexity += nutrition['cognition']
            creature.vocal_development += nutrition['vocal']
    
    def add_creature(self, creature: Creature):
        """Añadir criatura al mundo (nacimiento)"""
        self.creatures.append(creature)
        self.total_births += 1
        if config.DEBUG['LOG_BIRTHS']:
            print(f"🐣 Criatura {creature.id} nació (gen: {creature.generation})")
    
    def select_creature_at(self, pos: Tuple[float, float]):
        """Seleccionar criatura en posición"""
        x, y = pos
        for creature in self.creatures:
            dx = creature.x - x
            dy = creature.y - y
            dist = (dx*dx + dy*dy) ** 0.5
            if dist < creature.size:
                self.selected_creature = creature
                return
        self.selected_creature = None
    
    def get_creatures_near(self, x: float, y: float, radius: float) -> List[Creature]:
        """Obtener criaturas cerca de una posición"""
        nearby = []
        for creature in self.creatures:
            dx = creature.x - x
            dy = creature.y - y
            dist = (dx*dx + dy*dy) ** 0.5
            if dist < radius:
                nearby.append(creature)
        return nearby
    
    def get_data_near(self, x: float, y: float, radius: float) -> List[dict]:
        """Obtener datos cerca de una posición"""
        nearby = []
        for data in self.data_items:
            dx = data['x'] - x
            dy = data['y'] - y
            dist = (dx*dx + dy*dy) ** 0.5
            if dist < radius:
                nearby.append(data)
        return nearby
    
    def reset(self):
        """Reiniciar mundo"""
        self.creatures.clear()
        self.data_items.clear()
        self.selected_creature = None
        self.cycle = 0
        self.total_births = 0
        self.total_deaths = 0
        self.species_count = 0
    
    def save(self, filename: str):
        """Guardar estado del mundo"""
        state = {
            'width': self.width,
            'height': self.height,
            'creatures': [c.to_dict() for c in self.creatures],
            'data_items': self.data_items,
            'cycle': self.cycle,
            'total_births': self.total_births,
            'total_deaths': self.total_deaths,
            'species_count': self.species_count
        }
        with open(filename, 'wb') as f:
            pickle.dump(state, f)
    
    def load(self, filename: str):
        """Cargar estado del mundo"""
        with open(filename, 'rb') as f:
            state = pickle.load(f)
        
        self.width = state['width']
        self.height = state['height']
        self.data_items = state['data_items']
        self.cycle = state['cycle']
        self.total_births = state['total_births']
        self.total_deaths = state['total_deaths']
        self.species_count = state['species_count']
        
        # Reconstruir criaturas
        self.creatures.clear()
        for c_data in state['creatures']:
            creature = Creature.from_dict(c_data, self)
            self.creatures.append(creature)
    
    @property
    def population(self) -> int:
        """Población actual"""
        return len(self.creatures)
    
    @property
    def max_complexity(self) -> float:
        """Complejidad máxima en población"""
        if not self.creatures:
            return 0
        return max(c.complexity for c in self.creatures)
    
    @property
    def vocal_creatures(self) -> int:
        """Criaturas con capacidad vocal"""
        return sum(1 for c in self.creatures if c.can_vocalize())
