"""
Configuración global de DigiLife
"""

# Mundo
WORLD_WIDTH = 1400  # Aumentado para mejor visualización
WORLD_HEIGHT = 900  # Aumentado para mejor visualización
TOPOLOGY = 'bounded'  # 'bounded' o 'toroidal'
BACKGROUND_COLOR = (20, 20, 30)

# Seres
INITIAL_POPULATION = 25  # Optimizado para 60 FPS
MAX_POPULATION = 120  # Reducido para 60 FPS estables
INITIAL_ENERGY = 250  # Aumentado significativamente para mejor inicio
MAX_ENERGY = 350  # Aumentado para permitir más reservas
ENERGY_COST_PER_CYCLE = 0.2  # Reducido drásticamente para mayor supervivencia

# Reproducción
REPRODUCTION_ENERGY_THRESHOLD = 180  # Aumentado para evitar reproducción prematura
REPRODUCTION_ENERGY_COST = 35  # Reducido para facilitar reproducción
MUTATION_RATE_BASE = 0.05

# Tiempo (para conversión de ciclos a días)
CYCLES_PER_DAY = 100  # 100 ciclos = 1 día en el simulador

# Evolución
COMPLEXITY_THRESHOLD_VOCAL = 500
AUDIO_DATA_REQUIREMENT = 100

# Datos (Alimento)
DATA_SPAWN_RATE = 5  # por segundo (balanceado para presión evolutiva)
DATA_TYPES_DISTRIBUTION = {
    'numeric': 0.25,      # Común (energía básica)
    'text': 0.20,         # Balanceado (cognición)
    'audio': 0.20,        # Balanceado (vocal)
    'structured': 0.25,   # Aumentado (el mejor, pero más raro)
    'binary': 0.10        # Aumentado (relleno energético)
}

# Valores nutricionales (BALANCEADOS v2.8 - Favorece evolución)
DATA_NUTRITION = {
    'numeric': {'energy': 12, 'cognition': 3, 'vocal': 0},      # Mejorado
    'text': {'energy': 10, 'cognition': 8, 'vocal': 2},         # Más cognición
    'audio': {'energy': 10, 'cognition': 3, 'vocal': 8},        # Más vocal
    'structured': {'energy': 18, 'cognition': 15, 'vocal': 3},  # Significativamente mejor
    'binary': {'energy': 8, 'cognition': 2, 'vocal': 0}         # Mejorado
}

# Colores de datos
DATA_COLORS = {
    'numeric': (100, 150, 255),    # Azul
    'text': (100, 255, 100),        # Verde
    'audio': (255, 255, 100),       # Amarillo
    'structured': (200, 100, 255),  # Morado
    'binary': (200, 200, 200)       # Blanco
}

# Red Neuronal
NEURAL_INPUT_SIZE = 8
NEURAL_HIDDEN_SIZE = 16
NEURAL_OUTPUT_SIZE = 4
NEURAL_LEARNING_RATE = 0.1

# OpenCL y Optimización GPU
USE_GPU = True
GPU_THRESHOLD_CREATURES = 20  # Activar GPU con más de 20 criaturas
GPU_BATCH_SIZE = 64  # Procesar 64 criaturas por lote (aumentado)
GPU_PRIORITY_COMPLEX = True  # Priorizar GPU para criaturas complejas
COMPLEX_THRESHOLD = 1000  # Umbral de complejidad alta
OPENCL_FALLBACK_TO_CPU = True

# Vocalización
VOCABULARY_MAX_SIZE = 20
LEARNING_RATE = 0.1
ASSOCIATION_THRESHOLD = 5  # exposiciones necesarias para aprender palabra

# Palabras básicas y sus contextos
# Vocabulario básico (todas las criaturas vocales)
VOCABULARY_CONTEXTS = {
    'hambre': lambda c: c.energy < c.max_energy * 0.4,
    'datos': lambda c: c.sees_food_nearby() and c.energy < c.max_energy * 0.6,
    'ayuda': lambda c: c.energy < c.max_energy * 0.2,
    'hola': lambda c: c.sees_creature_nearby() and c.energy > c.max_energy * 0.5,
    'peligro': lambda c: c.detects_threat(),
    'bien': lambda c: c.energy > c.max_energy * 0.75,
    'malo': lambda c: c.energy < c.max_energy * 0.25
}

# Vocabulario avanzado (solo criaturas inteligentes 1500+)
ADVANCED_VOCABULARY_CONTEXTS = {
    'cohesion': lambda c: len(c.world.get_creatures_near(c.x, c.y, 100)) >= 3,  # Llamar a agruparse
    'reproducir': lambda c: c.can_reproduce(),  # Momento de reproducirse
    'defender': lambda c: c.detects_threat() and c.fitness > 100,  # Defender territorio
    'peligro_aqui': lambda c: c.detects_threat() and c.energy < c.max_energy * 0.5,  # Peligro específico
    'seguir': lambda c: hasattr(c, 'intelligence') and c.intelligence and c.energy > c.max_energy * 0.6,  # Seguir al líder
    'explorar': lambda c: len(c.world.get_data_near(c.x, c.y, 150)) == 0,  # No hay comida cerca
    'descansar': lambda c: c.energy > c.max_energy * 0.8 and c.age > 100,  # Conservar energía
    'atacar': lambda c: hasattr(c, 'is_predator') and c.is_predator and c.energy > c.max_energy * 0.4,  # Coordinar ataque
    'huir': lambda c: c.detects_threat() and c.fitness < 50,  # Huir de peligro
    'compartir': lambda c: c.sees_food_nearby() and c.energy > c.max_energy * 0.7  # Compartir recursos
}

# Visualización
CREATURE_SIZE_BASE = 10
CREATURE_SIZE_MAX = 40
SHOW_NEURAL_CONNECTIONS = False
SHOW_GENOME_VISUALIZATION = True
SHOW_ENERGY_BAR = True
SHOW_NAMES = True

# Colores de fases evolutivas
PHASE_COLORS = {
    'primitive': (255, 100, 100),    # Rojo
    'intermediate': (255, 165, 0),   # Naranja
    'advanced': (100, 255, 100),     # Verde
    'complex': (100, 150, 255)       # Azul
}

# Performance
TARGET_FPS = 60
PHYSICS_SUBSTEPS = 1

# UI
UI_PANEL_WIDTH = 350  # Aumentado para más información
UI_FONT_SIZE = 14
UI_BACKGROUND_COLOR = (40, 40, 50)
UI_TEXT_COLOR = (220, 220, 220)

# Debug
DEBUG = {
    'LOG_BIRTHS': False,
    'LOG_DEATHS': False,
    'LOG_VOCALIZATIONS': True,
    'LOG_MUTATIONS': False,
    'LOG_INTELLIGENCE': True,  # Nuevo: logs de descubrimientos y aprendizaje
    'SHOW_FPS': True,
    'SHOW_COLLISION_BOXES': False,
    'SHOW_NEURAL_ACTIVITY': False
}

# Audio (Beeps del sistema)
AUDIO_ENABLED = True
BEEP_FREQUENCY_MIN = 400   # Hz mínimo
BEEP_FREQUENCY_MAX = 1200  # Hz máximo
BEEP_DURATION_MIN = 50     # ms mínimo
BEEP_DURATION_MAX = 300    # ms máximo

# Interacciones sociales
PREDATION_ENABLED = True
PREDATION_COMPLEXITY_THRESHOLD = 200  # Complejidad mínima para depredar
PREDATION_STRENGTH_RATIO = 1.5  # Depredador debe ser 1.5x más fuerte
PREDATION_ENERGY_GAIN = 30  # Energía ganada al depredar
PREDATION_RANGE = 30  # Rango de detección de presas

COLLABORATION_ENABLED = True
COLLABORATION_COMPLEXITY_THRESHOLD = 150  # Complejidad mínima para colaborar
COLLABORATION_SIMILARITY_THRESHOLD = 0.7  # Similitud genética requerida
COLLABORATION_ENERGY_BONUS = 5  # Bonus de energía por colaboración
COLLABORATION_RANGE = 50  # Rango de detección de aliados

COMMUNICATION_ENABLED = True
COMMUNICATION_COMPLEXITY_THRESHOLD = 100  # Complejidad mínima para comunicarse
COMMUNICATION_RANGE = 80  # Rango de comunicación
COMMUNICATION_ENERGY_COST = 0.5  # Costo de comunicarse

# Enfermedades
DISEASES_ENABLED = True
DISEASE_MIN_POPULATION = 30  # Población mínima para brotes
DISEASE_OUTBREAK_INTERVAL_MIN = 500  # Ciclos mínimos entre brotes
DISEASE_OUTBREAK_INTERVAL_MAX = 1500  # Ciclos máximos entre brotes

# Especies
SPECIES_SIMILARITY_THRESHOLD = 0.8  # Similitud genética para misma especie
SPECIES_COMPLEXITY_FACTOR = 0.2  # Factor de complejidad en clasificación
