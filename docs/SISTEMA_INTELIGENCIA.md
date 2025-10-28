# 🧠 Sistema de Inteligencia Avanzada - DigiLife v2.9.3

## Descripción General

Las criaturas que alcanzan **complejidad 1500+** desarrollan **inteligencia avanzada**, permitiéndoles:
- Analizar el entorno y descubrir patrones
- Aprender estrategias de criaturas exitosas
- Compartir conocimiento con otras criaturas inteligentes
- Desarrollar "sabiduría" basada en experiencia acumulada

## Características del Sistema

### 1. Base de Conocimiento Global

El mundo mantiene una base de conocimiento compartida con tres categorías:

#### **Conocimiento de Supervivencia**
- Conservar energía cuando está baja
- Buscar alimento activamente
- Evitar depredadores
- Reproducirse con energía alta
- Explorar bordes vs permanecer en centro
- Seguir grupos
- Huir de amenazas

#### **Conocimiento Social**
- Colaborar con criaturas similares
- Comunicar peligro
- Compartir ubicación de alimento
- Formar grupos de protección
- Defender territorio
- Ayudar a criaturas débiles

#### **Conocimiento Estratégico**
- Patrullar zonas específicas
- Emboscar presas
- Cazar de forma coordinada
- Migrar hacia recursos
- Adaptarse a cambios del entorno
- Optimizar movimiento

### 2. Análisis del Entorno

El sistema analiza constantemente:

- **Zonas de comida**: Dónde aparece más alimento (centro, norte, sur, este, oeste)
- **Zonas peligrosas**: Ubicación de depredadores activos
- **Estrategias exitosas**: Comportamientos de las criaturas con mayor fitness

### 3. Aprendizaje Individual

Cada criatura inteligente puede:

#### **Descubrir Conocimiento**
- Probabilidad: 1% por frame
- Aprende de la base de conocimiento global
- Cada descubrimiento aumenta su sabiduría

#### **Analizar Situación Actual**
- Registra observaciones (energía, criaturas cercanas, comida)
- Detecta patrones en sus propias experiencias
- Genera insights personalizados

#### **Aprender de Exitosos**
- Probabilidad: 0.5% por frame
- Observa criaturas con alto fitness
- Adopta estrategias que funcionan

### 4. Compartir Conocimiento

Durante la **comunicación** entre criaturas inteligentes:
- Probabilidad: 20% de compartir conocimiento
- Transmite conocimientos que la otra no tiene
- Ambas criaturas aumentan su sabiduría

## Activación del Sistema

### Requisitos
- **Complejidad mínima**: 1500
- Se activa automáticamente al alcanzar el umbral
- Mensaje en consola: `🧠 Criatura X alcanzó inteligencia avanzada`

### Indicadores Visuales
En el panel de estadísticas (cuando se selecciona una criatura inteligente):

```
INTELIGENCIA AVANZADA
Sabiduría: 15
Conocimientos: 8
Descubrimientos recientes:
  • Descubrió: conservar energia baja
  • Descubrió: colaborar similares
  • energia_critica_frecuente
```

## Logs del Sistema

Con `LOG_INTELLIGENCE: True` en config.py, verás:

```
🧠 Criatura 7632 alcanzó inteligencia avanzada (comp: 1523.4)
🧠 Criatura 7632 Descubrió: buscar_alimento_activo (sabiduría: 1)
🎓 Criatura 7632 aprendió de criaturas exitosas
📚 Criatura 7632 compartió 3 conocimientos con Criatura 7499
```

## Impacto en la Simulación

### Ventajas de Criaturas Inteligentes
1. **Mayor adaptabilidad**: Aprenden de errores y éxitos
2. **Cooperación mejorada**: Comparten conocimiento útil
3. **Estrategias avanzadas**: Desarrollan tácticas complejas
4. **Evolución cultural**: Conocimiento se transmite sin genes

### Emergencia de Comportamientos
- **Grupos de aprendizaje**: Criaturas inteligentes se agrupan
- **Transmisión cultural**: Conocimiento pasa de generación en generación
- **Especialización**: Diferentes criaturas aprenden diferentes estrategias
- **Innovación**: Descubren nuevas formas de sobrevivir

## Configuración

### En config.py

```python
DEBUG = {
    'LOG_INTELLIGENCE': True,  # Activar logs de inteligencia
    # ... otros flags
}
```

### Ajustar Umbral de Inteligencia

Para cambiar cuándo se activa la inteligencia, modifica en el código:

```python
# En engine/creature.py
if self.complexity >= 1500:  # Cambiar este valor
    self.intelligence = CreatureIntelligence(self, self.world.knowledge_base)
```

## Estadísticas de Inteligencia

### Por Criatura
- **Sabiduría**: Número total de descubrimientos
- **Conocimientos**: Cantidad de conocimientos aprendidos
- **Insights**: Descubrimientos personalizados
- **Observaciones**: Memoria de experiencias (últimas 50)

### Global
- **Patrones descubiertos**: Conocimiento colectivo del mundo
- **Zonas de recursos**: Mapeo de áreas importantes
- **Estrategias exitosas**: Comportamientos que funcionan

## Futuras Mejoras

### v3.0 Planeado
- [ ] Memoria a largo plazo (recordar eventos importantes)
- [ ] Enseñanza activa (criaturas maestras)
- [ ] Innovación (crear nuevo conocimiento)
- [ ] Cultura de especies (conocimiento por especie)
- [ ] Lenguaje complejo (combinar palabras)
- [ ] Herramientas conceptuales (usar el entorno)

## Notas Técnicas

### Rendimiento
- Análisis limitado a 1% por frame
- Solo criaturas 1500+ complejidad
- Compartir conocimiento solo durante comunicación
- Impacto mínimo en FPS

### Persistencia
- Conocimiento se pierde al morir
- Pero puede transmitirse antes de morir
- Base de conocimiento global persiste
- Patrones descubiertos se acumulan

---

**¡Las criaturas ahora pueden aprender y evolucionar culturalmente!** 🧬🧠✨
