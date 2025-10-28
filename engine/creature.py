"""
Criatura digital - Ser vivo artificial
"""

import random
import math
import numpy as np
from typing import Optional, Tuple, List
import config
from .genome import Genome
from .neural_net import NeuralNetwork
from .vocal_system import VocalSystem


# Contador global de IDs
_creature_id_counter = 0

def get_next_id():
    global _creature_id_counter
    _creature_id_counter += 1
    return _creature_id_counter


class Creature:
    """Ser digital que evoluciona y aprende"""
    
    def __init__(self, x: float, y: float, world, parent=None):
        self.id = get_next_id()
        self.world = world
        
        # Posición y movimiento
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.direction = random.uniform(0, 2 * math.pi)
        
        # Genética
        if parent:
            # Pasar complejidad del padre para genoma evolutivo
            self.genome = parent.genome.mutate(complexity=parent.complexity)
            self.generation = parent.generation + 1
            
            # HERENCIA MEJORADA v2.8: Heredar rasgos del padre (más generoso)
            # Complejidad: 70% del padre (aumentado para favorecer evolución)
            self.complexity = parent.complexity * 0.7
            
            # Energía máxima: heredar capacidad del padre
            self.max_energy = parent.max_energy
            
            # Desarrollo vocal: 50% del padre (aumentado)
            self.vocal_development = parent.vocal_development * 0.5
        else:
            self.genome = Genome()
            self.generation = 0
            self.complexity = 0
            self.max_energy = config.MAX_ENERGY
            self.vocal_development = 0
        
        # Estado vital
        self.age = 0
        self.energy = config.INITIAL_ENERGY  # Siempre empezar con energía inicial
        
        # Red neuronal (heredar del padre si existe)
        parent_brain = parent.brain if parent else None
        self.brain = NeuralNetwork(
            config.NEURAL_INPUT_SIZE,
            config.NEURAL_HIDDEN_SIZE,
            config.NEURAL_OUTPUT_SIZE,
            parent=parent_brain
        )
        
        # Sistema de fitness (recompensas/castigos)
        if parent:
            # Heredar 20% del fitness del padre (aumentado de 10%)
            self.fitness = parent.fitness * 0.2
            # Bonus por generación (criaturas evolucionadas empiezan mejor)
            self.fitness += self.generation * 2
        else:
            self.fitness = 0
        
        self.food_eaten = 0
        self.distance_traveled = 0
        self.last_x = x
        self.last_y = y
        
        # Sistema vocal
        self.vocal_system = VocalSystem(self)
        
        # Memoria
        self.memory = []
        self.memory_size = 20
        
        # Apariencia
        self.size = config.CREATURE_SIZE_BASE
        self.color = self.calculate_color()
    
    def update(self, dt: float):
        """Actualizar criatura (OPTIMIZADO)"""
        self.age += dt
        
        # Consumir energía (BALANCEADO v2.8 - favorece criaturas avanzadas)
        base_cost = config.ENERGY_COST_PER_CYCLE * dt
        complexity_cost = (self.complexity / 100) * dt  # Reducido de /50 a /100
        
        # Aplicar bonus de eficiencia (criaturas evolucionadas son MÁS eficientes)
        efficiency = self.get_efficiency_bonus()
        energy_cost = (base_cost + complexity_cost) * efficiency
        
        self.energy -= energy_cost
        
        # Pensar (red neuronal) - SIEMPRE, es crítico
        self.think(dt)
        
        # Mover - SIEMPRE, es crítico
        self.move(dt)
        
        # Buscar alimento - SIEMPRE, es crítico
        self.seek_food()
        
        # Intentar reproducirse - Solo cada 10 frames para optimizar
        if self.age % 10 < dt:  # Aproximadamente cada 10 ciclos
            if self.can_reproduce():
                self.reproduce()
        
        # Vocalizar si es apropiado - Reducir frecuencia
        if self.can_vocalize() and random.random() < 0.005:  # 0.5% por frame
            self.vocal_system.vocalize()
        
        # Actualizar apariencia - Solo cada 5 frames
        if self.age % 5 < dt:
            self.update_appearance()
        
        # NUEVOS COMPORTAMIENTOS v2.8
        # Actualizar infección si existe
        if not self.update_infection(dt):
            return  # Criatura murió por enfermedad
        
        # Intentar depredación (solo criaturas avanzadas)
        if self.age % 20 < dt:  # Cada 20 ciclos
            self.try_predation(dt)
        
        # Intentar colaboración (solo criaturas desarrolladas)
        if self.age % 15 < dt:  # Cada 15 ciclos
            self.try_collaboration(dt)
        
        # Intentar comunicación (solo criaturas complejas)
        if self.age % 10 < dt:  # Cada 10 ciclos
            self.try_communication(dt)
    
    def think(self, dt: float):
        """Procesar información con INSTINTO BÁSICO + red neuronal"""
        # INSTINTO BÁSICO: Siempre buscar alimento si hay hambre
        # Esto garantiza comportamiento mínimo incluso con red neuronal débil
        
        # Balance instinto/IA según complejidad (EVOLUTIVO)
        # Primitivas: 80% instinto, 20% IA
        # Intermedias: 60% instinto, 40% IA
        # Avanzadas: 40% instinto, 60% IA
        # Complejas: 20% instinto, 80% IA
        instinct_strength = max(0.2, 0.8 - (self.complexity / 1000))
        
        # Instinto: buscar alimento más cercano
        nearest_food = self.find_nearest_food()
        instinct_x = 0
        instinct_y = 0
        
        if nearest_food:
            dx = nearest_food['x'] - self.x
            dy = nearest_food['y'] - self.y
            dist = math.sqrt(dx*dx + dy*dy)
            
            if dist > 0:
                # Normalizar y aplicar urgencia
                urgency = 1.0 - (self.energy / self.max_energy)
                instinct_x = (dx / dist) * urgency
                instinct_y = (dy / dist) * urgency
        else:
            # Sin alimento visible: exploración aleatoria
            instinct_x = random.uniform(-0.5, 0.5)
            instinct_y = random.uniform(-0.5, 0.5)
        
        # Red neuronal (solo si la criatura es compleja)
        neural_x = 0
        neural_y = 0
        
        if self.complexity > 50:  # Solo usar red neuronal si hay algo de desarrollo
            try:
                inputs = self.get_sensor_inputs()
                outputs = self.brain.forward(inputs)
                
                # Verificar que outputs tenga al menos 4 elementos
                if len(outputs) >= 4:
                    # Outputs: [arriba, abajo, izquierda, derecha]
                    neural_y = outputs[0] - outputs[1]
                    neural_x = outputs[3] - outputs[2]
            except Exception as e:
                # Si hay error, usar solo instinto
                pass
        
        # Combinar instinto + red neuronal
        move_x = instinct_x * instinct_strength + neural_x * (1 - instinct_strength)
        move_y = instinct_y * instinct_strength + neural_y * (1 - instinct_strength)
        
        # Aplicar movimiento
        self.apply_movement(move_x, move_y)
    
    def get_sensor_inputs(self) -> List[float]:
        """Obtener inputs de sensores para red neuronal (MEJORADOS)"""
        inputs = []
        
        # 1. Energía normalizada
        energy_ratio = self.energy / self.max_energy
        inputs.append(energy_ratio)
        
        # 2-3. Alimento más cercano (dirección relativa con intensidad)
        nearest_food = self.find_nearest_food()
        if nearest_food:
            dx = nearest_food['x'] - self.x
            dy = nearest_food['y'] - self.y
            dist = math.sqrt(dx*dx + dy*dy)
            
            # Normalizar dirección con intensidad (más fuerte si está cerca)
            if dist > 0:
                intensity = max(0.3, 1.0 - (dist / 500))  # Mínimo 0.3, máximo 1.0
                inputs.append((dx / dist) * intensity)  # Dirección X con intensidad
                inputs.append((dy / dist) * intensity)  # Dirección Y con intensidad
            else:
                inputs.append(1.0)  # Muy cerca, señal fuerte
                inputs.append(1.0)
        else:
            # Sin alimento visible, dar señal de exploración
            inputs.append(random.uniform(-0.2, 0.2))
            inputs.append(random.uniform(-0.2, 0.2))
        
        # 4-5. Criatura más cercana (para evitar colisiones)
        nearest_creature = self.find_nearest_creature()
        if nearest_creature:
            dx = nearest_creature.x - self.x
            dy = nearest_creature.y - self.y
            dist = math.sqrt(dx*dx + dy*dy)
            if dist > 0 and dist < 100:  # Solo si está muy cerca
                # Señal de evitación (invertida)
                inputs.append(-(dx / dist) * 0.5)
                inputs.append(-(dy / dist) * 0.5)
            else:
                inputs.append(0)
                inputs.append(0)
        else:
            inputs.append(0)
            inputs.append(0)
        
        # 6. Complejidad normalizada
        inputs.append(min(1.0, self.complexity / 1000))
        
        # 7. Urgencia de alimento (1.0 = muy hambriento) - AMPLIFICADA
        urgency = (1.0 - energy_ratio) * 1.5  # Amplificar urgencia
        inputs.append(min(1.0, urgency))
        
        # 8. Bias (siempre activo)
        inputs.append(1.0)
        
        return inputs
    
    def apply_movement(self, move_x: float, move_y: float):
        """Aplicar movimiento con anti-bordes y normalización"""
        # Añadir comportamiento anti-bordes FUERTE
        margin = 80
        if self.x < margin:
            move_x += 1.5  # Empuje muy fuerte
        elif self.x > self.world.width - margin:
            move_x -= 1.5
        
        if self.y < margin:
            move_y += 1.5
        elif self.y > self.world.height - margin:
            move_y -= 1.5
        
        # Normalizar si el movimiento es muy grande
        magnitude = math.sqrt(move_x*move_x + move_y*move_y)
        if magnitude > 2.0:
            move_x = (move_x / magnitude) * 2.0
            move_y = (move_y / magnitude) * 2.0
        
        # Aplicar movimiento con velocidad consistente
        speed = 100 * self.get_speed_multiplier()  # Velocidad alta y consistente
        self.vx = move_x * speed
        self.vy = move_y * speed
    
    def interpret_outputs(self, outputs: List[float]):
        """Interpretar outputs de red neuronal como acciones (LEGACY - no usado)"""
        # Esta función ya no se usa, el movimiento se maneja en think()
        pass
    
    def move(self, dt: float):
        """Mover criatura"""
        # Guardar posición anterior para calcular distancia
        old_x, old_y = self.x, self.y
        
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # Calcular distancia recorrida (para fitness)
        dx = self.x - old_x
        dy = self.y - old_y
        self.distance_traveled += math.sqrt(dx*dx + dy*dy)
        
        # Actualizar dirección
        if abs(self.vx) > 0.1 or abs(self.vy) > 0.1:
            self.direction = math.atan2(self.vy, self.vx)
        
        # Recompensa por acercarse a comida
        nearest_food = self.find_nearest_food()
        if nearest_food:
            old_dist = math.sqrt((old_x - nearest_food['x'])**2 + (old_y - nearest_food['y'])**2)
            new_dist = math.sqrt((self.x - nearest_food['x'])**2 + (self.y - nearest_food['y'])**2)
            if new_dist < old_dist:
                self.fitness += 0.1  # Pequeña recompensa por acercarse
        
        # Mantener dentro de límites con rebote suave
        if config.TOPOLOGY == 'bounded':
            margin = self.size * 2
            
            # Rebote en bordes con amortiguación
            if self.x < margin:
                self.x = margin
                self.vx = abs(self.vx) * 0.5  # Rebote amortiguado
                self.fitness -= 1  # Pequeño castigo por tocar borde
            elif self.x > self.world.width - margin:
                self.x = self.world.width - margin
                self.vx = -abs(self.vx) * 0.5
                self.fitness -= 1
            
            if self.y < margin:
                self.y = margin
                self.vy = abs(self.vy) * 0.5
                self.fitness -= 1
            elif self.y > self.world.height - margin:
                self.y = self.world.height - margin
                self.vy = -abs(self.vy) * 0.5
                self.fitness -= 1
        elif config.TOPOLOGY == 'toroidal':
            self.x = self.x % self.world.width
            self.y = self.y % self.world.height
    
    def seek_food(self):
        """Buscar y consumir alimento cercano"""
        nearby_data = self.world.get_data_near(self.x, self.y, self.size)
        for data in nearby_data:
            self.world.consume_data(self, data)
            # Recompensa por comer
            self.fitness += 10
            self.food_eaten += 1
            break  # Solo uno por frame
    
    def find_nearest_food(self) -> Optional[dict]:
        """Encontrar alimento más cercano (OPTIMIZADO)"""
        if not self.world.data_items:
            return None
        
        try:
            nearest = None
            min_dist = float('inf')
            max_search_dist = 500 * 500  # Límite de búsqueda (cuadrado para evitar sqrt)
            
            # Buscar solo en un subconjunto si hay muchos datos
            data_to_check = self.world.data_items
            if len(data_to_check) > 40:  # Reducido de 50 a 40
                # Muestreo aleatorio para reducir carga
                sample_size = min(40, len(data_to_check))
                data_to_check = random.sample(data_to_check, sample_size)
            
            for data in data_to_check:
                dx = data['x'] - self.x
                dy = data['y'] - self.y
                dist = dx*dx + dy*dy
                
                # Solo considerar si está dentro del rango de búsqueda
                if dist < max_search_dist and dist < min_dist:
                    min_dist = dist
                    nearest = data
            
            return nearest
        except Exception:
            # Si hay error, devolver None (usar exploración aleatoria)
            return None
    
    def find_nearest_creature(self) -> Optional['Creature']:
        """Encontrar criatura más cercana (OPTIMIZADO)"""
        try:
            nearest = None
            min_dist = float('inf')
            max_search_dist = 150 * 150  # Límite de búsqueda reducido
            
            # Buscar solo en un subconjunto si hay muchas criaturas
            creatures_to_check = self.world.creatures
            if len(creatures_to_check) > 25:  # Reducido de 30 a 25
                # Muestreo aleatorio para reducir carga
                sample_size = min(25, len(creatures_to_check))
                creatures_to_check = random.sample(creatures_to_check, sample_size)
            
            for creature in creatures_to_check:
                if creature is self:
                    continue
                dx = creature.x - self.x
                dy = creature.y - self.y
                dist = dx*dx + dy*dy
                
                # Solo considerar si está cerca
                if dist < max_search_dist and dist < min_dist:
                    min_dist = dist
                    nearest = creature
            
            return nearest
        except Exception:
            # Si hay error, devolver None
            return None
    
    def can_reproduce(self) -> bool:
        """Verificar si puede reproducirse (MEJORADO v2.8)"""
        # Criaturas avanzadas se reproducen más fácilmente
        phase = self.get_phase()
        age_thresholds = {
            'primitive': 100,
            'intermediate': 80,   # Más rápido
            'advanced': 60,       # Mucho más rápido
            'complex': 50         # Muy rápido
        }
        
        min_age = age_thresholds[phase]
        
        return (self.energy >= config.REPRODUCTION_ENERGY_THRESHOLD and
                self.age > min_age and
                self.world.population < config.MAX_POPULATION)
    
    def reproduce(self):
        """Reproducirse (asexual)"""
        self.energy -= config.REPRODUCTION_ENERGY_COST
        
        # Recompensa por reproducirse exitosamente
        self.fitness += 20
        
        # Crear descendiente cerca
        offset_x = random.uniform(-20, 20)
        offset_y = random.uniform(-20, 20)
        child = Creature(self.x + offset_x, self.y + offset_y, self.world, parent=self)
        
        # El hijo hereda parte del fitness del padre
        child.fitness = self.fitness * 0.1
        
        self.world.add_creature(child)
    
    def can_vocalize(self) -> bool:
        """Verificar si puede vocalizar"""
        return (self.complexity >= config.COMPLEXITY_THRESHOLD_VOCAL and
                self.vocal_development >= config.AUDIO_DATA_REQUIREMENT)
    
    def is_dead(self) -> bool:
        """Verificar si está muerta"""
        if self.energy <= 0:
            # Castigo severo por morir de hambre
            self.fitness -= 50
            return True
        return False
    
    def get_phase(self) -> str:
        """Obtener fase evolutiva"""
        if self.complexity < 200:
            return 'primitive'
        elif self.complexity < 500:
            return 'intermediate'
        elif self.complexity < 1000:
            return 'advanced'
        else:
            return 'complex'
    
    def get_speed_multiplier(self) -> float:
        """Multiplicador de velocidad según fase (MEJORADO)"""
        phase = self.get_phase()
        multipliers = {
            'primitive': 0.6,      # Aumentado de 0.5
            'intermediate': 0.85,  # Aumentado de 0.75
            'advanced': 1.1,       # Aumentado de 1.0
            'complex': 1.3         # Aumentado de 1.2
        }
        return multipliers[phase]
    
    def get_efficiency_bonus(self) -> float:
        """Bonus de eficiencia por evolución (MEJORADO v2.8)"""
        # Criaturas más evolucionadas son MUCHO más eficientes
        # Reducen significativamente el costo energético
        phase = self.get_phase()
        efficiency = {
            'primitive': 1.0,      # Sin bonus
            'intermediate': 0.85,  # 15% más eficiente (aumentado)
            'advanced': 0.7,       # 30% más eficiente (aumentado)
            'complex': 0.55        # 45% más eficiente (aumentado)
        }
        return efficiency[phase]
    
    def calculate_color(self) -> Tuple[int, int, int]:
        """Calcular color según fase"""
        phase = self.get_phase()
        return config.PHASE_COLORS[phase]
    
    def update_appearance(self):
        """Actualizar apariencia visual"""
        # Tamaño según complejidad
        size_range = config.CREATURE_SIZE_MAX - config.CREATURE_SIZE_BASE
        size_factor = min(1.0, self.complexity / 1000)
        self.size = config.CREATURE_SIZE_BASE + size_range * size_factor
        
        # Color según fase
        self.color = self.calculate_color()
    
    def sees_food_nearby(self) -> bool:
        """Detectar si hay comida cerca"""
        return len(self.world.get_data_near(self.x, self.y, 100)) > 0
    
    def sees_creature_nearby(self) -> bool:
        """Detectar si hay otra criatura cerca"""
        return len(self.world.get_creatures_near(self.x, self.y, 50)) > 1
    
    def detects_threat(self) -> bool:
        """Detectar amenaza (placeholder)"""
        return False
    
    def to_dict(self) -> dict:
        """Serializar a diccionario"""
        return {
            'id': self.id,
            'x': self.x,
            'y': self.y,
            'energy': self.energy,
            'complexity': self.complexity,
            'vocal_development': self.vocal_development,
            'age': self.age,
            'generation': self.generation,
            'genome': self.genome.to_dict()
        }
    
    @classmethod
    def from_dict(cls, data: dict, world):
        """Deserializar desde diccionario"""
        creature = cls(data['x'], data['y'], world)
        creature.id = data['id']
        creature.energy = data['energy']
        creature.complexity = data['complexity']
        creature.vocal_development = data['vocal_development']
        creature.age = data['age']
        creature.generation = data['generation']
        creature.genome = Genome.from_dict(data['genome'])
        return creature

    # ==================== NUEVOS SISTEMAS v2.8 ====================
    
    def try_predation(self, dt: float):
        """Intentar depredar a criaturas más débiles"""
        if not config.PREDATION_ENABLED:
            return
        
        if self.complexity < config.PREDATION_COMPLEXITY_THRESHOLD:
            return  # Solo criaturas desarrolladas pueden depredar
        
        # Buscar presas cercanas
        nearby = self.world.get_creatures_near(self.x, self.y, config.PREDATION_RANGE)
        
        for prey in nearby:
            if prey == self:
                continue
            
            # Verificar si somos significativamente más fuertes
            if self.fitness > prey.fitness * config.PREDATION_STRENGTH_RATIO:
                # Intentar depredar (aumentada probabilidad)
                if random.random() < 0.3:  # 30% de probabilidad
                    self.predate(prey)
                    break
    
    def predate(self, prey):
        """Depredar a otra criatura"""
        # Ganar energía de la presa
        energy_gained = min(config.PREDATION_ENERGY_GAIN, prey.energy * 0.5)
        self.energy = min(self.max_energy, self.energy + energy_gained)
        
        # Matar a la presa
        prey.energy = 0
        
        # Aumentar fitness del depredador
        self.fitness += 10
        
        # Actualizar estadísticas del mundo
        self.world.predation_kills += 1
        
        # Marcar como depredador activo
        self.is_predator = True
        
        print(f"🦁 Criatura {self.id} (comp: {self.complexity:.0f}) depredó a Criatura {prey.id} (comp: {prey.complexity:.0f})")
    
    def try_collaboration(self, dt: float):
        """Intentar colaborar con criaturas similares"""
        if not config.COLLABORATION_ENABLED:
            return
        
        if self.complexity < config.COLLABORATION_COMPLEXITY_THRESHOLD:
            return  # Solo criaturas desarrolladas pueden colaborar
        
        # Buscar aliados cercanos
        nearby = self.world.get_creatures_near(self.x, self.y, config.COLLABORATION_RANGE)
        
        for ally in nearby:
            if ally == self:
                continue
            
            # Verificar similitud genética
            similarity = self.calculate_genetic_similarity(ally)
            
            if similarity >= config.COLLABORATION_SIMILARITY_THRESHOLD:
                # Colaborar
                if random.random() < 0.05 * dt:  # 5% por frame
                    self.collaborate(ally)
                    break
    
    def collaborate(self, ally):
        """Colaborar con otra criatura"""
        # Ambos ganan energía
        bonus = config.COLLABORATION_ENERGY_BONUS
        self.energy = min(self.max_energy, self.energy + bonus)
        ally.energy = min(ally.max_energy, ally.energy + bonus)
        
        # Aumentar fitness de ambos
        self.fitness += 5
        ally.fitness += 5
        
        if random.random() < 0.1:  # 10% de mostrar mensaje
            print(f"🤝 Criatura {self.id} colaboró con Criatura {ally.id}")
    
    def try_communication(self, dt: float):
        """Intentar comunicarse con otras criaturas"""
        if not config.COMMUNICATION_ENABLED:
            return
        
        if self.complexity < config.COMMUNICATION_COMPLEXITY_THRESHOLD:
            return
        
        # Buscar criaturas cercanas
        nearby = self.world.get_creatures_near(self.x, self.y, config.COMMUNICATION_RANGE)
        
        if len(nearby) > 1 and random.random() < 0.02 * dt:  # 2% por frame
            self.communicate(nearby)
    
    def communicate(self, nearby_creatures):
        """Comunicarse con criaturas cercanas"""
        # Costo de energía
        self.energy -= config.COMMUNICATION_ENERGY_COST
        
        # Compartir información (aumentar complejidad de todos)
        complexity_share = self.complexity * 0.01
        
        for creature in nearby_creatures:
            if creature != self and creature.complexity >= config.COMMUNICATION_COMPLEXITY_THRESHOLD:
                creature.complexity += complexity_share * 0.5
                creature.fitness += 1
        
        self.fitness += 2
        
        if random.random() < 0.05:  # 5% de mostrar mensaje
            print(f"💬 Criatura {self.id} se comunicó con {len(nearby_creatures)-1} criaturas")
    
    def calculate_genetic_similarity(self, other: 'Creature') -> float:
        """Calcular similitud genética con otra criatura"""
        # Comparar genomas
        my_genome = set(self.genome.instructions)
        other_genome = set(other.genome.instructions)
        
        if not my_genome or not other_genome:
            return 0.0
        
        intersection = len(my_genome & other_genome)
        union = len(my_genome | other_genome)
        
        genome_similarity = intersection / union if union > 0 else 0
        
        # Considerar también complejidad similar
        complexity_diff = abs(self.complexity - other.complexity)
        complexity_similarity = 1.0 - min(1.0, complexity_diff / 500)
        
        # Promedio ponderado
        return genome_similarity * 0.7 + complexity_similarity * 0.3
    
    def get_species_id(self) -> int:
        """Obtener ID de especie basado en características genéticas"""
        # Usar hash del genoma + rango de complejidad
        genome_hash = hash(tuple(sorted(self.genome.instructions)))
        complexity_bracket = int(self.complexity / 100)  # Grupos de 100 complejidad
        
        return hash((genome_hash, complexity_bracket))
    
    def update_infection(self, dt: float):
        """Actualizar estado de infección"""
        if hasattr(self, 'infection') and self.infection:
            if not self.infection.update(self, dt):
                # La criatura murió por la enfermedad
                return False
            
            # Si la infección terminó, limpiar
            if not self.infection.is_active():
                self.infection = None
        
        return True

    # ==================== OPTIMIZACIÓN GPU v2.9 ====================
    
    def prepare_neural_inputs(self) -> List[float]:
        """Preparar inputs para procesamiento por lotes (sin ejecutar red)"""
        return self.get_sensor_inputs()
    
    def apply_neural_outputs(self, outputs: np.ndarray):
        """Aplicar outputs de la red neuronal procesada en GPU"""
        # Balance instinto/IA según complejidad
        instinct_strength = max(0.2, 0.8 - (self.complexity / 1000))
        
        # Instinto: buscar alimento más cercano
        nearest_food = self.find_nearest_food()
        instinct_x = 0
        instinct_y = 0
        
        if nearest_food:
            dx = nearest_food['x'] - self.x
            dy = nearest_food['y'] - self.y
            dist = math.sqrt(dx*dx + dy*dy)
            
            if dist > 0:
                urgency = 1.0 - (self.energy / self.max_energy)
                instinct_x = (dx / dist) * urgency
                instinct_y = (dy / dist) * urgency
        else:
            instinct_x = random.uniform(-0.5, 0.5)
            instinct_y = random.uniform(-0.5, 0.5)
        
        # Red neuronal (outputs ya procesados en GPU)
        neural_x = 0
        neural_y = 0
        
        if self.complexity > 50 and len(outputs) >= 4:
            neural_y = outputs[0] - outputs[1]
            neural_x = outputs[3] - outputs[2]
        
        # Combinar instinto + red neuronal
        move_x = instinct_x * instinct_strength + neural_x * (1 - instinct_strength)
        move_y = instinct_y * instinct_strength + neural_y * (1 - instinct_strength)
        
        # Aplicar movimiento
        self.apply_movement(move_x, move_y)
    
    def update_non_neural(self, dt: float):
        """Actualizar todo excepto la red neuronal (para procesamiento por lotes)"""
        self.age += dt
        
        # Consumir energía
        base_cost = config.ENERGY_COST_PER_CYCLE * dt
        complexity_cost = (self.complexity / 100) * dt
        efficiency = self.get_efficiency_bonus()
        energy_cost = (base_cost + complexity_cost) * efficiency
        self.energy -= energy_cost
        
        # Mover (ya aplicado en apply_neural_outputs)
        self.move(dt)
        
        # Buscar alimento
        self.seek_food()
        
        # Reproducción (cada 10 frames)
        if self.age % 10 < dt:
            if self.can_reproduce():
                self.reproduce()
        
        # Vocalización (reducida)
        if self.can_vocalize() and random.random() < 0.005:
            self.vocal_system.vocalize()
        
        # Apariencia (cada 5 frames)
        if self.age % 5 < dt:
            self.update_appearance()
        
        # Infección
        if not self.update_infection(dt):
            return
        
        # Comportamientos sociales (reducidos)
        if self.age % 20 < dt:
            self.try_predation(dt)
        
        if self.age % 15 < dt:
            self.try_collaboration(dt)
        
        if self.age % 10 < dt:
            self.try_communication(dt)
