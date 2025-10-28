"""
Panel de estadísticas
"""

import pygame
import math
import config


class StatsPanel:
    """Panel que muestra estadísticas de la simulación"""
    
    def __init__(self, screen, world):
        self.screen = screen
        self.world = world
        
        # Posición y tamaño
        self.x = config.WORLD_WIDTH
        self.y = 0
        self.width = config.UI_PANEL_WIDTH
        self.height = config.WORLD_HEIGHT
        
        # Fuentes (aumentadas para mejor lectura)
        self.font_title = pygame.font.Font(None, 28)
        self.font_normal = pygame.font.Font(None, 22)
        self.font_small = pygame.font.Font(None, 18)
        self.font_tiny = pygame.font.Font(None, 14)
        
        # Colores
        self.bg_color = config.UI_BACKGROUND_COLOR
        self.text_color = config.UI_TEXT_COLOR
        
        # Scroll para sección de criatura seleccionada
        self.scroll_offset = 0
        self.max_scroll = 0
        self.creature_section_start = 0
        self.creature_content_height = 0
        
        # Input de texto para renombrar
        self.renaming = False
        self.rename_text = ""
    
    def render(self):
        """Renderizar panel con scroll completo cuando hay criatura seleccionada"""
        # Fondo
        pygame.draw.rect(self.screen, self.bg_color,
                        (self.x, self.y, self.width, self.height))
        
        # Si hay criatura seleccionada, renderizar todo con scroll
        if self.world.selected_creature:
            self.render_with_scroll()
        else:
            # Sin criatura seleccionada, renderizar normal sin scroll
            self.render_without_scroll()
    
    def render_without_scroll(self):
        """Renderizar panel sin scroll (sin criatura seleccionada)"""
        y_offset = 20
        title = self.font_title.render("DigiLife Stats", True, (100, 200, 255))
        self.screen.blit(title, (self.x + 10, y_offset))
        y_offset += 40
        
        pygame.draw.line(self.screen, (100, 100, 100),
                        (self.x + 10, y_offset), (self.x + self.width - 10, y_offset), 1)
        y_offset += 20
        
        # Estadísticas globales
        days = self.world.cycle // config.CYCLES_PER_DAY
        
        stats = [
            ("Ciclo", f"{self.world.cycle}"),
            ("Días", f"{days}"),
            ("Población", f"{self.world.population}"),
            ("Nacimientos", f"{self.world.total_births}"),
            ("Muertes", f"{self.world.total_deaths}"),
            ("Especies", f"{self.world.species_count}"),
            ("", ""),
            ("Complejidad Max", f"{self.world.max_complexity:.0f}"),
            ("Con Voz", f"{self.world.vocal_creatures}"),
            ("Datos", f"{len(self.world.data_items)}"),
            ("", ""),
            ("Velocidad", f"{self.world.speed_multiplier:.1f}x"),
        ]
        
        for label, value in stats:
            if label:
                text = self.font_normal.render(f"{label}:", True, self.text_color)
                self.screen.blit(text, (self.x + 15, y_offset))
                
                value_text = self.font_normal.render(str(value), True, (150, 255, 150))
                self.screen.blit(value_text, (self.x + 180, y_offset))
            
            y_offset += 25
        
        # Situación Global
        y_offset += 10
        pygame.draw.line(self.screen, (100, 100, 100),
                        (self.x + 10, y_offset), (self.x + self.width - 10, y_offset), 2)
        y_offset += 15
        
        situation_title = self.font_title.render("Situación Global", True, (255, 200, 100))
        self.screen.blit(situation_title, (self.x + 10, y_offset))
        y_offset += 35
        
        ecosystem_stats = self.calculate_ecosystem_stats()
        
        env_status = ecosystem_stats['environment_status']
        env_color = {
            'Crítico': (255, 50, 50),
            'Difícil': (255, 150, 50),
            'Estable': (100, 255, 100),
            'Próspero': (100, 255, 255)
        }.get(env_status, (200, 200, 200))
        
        env_text = self.font_normal.render(f"Entorno: {env_status}", True, env_color)
        self.screen.blit(env_text, (self.x + 15, y_offset))
        y_offset += 30
        
        if ecosystem_stats['most_consumed_data']:
            data_type = ecosystem_stats['most_consumed_data']
            data_color = config.DATA_COLORS.get(data_type, (200, 200, 200))
            data_text = self.font_small.render(f"Preferencia: {data_type.title()}", True, data_color)
            self.screen.blit(data_text, (self.x + 15, y_offset))
            y_offset += 25
        
        if ecosystem_stats['fittest_creature']:
            creature = ecosystem_stats['fittest_creature']
            name = getattr(creature, 'custom_name', f"#{creature.id}")
            fitness_text = self.font_small.render(f"Más hábil: {name}", True, (100, 255, 100))
            self.screen.blit(fitness_text, (self.x + 15, y_offset))
            
            fitness_value = self.font_tiny.render(f"(Fitness: {creature.fitness:.0f})", True, (150, 150, 150))
            self.screen.blit(fitness_value, (self.x + 20, y_offset + 18))
            y_offset += 40
        
        if ecosystem_stats['weakest_creature']:
            creature = ecosystem_stats['weakest_creature']
            name = getattr(creature, 'custom_name', f"#{creature.id}")
            weak_text = self.font_small.render(f"Más débil: {name}", True, (255, 100, 100))
            self.screen.blit(weak_text, (self.x + 15, y_offset))
            
            fitness_value = self.font_tiny.render(f"(Fitness: {creature.fitness:.0f})", True, (150, 150, 150))
            self.screen.blit(fitness_value, (self.x + 20, y_offset + 18))
            y_offset += 40
        
        if ecosystem_stats['most_potential']:
            creature = ecosystem_stats['most_potential']
            name = getattr(creature, 'custom_name', f"#{creature.id}")
            potential_text = self.font_small.render(f"Más potencial: {name}", True, (255, 200, 100))
            self.screen.blit(potential_text, (self.x + 15, y_offset))
            
            potential_value = self.font_tiny.render(f"(Gen: {creature.generation}, Comp: {creature.complexity:.0f})", True, (150, 150, 150))
            self.screen.blit(potential_value, (self.x + 20, y_offset + 18))
            y_offset += 40
        
        y_offset += 5
        avg_stats = [
            ("Fitness Prom", f"{ecosystem_stats['avg_fitness']:.1f}"),
            ("Edad Prom", f"{ecosystem_stats['avg_age']:.1f}"),
            ("Energía Prom", f"{ecosystem_stats['avg_energy']:.1f}"),
        ]
        
        for label, value in avg_stats:
            text = self.font_small.render(f"{label}:", True, self.text_color)
            self.screen.blit(text, (self.x + 15, y_offset))
            
            value_text = self.font_small.render(str(value), True, (200, 200, 200))
            self.screen.blit(value_text, (self.x + 180, y_offset))
            y_offset += 22
        
        # Epidemias activas (versión sin scroll)
        if hasattr(self.world, 'disease_system'):
            epidemics = self.world.disease_system.get_active_epidemics()
            if epidemics and y_offset < self.height - 100:  # Solo si hay espacio
                y_offset += 15
                pygame.draw.line(self.screen, (255, 50, 50),
                                (self.x + 10, y_offset), (self.x + self.width - 10, y_offset), 2)
                y_offset += 15
                
                epidemic_title = self.font_small.render("EPIDEMIAS", True, (255, 100, 100))
                self.screen.blit(epidemic_title, (self.x + 10, y_offset))
                y_offset += 25
                
                for epidemic in epidemics[:1]:  # Máximo 1 para no saturar
                    disease_text = self.font_tiny.render(
                        f"* {epidemic['name']}", 
                        True, (255, 150, 150)
                    )
                    self.screen.blit(disease_text, (self.x + 15, y_offset))
                    y_offset += 18
                    
                    # Paciente cero e infectados
                    if epidemic.get('patient_zero_id'):
                        info_text = self.font_tiny.render(
                            f"  P0: #{epidemic['patient_zero_id']} | {epidemic['infected']} inf | {epidemic['deaths']} †", 
                            True, (200, 150, 150)
                        )
                        self.screen.blit(info_text, (self.x + 15, y_offset))
                        y_offset += 18
        
        # Depredación (versión sin scroll)
        if config.PREDATION_ENABLED and y_offset < self.height - 120:
            if self.world.active_predators > 0 or self.world.predation_kills > 0:
                y_offset += 10
                predation_title = self.font_small.render("DEPREDACION", True, (255, 150, 50))
                self.screen.blit(predation_title, (self.x + 10, y_offset))
                y_offset += 22
                
                predation_text = self.font_tiny.render(
                    f"{self.world.active_predators} activos | {self.world.predation_kills} muertes", 
                    True, (255, 180, 100)
                )
                self.screen.blit(predation_text, (self.x + 15, y_offset))
                y_offset += 20
                
                # Top 3 depredadores (versión compacta)
                top_predators = self.world.get_top_predators(3)
                if top_predators and y_offset < self.height - 60:
                    for i, (creature_id, kills, complexity) in enumerate(top_predators, 1):
                        creature_name = f"#{creature_id}"
                        for c in self.world.creatures:
                            if c.id == creature_id and hasattr(c, 'custom_name') and c.custom_name:
                                creature_name = c.custom_name
                                break
                        
                        predator_text = self.font_tiny.render(
                            f"{i}. {creature_name}: {kills} kills", 
                            True, (255, 180, 100)
                        )
                        self.screen.blit(predator_text, (self.x + 15, y_offset))
                        y_offset += 16
    
    def render_with_scroll(self):
        """Renderizar todo el panel con scroll (cuando hay criatura seleccionada)"""
        # Crear superficie temporal grande para todo el contenido
        temp_surface = pygame.Surface((self.width - 20, 3000), pygame.SRCALPHA)
        
        y_offset = 0
        
        # Título
        title = self.font_title.render("DigiLife Stats", True, (100, 200, 255))
        temp_surface.blit(title, (0, y_offset))
        y_offset += 40
        
        pygame.draw.line(temp_surface, (100, 100, 100),
                        (0, y_offset), (self.width - 20, y_offset), 1)
        y_offset += 20
        
        # Estadísticas globales
        days = self.world.cycle // config.CYCLES_PER_DAY
        
        stats = [
            ("Ciclo", f"{self.world.cycle}"),
            ("Días", f"{days}"),
            ("Población", f"{self.world.population}"),
            ("Nacimientos", f"{self.world.total_births}"),
            ("Muertes", f"{self.world.total_deaths}"),
            ("Especies", f"{self.world.species_count}"),
            ("", ""),
            ("Complejidad Max", f"{self.world.max_complexity:.0f}"),
            ("Con Voz", f"{self.world.vocal_creatures}"),
            ("Datos", f"{len(self.world.data_items)}"),
            ("", ""),
            ("Velocidad", f"{self.world.speed_multiplier:.1f}x"),
        ]
        
        for label, value in stats:
            if label:
                text = self.font_normal.render(f"{label}:", True, self.text_color)
                temp_surface.blit(text, (5, y_offset))
                
                value_text = self.font_normal.render(str(value), True, (150, 255, 150))
                temp_surface.blit(value_text, (170, y_offset))
            
            y_offset += 25
        
        # Situación Global
        y_offset += 10
        pygame.draw.line(temp_surface, (100, 100, 100),
                        (0, y_offset), (self.width - 20, y_offset), 2)
        y_offset += 15
        
        situation_title = self.font_title.render("Situación Global", True, (255, 200, 100))
        temp_surface.blit(situation_title, (0, y_offset))
        y_offset += 35
        
        ecosystem_stats = self.calculate_ecosystem_stats()
        
        env_status = ecosystem_stats['environment_status']
        env_color = {
            'Crítico': (255, 50, 50),
            'Difícil': (255, 150, 50),
            'Estable': (100, 255, 100),
            'Próspero': (100, 255, 255)
        }.get(env_status, (200, 200, 200))
        
        env_text = self.font_normal.render(f"Entorno: {env_status}", True, env_color)
        temp_surface.blit(env_text, (5, y_offset))
        y_offset += 30
        
        if ecosystem_stats['most_consumed_data']:
            data_type = ecosystem_stats['most_consumed_data']
            data_color = config.DATA_COLORS.get(data_type, (200, 200, 200))
            data_text = self.font_small.render(f"Preferencia: {data_type.title()}", True, data_color)
            temp_surface.blit(data_text, (5, y_offset))
            y_offset += 25
        
        if ecosystem_stats['fittest_creature']:
            creature = ecosystem_stats['fittest_creature']
            name = getattr(creature, 'custom_name', f"#{creature.id}")
            fitness_text = self.font_small.render(f"Más hábil: {name}", True, (100, 255, 100))
            temp_surface.blit(fitness_text, (5, y_offset))
            
            fitness_value = self.font_tiny.render(f"(Fitness: {creature.fitness:.0f})", True, (150, 150, 150))
            temp_surface.blit(fitness_value, (10, y_offset + 18))
            y_offset += 40
        
        if ecosystem_stats['weakest_creature']:
            creature = ecosystem_stats['weakest_creature']
            name = getattr(creature, 'custom_name', f"#{creature.id}")
            weak_text = self.font_small.render(f"Más débil: {name}", True, (255, 100, 100))
            temp_surface.blit(weak_text, (5, y_offset))
            
            fitness_value = self.font_tiny.render(f"(Fitness: {creature.fitness:.0f})", True, (150, 150, 150))
            temp_surface.blit(fitness_value, (10, y_offset + 18))
            y_offset += 40
        
        if ecosystem_stats['most_potential']:
            creature = ecosystem_stats['most_potential']
            name = getattr(creature, 'custom_name', f"#{creature.id}")
            potential_text = self.font_small.render(f"Más potencial: {name}", True, (255, 200, 100))
            temp_surface.blit(potential_text, (5, y_offset))
            
            potential_value = self.font_tiny.render(f"(Gen: {creature.generation}, Comp: {creature.complexity:.0f})", True, (150, 150, 150))
            temp_surface.blit(potential_value, (10, y_offset + 18))
            y_offset += 40
        
        y_offset += 5
        avg_stats = [
            ("Fitness Prom", f"{ecosystem_stats['avg_fitness']:.1f}"),
            ("Edad Prom", f"{ecosystem_stats['avg_age']:.1f}"),
            ("Energía Prom", f"{ecosystem_stats['avg_energy']:.1f}"),
        ]
        
        for label, value in avg_stats:
            text = self.font_small.render(f"{label}:", True, self.text_color)
            temp_surface.blit(text, (5, y_offset))
            
            value_text = self.font_small.render(str(value), True, (200, 200, 200))
            temp_surface.blit(value_text, (170, y_offset))
            y_offset += 22
        
        # Epidemias activas
        if hasattr(self.world, 'disease_system'):
            epidemics = self.world.disease_system.get_active_epidemics()
            if epidemics:
                y_offset += 15
                pygame.draw.line(temp_surface, (255, 50, 50),
                                (0, y_offset), (self.width - 20, y_offset), 2)
                y_offset += 15
                
                epidemic_title = self.font_title.render("EPIDEMIAS", True, (255, 100, 100))
                temp_surface.blit(epidemic_title, (0, y_offset))
                y_offset += 30
                
                for epidemic in epidemics:
                    # Nombre de la enfermedad
                    disease_text = self.font_small.render(
                        f"* {epidemic['name']}", 
                        True, (255, 150, 150)
                    )
                    temp_surface.blit(disease_text, (5, y_offset))
                    y_offset += 22
                    
                    # Paciente cero
                    if epidemic.get('patient_zero_id'):
                        patient_text = self.font_tiny.render(
                            f"  Paciente cero: #{epidemic['patient_zero_id']}", 
                            True, (255, 200, 100)
                        )
                        temp_surface.blit(patient_text, (5, y_offset))
                        y_offset += 18
                    
                    # Estadísticas
                    stats_text = self.font_tiny.render(
                        f"  Infectados: {epidemic['infected']} | Muertes: {epidemic['deaths']}", 
                        True, (200, 150, 150)
                    )
                    temp_surface.blit(stats_text, (5, y_offset))
                    y_offset += 18
                    
                    # Contagio y letalidad
                    danger_text = self.font_tiny.render(
                        f"  Contagio: {epidemic['contagion_rate']*100:.1f}% | Letalidad: {epidemic['lethality']*100:.1f}%", 
                        True, (255, 100, 100)
                    )
                    temp_surface.blit(danger_text, (5, y_offset))
                    y_offset += 18
                    
                    # Síntomas
                    symptoms_text = self.font_tiny.render(
                        f"  {epidemic['symptoms']}", 
                        True, (180, 180, 180)
                    )
                    temp_surface.blit(symptoms_text, (5, y_offset))
                    y_offset += 25
        
        # Depredación
        if config.PREDATION_ENABLED and (self.world.active_predators > 0 or self.world.predation_kills > 0):
            y_offset += 15
            pygame.draw.line(temp_surface, (255, 150, 50),
                            (0, y_offset), (self.width - 20, y_offset), 2)
            y_offset += 15
            
            predation_title = self.font_title.render("DEPREDACION", True, (255, 150, 50))
            temp_surface.blit(predation_title, (0, y_offset))
            y_offset += 30
            
            # Depredadores activos
            predators_text = self.font_small.render(
                f"Depredadores activos: {self.world.active_predators}", 
                True, (255, 180, 100)
            )
            temp_surface.blit(predators_text, (5, y_offset))
            y_offset += 25
            
            # Muertes por depredación
            kills_text = self.font_small.render(
                f"Muertes totales: {self.world.predation_kills}", 
                True, (255, 150, 150)
            )
            temp_surface.blit(kills_text, (5, y_offset))
            y_offset += 25
            
            # Tasa de depredación
            if self.world.total_deaths > 0:
                predation_rate = (self.world.predation_kills / self.world.total_deaths) * 100
                rate_text = self.font_tiny.render(
                    f"Tasa: {predation_rate:.1f}% de todas las muertes", 
                    True, (200, 200, 200)
                )
                temp_surface.blit(rate_text, (5, y_offset))
                y_offset += 25
            
            # Top 5 depredadores
            top_predators = self.world.get_top_predators(5)
            if top_predators:
                y_offset += 5
                top_title = self.font_small.render("Top 5 Depredadores:", True, (255, 200, 100))
                temp_surface.blit(top_title, (5, y_offset))
                y_offset += 22
                
                for i, (creature_id, kills, complexity) in enumerate(top_predators, 1):
                    # Buscar si la criatura tiene nombre personalizado
                    creature_name = f"#{creature_id}"
                    for c in self.world.creatures:
                        if c.id == creature_id and hasattr(c, 'custom_name') and c.custom_name:
                            creature_name = c.custom_name
                            break
                    
                    predator_text = self.font_tiny.render(
                        f"  {i}. {creature_name} - {kills} kills (comp: {complexity:.0f})", 
                        True, (255, 180, 100)
                    )
                    temp_surface.blit(predator_text, (5, y_offset))
                    y_offset += 18
        
        # Criatura seleccionada
        y_offset += 20
        pygame.draw.line(temp_surface, (100, 100, 100),
                        (0, y_offset), (self.width - 20, y_offset), 1)
        y_offset += 20
        
        # Renderizar info de criatura en la misma superficie
        y_offset = self.render_creature_info(temp_surface, y_offset)
        
        # Guardar altura total del contenido
        self.creature_content_height = y_offset
        
        # Calcular scroll máximo
        self.max_scroll = max(0, self.creature_content_height - self.height + 40)
        
        # Limitar scroll offset
        self.scroll_offset = max(0, min(self.max_scroll, self.scroll_offset))
        
        # Crear superficie visible con clip
        visible_surface = pygame.Surface((self.width - 20, self.height))
        visible_surface.fill(self.bg_color)
        
        # Copiar contenido con offset de scroll
        visible_surface.blit(temp_surface, (0, -self.scroll_offset))
        
        # Renderizar en pantalla
        self.screen.blit(visible_surface, (self.x + 10, 0))
        
        # Renderizar scrollbar si es necesario
        if self.max_scroll > 0:
            self.render_scrollbar(0, self.height)
    
    def render_creature_info(self, surface, y_offset):
        """Renderizar información de criatura en una superficie"""
        creature = self.world.selected_creature
        
        # Título
        title = self.font_title.render("Criatura Seleccionada", True, (255, 200, 100))
        surface.blit(title, (0, y_offset))
        y_offset += 35
        
        # Nombre personalizado o ID
        if hasattr(creature, 'custom_name') and creature.custom_name:
            name_text = f"Nombre: {creature.custom_name}"
            name_color = (255, 255, 100)
        else:
            name_text = f"ID: {creature.id}"
            name_color = (200, 255, 200)
        
        if self.renaming:
            input_text = f"Nombre: {self.rename_text}_"
            text = self.font_normal.render(input_text, True, (255, 255, 100))
        else:
            text = self.font_normal.render(name_text, True, name_color)
        
        surface.blit(text, (0, y_offset))
        y_offset += 30
        
        # Botón de renombrar
        if not self.renaming:
            rename_hint = self.font_tiny.render("(Presiona N para renombrar)", True, (150, 150, 150))
            surface.blit(rename_hint, (0, y_offset))
            y_offset += 25
        else:
            rename_hint = self.font_tiny.render("(ENTER: confirmar, ESC: cancelar)", True, (255, 200, 100))
            surface.blit(rename_hint, (0, y_offset))
            y_offset += 25
        
        # Calcular velocidad
        speed = math.sqrt(creature.vx**2 + creature.vy**2)
        
        # Info básica
        info = [
            ("Generación", f"{creature.generation}"),
            ("Edad", f"{creature.age:.1f} ciclos"),
            ("Energía", f"{creature.energy:.1f}/{creature.max_energy}"),
            ("Complejidad", f"{creature.complexity:.0f}"),
            ("Fitness", f"{creature.fitness:.1f}"),
            ("Fase", creature.get_phase().title()),
            ("Genoma", f"{len(creature.genome)} inst"),
            ("", ""),
            ("Posición X", f"{creature.x:.1f}"),
            ("Posición Y", f"{creature.y:.1f}"),
            ("Velocidad", f"{speed:.2f}"),
            ("", ""),
            ("Comida", f"{creature.food_eaten}"),
            ("Distancia", f"{creature.distance_traveled:.1f}"),
        ]
        
        for label, value in info:
            if label:
                text = self.font_small.render(f"{label}:", True, self.text_color)
                surface.blit(text, (0, y_offset))
                
                value_text = self.font_small.render(str(value), True, (200, 200, 200))
                surface.blit(value_text, (130, y_offset))
            
            y_offset += 20
        
        # Vocabulario si tiene
        if hasattr(creature, 'vocal_system') and creature.vocal_system.get_vocabulary_size() > 0:
            y_offset += 10
            vocab_title = self.font_small.render("Vocabulario:", True, (150, 200, 255))
            surface.blit(vocab_title, (0, y_offset))
            y_offset += 22
            
            for word, count in list(creature.vocal_system.vocabulary.items())[:8]:
                word_text = self.font_tiny.render(f"  '{word}' ({count}x)", True, (180, 180, 180))
                surface.blit(word_text, (10, y_offset))
                y_offset += 18
        
        return y_offset
    
    def calculate_ecosystem_stats(self):
        """Calcular estadísticas avanzadas del ecosistema"""
        if not self.world.creatures:
            return {
                'environment_status': 'Crítico',
                'most_consumed_data': None,
                'fittest_creature': None,
                'weakest_creature': None,
                'most_potential': None,
                'avg_fitness': 0,
                'avg_age': 0,
                'avg_energy': 0
            }
        
        # Estado del entorno basado en población y recursos (AJUSTADO)
        population_ratio = self.world.population / config.MAX_POPULATION
        data_ratio = len(self.world.data_items) / max(1, config.DATA_SPAWN_RATE * 5)  # Más generoso
        
        # Calcular salud general
        avg_energy_ratio = 0
        if self.world.creatures:
            avg_energy_ratio = sum(c.energy / c.max_energy for c in self.world.creatures) / len(self.world.creatures)
        
        # Estado basado en múltiples factores
        health_score = (population_ratio * 0.4 + data_ratio * 0.3 + avg_energy_ratio * 0.3)
        
        if health_score < 0.2:
            env_status = 'Crítico'
        elif health_score < 0.4:
            env_status = 'Difícil'
        elif health_score < 0.7:
            env_status = 'Estable'
        else:
            env_status = 'Próspero'
        
        # Tipo de dato más consumido (simulado por distribución)
        # En una implementación completa, trackearíamos esto en world
        most_consumed = max(config.DATA_TYPES_DISTRIBUTION.items(), key=lambda x: x[1])[0]
        
        # Criatura más hábil (mayor fitness)
        fittest = max(self.world.creatures, key=lambda c: c.fitness)
        
        # Criatura más débil (menor fitness, pero viva)
        weakest = min(self.world.creatures, key=lambda c: c.fitness)
        
        # Criatura con más potencial (joven + alta complejidad + buen fitness)
        potential_score = lambda c: (c.complexity * 0.5 + c.fitness * 0.3 + (1000 - c.age) * 0.2)
        most_potential = max(self.world.creatures, key=potential_score)
        
        # Promedios
        avg_fitness = sum(c.fitness for c in self.world.creatures) / len(self.world.creatures)
        avg_age = sum(c.age for c in self.world.creatures) / len(self.world.creatures)
        avg_energy = sum(c.energy for c in self.world.creatures) / len(self.world.creatures)
        
        return {
            'environment_status': env_status,
            'most_consumed_data': most_consumed,
            'fittest_creature': fittest,
            'weakest_creature': weakest,
            'most_potential': most_potential,
            'avg_fitness': avg_fitness,
            'avg_age': avg_age,
            'avg_energy': avg_energy
        }
    
    def handle_event(self, event):
        """Manejar eventos del panel"""
        if not self.world.selected_creature:
            return False
        
        # Scroll en la sección de criatura seleccionada
        if event.type == pygame.MOUSEWHEEL:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if self.x < mouse_x < self.x + self.width:
                self.scroll_offset -= event.y * 20
                self.scroll_offset = max(0, min(self.max_scroll, self.scroll_offset))
                return True
        
        # Renombrar criatura
        if event.type == pygame.KEYDOWN:
            if self.renaming:
                if event.key == pygame.K_RETURN:
                    # Confirmar nombre
                    if self.rename_text.strip():
                        self.world.selected_creature.custom_name = self.rename_text.strip()
                    self.renaming = False
                    self.rename_text = ""
                    return True
                elif event.key == pygame.K_ESCAPE:
                    # Cancelar
                    self.renaming = False
                    self.rename_text = ""
                    return True
                elif event.key == pygame.K_BACKSPACE:
                    self.rename_text = self.rename_text[:-1]
                    return True
                elif len(self.rename_text) < 20 and event.unicode.isprintable():
                    self.rename_text += event.unicode
                    return True
            elif event.key == pygame.K_n:
                # Iniciar renombrado
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if self.x < mouse_x < self.x + self.width:
                    self.renaming = True
                    self.rename_text = getattr(self.world.selected_creature, 'custom_name', '')
                    return True
        
        return False
    

    def render_scrollbar(self, y_start, available_height):
        """Renderizar barra de scroll"""
        # Barra de fondo
        bar_x = self.x + self.width - 12
        bar_y = y_start + 5
        bar_height = available_height - 10
        
        pygame.draw.rect(self.screen, (50, 50, 60),
                        (bar_x, bar_y, 8, bar_height), border_radius=4)
        
        # Handle de scroll
        if self.max_scroll > 0:
            visible_ratio = available_height / self.creature_content_height
            handle_height = max(20, bar_height * visible_ratio)
            handle_y = bar_y + (self.scroll_offset / self.max_scroll) * (bar_height - handle_height)
            
            pygame.draw.rect(self.screen, (100, 150, 255),
                            (bar_x, int(handle_y), 8, int(handle_height)), border_radius=4)
