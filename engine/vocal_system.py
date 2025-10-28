"""
Sistema de vocalización - Comunicación emergente con beeps
"""

import random
import sys
from typing import Dict, Optional
import config

# Intentar importar winsound (Windows) o usar beep del sistema (Linux/Mac)
BEEP_AVAILABLE = True
try:
    if sys.platform == 'win32':
        import winsound
        BEEP_METHOD = 'winsound'
    else:
        # Linux/Mac usan el beep del sistema
        BEEP_METHOD = 'system'
except ImportError:
    BEEP_AVAILABLE = False
    BEEP_METHOD = None


def play_beep(frequency: int, duration: int):
    """Reproducir beep del sistema con volumen máximo"""
    if not config.AUDIO_ENABLED:
        return
    
    try:
        if sys.platform == 'win32':
            # Windows: usar winsound (volumen controlado por sistema)
            import winsound
            winsound.Beep(frequency, duration)
        else:
            # Linux/Mac: intentar varios métodos
            import os
            import subprocess
            
            # Método 1: beep command (si está instalado)
            # -f: frecuencia en Hz, -l: duración en ms
            # Redirigir stderr para evitar mensajes de error
            try:
                subprocess.run(
                    ['beep', '-f', str(frequency), '-l', str(duration)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=1
                )
            except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
                # Método 2: usar printf con el bell character (más universal)
                # Esto hace un beep simple del sistema
                os.system('printf "\\a" 2>/dev/null')
                
    except Exception as e:
        # Silenciar errores de audio
        pass


class VocalSystem:
    """Sistema de vocalización de una criatura"""
    
    def __init__(self, creature):
        self.creature = creature
        self.vocabulary: Dict[str, int] = {}  # palabra -> veces usada
        self.associations: Dict[str, int] = {}  # palabra -> veces asociada con contexto
        
        # Características vocales únicas (frecuencias de beep)
        # Cada criatura tiene su propia "voz" basada en frecuencia
        self.base_frequency = random.randint(400, 1200)  # Hz
        self.frequency_variation = random.randint(50, 200)  # Variación por palabra
        
        # Si la criatura es suficientemente compleja, darle algunas palabras básicas ya aprendidas
        if creature.complexity >= config.COMPLEXITY_THRESHOLD_VOCAL:
            basic_words = ['hola', 'bien', 'datos']
            for word in basic_words:
                # Darles suficientes asociaciones para que ya las conozcan
                self.associations[word] = config.ASSOCIATION_THRESHOLD
    
    def vocalize(self):
        """Emitir vocalización según contexto (OPTIMIZADO v2.9)"""
        if not config.AUDIO_ENABLED:
            return
        
        # Solo vocalizar si hay suficiente complejidad
        if self.creature.complexity < config.COMPLEXITY_THRESHOLD_VOCAL:
            return
        
        # Determinar qué decir según contexto (sin audio real, solo log)
        word = self.choose_word()
        
        if word:
            self.speak(word)
            
            # Registrar uso
            if word not in self.vocabulary:
                self.vocabulary[word] = 0
            self.vocabulary[word] += 1
            
            if config.DEBUG['LOG_VOCALIZATIONS']:
                print(f"🗣️  Criatura {self.creature.id} dice: '{word}'")
    
    def choose_word(self) -> Optional[str]:
        """Elegir palabra apropiada según contexto"""
        # Evaluar contextos
        for word, context_func in config.VOCABULARY_CONTEXTS.items():
            try:
                if context_func(self.creature):
                    # Verificar si ha aprendido esta palabra
                    if self.has_learned(word):
                        return word
                    else:
                        # Intentar aprender
                        self.try_learn(word)
            except:
                pass
        
        # Si no hay palabra apropiada según contexto, elegir una palabra aprendida al azar
        learned_words = [w for w, count in self.associations.items() 
                        if count >= config.ASSOCIATION_THRESHOLD]
        
        if learned_words:
            return random.choice(learned_words)
        
        # Si aún no ha aprendido ninguna palabra, intentar aprender una básica
        if self.creature.complexity >= 600:
            basic_words = ['hola', 'bien', 'datos']
            word = random.choice(basic_words)
            self.try_learn(word)
            # Dar un boost inicial para que aprenda más rápido
            if word in self.associations:
                self.associations[word] = min(config.ASSOCIATION_THRESHOLD, 
                                             self.associations[word] + 2)
            return word
        
        return None
    
    def has_learned(self, word: str) -> bool:
        """Verificar si ha aprendido una palabra"""
        if word not in self.associations:
            return False
        return self.associations[word] >= config.ASSOCIATION_THRESHOLD
    
    def try_learn(self, word: str):
        """Intentar aprender una palabra por asociación"""
        if word not in self.associations:
            self.associations[word] = 0
        self.associations[word] += 1
    
    def speak(self, word: str):
        """Emitir beep característico de la criatura"""
        if not config.AUDIO_ENABLED:
            return
        
        # Cada palabra tiene una secuencia de beeps única
        # Basada en el hash de la palabra + características de la criatura
        word_hash = hash(word) % 5  # 0-4 patrones diferentes
        
        # Patrones de beeps según la palabra
        patterns = [
            [(0, 100)],                    # Beep corto
            [(0, 150), (50, 100)],        # Dos beeps
            [(0, 80), (30, 80), (30, 80)], # Tres beeps rápidos
            [(0, 200)],                    # Beep largo
            [(0, 100), (100, 150)]        # Beep corto + largo
        ]
        
        pattern = patterns[word_hash]
        
        # Reproducir secuencia de beeps
        for delay, duration in pattern:
            if delay > 0:
                # Pequeña pausa entre beeps (no bloqueante)
                pass
            
            # Frecuencia única de esta criatura + variación por palabra
            frequency = self.base_frequency + (word_hash * self.frequency_variation)
            frequency = max(200, min(2000, frequency))  # Limitar rango audible
            
            # Duración ajustada por complejidad (criaturas más complejas = beeps más elaborados)
            adjusted_duration = int(duration * (1 + self.creature.complexity / 2000))
            adjusted_duration = max(50, min(300, adjusted_duration))
            
            # Reproducir beep
            play_beep(frequency, adjusted_duration)
    
    def get_vocabulary_size(self) -> int:
        """Obtener tamaño del vocabulario aprendido"""
        return len([w for w, count in self.associations.items() 
                   if count >= config.ASSOCIATION_THRESHOLD])
