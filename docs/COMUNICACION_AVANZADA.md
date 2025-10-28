# 🗣️ Sistema de Comunicación Avanzada - DigiLife v2.9.3

## Descripción General

Las criaturas inteligentes (complejidad 1500+) tienen acceso a un **vocabulario avanzado** con palabras que producen **efectos reales** en el comportamiento de las criaturas que las escuchan.

## Vocabulario Básico (500+ complejidad)

Todas las criaturas vocales pueden usar estas palabras con **efectos reales**:

### 1. **hambre** 🍽️
**Contexto:** Energía < 40%

**Efecto:**
- Criaturas cercanas que ven comida reciben +0.3 fitness
- Pequeño impulso hacia comida conocida (fuerza 0.1)
- +0.5 fitness para el hablante

**Uso:** Coordinar búsqueda de alimento

---

### 2. **datos** 🍽️
**Contexto:** Ve comida cerca y necesita energía

**Efecto:**
- Criaturas hambrientas (< 50% energía) se mueven hacia la comida
- Fuerza de atracción 0.25
- +0.5 fitness por criatura que responde
- +1 fitness para el hablante

**Uso:** Compartir ubicación de recursos

---

### 3. **ayuda** 🆘
**Contexto:** Energía < 20%

**Efecto:**
- Criaturas con energía > 40% se acercan (fuerza 0.3)
- Transferencia de energía si están cerca (< 30px): 5 energía o 5%
- +1 fitness por ayudante
- +2 fitness para el hablante

**Uso:** Solicitar asistencia en emergencia

---

### 4. **hola** 👋
**Contexto:** Ve criaturas cerca y está bien

**Efecto:**
- +0.2 fitness mutuo por interacción social
- Bonus extra (+0.3) si similitud genética > 70%
- Fortalece lazos sociales

**Uso:** Mantener cohesión social

---

### 5. **peligro** ⚡
**Contexto:** Detecta amenaza

**Efecto:**
- Criaturas cercanas se alejan del hablante (fuerza 0.2)
- +0.3 fitness por reaccionar a alerta
- +1 fitness para el hablante

**Uso:** Alerta general de amenaza

---

### 6. **bien** 😊
**Contexto:** Energía > 75%

**Efecto:**
- Criaturas cercanas reducen velocidad a 90% (relajación)
- +0.5 energía por criatura (estado positivo)
- +0.2 fitness por criatura
- +0.5 fitness para el hablante

**Uso:** Comunicar estado positivo, reducir estrés

---

### 7. **malo** 😰
**Contexto:** Energía < 25%

**Efecto:**
- Criaturas aumentan velocidad a 110% (alerta)
- +0.2 fitness por aumentar precaución
- +0.3 fitness para el hablante

**Uso:** Advertir de condiciones adversas

## Vocabulario Avanzado (1500+ complejidad)

Criaturas inteligentes tienen acceso a palabras con **efectos reales**:

### 1. **cohesion** 🤝
**Contexto:** 3+ criaturas cercanas

**Efecto:**
- Criaturas cercanas se mueven hacia el hablante
- Forma grupos cohesionados
- +0.5 fitness por criatura que responde
- +2 fitness para el hablante

**Uso:** Formar grupos de protección o caza

---

### 2. **reproducir** 👶
**Contexto:** Puede reproducirse

**Efecto:**
- Estimula reproducción en criaturas cercanas con energía suficiente
- 30% probabilidad de reproducirse por criatura
- Aumenta población rápidamente

**Uso:** Coordinar explosión demográfica cuando hay recursos

---

### 3. **defender** 🛡️
**Contexto:** Detecta amenaza y fitness > 100

**Efecto:**
- Criaturas cercanas entran en "modo defensa"
- +5 fitness temporal a cada criatura
- +3 energía (adrenalina)
- +3 fitness para el hablante

**Uso:** Preparar grupo para enfrentar depredadores

---

### 4. **peligro_aqui** ⚠️
**Contexto:** Detecta amenaza y energía < 50%

**Efecto:**
- Criaturas cercanas huyen de la ubicación del hablante
- Fuerza de repulsión 0.5
- Radio de efecto: 100 píxeles

**Uso:** Alertar sobre ubicación específica de peligro

---

### 5. **seguir** 👑
**Contexto:** Es inteligente y energía > 60%

**Efecto:**
- Criaturas con menos fitness siguen al hablante
- Mantienen distancia de 30-200 píxeles
- +0.3 fitness por seguidor
- +3 fitness para el líder

**Uso:** Liderazgo y coordinación de grupo

---

### 6. **explorar** 🔍
**Contexto:** No hay comida cerca (150px)

**Efecto:**
- Criaturas cercanas se dispersan en direcciones aleatorias
- Fuerza de dispersión 0.4
- +0.5 fitness por explorador

**Uso:** Buscar nuevas zonas de recursos

---

### 7. **descansar** 😴
**Contexto:** Energía > 80% y edad > 100

**Efecto:**
- Criaturas cercanas reducen velocidad a 50%
- +1 energía por criatura (recuperación)
- Conserva energía del grupo

**Uso:** Recuperación después de actividad intensa

---

### 8. **atacar** 🎯
**Contexto:** Es depredador y energía > 40%

**Efecto:**
- Depredadores cercanos coordinan ataque a presa común
- Máximo 3 atacantes simultáneos
- Umbral de fitness reducido (1.2x vs 1.5x)
- Fuerza de persecución 0.4

**Uso:** Caza coordinada de presas grandes

---

### 9. **huir** 🏃
**Contexto:** Detecta amenaza y fitness < 50

**Efecto:**
- Grupo huye de amenazas cercanas
- Fuerza de huida 0.6
- Radio de detección: 150 píxeles

**Uso:** Escape coordinado de depredadores

---

### 10. **compartir** 💝
**Contexto:** Ve comida cerca y energía > 70%

**Efecto:**
- Transfiere energía a criaturas débiles (< 30% energía)
- Transferencia: 10 energía o 10% de la propia
- +2 fitness por criatura ayudada
- +3 fitness por criatura ayudada (altruismo)

**Uso:** Mantener grupo saludable, evitar muertes

---

## Mecánicas de Comunicación

### Alcance
- **Radio de escucha:** 120 píxeles
- Solo criaturas dentro del radio reciben efectos
- El hablante siempre se incluye en la lista

### Aprendizaje
- Criaturas inteligentes empiezan con: cohesión, defender, seguir
- Otras palabras se aprenden por contexto (5 exposiciones)
- Umbral de aprendizaje: `ASSOCIATION_THRESHOLD = 5`

### Frecuencia
- Probabilidad de vocalizar: 2% por frame
- Efectos se aplican inmediatamente
- No hay cooldown entre vocalizaciones

## Comportamientos Emergentes

### Grupos Coordinados
- Líder usa "seguir" → Grupo se forma
- Líder usa "explorar" → Grupo se dispersa
- Líder usa "cohesion" → Grupo se reagrupa

### Defensa Colectiva
1. Criatura detecta depredador
2. Usa "peligro_aqui" o "defender"
3. Grupo se prepara o huye coordinadamente

### Caza en Manada
1. Depredador detecta presa
2. Usa "atacar"
3. Otros depredadores convergen
4. Ataque coordinado

### Altruismo
1. Criatura fuerte ve débiles
2. Usa "compartir"
3. Transfiere energía
4. Grupo sobrevive más tiempo

### Explosión Demográfica
1. Recursos abundantes
2. Criatura usa "reproducir"
3. Múltiples reproducciones simultáneas
4. Población crece rápidamente

## Logs del Sistema

Con `LOG_VOCALIZATIONS: True`:

```bash
🗣️  Criatura 7632 dice: 'cohesion'
🤝 Criatura 7632 llamó a cohesión - 5 criaturas responden

🗣️  Criatura 7499 dice: 'reproducir'
👶 Criatura 7499 estimuló reproducción - 3 criaturas se reprodujeron

🗣️  Criatura 7543 dice: 'defender'
🛡️  Criatura 7543 activó modo defensa en 4 criaturas

🗣️  Criatura 7589 dice: 'atacar'
🎯 Criatura 7589 coordinó ataque grupal contra Criatura 7201

🗣️  Criatura 7616 dice: 'compartir'
💝 Criatura 7616 compartió energía con 2 criaturas débiles
```

## Configuración

### Activar/Desactivar Logs

```python
# En config.py
DEBUG = {
    'LOG_VOCALIZATIONS': True,  # Ver todas las vocalizaciones y efectos
}
```

### Ajustar Alcance de Comunicación

```python
# En engine/vocal_system.py, método vocalize()
listeners = self.creature.world.get_creatures_near(
    self.creature.x, self.creature.y, 120  # Cambiar este valor
)
```

### Modificar Efectos

Los efectos están en `engine/communication_effects.py`. Puedes ajustar:
- Fuerzas de atracción/repulsión
- Bonos de fitness
- Probabilidades
- Transferencias de energía

## Estrategias Avanzadas

### Líder de Manada
1. Alcanzar complejidad 1500+
2. Mantener fitness alto
3. Usar "seguir" para formar grupo
4. Alternar "cohesion" y "explorar"
5. Usar "defender" ante amenazas

### Depredador Alfa
1. Ser depredador con kills
2. Usar "atacar" para coordinar
3. Usar "seguir" para mantener manada
4. Cazar presas más grandes en grupo

### Altruista
1. Mantener energía alta
2. Usar "compartir" frecuentemente
3. Aumentar fitness por altruismo
4. Formar grupos leales

## Notas Técnicas

### Rendimiento
- Efectos se calculan solo cuando hay listeners
- Máximo 3 atacantes en caza coordinada
- Efectos son instantáneos (no acumulativos)

### Balance
- Efectos diseñados para no ser OP
- Requiere inteligencia (1500+) para acceso
- Costos de energía en comunicación
- Cooldowns implícitos por probabilidad

---

**¡La comunicación ahora tiene poder real en el ecosistema!** 🗣️✨
