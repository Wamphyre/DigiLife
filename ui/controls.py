"""
Panel de controles (placeholder)
"""

import pygame
import config


class ControlPanel:
    """Panel de controles de la simulación"""
    
    def __init__(self, screen):
        self.screen = screen
        
        # Por ahora, los controles son por teclado
        # En el futuro se pueden añadir botones con pygame_gui
    
    def render(self):
        """Renderizar controles"""
        pass
    
    def handle_event(self, event):
        """Manejar eventos de UI"""
        pass
