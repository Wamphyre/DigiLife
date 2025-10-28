"""
Menú de configuración interactivo
"""

import pygame
import config


class ConfigMenu:
    """Menú para ajustar parámetros de la simulación"""
    
    def __init__(self, screen, world):
        self.screen = screen
        self.world = world
        self.visible = False
        
        # Dimensiones - más grande para mejor visualización
        self.width = 600
        self.height = 700
        self.x = (screen.get_width() - self.width) // 2
        self.y = (screen.get_height() - self.height) // 2
        
        # Fuentes
        self.font_title = pygame.font.Font(None, 32)
        self.font_label = pygame.font.Font(None, 20)
        self.font_value = pygame.font.Font(None, 18)
        
        # Colores
        self.bg_color = (30, 30, 40)
        self.panel_color = (40, 40, 50)
        self.text_color = (220, 220, 220)
        self.highlight_color = (100, 150, 255)
        self.button_color = (60, 60, 80)
        self.button_hover_color = (80, 80, 100)
        
        # Parámetros ajustables
        self.params = [
            {
                'name': 'Tasa de Datos',
                'key': 'data_rate',
                'value': config.DATA_SPAWN_RATE,
                'min': 0.5,
                'max': 20,
                'step': 0.5,
                'format': '{:.1f}/seg'
            },
            {
                'name': 'Población Máxima',
                'key': 'max_population',
                'value': config.MAX_POPULATION,
                'min': 10,
                'max': 500,
                'step': 10,
                'format': '{:.0f}'
            },
            {
                'name': 'Energía Inicial',
                'key': 'initial_energy',
                'value': config.INITIAL_ENERGY,
                'min': 50,
                'max': 300,
                'step': 10,
                'format': '{:.0f}'
            },
            {
                'name': 'Costo Energético',
                'key': 'energy_cost',
                'value': config.ENERGY_COST_PER_CYCLE,
                'min': 0.1,
                'max': 2.0,
                'step': 0.1,
                'format': '{:.1f}/ciclo'
            },
            {
                'name': 'Tasa de Mutación',
                'key': 'mutation_rate',
                'value': config.MUTATION_RATE_BASE,
                'min': 0.01,
                'max': 0.5,
                'step': 0.01,
                'format': '{:.2f}'
            },
            {
                'name': 'Umbral Vocal',
                'key': 'vocal_threshold',
                'value': config.COMPLEXITY_THRESHOLD_VOCAL,
                'min': 100,
                'max': 1000,
                'step': 50,
                'format': '{:.0f}'
            },
            {
                'name': 'Umbral Reproducción',
                'key': 'reproduction_threshold',
                'value': config.REPRODUCTION_ENERGY_THRESHOLD,
                'min': 100,
                'max': 200,
                'step': 10,
                'format': '{:.0f}'
            }
        ]
        
        # Sliders
        self.sliders = []
        self.create_sliders()
        
        # Botones
        self.buttons = [
            {'label': 'Aplicar', 'action': 'apply', 'rect': None},
            {'label': 'Restablecer', 'action': 'reset', 'rect': None},
            {'label': 'Cerrar', 'action': 'close', 'rect': None}
        ]
        self.create_buttons()
        
        # Estado
        self.dragging_slider = None
        self.hover_button = None
    
    def create_sliders(self):
        """Crear sliders para cada parámetro"""
        y_offset = 80
        slider_height = 70  # Aumentado para más espacio
        
        for param in self.params:
            slider = {
                'param': param,
                'x': self.x + 30,
                'y': self.y + y_offset,
                'width': self.width - 60,
                'height': 22,  # Altura de la barra
                'handle_x': 0  # Se calculará
            }
            
            # Calcular posición inicial del handle (con límites)
            value_range = param['max'] - param['min']
            # Asegurar que el valor esté dentro del rango
            clamped_value = max(param['min'], min(param['max'], param['value']))
            normalized = (clamped_value - param['min']) / value_range
            slider['handle_x'] = slider['x'] + normalized * slider['width']
            
            self.sliders.append(slider)
            y_offset += slider_height
    
    def create_buttons(self):
        """Crear botones"""
        button_width = 140
        button_height = 40
        button_spacing = 10
        
        total_width = len(self.buttons) * button_width + (len(self.buttons) - 1) * button_spacing
        start_x = self.x + (self.width - total_width) // 2
        button_y = self.y + self.height - 60
        
        for i, button in enumerate(self.buttons):
            button['rect'] = pygame.Rect(
                start_x + i * (button_width + button_spacing),
                button_y,
                button_width,
                button_height
            )
    
    def toggle(self):
        """Mostrar/ocultar menú"""
        self.visible = not self.visible
    
    def show(self):
        """Mostrar menú"""
        self.visible = True
    
    def hide(self):
        """Ocultar menú"""
        self.visible = False
    
    def handle_event(self, event):
        """Manejar eventos del menú"""
        if not self.visible:
            return False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Click izquierdo
                # Verificar sliders
                for slider in self.sliders:
                    handle_rect = pygame.Rect(
                        slider['handle_x'] - 8,
                        slider['y'] - 5,
                        16,
                        slider['height'] + 10
                    )
                    if handle_rect.collidepoint(event.pos):
                        self.dragging_slider = slider
                        return True
                
                # Verificar botones
                for button in self.buttons:
                    if button['rect'].collidepoint(event.pos):
                        self.handle_button_click(button['action'])
                        return True
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging_slider = None
        
        elif event.type == pygame.MOUSEMOTION:
            # Arrastrar slider
            if self.dragging_slider:
                slider = self.dragging_slider
                new_x = max(slider['x'], min(slider['x'] + slider['width'], event.pos[0]))
                slider['handle_x'] = new_x
                
                # Actualizar valor
                normalized = (new_x - slider['x']) / slider['width']
                param = slider['param']
                value_range = param['max'] - param['min']
                new_value = param['min'] + normalized * value_range
                
                # Redondear según step
                new_value = round(new_value / param['step']) * param['step']
                param['value'] = new_value
                
                return True
            
            # Hover en botones
            self.hover_button = None
            for button in self.buttons:
                if button['rect'].collidepoint(event.pos):
                    self.hover_button = button
                    break
        
        return False
    
    def handle_button_click(self, action):
        """Manejar click en botón"""
        if action == 'apply':
            self.apply_changes()
        elif action == 'reset':
            self.reset_defaults()
        elif action == 'close':
            self.hide()
    
    def apply_changes(self):
        """Aplicar cambios a la configuración"""
        changes_made = []
        
        for param in self.params:
            key = param['key']
            value = param['value']
            
            if key == 'data_rate':
                config.DATA_SPAWN_RATE = value
                changes_made.append(f"Tasa de Datos: {value:.1f}/seg")
            elif key == 'max_population':
                config.MAX_POPULATION = int(value)
                changes_made.append(f"Población Máxima: {int(value)}")
            elif key == 'initial_energy':
                old_initial = config.INITIAL_ENERGY
                config.INITIAL_ENERGY = value
                config.MAX_ENERGY = value * 1.5  # Actualizar también MAX_ENERGY
                # Aplicar boost de energía a criaturas existentes
                if hasattr(self, 'world') and self.world and self.world.creatures:
                    energy_boost = value - old_initial
                    for creature in self.world.creatures:
                        creature.max_energy = config.MAX_ENERGY
                        creature.energy = min(creature.energy + energy_boost, creature.max_energy)
                changes_made.append(f"Energía Inicial: {value:.0f}")
            elif key == 'energy_cost':
                config.ENERGY_COST_PER_CYCLE = value
                changes_made.append(f"Costo Energético: {value:.1f}/ciclo")
            elif key == 'mutation_rate':
                config.MUTATION_RATE_BASE = value
                changes_made.append(f"Tasa de Mutación: {value:.2f}")
            elif key == 'vocal_threshold':
                config.COMPLEXITY_THRESHOLD_VOCAL = value
                changes_made.append(f"Umbral Vocal: {value:.0f}")
            elif key == 'reproduction_threshold':
                config.REPRODUCTION_ENERGY_THRESHOLD = value
                changes_made.append(f"Umbral Reproducción: {value:.0f}")
        
        print("✅ Configuración aplicada:")
        for change in changes_made:
            print(f"   • {change}")
    
    def reset_defaults(self):
        """Restablecer valores por defecto (MEJORADOS v2.7)"""
        defaults = {
            'data_rate': 5,  # Mejorado para mejor supervivencia
            'max_population': 120,
            'initial_energy': 150,  # Balanceado para supervivencia
            'energy_cost': 0.5,  # Reducido para mejor supervivencia
            'mutation_rate': 0.05,
            'vocal_threshold': 500,
            'reproduction_threshold': 180
        }
        
        for param in self.params:
            param['value'] = defaults[param['key']]
        
        # Actualizar sliders
        for slider in self.sliders:
            param = slider['param']
            value_range = param['max'] - param['min']
            normalized = (param['value'] - param['min']) / value_range
            slider['handle_x'] = slider['x'] + normalized * slider['width']
        
        print("🔄 Valores restablecidos")
    
    def render(self):
        """Renderizar menú"""
        if not self.visible:
            return
        
        # Overlay semi-transparente
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Panel principal - fondo sólido sin transparencia
        panel_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(self.screen, self.bg_color, panel_rect)
        pygame.draw.rect(self.screen, self.highlight_color, panel_rect, 3)
        
        # Título
        title = self.font_title.render("Configuracion", True, self.highlight_color)
        title_rect = title.get_rect(center=(self.x + self.width // 2, self.y + 30))
        self.screen.blit(title, title_rect)
        
        # Sliders
        for slider in self.sliders:
            self.render_slider(slider)
        
        # Botones
        for button in self.buttons:
            self.render_button(button)
    
    def render_slider(self, slider):
        """Renderizar un slider"""
        param = slider['param']
        
        # Label
        label = self.font_label.render(param['name'], True, self.text_color)
        self.screen.blit(label, (slider['x'], slider['y'] - 25))
        
        # Valor
        value_text = param['format'].format(param['value'])
        value = self.font_value.render(value_text, True, self.highlight_color)
        value_rect = value.get_rect(right=slider['x'] + slider['width'], top=slider['y'] - 25)
        self.screen.blit(value, value_rect)
        
        # Track (barra) - sin bordes redondeados para evitar artefactos
        track_rect = pygame.Rect(slider['x'], slider['y'], slider['width'], slider['height'])
        pygame.draw.rect(self.screen, (60, 60, 70), track_rect)
        pygame.draw.rect(self.screen, (100, 100, 110), track_rect, 1)
        
        # Fill (parte llena)
        fill_width = max(2, int(slider['handle_x'] - slider['x']))
        if fill_width > 2:
            fill_rect = pygame.Rect(slider['x'], slider['y'], fill_width, slider['height'])
            pygame.draw.rect(self.screen, self.highlight_color, fill_rect)
        
        # Handle (manija) - rectángulo simple sin bordes redondeados
        handle_x = int(slider['handle_x']) - 8
        handle_rect = pygame.Rect(
            handle_x,
            slider['y'] - 4,
            16,
            slider['height'] + 8
        )
        pygame.draw.rect(self.screen, (220, 220, 220), handle_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), handle_rect, 2)
    
    def render_button(self, button):
        """Renderizar un botón"""
        is_hover = button == self.hover_button
        color = self.button_hover_color if is_hover else self.button_color
        
        # Fondo del botón - sin bordes redondeados
        btn_rect = button['rect']
        pygame.draw.rect(self.screen, color, btn_rect)
        
        # Borde
        border_color = self.highlight_color if is_hover else (100, 100, 100)
        pygame.draw.rect(self.screen, border_color, btn_rect, 2)
        
        # Texto
        text = self.font_label.render(button['label'], True, self.text_color)
        text_rect = text.get_rect(center=btn_rect.center)
        self.screen.blit(text, text_rect)
