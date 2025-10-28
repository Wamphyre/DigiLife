"""
Generador de datos/alimento
"""

import random
import config


class DataGenerator:
    """Genera datos que sirven de alimento para las criaturas"""
    
    def __init__(self, world):
        self.world = world
        self.distribution = config.DATA_TYPES_DISTRIBUTION
    
    def random_type(self) -> str:
        """Generar tipo de dato aleatorio según distribución"""
        rand = random.random()
        cumulative = 0
        
        for data_type, probability in self.distribution.items():
            cumulative += probability
            if rand <= cumulative:
                return data_type
        
        return 'numeric'  # Fallback
    
    def generate_cluster(self, x: float, y: float, count: int, radius: float):
        """Generar cluster de datos en una zona"""
        for _ in range(count):
            angle = random.uniform(0, 2 * 3.14159)
            dist = random.uniform(0, radius)
            data_x = x + dist * random.cos(angle)
            data_y = y + dist * random.sin(angle)
            
            data_type = self.random_type()
            data_item = {
                'type': data_type,
                'x': data_x,
                'y': data_y,
                'size': 5,
                'color': config.DATA_COLORS[data_type]
            }
            self.world.data_items.append(data_item)
