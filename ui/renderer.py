"""
Renderizador principal del mundo
"""

import pygame
import math
import config


class Renderer:
    """Renderiza el mundo y las criaturas"""
    
    def __init__(self, screen, world):
        self.screen = screen
        self.world = world
        
        # Superficie para el mundo
        self.world_surface = pygame.Surface((config.WORLD_WIDTH, config.WORLD_HEIGHT))
        
        # Cámara
        self.camera_x = 0
        self.camera_y = 0
        self.zoom = 1.0
        self.following_creature = False
        self.auto_zoom_target = 1.5  # Zoom al seleccionar criatura
        
        # Escala para pantalla completa
        self.scale_factor = 1.0
        
        # Fuentes
        self.font_small = pygame.font.Font(None, 16)
        self.font_medium = pygame.font.Font(None, 20)
    
    def render(self):
        """Renderizar frame completo"""
        # Seguir criatura seleccionada si está activo
        if self.following_creature and self.world.selected_creature:
            self.follow_selected_creature()
        
        # Limpiar superficie del mundo
        self.world_surface.fill(config.BACKGROUND_COLOR)
        
        # Renderizar datos (alimento)
        self.render_data()
        
        # Renderizar criaturas
        self.render_creatures()
        
        # Renderizar criatura seleccionada (highlight)
        if self.world.selected_creature:
            self.render_selected_highlight()
        
        # Escalar y blit mundo a pantalla
        if hasattr(self, 'scale_factor') and self.scale_factor != 1.0:
            # Escalar el mundo para pantalla completa
            scaled_width = int(config.WORLD_WIDTH * self.scale_factor)
            scaled_height = int(config.WORLD_HEIGHT * self.scale_factor)
            scaled_surface = pygame.transform.scale(
                self.world_surface,
                (scaled_width, scaled_height)
            )
            self.screen.blit(scaled_surface, (0, 0))
        else:
            # Renderizado normal
            self.screen.blit(self.world_surface, (0, 0))
    
    def follow_selected_creature(self):
        """Seguir criatura seleccionada con la cámara"""
        creature = self.world.selected_creature
        if creature not in self.world.creatures:
            self.following_creature = False
            return
        
        # Centrar cámara en la criatura
        target_x = creature.x - (config.WORLD_WIDTH / 2) / self.zoom
        target_y = creature.y - (config.WORLD_HEIGHT / 2) / self.zoom
        
        # Suavizar movimiento de cámara
        self.camera_x += (target_x - self.camera_x) * 0.1
        self.camera_y += (target_y - self.camera_y) * 0.1
        
        # Aplicar límites
        self.apply_camera_limits()
        
        # Suavizar zoom
        self.zoom += (self.auto_zoom_target - self.zoom) * 0.05
    
    def start_following(self):
        """Iniciar seguimiento de criatura seleccionada"""
        if self.world.selected_creature:
            self.following_creature = True
    
    def stop_following(self):
        """Detener seguimiento"""
        self.following_creature = False
    
    def render_data(self):
        """Renderizar datos/alimento"""
        for data in self.world.data_items:
            x, y = self.world_to_screen(data['x'], data['y'])
            size = int(data['size'] * self.zoom)
            pygame.draw.circle(self.world_surface, data['color'], (int(x), int(y)), size)
    
    def render_creatures(self):
        """Renderizar todas las criaturas"""
        for creature in self.world.creatures:
            self.render_creature(creature)
    
    def render_creature(self, creature):
        """Renderizar una criatura"""
        x, y = self.world_to_screen(creature.x, creature.y)
        size = int(creature.size * self.zoom)
        
        # Dibujar forma según fase evolutiva
        phase = creature.get_phase()
        
        if phase == 'primitive':
            # Círculo simple
            pygame.draw.circle(self.world_surface, creature.color, (int(x), int(y)), size)
            pygame.draw.circle(self.world_surface, (255, 255, 255), (int(x), int(y)), size, 1)
        
        elif phase == 'intermediate':
            # Hexágono
            self.draw_polygon(x, y, size, 6, creature.color, creature.direction)
        
        elif phase == 'advanced':
            # Octógono
            self.draw_polygon(x, y, size, 8, creature.color, creature.direction)
        
        else:  # complex
            # Estrella de 8 puntas
            self.draw_star(x, y, size, creature.color, creature.direction)
        
        # Dirección (línea)
        end_x = x + math.cos(creature.direction) * size * 0.7
        end_y = y + math.sin(creature.direction) * size * 0.7
        pygame.draw.line(self.world_surface, (255, 255, 255), 
                        (int(x), int(y)), (int(end_x), int(end_y)), 2)
        
        # Barra de energía si está activado
        if config.SHOW_ENERGY_BAR:
            self.render_energy_bar(creature, x, y, size)
        
        # Nombre si está activado o si tiene nombre personalizado
        if (config.SHOW_NAMES and self.zoom > 0.8) or (hasattr(creature, 'custom_name') and creature.custom_name):
            self.render_creature_name(creature, x, y, size)
        
        # Indicador vocal
        if creature.can_vocalize():
            self.render_vocal_indicator(x, y, size)
    
    def render_energy_bar(self, creature, x, y, size):
        """Renderizar barra de energía"""
        bar_width = size * 2
        bar_height = 4
        bar_x = x - bar_width / 2
        bar_y = y - size - 10
        
        # Fondo
        pygame.draw.rect(self.world_surface, (50, 50, 50),
                        (int(bar_x), int(bar_y), int(bar_width), bar_height))
        
        # Energía
        energy_ratio = creature.energy / creature.max_energy
        energy_width = bar_width * energy_ratio
        
        # Color según nivel
        if energy_ratio > 0.6:
            color = (0, 255, 0)
        elif energy_ratio > 0.3:
            color = (255, 255, 0)
        else:
            color = (255, 0, 0)
        
        pygame.draw.rect(self.world_surface, color,
                        (int(bar_x), int(bar_y), int(energy_width), bar_height))
    
    def render_creature_name(self, creature, x, y, size):
        """Renderizar nombre de criatura"""
        # Usar nombre personalizado si existe
        if hasattr(creature, 'custom_name') and creature.custom_name:
            name = creature.custom_name
            color = (255, 255, 100)  # Amarillo para nombres personalizados
        else:
            name = f"C-{creature.id}"
            color = (200, 200, 200)
        
        text = self.font_small.render(name, True, color)
        text_rect = text.get_rect(center=(int(x), int(y - size - 10)))  # Encima de la criatura
        
        # Fondo semi-transparente para mejor legibilidad
        bg_rect = text_rect.inflate(8, 4)
        pygame.draw.rect(self.world_surface, (0, 0, 0, 180), bg_rect, border_radius=3)
        pygame.draw.rect(self.world_surface, color, bg_rect, 1, border_radius=3)
        
        self.world_surface.blit(text, text_rect)
    
    def render_vocal_indicator(self, x, y, size):
        """Renderizar indicador de capacidad vocal"""
        # Estrella pequeña
        star_x = x + size - 5
        star_y = y - size + 5
        pygame.draw.circle(self.world_surface, (255, 255, 0), 
                          (int(star_x), int(star_y)), 3)
    
    def render_selected_highlight(self):
        """Resaltar criatura seleccionada"""
        creature = self.world.selected_creature
        if creature not in self.world.creatures:
            self.world.selected_creature = None
            return
        
        x, y = self.world_to_screen(creature.x, creature.y)
        size = int(creature.size * self.zoom) + 5
        
        # Círculo pulsante
        pulse = abs(math.sin(pygame.time.get_ticks() / 200)) * 5
        pygame.draw.circle(self.world_surface, (255, 255, 0), 
                          (int(x), int(y)), size + int(pulse), 2)
    
    def world_to_screen(self, x, y):
        """Convertir coordenadas del mundo a pantalla"""
        screen_x = (x - self.camera_x) * self.zoom
        screen_y = (y - self.camera_y) * self.zoom
        return screen_x, screen_y
    
    def screen_to_world(self, pos):
        """Convertir coordenadas de pantalla a mundo"""
        x, y = pos
        # Ajustar por escala de pantalla completa
        x = x / self.scale_factor
        y = y / self.scale_factor
        # Ajustar por zoom y cámara
        world_x = x / self.zoom + self.camera_x
        world_y = y / self.zoom + self.camera_y
        return world_x, world_y
    
    def handle_zoom(self, delta):
        """Manejar zoom con rueda del ratón"""
        zoom_speed = 0.1
        old_zoom = self.zoom
        self.zoom += delta * zoom_speed
        self.zoom = max(0.5, min(2.0, self.zoom))
        
        # Aplicar límites después del zoom
        self.apply_camera_limits()
    
    def handle_pan(self, rel):
        """Manejar paneo con arrastre"""
        if rel != (0, 0):  # Solo si hay movimiento real
            dx, dy = rel
            self.camera_x -= dx / self.zoom
            self.camera_y -= dy / self.zoom
            
            # Aplicar límites para mantener la cámara dentro del mundo
            self.apply_camera_limits()
            
            # Detener seguimiento al hacer pan manual
            self.following_creature = False
    
    def apply_camera_limits(self):
        """Aplicar límites a la cámara para mantenerla dentro del mundo"""
        # Calcular el área visible
        visible_width = config.WORLD_WIDTH / self.zoom
        visible_height = config.WORLD_HEIGHT / self.zoom
        
        # Límites de la cámara
        min_x = 0
        max_x = max(0, config.WORLD_WIDTH - visible_width)
        min_y = 0
        max_y = max(0, config.WORLD_HEIGHT - visible_height)
        
        # Aplicar límites
        self.camera_x = max(min_x, min(max_x, self.camera_x))
        self.camera_y = max(min_y, min(max_y, self.camera_y))
    
    def draw_polygon(self, x, y, size, sides, color, rotation):
        """Dibujar polígono regular"""
        points = []
        angle_step = 2 * math.pi / sides
        
        for i in range(sides):
            angle = rotation + i * angle_step
            px = x + math.cos(angle) * size
            py = y + math.sin(angle) * size
            points.append((int(px), int(py)))
        
        pygame.draw.polygon(self.world_surface, color, points)
        pygame.draw.polygon(self.world_surface, (255, 255, 255), points, 1)
    
    def draw_star(self, x, y, size, color, rotation):
        """Dibujar estrella de 8 puntas"""
        points = []
        outer_radius = size
        inner_radius = size * 0.5
        num_points = 8
        
        for i in range(num_points * 2):
            angle = rotation + (i * math.pi / num_points)
            radius = outer_radius if i % 2 == 0 else inner_radius
            px = x + math.cos(angle) * radius
            py = y + math.sin(angle) * radius
            points.append((int(px), int(py)))
        
        pygame.draw.polygon(self.world_surface, color, points)
        pygame.draw.polygon(self.world_surface, (255, 255, 255), points, 1)
