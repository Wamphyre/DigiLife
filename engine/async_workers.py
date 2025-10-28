"""
Sistema de workers asíncronos para operaciones no críticas
Mejora el rendimiento distribuyendo carga en múltiples threads
"""

import threading
import queue
from typing import Callable, Any, List
from concurrent.futures import ThreadPoolExecutor, as_completed
import config


class AsyncWorkerPool:
    """Pool de workers para procesamiento asíncrono"""
    
    def __init__(self, num_workers: int = 4):
        self.num_workers = num_workers
        self.executor = ThreadPoolExecutor(max_workers=num_workers)
        self.task_queue = queue.Queue()
        self.running = True
        
        print(f"✅ Pool de workers inicializado con {num_workers} threads")
    
    def submit_task(self, func: Callable, *args, **kwargs):
        """Enviar tarea al pool"""
        return self.executor.submit(func, *args, **kwargs)
    
    def map_parallel(self, func: Callable, items: List[Any]) -> List[Any]:
        """Mapear función sobre lista en paralelo"""
        futures = [self.executor.submit(func, item) for item in items]
        results = []
        for future in as_completed(futures):
            try:
                results.append(future.result())
            except Exception as e:
                print(f"⚠️  Error en worker: {e}")
                results.append(None)
        return results
    
    def shutdown(self):
        """Cerrar pool de workers"""
        self.running = False
        self.executor.shutdown(wait=True)


# Instancia global
_worker_pool = None

def get_worker_pool() -> AsyncWorkerPool:
    """Obtener instancia global del pool de workers"""
    global _worker_pool
    if _worker_pool is None:
        # Usar número de CPUs disponibles
        import os
        num_workers = max(2, os.cpu_count() // 2)  # Usar mitad de CPUs
        _worker_pool = AsyncWorkerPool(num_workers)
    return _worker_pool


def shutdown_workers():
    """Cerrar workers al salir"""
    global _worker_pool
    if _worker_pool is not None:
        _worker_pool.shutdown()
        _worker_pool = None


# Funciones helper para operaciones comunes

def parallel_distance_check(creatures: List, x: float, y: float, radius: float) -> List:
    """Verificar distancias en paralelo"""
    def check_distance(creature):
        dx = creature.x - x
        dy = creature.y - y
        dist = (dx*dx + dy*dy) ** 0.5
        return creature if dist < radius else None
    
    pool = get_worker_pool()
    results = pool.map_parallel(check_distance, creatures)
    return [r for r in results if r is not None]


def parallel_update_infections(creatures: List, dt: float):
    """Actualizar infecciones en paralelo"""
    def update_infection(creature):
        if hasattr(creature, 'infection') and creature.infection:
            return creature.update_infection(dt)
        return True
    
    pool = get_worker_pool()
    return pool.map_parallel(update_infection, creatures)


def parallel_calculate_fitness(creatures: List):
    """Calcular fitness en paralelo"""
    def calc_fitness(creature):
        # Fitness basado en múltiples factores
        age_factor = min(1.0, creature.age / 500)
        energy_factor = creature.energy / creature.max_energy
        complexity_factor = min(1.0, creature.complexity / 500)
        
        fitness = (
            age_factor * 30 +
            energy_factor * 20 +
            complexity_factor * 30 +
            creature.food_eaten * 2 +
            creature.generation * 5
        )
        
        creature.fitness = fitness
        return fitness
    
    pool = get_worker_pool()
    return pool.map_parallel(calc_fitness, creatures)
