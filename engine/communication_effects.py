"""
Sistema de efectos de comunicación avanzada
Las palabras tienen efectos reales en el comportamiento
"""

import random
import math
import config


class CommunicationEffects:
    """Efectos de la comunicación avanzada entre criaturas"""
    
    @staticmethod
    def apply_word_effect(speaker, listeners, word):
        """Aplicar efecto de una palabra a las criaturas que la escuchan"""
        
        # === VOCABULARIO BÁSICO ===
        if word == 'hambre':
            # Efecto: Criaturas cercanas comparten ubicación de comida
            CommunicationEffects._effect_hunger(speaker, listeners)
        
        elif word == 'datos':
            # Efecto: Criaturas cercanas se mueven hacia la comida que ve el hablante
            CommunicationEffects._effect_food_location(speaker, listeners)
        
        elif word == 'ayuda':
            # Efecto: Criaturas cercanas se acercan para ayudar
            CommunicationEffects._effect_help(speaker, listeners)
        
        elif word == 'hola':
            # Efecto: Criaturas cercanas responden con pequeño bonus social
            CommunicationEffects._effect_greeting(speaker, listeners)
        
        elif word == 'peligro':
            # Efecto: Criaturas cercanas aumentan alerta y se alejan ligeramente
            CommunicationEffects._effect_danger(speaker, listeners)
        
        elif word == 'bien':
            # Efecto: Criaturas cercanas se relajan (reducen estrés)
            CommunicationEffects._effect_good(speaker, listeners)
        
        elif word == 'malo':
            # Efecto: Criaturas cercanas aumentan precaución
            CommunicationEffects._effect_bad(speaker, listeners)
        
        # === VOCABULARIO AVANZADO ===
        elif word == 'cohesion':
            # Efecto: Criaturas cercanas se mueven hacia el hablante (cohesión de grupo)
            CommunicationEffects._effect_cohesion(speaker, listeners)
        
        elif word == 'reproducir':
            # Efecto: Estimula reproducción en criaturas cercanas con energía suficiente
            CommunicationEffects._effect_reproduce(speaker, listeners)
        
        elif word == 'defender':
            # Efecto: Criaturas cercanas aumentan fitness temporalmente (modo defensa)
            CommunicationEffects._effect_defend(speaker, listeners)
        
        elif word == 'peligro_aqui':
            # Efecto: Criaturas cercanas huyen de la ubicación del hablante
            CommunicationEffects._effect_danger_here(speaker, listeners)
        
        elif word == 'seguir':
            # Efecto: Criaturas cercanas siguen al hablante
            CommunicationEffects._effect_follow(speaker, listeners)
        
        elif word == 'explorar':
            # Efecto: Criaturas cercanas se dispersan para explorar
            CommunicationEffects._effect_explore(speaker, listeners)
        
        elif word == 'descansar':
            # Efecto: Criaturas cercanas reducen movimiento (conservar energía)
            CommunicationEffects._effect_rest(speaker, listeners)
        
        elif word == 'atacar':
            # Efecto: Criaturas depredadoras coordinan ataque
            CommunicationEffects._effect_attack(speaker, listeners)
        
        elif word == 'huir':
            # Efecto: Criaturas cercanas huyen en dirección opuesta a amenazas
            CommunicationEffects._effect_flee(speaker, listeners)
        
        elif word == 'compartir':
            # Efecto: Hablante comparte energía con criaturas débiles cercanas
            CommunicationEffects._effect_share(speaker, listeners)
    
    # === EFECTOS DE VOCABULARIO BÁSICO ===
    
    @staticmethod
    def _effect_hunger(speaker, listeners):
        """Hambre: Criaturas cercanas comparten ubicación de comida (OPTIMIZADO)"""
        # OPTIMIZACIÓN: Solo procesar primeras 5 criaturas
        for creature in listeners[:5]:
            if creature == speaker:
                continue
            
            # OPTIMIZACIÓN: Solo bonus de fitness, sin búsqueda de comida
            creature.fitness += 0.3
        
        speaker.fitness += 0.5
    
    @staticmethod
    def _effect_food_location(speaker, listeners):
        """Datos: Criaturas se mueven hacia la comida que ve el hablante (OPTIMIZADO)"""
        # OPTIMIZACIÓN: Cachear búsqueda de comida una sola vez
        nearby_food = speaker.world.get_data_near(speaker.x, speaker.y, 80)  # Radio reducido
        if not nearby_food:
            # Si no hay comida, solo dar bonus de fitness
            speaker.fitness += 0.5
            return
        
        food = nearby_food[0]  # Comida más cercana al hablante
        
        # OPTIMIZACIÓN: Solo procesar primeras 5 criaturas hambrientas
        processed = 0
        for creature in listeners:
            if creature == speaker or processed >= 5:
                continue
            
            # Criaturas hambrientas responden más
            if creature.energy < creature.max_energy * 0.5:
                dx = food['x'] - creature.x
                dy = food['y'] - creature.y
                distance = math.sqrt(dx**2 + dy**2)
                
                if distance > 0 and distance < 150:  # Radio reducido
                    force = 0.2  # Fuerza reducida
                    creature.vx += (dx / distance) * force
                    creature.vy += (dy / distance) * force
                    creature.fitness += 0.3
                    processed += 1
        
        speaker.fitness += 1
        
        if processed > 0 and config.DEBUG.get('LOG_VOCALIZATIONS', False):
            print(f"🍽️  Criatura {speaker.id} señaló comida - {processed} criaturas responden")
    
    @staticmethod
    def _effect_help(speaker, listeners):
        """Ayuda: Criaturas cercanas se acercan para ayudar"""
        helped = 0
        for creature in listeners:
            if creature == speaker:
                continue
            
            # Solo criaturas con energía suficiente pueden ayudar
            if creature.energy > creature.max_energy * 0.4:
                # Moverse hacia el que pide ayuda
                dx = speaker.x - creature.x
                dy = speaker.y - creature.y
                distance = math.sqrt(dx**2 + dy**2)
                
                if distance > 0 and distance < 150:
                    force = 0.3
                    creature.vx += (dx / distance) * force
                    creature.vy += (dy / distance) * force
                    
                    # Transferir pequeña cantidad de energía
                    if distance < 30:
                        transfer = min(5, creature.energy * 0.05)
                        creature.energy -= transfer
                        speaker.energy += transfer
                        creature.fitness += 1
                        helped += 1
        
        if helped > 0:
            speaker.fitness += 2
            if config.DEBUG.get('LOG_VOCALIZATIONS', False):
                print(f"🆘 Criatura {speaker.id} pidió ayuda - {helped} criaturas respondieron")
    
    @staticmethod
    def _effect_greeting(speaker, listeners):
        """Hola: Bonus social por saludo"""
        for creature in listeners:
            if creature == speaker:
                continue
            
            # Pequeño bonus de fitness por interacción social
            creature.fitness += 0.2
            speaker.fitness += 0.2
            
            # Si son similares genéticamente, bonus extra
            if hasattr(speaker, 'calculate_genetic_similarity'):
                similarity = speaker.calculate_genetic_similarity(creature)
                if similarity > 0.7:
                    creature.fitness += 0.3
                    speaker.fitness += 0.3
    
    @staticmethod
    def _effect_danger(speaker, listeners):
        """Peligro: Criaturas aumentan alerta y se alejan"""
        for creature in listeners:
            if creature == speaker:
                continue
            
            # Alejarse ligeramente del hablante (zona de peligro)
            dx = creature.x - speaker.x
            dy = creature.y - speaker.y
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance > 0 and distance < 100:
                force = 0.2
                creature.vx += (dx / distance) * force
                creature.vy += (dy / distance) * force
                creature.fitness += 0.3  # Bonus por reaccionar a alerta
        
        speaker.fitness += 1
        
        if config.DEBUG.get('LOG_VOCALIZATIONS', False):
            print(f"⚡ Criatura {speaker.id} alertó peligro - {len(listeners)-1} criaturas en alerta")
    
    @staticmethod
    def _effect_good(speaker, listeners):
        """Bien: Criaturas se relajan (reducen estrés)"""
        for creature in listeners:
            if creature == speaker:
                continue
            
            # Reducir velocidad ligeramente (relajación)
            creature.vx *= 0.9
            creature.vy *= 0.9
            
            # Pequeño bonus de energía (estado positivo)
            creature.energy += 0.5
            creature.fitness += 0.2
        
        speaker.fitness += 0.5
    
    @staticmethod
    def _effect_bad(speaker, listeners):
        """Malo: Criaturas aumentan precaución"""
        for creature in listeners:
            if creature == speaker:
                continue
            
            # Aumentar alerta (pequeño boost de velocidad)
            if creature.energy > creature.max_energy * 0.3:
                creature.vx *= 1.1
                creature.vy *= 1.1
                creature.fitness += 0.2
        
        speaker.fitness += 0.3
    
    # === EFECTOS DE VOCABULARIO AVANZADO ===
    
    @staticmethod
    def _effect_cohesion(speaker, listeners):
        """Cohesión: Criaturas se mueven hacia el hablante (OPTIMIZADO)"""
        # OPTIMIZACIÓN: Solo procesar primeras 8 criaturas
        processed = 0
        for creature in listeners:
            if creature == speaker or processed >= 8:
                continue
            
            # Calcular dirección hacia el hablante
            dx = speaker.x - creature.x
            dy = speaker.y - creature.y
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance > 0 and distance < 120:  # Radio reducido
                # Aplicar fuerza de atracción
                force = 0.25  # Fuerza reducida
                creature.vx += (dx / distance) * force
                creature.vy += (dy / distance) * force
                
                # Bonus de fitness por cohesión
                creature.fitness += 0.4
                processed += 1
        
        speaker.fitness += 2
        
        if processed > 0 and config.DEBUG.get('LOG_VOCALIZATIONS', False):
            print(f"🤝 Criatura {speaker.id} llamó a cohesión - {processed} criaturas responden")
    
    @staticmethod
    def _effect_reproduce(speaker, listeners):
        """Reproducir: Estimula reproducción en grupo"""
        reproduced = 0
        for creature in listeners:
            if creature == speaker:
                continue
            
            if creature.can_reproduce() and random.random() < 0.3:  # 30% de reproducirse
                creature.reproduce()
                reproduced += 1
        
        if reproduced > 0 and config.DEBUG.get('LOG_VOCALIZATIONS', False):
            print(f"👶 Criatura {speaker.id} estimuló reproducción - {reproduced} criaturas se reprodujeron")
    
    @staticmethod
    def _effect_defend(speaker, listeners):
        """Defender: Modo defensa aumenta fitness temporalmente"""
        for creature in listeners:
            if creature == speaker:
                continue
            
            # Bonus temporal de fitness (modo defensa)
            creature.fitness += 5
            creature.energy += 3  # Adrenalina
        
        speaker.fitness += 3
        
        if config.DEBUG.get('LOG_VOCALIZATIONS', False):
            print(f"🛡️  Criatura {speaker.id} activó defensa - {len(listeners)-1} criaturas")
    
    @staticmethod
    def _effect_danger_here(speaker, listeners):
        """Peligro aquí: Criaturas huyen de esta ubicación"""
        for creature in listeners:
            if creature == speaker:
                continue
            
            # Calcular dirección opuesta al hablante
            dx = creature.x - speaker.x
            dy = creature.y - speaker.y
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance > 0 and distance < 100:
                # Aplicar fuerza de repulsión (huir)
                force = 0.5
                creature.vx += (dx / distance) * force
                creature.vy += (dy / distance) * force
        
        if config.DEBUG.get('LOG_VOCALIZATIONS', False) and random.random() < 0.1:
            print(f"⚠️  Criatura {speaker.id} alertó peligro - {len(listeners)-1} criaturas huyen")
    
    @staticmethod
    def _effect_follow(speaker, listeners):
        """Seguir: Criaturas siguen al líder"""
        for creature in listeners:
            if creature == speaker:
                continue
            
            # Solo criaturas con menos fitness siguen al líder
            if creature.fitness < speaker.fitness:
                # Calcular dirección hacia el líder
                dx = speaker.x - creature.x
                dy = speaker.y - creature.y
                distance = math.sqrt(dx**2 + dy**2)
                
                if distance > 30 and distance < 200:  # Mantener distancia
                    force = 0.2
                    creature.vx += (dx / distance) * force
                    creature.vy += (dy / distance) * force
                    creature.fitness += 0.3
        
        speaker.fitness += 3  # Bonus por liderazgo
        
        if config.DEBUG.get('LOG_VOCALIZATIONS', False):
            print(f"👑 Criatura {speaker.id} lidera grupo")
    
    @staticmethod
    def _effect_explore(speaker, listeners):
        """Explorar: Criaturas se dispersan"""
        for creature in listeners:
            if creature == speaker:
                continue
            
            # Aplicar velocidad aleatoria para dispersión
            if random.random() < 0.5:
                angle = random.uniform(0, 2 * math.pi)
                force = 0.4
                creature.vx += math.cos(angle) * force
                creature.vy += math.sin(angle) * force
                creature.fitness += 0.5
        
        if config.DEBUG.get('LOG_VOCALIZATIONS', False):
            print(f"🔍 Criatura {speaker.id} inició exploración")
    
    @staticmethod
    def _effect_rest(speaker, listeners):
        """Descansar: Reducir movimiento para conservar energía"""
        for creature in listeners:
            if creature == speaker:
                continue
            
            # Reducir velocidad
            creature.vx *= 0.5
            creature.vy *= 0.5
            
            # Pequeño bonus de energía por descansar
            creature.energy += 1
        
        if config.DEBUG.get('LOG_VOCALIZATIONS', False):
            print(f"😴 Criatura {speaker.id} llamó a descansar")
    
    @staticmethod
    def _effect_attack(speaker, listeners):
        """Atacar: Coordinar ataque entre depredadores (OPTIMIZADO)"""
        if not config.PREDATION_ENABLED:
            return
        
        # OPTIMIZACIÓN: Filtrar depredadores de listeners (ya limitados)
        predators = [c for c in listeners[:5] if hasattr(c, 'is_predator') and c.is_predator]
        
        if len(predators) >= 2:
            # OPTIMIZACIÓN: Buscar solo en listeners, no hacer búsqueda adicional
            for prey in listeners[:8]:  # Solo primeras 8
                if prey not in predators and prey != speaker:
                    # Coordinar ataque (máximo 2 atacantes para reducir carga)
                    for predator in predators[:2]:
                        if predator.fitness > prey.fitness * 1.2:
                            # Mover hacia la presa
                            dx = prey.x - predator.x
                            dy = prey.y - predator.y
                            distance = math.sqrt(dx**2 + dy**2)
                            
                            if distance > 0:
                                force = 0.3  # Fuerza reducida
                                predator.vx += (dx / distance) * force
                                predator.vy += (dy / distance) * force
                    
                    if config.DEBUG.get('LOG_VOCALIZATIONS', False):
                        print(f"🎯 Criatura {speaker.id} coordinó ataque contra #{prey.id}")
                    break
    
    @staticmethod
    def _effect_flee(speaker, listeners):
        """Huir: Grupo huye de amenazas (OPTIMIZADO)"""
        # OPTIMIZACIÓN: Buscar amenazas solo en listeners
        threats = [c for c in listeners[:5] if hasattr(c, 'is_predator') and c.is_predator]
        
        if threats:
            threat = threats[0]
            
            for creature in listeners:
                if creature == speaker or creature in threats:
                    continue
                
                # Huir de la amenaza
                dx = creature.x - threat.x
                dy = creature.y - threat.y
                distance = math.sqrt(dx**2 + dy**2)
                
                if distance > 0 and distance < 150:
                    force = 0.6
                    creature.vx += (dx / distance) * force
                    creature.vy += (dy / distance) * force
            
            if config.DEBUG.get('LOG_VOCALIZATIONS', False):
                print(f"🏃 Criatura {speaker.id} ordenó huida")
    
    @staticmethod
    def _effect_share(speaker, listeners):
        """Compartir: Transferir energía a criaturas débiles"""
        if speaker.energy < speaker.max_energy * 0.5:
            return  # No compartir si está débil
        
        shared = 0
        for creature in listeners:
            if creature == speaker:
                continue
            
            # Compartir con criaturas débiles
            if creature.energy < creature.max_energy * 0.3:
                transfer = min(10, speaker.energy * 0.1)
                speaker.energy -= transfer
                creature.energy += transfer
                creature.fitness += 2
                shared += 1
        
        if shared > 0:
            speaker.fitness += shared * 3  # Bonus por altruismo
            
            if config.DEBUG.get('LOG_VOCALIZATIONS', False):
                print(f"💝 Criatura {speaker.id} compartió energía con {shared} criaturas débiles")
