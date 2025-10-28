"""
Sistema de conocimiento e insights - Criaturas inteligentes aprenden del entorno
"""

import random
from typing import List, Dict, Optional, Tuple
import config


class KnowledgeBase:
    """Base de conocimiento compartida del mundo"""
    
    def __init__(self):
        # Conocimiento básico disponible para descubrir
        self.survival_knowledge = [
            'conservar_energia_baja',
            'buscar_alimento_activo',
            'evitar_depredadores',
            'reproducir_energia_alta',
            'explorar_bordes',
            'permanecer_centro',
            'seguir_grupo',
            'huir_amenaza'
        ]
        
        self.social_knowledge = [
            'colaborar_similares',
            'comunicar_peligro',
            'compartir_alimento',
            'formar_grupos',
            'defender_territorio',
            'ayudar_debiles'
        ]
        
        self.strategic_knowledge = [
            'patrullar_zona',
            'emboscar_presas',
            'cazar_coordinado',
            'migrar_recursos',
            'adaptarse_estacion',
            'optimizar_movimiento'
        ]
        
        # Patrones descubiertos por criaturas
        self.discovered_patterns = {}
        
        # Estadísticas del mundo para análisis
        self.world_stats = {
            'food_hotspots': [],  # Zonas con más comida
            'danger_zones': [],   # Zonas peligrosas
            'safe_zones': [],     # Zonas seguras
            'successful_strategies': []  # Estrategias exitosas
        }
    
    def update_world_stats(self, world):
        """Actualizar estadísticas del mundo para análisis"""
        # Analizar zonas de comida (cada 100 ciclos)
        if world.cycle % 100 == 0:
            self._analyze_food_distribution(world)
            self._analyze_danger_zones(world)
            self._analyze_successful_creatures(world)
    
    def _analyze_food_distribution(self, world):
        """Analizar dónde aparece más comida"""
        if not world.data_items:
            return
        
        # Dividir mundo en cuadrantes
        quadrants = {
            'center': 0,
            'north': 0,
            'south': 0,
            'east': 0,
            'west': 0
        }
        
        center_x = world.width / 2
        center_y = world.height / 2
        
        for data in world.data_items:
            dx = abs(data['x'] - center_x)
            dy = abs(data['y'] - center_y)
            
            if dx < world.width * 0.2 and dy < world.height * 0.2:
                quadrants['center'] += 1
            elif data['y'] < center_y:
                quadrants['north'] += 1
            else:
                quadrants['south'] += 1
            
            if data['x'] < center_x:
                quadrants['west'] += 1
            else:
                quadrants['east'] += 1
        
        # Guardar zona con más comida
        self.world_stats['food_hotspots'] = sorted(
            quadrants.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:2]
    
    def _analyze_danger_zones(self, world):
        """Analizar zonas peligrosas (con depredadores)"""
        if not config.PREDATION_ENABLED:
            return
        
        danger_zones = []
        for creature in world.creatures:
            if hasattr(creature, 'is_predator') and creature.is_predator:
                danger_zones.append((creature.x, creature.y))
        
        self.world_stats['danger_zones'] = danger_zones
    
    def _analyze_successful_creatures(self, world):
        """Analizar estrategias de criaturas exitosas"""
        if not world.creatures:
            return
        
        # Top 10% de criaturas por fitness
        sorted_creatures = sorted(world.creatures, key=lambda c: c.fitness, reverse=True)
        top_creatures = sorted_creatures[:max(1, len(sorted_creatures) // 10)]
        
        strategies = []
        for creature in top_creatures:
            strategy = {
                'complexity': creature.complexity,
                'energy_ratio': creature.energy / creature.max_energy,
                'age': creature.age,
                'is_predator': getattr(creature, 'is_predator', False),
                'genome_size': len(creature.genome)
            }
            strategies.append(strategy)
        
        self.world_stats['successful_strategies'] = strategies


class CreatureIntelligence:
    """Sistema de inteligencia avanzada para criaturas"""
    
    def __init__(self, creature, knowledge_base: KnowledgeBase):
        self.creature = creature
        self.knowledge_base = knowledge_base
        
        # Conocimiento adquirido por esta criatura
        self.learned_knowledge = set()
        
        # Insights descubiertos
        self.insights = []
        
        # Estrategias aprendidas
        self.strategies = []
        
        # Memoria de observaciones
        self.observations = []
        self.max_observations = 50
        
        # Nivel de sabiduría (aumenta con descubrimientos)
        self.wisdom = 0
    
    def can_learn(self) -> bool:
        """Verificar si la criatura puede aprender (muy inteligente)"""
        return self.creature.complexity >= 1500
    
    def analyze_environment(self, dt: float):
        """Analizar entorno y descubrir patrones (solo criaturas muy inteligentes)"""
        if not self.can_learn():
            return
        
        # Limitar frecuencia de análisis (costoso)
        if random.random() > 0.01:  # 1% por frame
            return
        
        # Intentar descubrir nuevo conocimiento
        self._try_discover_knowledge()
        
        # Analizar situación actual
        self._analyze_current_situation()
        
        # Aprender de criaturas exitosas
        if random.random() < 0.005:  # 0.5% por frame
            self._learn_from_successful()
    
    def _try_discover_knowledge(self):
        """Intentar descubrir nuevo conocimiento"""
        # Elegir categoría aleatoria
        categories = [
            self.knowledge_base.survival_knowledge,
            self.knowledge_base.social_knowledge,
            self.knowledge_base.strategic_knowledge
        ]
        
        category = random.choice(categories)
        
        # Intentar aprender algo nuevo
        available = [k for k in category if k not in self.learned_knowledge]
        if available:
            new_knowledge = random.choice(available)
            self.learned_knowledge.add(new_knowledge)
            self.wisdom += 1
            
            # Registrar descubrimiento
            insight = f"Descubrió: {new_knowledge.replace('_', ' ')}"
            self.insights.append(insight)
            
            if config.DEBUG.get('LOG_INTELLIGENCE', False):
                print(f"🧠 Criatura {self.creature.id} {insight} (sabiduría: {self.wisdom})")
    
    def _analyze_current_situation(self):
        """Analizar situación actual y tomar decisiones inteligentes"""
        # Registrar observación
        observation = {
            'energy': self.creature.energy / self.creature.max_energy,
            'nearby_creatures': len(self.creature.world.get_creatures_near(
                self.creature.x, self.creature.y, 100
            )),
            'nearby_food': len(self.creature.world.get_data_near(
                self.creature.x, self.creature.y, 100
            )),
            'cycle': self.creature.world.cycle
        }
        
        self.observations.append(observation)
        if len(self.observations) > self.max_observations:
            self.observations.pop(0)
        
        # Analizar patrones en observaciones
        if len(self.observations) >= 10:
            self._detect_patterns()
    
    def _detect_patterns(self):
        """Detectar patrones en observaciones"""
        # Analizar tendencias de energía
        recent_energy = [obs['energy'] for obs in self.observations[-10:]]
        avg_energy = sum(recent_energy) / len(recent_energy)
        
        # Descubrir insight basado en datos
        if avg_energy < 0.3 and 'conservar_energia_baja' in self.learned_knowledge:
            if 'energia_critica_frecuente' not in [i for i in self.insights]:
                self.insights.append('energia_critica_frecuente')
                self.wisdom += 1
    
    def _learn_from_successful(self):
        """Aprender observando criaturas exitosas"""
        successful = self.knowledge_base.world_stats.get('successful_strategies', [])
        if not successful:
            return
        
        # Analizar estrategia exitosa
        strategy = random.choice(successful)
        
        # Si la estrategia es muy diferente a la nuestra, aprender
        if strategy['complexity'] > self.creature.complexity * 0.8:
            # Aprender algo de la estrategia
            if strategy['is_predator'] and 'emboscar_presas' not in self.learned_knowledge:
                if 'emboscar_presas' in self.knowledge_base.strategic_knowledge:
                    self.learned_knowledge.add('emboscar_presas')
                    self.wisdom += 1
                    
                    if config.DEBUG.get('LOG_INTELLIGENCE', False):
                        print(f"🎓 Criatura {self.creature.id} aprendió de criaturas exitosas")
    
    def share_knowledge(self, other_creature):
        """Compartir conocimiento con otra criatura inteligente"""
        if not hasattr(other_creature, 'intelligence'):
            return
        
        if not other_creature.intelligence.can_learn():
            return
        
        # Compartir conocimiento que el otro no tiene
        shared = 0
        for knowledge in self.learned_knowledge:
            if knowledge not in other_creature.intelligence.learned_knowledge:
                if random.random() < 0.3:  # 30% de compartir cada pieza
                    other_creature.intelligence.learned_knowledge.add(knowledge)
                    other_creature.intelligence.wisdom += 1
                    shared += 1
        
        if shared > 0 and config.DEBUG.get('LOG_INTELLIGENCE', False):
            print(f"📚 Criatura {self.creature.id} compartió {shared} conocimientos con Criatura {other_creature.id}")
    
    def get_knowledge_summary(self) -> Dict:
        """Obtener resumen del conocimiento de la criatura"""
        return {
            'wisdom': self.wisdom,
            'knowledge_count': len(self.learned_knowledge),
            'insights_count': len(self.insights),
            'recent_insights': self.insights[-3:] if self.insights else []
        }
