"""
Inspector detallado de criaturas
"""

import pygame
import config


class CreatureInspector:
    """Inspector detallado para examinar criaturas"""
    
    def __init__(self, screen, creature):
        self.screen = screen
        self.creature = creature
        
        # Ventana modal
        self.width = 400
        self.height = 500
        self.x = (screen.get_width() - self.width) // 2
        self.y = (screen.get_height() - self.height) // 2
        
        self.font = pygame.font.Font(None, 18)
    
    def render(self):
        """Renderizar inspector"""
        # Fondo semi-transparente
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Ventana
        pygame.draw.rect(self.screen, (40, 40, 50),
                        (self.x, self.y, self.width, self.height))
        pygame.draw.rect(self.screen, (100, 100, 100),
                        (self.x, self.y, self.width, self.height), 2)
        
        # Contenido
        y_offset = self.y + 20
        
        # Título
        title = self.font.render(f"Criatura {self.creature.id}", True, (255, 255, 255))
        self.screen.blit(title, (self.x + 20, y_offset))
        y_offset += 40
        
        # Información detallada
        info = [
            f"Generación: {self.creature.generation}",
            f"Edad: {self.creature.age:.1f} ciclos",
            f"Energía: {self.creature.energy:.1f}/{self.creature.max_energy}",
            f"Complejidad: {self.creature.complexity:.0f}",
            f"Fase: {self.creature.get_phase().title()}",
            "",
            f"Genoma: {len(self.creature.genome)} instrucciones",
            f"Vocabulario: {self.creature.vocal_system.get_vocabulary_size()} palabras",
            "",
            "Palabras conocidas:",
        ]
        
        for line in info:
            text = self.font.render(line, True, (200, 200, 200))
            self.screen.blit(text, (self.x + 20, y_offset))
            y_offset += 25
        
        # Vocabulario
        for word, count in list(self.creature.vocal_system.vocabulary.items())[:5]:
            text = self.font.render(f"  - '{word}' ({count} veces)", True, (150, 200, 150))
            self.screen.blit(text, (self.x + 30, y_offset))
            y_offset += 20
        
        # Instrucción para cerrar
        y_offset = self.y + self.height - 40
        instruction = self.font.render("Presiona ESC para cerrar", True, (150, 150, 150))
        self.screen.blit(instruction, (self.x + 20, y_offset))
