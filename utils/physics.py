"""
Motor de física básico
"""

import math


class Physics:
    """Física simple para el mundo"""
    
    @staticmethod
    def distance(x1: float, y1: float, x2: float, y2: float) -> float:
        """Calcular distancia euclidiana"""
        dx = x2 - x1
        dy = y2 - y1
        return math.sqrt(dx * dx + dy * dy)
    
    @staticmethod
    def angle_between(x1: float, y1: float, x2: float, y2: float) -> float:
        """Calcular ángulo entre dos puntos"""
        return math.atan2(y2 - y1, x2 - x1)
    
    @staticmethod
    def normalize_vector(x: float, y: float) -> tuple:
        """Normalizar vector"""
        length = math.sqrt(x * x + y * y)
        if length == 0:
            return 0, 0
        return x / length, y / length
    
    @staticmethod
    def check_collision_circle(x1: float, y1: float, r1: float,
                               x2: float, y2: float, r2: float) -> bool:
        """Verificar colisión entre dos círculos"""
        dist = Physics.distance(x1, y1, x2, y2)
        return dist < (r1 + r2)
