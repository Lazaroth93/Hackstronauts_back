
        
       """
TrajectoryAgent - Analiza trayectorias orbitales de asteroides.

Funcionalidad:
- Calcula elementos orbitales básicos
- Determina aproximaciones cercanas
- Calcula probabilidades de impacto
- Genera predicciones con confianza
"""

import math
import os
from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent, AgentState
from ..supervisors.hybrid_supervisor import HybridSupervisor
from dotenv import load_dotenv

load_dotenv()


class TrajectoryAgent(BaseAgent):
    """Agente que analiza trayectorias orbitales de asteroides."""
    
    def __init__(self, supervisor: Optional[HybridSupervisor] = None):
        super().__init__(
            name="TrajectoryAgent",
            description="Analiza trayectorias orbitales de asteroides"
        )
        self.supervisor = supervisor
        
        # Constantes astronómicas básicas
        self.AU = 1.496e11  # Unidad astronómica en metros
        self.earth_radius = 6.371e6  # Radio de la Tierra en metros
    
    async def execute(self, state: AgentState) -> AgentState:
        """Ejecuta análisis de trayectoria orbital."""
        print("TrajectoryAgent: Analizando trayectoria...")
        
        try:
            if not self.validate_input(state):
                self.log_error(state, "Datos inválidos")
                return state
            
            # Obtener datos del asteroide
            asteroid_data = state.data_collection_result.get("asteroid_data", {})
            
            # Calcular elementos orbitales básicos
            orbital_elements = self._calculate_orbital_elements(asteroid_data)
            
            # Calcular aproximaciones cercanas
            close_approaches = self._calculate_close_approaches(asteroid_data)
            
            # Calcular probabilidad de impacto
            impact_probability = self._calculate_impact_probability(close_approaches)
            
            # Generar predicción LLM
            prediction = await self._generate_prediction(asteroid_data, {
                "orbital_elements": orbital_elements,
                "close_approaches": close_approaches,
                "impact_probability": impact_probability
            })
            
            # Supervisión híbrida con confianza mejorada
            if self.supervisor:
                trajectory_data = {
                    "orbital_elements": orbital_elements,
                    "close_approaches": close_approaches,
                    "impact_probability": impact_probability,
                    "prediction": prediction
                }
                supervision_result = await self.supervisor.supervise_agent_execution(
                    self.name, trajectory_data, {"agent_name": self.name}
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
                    state.trajectory_analysis["confidence_metrics"] = {
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
                    print(f"TrajectoryAgent: Confianza general: {confidence_metrics.overall_confidence:.1%}")
                    print(f"TrajectoryAgent: Confianza orbital: {confidence_metrics.orbital_confidence:.1%}")
                    print(f"TrajectoryAgent: Confianza de predicción: {confidence_metrics.prediction_confidence:.1%}")
            
            # Actualizar estado (preservando confianzas si existen)
            state.trajectory_analysis.update({
                "orbital_elements": orbital_elements,
                "close_approaches": close_approaches,
                "impact_probability": impact_probability,
                "prediction": prediction,
                "status": "success"
            })
            
            print(f"TrajectoryAgent: Probabilidad de impacto: {impact_probability:.1%}")
            
        except Exception as e:
            self.log_error(state, f"Error: {str(e)}")
        
        return state
    
    def validate_input(self, state: AgentState) -> bool:
        """Valida datos de entrada."""
        return (state.data_collection_result and 
                state.data_collection_result.get("asteroid_data"))
    
    def _calculate_orbital_elements(self, asteroid_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula elementos orbitales básicos."""
        orbital_data = asteroid_data.get("orbital_data", {})
        
        # Extraer elementos básicos
        eccentricity = float(orbital_data.get("eccentricity", 0.0))
        inclination = float(orbital_data.get("inclination", 0.0))
        semi_major_axis = float(orbital_data.get("semi_major_axis", 1.0))
        
        # Calcular período orbital (Tercera ley de Kepler)
        orbital_period = math.sqrt(semi_major_axis ** 3)  # años
        
        # Calcular velocidad orbital promedio
        orbital_velocity = 29.8 / math.sqrt(semi_major_axis)  # km/s
        
        return {
            "eccentricity": eccentricity,
            "inclination": inclination,  # grados
            "semi_major_axis": semi_major_axis,  # AU
            "orbital_period": orbital_period,  # años
            "orbital_velocity": orbital_velocity,  # km/s
            "orbital_type": self._classify_orbital_type(eccentricity, inclination)
        }
    
    def _calculate_close_approaches(self, asteroid_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Calcula aproximaciones cercanas a la Tierra."""
        approaches = []
        approach_data = asteroid_data.get("close_approach_data", [])
        
        for approach in approach_data:
            # Calcular distancia de aproximación
            miss_distance_km = float(approach.get("miss_distance", {}).get("kilometers", "0"))
            miss_distance_au = miss_distance_km / self.AU
            
            # Calcular velocidad relativa
            relative_velocity = float(approach.get("relative_velocity", {}).get("kilometers_per_hour", "0"))
            relative_velocity_ms = relative_velocity / 3.6  # m/s
            
            # Determinar si es aproximación cercana
            is_close = miss_distance_au < 0.05  # Menos de 0.05 AU
            
            approach_info = {
                "date": approach.get("close_approach_date", "Unknown"),
                "miss_distance_km": miss_distance_km,
                "miss_distance_au": miss_distance_au,
                "relative_velocity_kmh": relative_velocity,
                "relative_velocity_ms": relative_velocity_ms,
                "is_close_approach": is_close,
                "orbiting_body": approach.get("orbiting_body", "Earth")
            }
            approaches.append(approach_info)
        
        # Ordenar por distancia (más cercanas primero)
        return sorted(approaches, key=lambda x: x["miss_distance_au"])
    
    def _calculate_impact_probability(self, close_approaches: List[Dict[str, Any]]) -> float:
        """Calcula probabilidad de impacto con la Tierra."""
        if not close_approaches:
            return 0.0
        
        # Obtener la aproximación más cercana
        closest = close_approaches[0]
        miss_distance_au = closest["miss_distance_au"]
        
        # Calcular probabilidad basada en distancia
        if miss_distance_au > 0.01:
            return 0.001  # Muy lejos
        elif miss_distance_au < 0.001:
            return 0.1    # Muy cerca
        elif miss_distance_au < 0.005:
            return 0.05   # Cerca
        else:
            return 0.01   # Moderadamente cerca
    
    def _classify_orbital_type(self, eccentricity: float, inclination: float) -> str:
        """Clasifica el tipo de órbita del asteroide."""
        if eccentricity < 0.1 and inclination < 5:
            return "Near-Earth Asteroid (NEA)"
        elif eccentricity > 0.8:
            return "High Eccentricity"
        elif inclination > 30:
            return "High Inclination"
        else:
            return "Standard Orbit"
    
    async def _generate_prediction(self, asteroid_data: Dict[str, Any], 
                                 trajectory_data: Dict[str, Any]) -> Dict[str, Any]:
        """Genera predicción usando LLM."""
        try:
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                return self._get_fallback_prediction(asteroid_data, trajectory_data)
            
            # Crear prompt simple
            name = asteroid_data.get("name", "Unknown")
            impact_prob = trajectory_data.get("impact_probability", 0)
            approaches = trajectory_data.get("close_approaches", [])
            
            prompt = f"""
            Analiza esta trayectoria orbital del asteroide {name}:
            
            Probabilidad de impacto: {impact_prob:.1%}
            Aproximaciones cercanas: {len(approaches)}
            
            Responde en JSON con:
            - risk_level: "Bajo", "Medio", o "Alto"
            - impact_probability_100y: probabilidad en 100 años (0-1)
            - recommendations: lista de recomendaciones
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
                        "max_tokens": 600
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
        
        return self._get_fallback_prediction(asteroid_data, trajectory_data)
    
    def _get_fallback_prediction(self, asteroid_data: Dict[str, Any], 
                               trajectory_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predicción de respaldo."""
        impact_prob = trajectory_data.get("impact_probability", 0)
        
        # Determinar nivel de riesgo
        if impact_prob > 0.1:
            risk_level = "Alto"
        elif impact_prob > 0.01:
            risk_level = "Medio"
        else:
            risk_level = "Bajo"
        
        return {
            "risk_level": risk_level,
            "impact_probability_100y": impact_prob,
            "recommendations": [
                "Monitorear continuamente",
                "Actualizar predicciones regularmente",
                "Mantener sistemas de alerta activos"
            ],
            "confidence_level": 0.6,
            "summary": f"Análisis de trayectoria para {asteroid_data.get('name', 'Unknown')}. Riesgo: {risk_level}"
        }