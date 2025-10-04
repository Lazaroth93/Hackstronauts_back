"""
ImpactAnalyzerAgent - Analiza los efectos de impacto de asteroides.

Funcionalidad:
- Calcula energía del impacto
- Estima tamaño del cráter
- Evalúa efectos sísmicos y tsunamis
- Analiza daños potenciales
- Genera predicciones con confianza
"""

import math
import os
from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent, AgentState
from ..supervisors.hybrid_supervisor import HybridSupervisor
from dotenv import load_dotenv

load_dotenv()


class ImpactAnalyzerAgent(BaseAgent):
    """Agente que analiza efectos de impacto de asteroides."""
    
    def __init__(self, supervisor: Optional[HybridSupervisor] = None):
        super().__init__(
            name="ImpactAnalyzerAgent",
            description="Analiza efectos de impacto de asteroides"
        )
        self.supervisor = supervisor
        
        # Constantes físicas básicas
        self.asteroid_density = 2000  # kg/m³
        self.impact_velocity = 17000  # m/s (típica)
        self.earth_radius = 6.371e6  # m
    
    async def execute(self, state: AgentState) -> AgentState:
        """Ejecuta análisis de impacto del asteroide."""
        print("ImpactAnalyzerAgent: Analizando impacto...")
        
        try:
            if not self.validate_input(state):
                self.log_error(state, "Datos inválidos")
                return state
            
            # Obtener datos
            asteroid_data = state.data_collection_result.get("asteroid_data", {})
            trajectory_data = state.trajectory_analysis
            
            # Calcular masa del asteroide
            diameter = (asteroid_data.get("diameter_min", 1) + asteroid_data.get("diameter_max", 1)) / 2
            mass = self._calculate_mass(diameter)
            
            # Calcular energía del impacto
            impact_energy = self._calculate_impact_energy(mass, trajectory_data)
            
            # Calcular tamaño del cráter
            crater_size = self._calculate_crater_size(impact_energy)
            
            # Calcular efectos sísmicos
            seismic_effects = self._calculate_seismic_effects(impact_energy)
            
            # Calcular efectos de tsunami
            tsunami_effects = self._calculate_tsunami_effects(impact_energy)
            
            # Analizar daños potenciales
            damage_assessment = self._assess_damage_potential(impact_energy, crater_size)
            
            # Generar predicción LLM
            prediction = await self._generate_prediction(asteroid_data, {
                "impact_energy": impact_energy,
                "crater_size": crater_size,
                "seismic_effects": seismic_effects,
                "tsunami_effects": tsunami_effects,
                "damage_assessment": damage_assessment
            })
            
            # Supervisión híbrida con confianza mejorada
            if self.supervisor:
                impact_data = {
                    "impact_energy": impact_energy,
                    "crater_size": crater_size,
                    "seismic_effects": seismic_effects,
                    "tsunami_effects": tsunami_effects,
                    "damage_assessment": damage_assessment,
                    "prediction": prediction
                }
                supervision_result = await self.supervisor.supervise_agent_execution(
                    self.name, impact_data, {"agent_name": self.name}
                )
                state.supervision_results = supervision_result
                
                # Calcular confianzas específicas usando el sistema mejorado
                if hasattr(self.supervisor, 'confidence_system'):
                    # Obtener datos del asteroide del DataCollector
                    asteroid_data = state.data_collection_result.get("asteroid_data", {})
                    
                    confidence_metrics = self.supervisor.confidence_system.update_confidence(
                        validation_reports=supervision_result.get("validation_reports", []),
                        asteroid_data=asteroid_data,
                        prediction_data=prediction
                    )
                    
                    # Agregar confianzas específicas al resultado
                    state.impact_analysis["confidence_metrics"] = {
                        "overall_confidence": confidence_metrics.overall_confidence,
                        "scientific_confidence": confidence_metrics.scientific_confidence,
                        "rag_confidence": confidence_metrics.rag_confidence,
                        "orbital_confidence": confidence_metrics.orbital_confidence,
                        "data_quality_confidence": confidence_metrics.data_quality_confidence,
                        "prediction_confidence": confidence_metrics.prediction_confidence,
                        "trend": confidence_metrics.trend,
                        "alert_level": confidence_metrics.alert_level
                    }
                    
                    # Mostrar confianzas en consola
                    print(f"ImpactAnalyzerAgent: Confianza general: {confidence_metrics.overall_confidence:.1%}")
                    print(f"ImpactAnalyzerAgent: Confianza científica: {confidence_metrics.scientific_confidence:.1%}")
                    print(f"ImpactAnalyzerAgent: Confianza de predicción: {confidence_metrics.prediction_confidence:.1%}")
            
            # Actualizar estado (preservando confianzas si existen)
            state.impact_analysis.update({
                "impact_energy": impact_energy,
                "crater_size": crater_size,
                "seismic_effects": seismic_effects,
                "tsunami_effects": tsunami_effects,
                "damage_assessment": damage_assessment,
                "prediction": prediction,
                "status": "success"
            })
            
            print(f"ImpactAnalyzerAgent: Energía: {impact_energy['total_energy_mt_tnt']:.1f} MT TNT")
            print(f"ImpactAnalyzerAgent: Cráter: {crater_size['diameter_km']:.1f} km")
            
        except Exception as e:
            self.log_error(state, f"Error: {str(e)}")
        
        return state
    
    def validate_input(self, state: AgentState) -> bool:
        """Valida datos de entrada."""
        return (state.data_collection_result and 
                state.trajectory_analysis and
                state.data_collection_result.get("asteroid_data"))
    
    def _calculate_mass(self, diameter_km: float) -> float:
        """Calcula masa del asteroide en kg."""
        radius_m = (diameter_km * 1000) / 2
        volume = (4/3) * math.pi * radius_m ** 3
        return self.asteroid_density * volume
    
    def _calculate_impact_energy(self, mass: float, trajectory_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula energía del impacto."""
        # Obtener velocidad de impacto
        close_approaches = trajectory_data.get("close_approaches", [])
        if close_approaches:
            velocity_ms = close_approaches[0].get("relative_velocity_ms", self.impact_velocity)
        else:
            velocity_ms = self.impact_velocity
        
        # Calcular energía cinética: E = 0.5 * m * v²
        kinetic_energy = 0.5 * mass * velocity_ms ** 2  # Joules
        
        # Convertir a megatones de TNT (1 MT TNT = 4.184e15 J)
        energy_mt_tnt = kinetic_energy / (4.184e15)
        
        # Calcular equivalente en bombas de Hiroshima
        hiroshima_bombs = energy_mt_tnt / 0.015  # 0.015 MT TNT por bomba
        
        # Clasificar el impacto
        if energy_mt_tnt < 0.1:
            classification = "Local"
        elif energy_mt_tnt < 1:
            classification = "Regional"
        elif energy_mt_tnt < 100:
            classification = "Continental"
        elif energy_mt_tnt < 10000:
            classification = "Global"
        else:
            classification = "Extinction Level"
        
        return {
            "total_energy_joules": kinetic_energy,
            "total_energy_mt_tnt": energy_mt_tnt,
            "equivalent_hiroshima_bombs": hiroshima_bombs,
            "asteroid_mass_kg": mass,
            "impact_velocity_ms": velocity_ms,
            "classification": classification
        }
    
    def _calculate_crater_size(self, impact_energy: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula tamaño del cráter."""
        energy_joules = impact_energy["total_energy_joules"]
        
        # Fórmula simplificada de escalado de cráteres
        # D = 1.2 * (E/ρ)^(1/3) donde E está en Joules y ρ en kg/m³
        target_density = 3000  # kg/m³ (densidad promedio de la corteza)
        crater_diameter_m = 1.2 * (energy_joules / target_density) ** (1/3)
        crater_diameter_km = crater_diameter_m / 1000
        
        # Profundidad típicamente 1/3 del diámetro
        crater_depth_km = crater_diameter_km / 3
        
        # Clasificar el cráter
        if crater_diameter_km < 1:
            crater_type = "Simple"
        elif crater_diameter_km < 10:
            crater_type = "Complex"
        elif crater_diameter_km < 100:
            crater_type = "Multi-ring"
        else:
            crater_type = "Basin"
        
        return {
            "diameter_km": crater_diameter_km,
            "depth_km": crater_depth_km,
            "area_km2": math.pi * (crater_diameter_km / 2) ** 2,
            "crater_type": crater_type
        }
    
    def _calculate_seismic_effects(self, impact_energy: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula efectos sísmicos."""
        energy_mt_tnt = impact_energy["total_energy_mt_tnt"]
        
        # Magnitud sísmica basada en energía (escala de Richter)
        # M = log10(E) - 4.8, donde E está en Joules
        energy_joules = impact_energy["total_energy_joules"]
        magnitude = math.log10(energy_joules) - 4.8
        
        # Ajustar por tipo de impacto
        magnitude *= 0.7  # Factor de ajuste para impactos
        
        # Calcular radio de efectos sísmicos
        if magnitude >= 6.0:
            seismic_radius_km = 1000 * (10 ** (magnitude - 6))
        else:
            seismic_radius_km = 100 * (10 ** (magnitude - 4))
        
        # Clasificar intensidad
        if magnitude < 4:
            intensity = "Light"
        elif magnitude < 5:
            intensity = "Moderate"
        elif magnitude < 6:
            intensity = "Strong"
        elif magnitude < 7:
            intensity = "Major"
        else:
            intensity = "Great"
        
        return {
            "magnitude": magnitude,
            "intensity": intensity,
            "seismic_radius_km": seismic_radius_km,
            "damage_radius_km": seismic_radius_km * 0.5
        }
    
    def _calculate_tsunami_effects(self, impact_energy: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula efectos de tsunami."""
        energy_mt_tnt = impact_energy["total_energy_mt_tnt"]
        
        # Asumir 70% de probabilidad de impacto oceánico
        ocean_impact_probability = 0.7
        
        if ocean_impact_probability < 0.5:
            return {
                "tsunami_risk": "low",
                "max_wave_height_m": 0,
                "tsunami_radius_km": 0,
                "ocean_impact_probability": ocean_impact_probability
            }
        
        # Calcular altura máxima de la ola
        if energy_mt_tnt > 1000:
            max_wave_height_m = 100 + 50 * math.log10(energy_mt_tnt / 1000)
        elif energy_mt_tnt > 100:
            max_wave_height_m = 50 + 25 * math.log10(energy_mt_tnt / 100)
        elif energy_mt_tnt > 10:
            max_wave_height_m = 20 + 15 * math.log10(energy_mt_tnt / 10)
        else:
            max_wave_height_m = 5 + 10 * math.log10(energy_mt_tnt)
        
        # Calcular radio de efectos
        tsunami_radius_km = 1000 * math.sqrt(energy_mt_tnt / 100)
        
        # Clasificar riesgo
        if max_wave_height_m < 1:
            tsunami_risk = "Low"
        elif max_wave_height_m < 5:
            tsunami_risk = "Moderate"
        elif max_wave_height_m < 20:
            tsunami_risk = "High"
        else:
            tsunami_risk = "Extreme"
        
        return {
            "tsunami_risk": tsunami_risk,
            "max_wave_height_m": max_wave_height_m,
            "tsunami_radius_km": tsunami_radius_km,
            "ocean_impact_probability": ocean_impact_probability
        }
    
    def _assess_damage_potential(self, impact_energy: Dict[str, Any], 
                                crater_size: Dict[str, Any]) -> Dict[str, Any]:
        """Evalúa daños potenciales."""
        energy_mt_tnt = impact_energy["total_energy_mt_tnt"]
        crater_area = crater_size["area_km2"]
        
        # Calcular área total afectada
        seismic_radius = 1000  # km (estimación conservadora)
        seismic_area = math.pi * seismic_radius ** 2
        total_affected_area = crater_area + seismic_area
        
        # Estimar población afectada
        population_density = 50  # personas/km²
        estimated_casualties = total_affected_area * population_density
        
        # Clasificar nivel de daños
        if energy_mt_tnt < 1:
            damage_level = "Minor"
        elif energy_mt_tnt < 100:
            damage_level = "Moderate"
        elif energy_mt_tnt < 1000:
            damage_level = "Severe"
        elif energy_mt_tnt < 10000:
            damage_level = "Catastrophic"
        else:
            damage_level = "Extinction Level"
        
        # Estimar daños económicos (muy aproximado)
        economic_damage = total_affected_area * 1000000  # $1M por km²
        
        return {
            "total_affected_area_km2": total_affected_area,
            "crater_area_km2": crater_area,
            "seismic_area_km2": seismic_area,
            "estimated_casualties": int(estimated_casualties),
            "damage_level": damage_level,
            "economic_damage_usd": economic_damage
        }
    
    async def _generate_prediction(self, asteroid_data: Dict[str, Any], 
                                 impact_data: Dict[str, Any]) -> Dict[str, Any]:
        """Genera predicción usando LLM."""
        try:
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                return self._get_fallback_prediction(asteroid_data, impact_data)
            
            # Crear prompt simple
            name = asteroid_data.get("name", "Unknown")
            energy_mt = impact_data["impact_energy"]["total_energy_mt_tnt"]
            crater_diameter = impact_data["crater_size"]["diameter_km"]
            magnitude = impact_data["seismic_effects"]["magnitude"]
            damage_level = impact_data["damage_assessment"]["damage_level"]
            
            prompt = f"""
            Analiza este impacto de asteroide para {name}:
            
            Energía del impacto: {energy_mt:.1f} MT TNT
            Diámetro del cráter: {crater_diameter:.1f} km
            Magnitud sísmica: {magnitude:.1f}
            Nivel de daños: {damage_level}
            
            Responde en JSON con:
            - threat_level: "Bajo", "Medio", "Alto", o "Extremo"
            - immediate_actions: lista de acciones inmediatas
            - evacuation_radius_km: radio de evacuación recomendado
            - confidence_level: nivel de confianza (0-1)
            - summary: resumen en español
            """
            
            # Llamar a Groq API
            import httpx
            import json
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                    json={
                        "model": "llama-3.1-8b-instant",
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.3,
                        "max_tokens": 800
                    },
                    timeout=30.0
                )
            
            if response.status_code == 200:
                content = response.json()["choices"][0]["message"]["content"]
                try:
                    return json.loads(content)
                except:
                    pass
            
        except Exception as e:
            print(f"Error LLM: {e}")
        
        return self._get_fallback_prediction(asteroid_data, impact_data)
    
    def _get_fallback_prediction(self, asteroid_data: Dict[str, Any], 
                               impact_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predicción de respaldo."""
        damage_level = impact_data["damage_assessment"]["damage_level"]
        
        # Determinar nivel de amenaza
        if damage_level == "Extinction Level":
            threat_level = "Extremo"
        elif damage_level == "Catastrophic":
            threat_level = "Alto"
        elif damage_level == "Severe":
            threat_level = "Medio"
        else:
            threat_level = "Bajo"
        
        return {
            "threat_level": threat_level,
            "immediate_actions": [
                "Monitorear continuamente",
                "Preparar sistemas de alerta",
                "Evaluar estrategias de mitigación"
            ],
            "evacuation_radius_km": 100,
            "confidence_level": 0.6,
            "summary": f"Análisis de impacto para {asteroid_data.get('name', 'Unknown')}. Nivel de amenaza: {threat_level}"
        }