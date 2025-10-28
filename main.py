#!/usr/bin/env python3
"""
DigiLife - Simulador de Vida Artificial
Punto de entrada principal
"""

import sys
import argparse
import pygame
from pathlib import Path

# Importar configuración
import config

# Importar módulos del motor
from engine.world import World
from ui.renderer import Renderer
from ui.controls import ControlPanel
from ui.stats_panel import StatsPanel
from ui.menu import ConfigMenu
from ui.help_menu import HelpMenu


class DigiLife:
    """Clase principal de la aplicación"""
    
    def __init__(self, args):
        """Inicializar DigiLife"""
        self.args = args
        self.running = False
        self.paused = False
        self.clock = None
        self.screen = None
        self.fullscreen = False
        self.window_width = config.WORLD_WIDTH + config.UI_PANEL_WIDTH
        self.window_height = config.WORLD_HEIGHT
        
        # Aplicar argumentos a configuración
        if args.population:
            config.INITIAL_POPULATION = args.population
        if args.data_rate:
            config.DATA_SPAWN_RATE = args.data_rate
        if args.world_size:
            w, h = map(int, args.world_size.split('x'))
            config.WORLD_WIDTH = w
            config.WORLD_HEIGHT = h
        if args.no_gpu:
            config.USE_GPU = False
        if args.no_audio:
            config.AUDIO_ENABLED = False
        if args.debug:
            for key in config.DEBUG:
                config.DEBUG[key] = True
        if args.fps:
            config.TARGET_FPS = args.fps
        
        print("Inicializando DigiLife...")
        self.init_pygame()
        self.init_components()
        
        # Cargar simulación si se especificó
        if args.load:
            self.load_simulation(args.load)
        
        print("✅ DigiLife iniciado correctamente")
    
    def init_pygame(self):
        """Inicializar Pygame"""
        pygame.init()
        
        # Configurar pantalla
        flags = pygame.DOUBLEBUF | pygame.RESIZABLE
        if self.args.fullscreen:
            flags |= pygame.FULLSCREEN
            self.fullscreen = True
        
        self.screen = pygame.display.set_mode((self.window_width, self.window_height), flags)
        pygame.display.set_caption("DigiLife - Simulador de Vida Artificial")
        
        self.clock = pygame.time.Clock()
    
    def init_components(self):
        """Inicializar componentes del simulador"""
        # Mundo
        self.world = World(config.WORLD_WIDTH, config.WORLD_HEIGHT)
        
        # Renderer
        self.renderer = Renderer(self.screen, self.world)
        
        # Paneles UI
        self.control_panel = ControlPanel(self.screen)
        self.stats_panel = StatsPanel(self.screen, self.world)
        self.config_menu = ConfigMenu(self.screen, self.world)
        self.help_menu = HelpMenu(self.screen)
        
        # Poblar mundo inicial
        self.world.populate(config.INITIAL_POPULATION)
    
    def handle_events(self):
        """Manejar eventos de entrada"""
        for event in pygame.event.get():
            # Primero, dejar que los menús manejen el evento si están visibles
            if self.config_menu.handle_event(event):
                continue
            if self.help_menu.handle_event(event):
                continue
            
            # Panel de estadísticas maneja scroll
            if self.stats_panel.handle_event(event):
                continue
            
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                self.handle_keydown(event.key)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mouse_click(event.pos, event.button)
            
            elif event.type == pygame.MOUSEWHEEL:
                if not self.config_menu.visible and not self.help_menu.visible:
                    self.renderer.handle_zoom(event.y)
            
            elif event.type == pygame.VIDEORESIZE:
                # Manejar redimensionamiento de ventana
                if not self.fullscreen:
                    self.window_width = event.w
                    self.window_height = event.h
                    self.screen = pygame.display.set_mode(
                        (self.window_width, self.window_height),
                        pygame.DOUBLEBUF | pygame.RESIZABLE
                    )
                    self.reinit_ui()
        
        # Manejar arrastre de ratón (solo si el menú no está visible)
        if not self.config_menu.visible and not self.help_menu.visible:
            mouse_buttons = pygame.mouse.get_pressed()
            # Botón derecho O botón central para pan
            if mouse_buttons[2] or mouse_buttons[1]:
                rel = pygame.mouse.get_rel()
                if rel != (0, 0):  # Solo si hay movimiento
                    self.renderer.handle_pan(rel)
    
    def handle_keydown(self, key):
        """Manejar teclas presionadas"""
        if key == pygame.K_SPACE:
            self.paused = not self.paused
        elif key == pygame.K_ESCAPE:
            if self.config_menu.visible:
                self.config_menu.hide()
            else:
                self.running = False
        elif key == pygame.K_m:
            self.config_menu.toggle()
        elif key == pygame.K_h:
            self.help_menu.toggle()
        elif key == pygame.K_f:
            # Toggle seguimiento de criatura
            if self.renderer.following_creature:
                self.renderer.stop_following()
                print("📷 Seguimiento desactivado")
            else:
                self.renderer.start_following()
                print("📷 Seguimiento activado")
        elif key == pygame.K_r:
            self.reset_simulation()
        elif key == pygame.K_s:
            self.save_simulation()
        elif key == pygame.K_l:
            self.load_simulation()
        elif key == pygame.K_F11:
            self.toggle_fullscreen()
        elif key == pygame.K_PLUS or key == pygame.K_EQUALS or key == pygame.K_KP_PLUS:
            self.world.speed_multiplier = min(10, self.world.speed_multiplier * 2)
            print(f"⚡ Velocidad: {self.world.speed_multiplier}x")
        elif key == pygame.K_MINUS or key == pygame.K_UNDERSCORE or key == pygame.K_KP_MINUS:
            self.world.speed_multiplier = max(0.5, self.world.speed_multiplier / 2)
            print(f"🐌 Velocidad: {self.world.speed_multiplier}x")
    
    def handle_mouse_click(self, pos, button):
        """Manejar clicks del ratón"""
        if button == 1:  # Click izquierdo
            # Calcular límite del mundo escalado
            scaled_world_width = int(config.WORLD_WIDTH * self.renderer.scale_factor)
            
            # Verificar si click en mundo o UI
            if pos[0] < scaled_world_width:
                world_pos = self.renderer.screen_to_world(pos)
                prev_selected = self.world.selected_creature
                self.world.select_creature_at(world_pos)
                # Iniciar seguimiento automático solo si seleccionamos una nueva criatura
                if self.world.selected_creature and self.world.selected_creature != prev_selected:
                    self.renderer.start_following()
                    print(f"📍 Criatura seleccionada: {self.world.selected_creature.id}")
    
    def update(self, dt):
        """Actualizar simulación"""
        if not self.paused:
            self.world.update(dt)
    
    def render(self):
        """Renderizar frame"""
        # Limpiar pantalla
        self.screen.fill(config.BACKGROUND_COLOR)
        
        # Renderizar mundo
        self.renderer.render()
        
        # Renderizar UI
        self.stats_panel.render()
        
        # Renderizar menú de configuración (si está visible)
        self.config_menu.render()
        
        # Renderizar menú de ayuda (si está visible)
        self.help_menu.render()
        
        # Mostrar FPS si está activado
        if config.DEBUG['SHOW_FPS']:
            self.render_fps()
        
        # Mostrar indicadores de controles (solo si no hay menús abiertos)
        if not self.config_menu.visible and not self.help_menu.visible:
            self.render_menu_hint()
        
        # Mostrar indicador de seguimiento
        if self.renderer.following_creature and self.world.selected_creature:
            self.render_following_indicator()
        
        # Actualizar pantalla
        pygame.display.flip()
    
    def render_fps(self):
        """Renderizar contador de FPS"""
        font = pygame.font.Font(None, 24)
        fps = self.clock.get_fps()
        fps_text = font.render(f"FPS: {fps:.1f}", True, (0, 255, 0))
        self.screen.blit(fps_text, (10, 10))
    
    def render_menu_hint(self):
        """Renderizar indicadores de controles"""
        font = pygame.font.Font(None, 16)
        hints = [
            "M: Menú Config",
            "H: Ayuda",
            "F: Seguir criatura",
            "N: Renombrar",
            "ESPACIO: Pausa",
            "+/-: Velocidad",
            "F11: Pantalla completa",
            "Click: Seleccionar",
            "Botón Der: Pan",
            "Rueda: Zoom"
        ]
        
        # Calcular posición según si estamos en pantalla completa
        if self.fullscreen:
            # En pantalla completa, usar altura real de pantalla
            screen_height = self.screen.get_height()
        else:
            # En modo ventana, usar altura del mundo
            screen_height = config.WORLD_HEIGHT
        
        y_offset = screen_height - 25 - (len(hints) * 18)
        
        # Fondo semi-transparente
        bg_surface = pygame.Surface((200, len(hints) * 18 + 10))
        bg_surface.set_alpha(200)
        bg_surface.fill((20, 20, 30))
        self.screen.blit(bg_surface, (5, y_offset - 5))
        
        for hint in hints:
            hint_text = font.render(hint, True, (180, 180, 180))
            self.screen.blit(hint_text, (10, y_offset))
            y_offset += 18
    
    def render_following_indicator(self):
        """Renderizar indicador de seguimiento activo"""
        font = pygame.font.Font(None, 20)
        creature = self.world.selected_creature
        
        if hasattr(creature, 'custom_name') and creature.custom_name:
            text = f"Siguiendo: {creature.custom_name}"
        else:
            text = f"Siguiendo: C-{creature.id}"
        
        indicator = font.render(text, True, (255, 255, 100))
        
        # Calcular centro según si estamos en pantalla completa
        if self.fullscreen:
            # En pantalla completa, centrar en el mundo escalado
            scaled_world_width = int(config.WORLD_WIDTH * self.renderer.scale_factor)
            center_x = scaled_world_width // 2
        else:
            # En modo ventana, centrar en el mundo normal
            center_x = config.WORLD_WIDTH // 2
        
        # Fondo
        bg_rect = indicator.get_rect(center=(center_x, 30))
        bg_rect.inflate_ip(20, 10)
        
        # Dibujar fondo directamente
        pygame.draw.rect(self.screen, (40, 40, 50), bg_rect, border_radius=5)
        
        # Borde
        pygame.draw.rect(self.screen, (255, 255, 100), bg_rect, 2, border_radius=5)
        
        # Texto
        text_rect = indicator.get_rect(center=(center_x, 30))
        self.screen.blit(indicator, text_rect)
    
    def reset_simulation(self):
        """Reiniciar simulación"""
        print("Reiniciando simulación...")
        self.world.reset()
        self.world.populate(config.INITIAL_POPULATION)
    
    def save_simulation(self, filename=None):
        """Guardar estado de la simulación"""
        if filename is None:
            from datetime import datetime
            filename = f"digilife_save_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl"
        
        try:
            self.world.save(filename)
            print(f"✅ Simulación guardada: {filename}")
        except Exception as e:
            print(f"❌ Error al guardar: {e}")
    
    def load_simulation(self, filename=None):
        """Cargar simulación guardada"""
        if filename is None:
            # TODO: Mostrar diálogo de selección de archivo
            print("⚠️  Especifica un archivo con --load")
            return
        
        try:
            self.world.load(filename)
            print(f"✅ Simulación cargada: {filename}")
        except Exception as e:
            print(f"❌ Error al cargar: {e}")
    
    def run(self):
        """Loop principal"""
        self.running = True
        
        print("\n" + "=" * 60)
        print("DigiLife ejecutándose")
        print("=" * 60)
        print("Controles:")
        print("  ESPACIO - Play/Pause")
        print("  M       - Menú de configuración")
        print("  H       - Menú de ayuda")
        print("  F       - Seguir criatura seleccionada")
        print("  N       - Renombrar criatura")
        print("  R       - Reiniciar")
        print("  S       - Guardar")
        print("  ESC     - Salir")
        print("  +/-     - Velocidad")
        print("  F11     - Pantalla completa")
        print("=" * 60 + "\n")
        
        while self.running:
            # Delta time
            dt = self.clock.tick(config.TARGET_FPS) / 1000.0
            
            # Eventos
            self.handle_events()
            
            # Actualizar
            self.update(dt)
            
            # Renderizar
            self.render()
        
        self.cleanup()
    
    def toggle_fullscreen(self):
        """Alternar pantalla completa"""
        self.fullscreen = not self.fullscreen
        
        if self.fullscreen:
            # Cambiar a pantalla completa manteniendo dimensiones
            self.screen = pygame.display.set_mode(
                (0, 0),  # Pygame usa resolución nativa
                pygame.DOUBLEBUF | pygame.FULLSCREEN
            )
            print(f"🖥️  Pantalla completa: {self.screen.get_width()}x{self.screen.get_height()}")
        else:
            # Volver a ventana normal
            self.screen = pygame.display.set_mode(
                (self.window_width, self.window_height),
                pygame.DOUBLEBUF | pygame.RESIZABLE
            )
            print(f"🪟 Modo ventana: {self.window_width}x{self.window_height}")
        
        # Reinicializar componentes UI con nueva pantalla
        self.reinit_ui()
    
    def reinit_ui(self):
        """Reinicializar componentes de UI después de cambio de pantalla"""
        # Actualizar referencias de pantalla en todos los componentes
        self.renderer.screen = self.screen
        self.stats_panel.screen = self.screen
        self.config_menu.screen = self.screen
        self.help_menu.screen = self.screen
        
        if self.fullscreen:
            # Calcular factor de escala para el mundo
            available_width = self.screen.get_width() - config.UI_PANEL_WIDTH
            available_height = self.screen.get_height()
            
            scale_x = available_width / config.WORLD_WIDTH
            scale_y = available_height / config.WORLD_HEIGHT
            
            # Usar el menor factor para mantener proporciones
            self.renderer.scale_factor = min(scale_x, scale_y)
            
            # Calcular tamaño escalado del mundo
            scaled_world_width = int(config.WORLD_WIDTH * self.renderer.scale_factor)
            scaled_world_height = int(config.WORLD_HEIGHT * self.renderer.scale_factor)
            
            # Posicionar panel de estadísticas después del mundo escalado
            self.stats_panel.x = scaled_world_width
            self.stats_panel.width = self.screen.get_width() - scaled_world_width
            self.stats_panel.height = self.screen.get_height()
            
            print(f"📐 Escala: {self.renderer.scale_factor:.2f}x - Mundo: {scaled_world_width}x{scaled_world_height}")
        else:
            # En modo ventana, sin escala
            self.renderer.scale_factor = 1.0
            self.stats_panel.x = config.WORLD_WIDTH
            self.stats_panel.width = config.UI_PANEL_WIDTH
            self.stats_panel.height = config.WORLD_HEIGHT
        
        # Reposicionar menús centrados
        self.config_menu.x = (self.screen.get_width() - self.config_menu.width) // 2
        self.config_menu.y = (self.screen.get_height() - self.config_menu.height) // 2
        
        self.help_menu.x = (self.screen.get_width() - self.help_menu.width) // 2
        self.help_menu.y = (self.screen.get_height() - self.help_menu.height) // 2
        
        # Recrear sliders con nuevas posiciones
        self.config_menu.sliders.clear()
        self.config_menu.create_sliders()
        
        # Recrear botones con nuevas posiciones
        self.config_menu.create_buttons()
    
    def cleanup(self):
        """Limpieza al salir"""
        print("\nCerrando DigiLife...")
        pygame.quit()
        sys.exit(0)


def parse_arguments():
    """Parsear argumentos de línea de comandos"""
    parser = argparse.ArgumentParser(
        description='DigiLife - Simulador de Vida Artificial'
    )
    
    parser.add_argument(
        '--population', type=int,
        help='Población inicial (default: 10)'
    )
    parser.add_argument(
        '--data-rate', type=int,
        help='Tasa de generación de datos/seg (default: 2)'
    )
    parser.add_argument(
        '--world-size', type=str,
        help='Tamaño del mundo WxH (default: 800x600)'
    )
    parser.add_argument(
        '--no-gpu', action='store_true',
        help='Desactivar aceleración GPU'
    )
    parser.add_argument(
        '--no-audio', action='store_true',
        help='Desactivar vocalizaciones'
    )
    parser.add_argument(
        '--debug', action='store_true',
        help='Modo debug con logs detallados'
    )
    parser.add_argument(
        '--fullscreen', action='store_true',
        help='Iniciar en pantalla completa'
    )
    parser.add_argument(
        '--fps', type=int,
        help='FPS objetivo (default: 60)'
    )
    parser.add_argument(
        '--load', type=str,
        help='Cargar simulación guardada'
    )
    
    return parser.parse_args()


def main():
    """Función principal"""
    args = parse_arguments()
    
    try:
        app = DigiLife(args)
        app.run()
    except KeyboardInterrupt:
        print("\n\nInterrumpido por usuario")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
