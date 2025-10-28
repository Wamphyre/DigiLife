"""
Menú de ayuda con información sobre formas y consejos
"""

import pygame
import config


class HelpMenu:
    """Menú de ayuda interactivo"""
    
    def __init__(self, screen):
        self.screen = screen
        self.visible = False
        
        # Dimensiones - más grande para mostrar todo el contenido
        self.width = 800
        self.height = 750
        self.x = (screen.get_width() - self.width) // 2
        self.y = (screen.get_height() - self.height) // 2
        
        # Fuentes
        self.font_title = pygame.font.Font(None, 36)
        self.font_subtitle = pygame.font.Font(None, 24)
        self.font_text = pygame.font.Font(None, 18)
        self.font_small = pygame.font.Font(None, 16)
        
        # Colores
        self.bg_color = (25, 25, 35)
        self.text_color = (220, 220, 220)
        self.highlight_color = (100, 200, 255)
        self.section_color = (40, 40, 50)
        
        # Scroll
        self.scroll_offset = 0
        self.max_scroll = 0
        self.content_height = 0
        
        # Contenido
        self.content = self.create_content()
    
    def create_content(self):
        """Crear contenido del menú de ayuda"""
        return [
            {'type': 'title', 'text': 'Guia de DigiLife'},
            {'type': 'space', 'height': 20},
            
            {'type': 'subtitle', 'text': 'FORMAS EVOLUTIVAS'},
            {'type': 'space', 'height': 10},
            
            {'type': 'phase', 'color': (255, 100, 100), 
             'name': 'PRIMITIVA (0-200)', 'desc': 'Circulo - Movimiento aleatorio'},
            {'type': 'phase', 'color': (255, 165, 0), 
             'name': 'INTERMEDIA (200-500)', 'desc': 'Hexagono - Busca alimento'},
            {'type': 'phase', 'color': (100, 255, 100), 
             'name': 'AVANZADA (500-1000)', 'desc': 'Octogono - Vocalizaciones'},
            {'type': 'phase', 'color': (100, 150, 255), 
             'name': 'COMPLEJA (1000+)', 'desc': 'Estrella - Lenguaje completo'},
            
            {'type': 'space', 'height': 20},
            {'type': 'subtitle', 'text': 'TIPOS DE DATOS (Alimento)'},
            {'type': 'space', 'height': 10},
            
            {'type': 'data', 'color': (100, 150, 255), 'name': 'Numérico', 'effect': '+10 energía'},
            {'type': 'data', 'color': (100, 255, 100), 'name': 'Texto', 'effect': '+5 energía, +3 cognición'},
            {'type': 'data', 'color': (255, 255, 100), 'name': 'Audio', 'effect': '+8 energía, +5 vocal'},
            {'type': 'data', 'color': (200, 100, 255), 'name': 'Estructurado', 'effect': '+15 energía, +10 cognición'},
            {'type': 'data', 'color': (200, 200, 200), 'name': 'Binario', 'effect': '+3 energía'},
            
            {'type': 'space', 'height': 20},
            {'type': 'subtitle', 'text': 'CONTROLES'},
            {'type': 'space', 'height': 10},
            
            {'type': 'control', 'key': 'ESPACIO', 'desc': 'Pausar/Reanudar simulación'},
            {'type': 'control', 'key': 'M', 'desc': 'Abrir menú de configuración'},
            {'type': 'control', 'key': 'H', 'desc': 'Abrir/Cerrar esta ayuda'},
            {'type': 'control', 'key': 'F', 'desc': 'Seguir criatura seleccionada'},
            {'type': 'control', 'key': '+/-', 'desc': 'Aumentar/Reducir velocidad'},
            {'type': 'control', 'key': 'Click', 'desc': 'Seleccionar criatura'},
            {'type': 'control', 'key': 'Rueda', 'desc': 'Zoom in/out'},
            {'type': 'control', 'key': 'Boton Der/Central', 'desc': 'Arrastrar para mover vista'},
            {'type': 'control', 'key': 'N', 'desc': 'Renombrar criatura seleccionada'},
            {'type': 'control', 'key': 'R', 'desc': 'Reiniciar simulación'},
            {'type': 'control', 'key': 'S', 'desc': 'Guardar simulación'},
            {'type': 'control', 'key': 'F11', 'desc': 'Pantalla completa'},
            {'type': 'control', 'key': 'ESC', 'desc': 'Salir'},
            
            {'type': 'space', 'height': 20},
            {'type': 'subtitle', 'text': 'CONSEJOS DE OBSERVACION'},
            {'type': 'space', 'height': 10},
            
            {'type': 'tip', 'text': '• Usa ZOOM (rueda) para ver detalles de las formas'},
            {'type': 'tip', 'text': '• Click izquierdo para seleccionar criaturas'},
            {'type': 'tip', 'text': '• Botón derecho + arrastrar para mover la vista'},
            {'type': 'tip', 'text': '• Presiona F para seguir criatura seleccionada'},
            {'type': 'tip', 'text': '• Presiona N para renombrar criatura'},
            {'type': 'tip', 'text': '• Acelera con + para ver evolución rápida'},
            {'type': 'tip', 'text': '• Punto amarillo indica vocalizacion'},
            {'type': 'tip', 'text': '• Barra verde = mucha energía, roja = poca'},
            {'type': 'tip', 'text': '• Nombres amarillos = criaturas renombradas'},
            
            {'type': 'space', 'height': 20},
            {'type': 'subtitle', 'text': 'LINEA DE TIEMPO'},
            {'type': 'space', 'height': 10},
            
            {'type': 'timeline', 'time': '0-2 min', 'event': 'Círculos rojos, movimiento aleatorio'},
            {'type': 'timeline', 'time': '2-5 min', 'event': 'Aparecen hexágonos naranjas'},
            {'type': 'timeline', 'time': '5-10 min', 'event': 'Octógonos verdes, primeras voces'},
            {'type': 'timeline', 'time': '10-15 min', 'event': 'Estrellas azules, lenguaje completo'},
            
            {'type': 'space', 'height': 30},
        ]
    
    def toggle(self):
        """Mostrar/ocultar menú"""
        self.visible = not self.visible
        if self.visible:
            self.scroll_offset = 0
    
    def handle_event(self, event):
        """Manejar eventos del menú"""
        if not self.visible:
            return False
        
        if event.type == pygame.MOUSEWHEEL:
            # Scroll
            self.scroll_offset -= event.y * 30
            self.scroll_offset = max(0, min(self.max_scroll, self.scroll_offset))
            return True
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_h:
                self.visible = False
                return True
        
        return False
    
    def render(self):
        """Renderizar menú"""
        if not self.visible:
            return
        
        # Overlay semi-transparente
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Panel principal - sin bordes redondeados para evitar artefactos
        panel_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(self.screen, self.bg_color, panel_rect)
        pygame.draw.rect(self.screen, self.highlight_color, panel_rect, 3)
        
        # Crear superficie de contenido con scroll - más grande para todo el contenido
        content_surface = pygame.Surface((self.width - 40, self.height * 3))
        content_surface.fill(self.bg_color)
        
        # Renderizar contenido
        y_offset = 20
        for item in self.content:
            y_offset = self.render_item(content_surface, item, y_offset)
        
        self.content_height = y_offset
        visible_height = self.height - 80
        self.max_scroll = max(0, self.content_height - visible_height)
        
        # Blit contenido con scroll - área visible más grande
        visible_height = self.height - 80  # Más espacio para contenido
        self.screen.blit(content_surface, 
                        (self.x + 20, self.y + 60),
                        (0, self.scroll_offset, self.width - 40, visible_height))
        
        # Indicador de scroll
        if self.max_scroll > 0:
            self.render_scrollbar()
        
        # Instrucción de cierre en la parte inferior
        close_text = self.font_small.render("Presiona H o ESC para cerrar | Usa rueda para scroll", True, (150, 150, 150))
        close_rect = close_text.get_rect(center=(self.x + self.width // 2, self.y + self.height - 25))
        self.screen.blit(close_text, close_rect)
    
    def render_item(self, surface, item, y):
        """Renderizar un item de contenido"""
        item_type = item['type']
        
        if item_type == 'title':
            text = self.font_title.render(item['text'], True, self.highlight_color)
            surface.blit(text, (20, y))
            return y + 50
        
        elif item_type == 'subtitle':
            text = self.font_subtitle.render(item['text'], True, self.highlight_color)
            surface.blit(text, (20, y))
            return y + 35
        
        elif item_type == 'space':
            return y + item['height']
        
        elif item_type == 'phase':
            # Círculo de color en lugar de símbolo
            pygame.draw.circle(surface, item['color'], (40, y + 15), 12)
            
            # Nombre de fase
            name = self.font_text.render(item['name'], True, self.text_color)
            surface.blit(name, (70, y + 5))
            
            # Descripción
            desc = self.font_small.render(item['desc'], True, (180, 180, 180))
            surface.blit(desc, (70, y + 25))
            
            return y + 50
        
        elif item_type == 'data':
            # Círculo de color
            pygame.draw.circle(surface, item['color'], (40, y + 12), 10)
            
            # Nombre
            name = self.font_text.render(item['name'], True, self.text_color)
            surface.blit(name, (65, y + 2))
            
            # Efecto
            effect = self.font_text.render(item['effect'], True, (180, 180, 180))
            surface.blit(effect, (200, y + 2))  # Más espacio y fuente más grande
            
            return y + 35  # Más espacio entre líneas
        
        elif item_type == 'control':
            # Tecla
            key_text = self.font_text.render(item['key'], True, self.highlight_color)
            surface.blit(key_text, (30, y))
            
            # Descripción
            desc = self.font_text.render(item['desc'], True, self.text_color)
            surface.blit(desc, (200, y))  # Más espacio para la descripción
            
            return y + 30  # Más espacio entre líneas
        
        elif item_type == 'tip':
            text = self.font_text.render(item['text'], True, (200, 255, 200))
            surface.blit(text, (30, y))
            return y + 28  # Más espacio entre tips
        
        elif item_type == 'timeline':
            # Tiempo
            time_text = self.font_text.render(item['time'], True, self.highlight_color)
            surface.blit(time_text, (30, y))
            
            # Evento
            event_text = self.font_text.render(item['event'], True, self.text_color)
            surface.blit(event_text, (140, y))  # Más espacio y fuente más grande
            
            return y + 32  # Más espacio entre líneas
        
        return y
    
    def render_scrollbar(self):
        """Renderizar barra de scroll"""
        # Barra de fondo
        bar_x = self.x + self.width - 15
        bar_y = self.y + 60
        bar_height = self.height - 100
        
        pygame.draw.rect(self.screen, (50, 50, 60),
                        (bar_x, bar_y, 10, bar_height))
        
        # Handle de scroll
        visible_height = self.height - 80
        handle_height = max(30, bar_height * (visible_height / self.content_height))
        handle_y = bar_y + (self.scroll_offset / self.max_scroll) * (bar_height - handle_height)
        
        pygame.draw.rect(self.screen, self.highlight_color,
                        (bar_x, int(handle_y), 10, int(handle_height)))
