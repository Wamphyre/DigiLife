"""
Sistema de enfermedades y epidemias
"""

import random
from typing import Dict, List, Optional


class Disease:
    """Enfermedad que puede afectar a las criaturas"""
    
    # Nombres de enfermedades
    DISEASE_NAMES = [
        "Virus Digital", "Corrupción de Datos", "Fragmentación Genética",
        "Sobrecarga Neural", "Degradación Energética", "Mutación Caótica",
        "Infección Binaria", "Síndrome de Complejidad", "Fatiga Cognitiva",
        "Desincronización", "Entropía Acelerada", "Glitch Sistémico"
    ]
    
    # Síntomas posibles
    SYMPTOMS = [
        {'name': 'Pérdida de energía', 'energy_drain': 0.5, 'complexity_loss': 0},
        {'name': 'Confusión neural', 'energy_drain': 0.2, 'complexity_loss': 0.3},
        {'name': 'Debilidad motora', 'energy_drain': 0.3, 'complexity_loss': 0.1},
        {'name': 'Degradación cognitiva', 'energy_drain': 0.1, 'complexity_loss': 0.5},
        {'name': 'Fatiga extrema', 'energy_drain': 0.8, 'complexity_loss': 0.2},
        {'name': 'Desorientación', 'energy_drain': 0.4, 'complexity_loss': 0.4},
    ]
    
    def __init__(self):
        self.name = random.choice(self.DISEASE_NAMES)
        self.symptoms = random.sample(self.SYMPTOMS, k=random.randint(1, 3))
        self.contagion_rate = random.uniform(0.05, 0.25)  # 5-25% por contacto
        self.duration = random.randint(50, 200)  # ciclos
        self.lethality = random.uniform(0.01, 0.1)  # 1-10% de muerte
        self.active = True
        self.infected_count = 0
        self.deaths_caused = 0
        self.patient_zero_id = None  # ID del paciente cero
    
    def get_total_energy_drain(self) -> float:
        """Obtener drenaje total de energía por ciclo"""
        return sum(s['energy_drain'] for s in self.symptoms)
    
    def get_total_complexity_loss(self) -> float:
        """Obtener pérdida total de complejidad por ciclo"""
        return sum(s['complexity_loss'] for s in self.symptoms)
    
    def get_symptoms_text(self) -> str:
        """Obtener texto descriptivo de síntomas"""
        return ", ".join(s['name'] for s in self.symptoms)


class Infection:
    """Infección activa en una criatura"""
    
    def __init__(self, disease: Disease):
        self.disease = disease
        self.duration_left = disease.duration
        self.severity = random.uniform(0.5, 1.5)  # Multiplicador de efectos
    
    def update(self, creature, dt: float) -> bool:
        """Actualizar infección. Retorna True si la criatura sobrevive"""
        self.duration_left -= 1
        
        # Aplicar efectos
        energy_loss = self.disease.get_total_energy_drain() * self.severity * dt
        complexity_loss = self.disease.get_total_complexity_loss() * self.severity * dt
        
        creature.energy -= energy_loss
        creature.complexity = max(0, creature.complexity - complexity_loss)
        
        # Chequear letalidad
        if random.random() < self.disease.lethality * dt:
            creature.energy = 0  # Muerte por enfermedad
            self.disease.deaths_caused += 1
            return False
        
        return True
    
    def is_active(self) -> bool:
        """Verificar si la infección sigue activa"""
        return self.duration_left > 0


class DiseaseSystem:
    """Sistema de gestión de enfermedades en el mundo"""
    
    def __init__(self, world):
        self.world = world
        self.active_diseases: List[Disease] = []
        self.outbreak_timer = 0
        self.outbreak_interval = random.randint(500, 1500)  # Cada 5-15 días
        self.min_population_for_outbreak = 30  # Mínimo de población para brote
    
    def update(self, dt: float):
        """Actualizar sistema de enfermedades"""
        self.outbreak_timer += 1
        
        # Verificar si es momento de un brote
        if (self.outbreak_timer >= self.outbreak_interval and 
            self.world.population >= self.min_population_for_outbreak):
            self.trigger_outbreak()
            self.outbreak_timer = 0
            self.outbreak_interval = random.randint(500, 1500)
        
        # Actualizar enfermedades activas
        for disease in self.active_diseases[:]:
            if disease.infected_count == 0 and disease.active:
                disease.active = False
                print(f"🏥 Epidemia '{disease.name}' erradicada")
                print(f"   Infectados totales: {disease.infected_count}")
                print(f"   Muertes causadas: {disease.deaths_caused}")
    
    def trigger_outbreak(self):
        """Desencadenar un brote de enfermedad"""
        disease = Disease()
        self.active_diseases.append(disease)
        
        # Infectar paciente cero (criatura aleatoria)
        if self.world.creatures:
            patient_zero = random.choice(self.world.creatures)
            disease.patient_zero_id = patient_zero.id  # Guardar ID del paciente cero
            self.infect_creature(patient_zero, disease)
            
            print(f"\n🦠 ¡BROTE DE EPIDEMIA!")
            print(f"   Enfermedad: {disease.name}")
            print(f"   Síntomas: {disease.get_symptoms_text()}")
            print(f"   Contagio: {disease.contagion_rate*100:.1f}%")
            print(f"   Letalidad: {disease.lethality*100:.1f}%")
            print(f"   Paciente cero: Criatura {patient_zero.id}\n")
    
    def infect_creature(self, creature, disease: Disease):
        """Infectar una criatura"""
        if not hasattr(creature, 'infection') or creature.infection is None:
            creature.infection = Infection(disease)
            disease.infected_count += 1
    
    def try_spread(self, infected_creature, nearby_creatures: List):
        """Intentar propagar enfermedad a criaturas cercanas"""
        if not hasattr(infected_creature, 'infection') or infected_creature.infection is None:
            return
        
        disease = infected_creature.infection.disease
        
        for creature in nearby_creatures:
            if creature != infected_creature:
                # Verificar si ya está infectada
                if not hasattr(creature, 'infection') or creature.infection is None:
                    # Intentar contagio
                    if random.random() < disease.contagion_rate:
                        self.infect_creature(creature, disease)
    
    def get_active_epidemics(self) -> List[Dict]:
        """Obtener información de epidemias activas"""
        epidemics = []
        for disease in self.active_diseases:
            if disease.active:
                # Contar infectados actuales
                current_infected = sum(
                    1 for c in self.world.creatures 
                    if hasattr(c, 'infection') and 
                    c.infection and 
                    c.infection.disease == disease
                )
                
                epidemics.append({
                    'name': disease.name,
                    'infected': current_infected,
                    'deaths': disease.deaths_caused,
                    'symptoms': disease.get_symptoms_text(),
                    'patient_zero_id': disease.patient_zero_id,
                    'contagion_rate': disease.contagion_rate,
                    'lethality': disease.lethality
                })
        
        return epidemics
