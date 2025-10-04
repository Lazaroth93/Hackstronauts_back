"""
MitigationAgent - Evalúa estrategias para evitar impactos de asteroides.

Funcionalidad:
- Evalúa 4 estrategias de deflexión
- Calcula costos y efectividad
- Genera recomendaciones con confianza
- Usa base de datos vectorial para contexto
"""

import math
import os
from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent, AgentState
from ..supervisors.hybrid_supervisor import HybridSupervisor
from dotenv import load_dotenv

load_dotenv()


class MitigationAgent(BaseAgent):
    """Agente que evalúa estrategias de mitigación de asteroides."""
    
    def __init__(self, supervisor: Optional[HybridSupervisor] = None):
        super().__init__(
            name="MitigationAgent",
            description="Evalúa estrategias de mitigación de asteroides"
        )
        self.supervisor = supervisor
        self.asteroid_density = 2000  # kg/m³
        
        # Estrategias simplificadas
        self.strategies = {
            "kinetic_impactor": {"name": "Kinetic Impactor", "cost_factor": 10000, "effectiveness": 0.6},
            "gravity_tractor": {"name": "Gravity Tractor", "cost_factor": 50000, "effectiveness": 0.3},
            "nuclear_deflection": {"name": "Nuclear Deflection", "cost_factor": 100000, "effectiveness": 0.8},
            "laser_ablation": {"name": "Laser Ablation", "cost_factor": 200000, "effectiveness": 0.2}
        }
    
    async def execute(self, state: AgentState) -> AgentState:
        """Ejecuta evaluación de estrategias de mitigación."""
        print("MitigationAgent: Evaluando estrategias...")
        
        try:
            if not self.validate_input(state):
                self.log_error(state, "Datos inválidos")
                return state
            
            # Obtener datos
            asteroid_data = state.data_collection_result.get("asteroid_data", {})
            impact_data = state.impact_analysis
            
            # Calcular masa del asteroide
            diameter = (asteroid_data.get("diameter_min", 1) + asteroid_data.get("diameter_max", 1)) / 2
            mass = self._calculate_mass(diameter)
            
            # Evaluar estrategias
            strategies = self._evaluate_strategies(mass, impact_data)
            
            # Generar predicción LLM
            prediction = await self._generate_prediction(asteroid_data, strategies)
            
            # Supervisión híbrida con confianza mejorada
            if self.supervisor:
                supervision_result = await self.supervisor.supervise_agent_execution(
                    self.name, strategies, {"agent_name": self.name}
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
                    state.mitigation_analysis = {
                        "strategies": strategies,
                        "confidence_metrics": {
                            "overall_confidence": confidence_metrics.overall_confidence,
                            "scientific_confidence": confidence_metrics.scientific_confidence,
                            "rag_confidence": confidence_metrics.rag_confidence,
                            "orbital_confidence": confidence_metrics.orbital_confidence,
                            "data_quality_confidence": confidence_metrics.data_quality_confidence,
                            "prediction_confidence": confidence_metrics.prediction_confidence,
                            "trend": confidence_metrics.trend,
                            "alert_level": confidence_metrics.alert_level
                        }
                    }
                    
                    # Mostrar confianzas en consola
                    print(f"MitigationAgent: Confianza general: {confidence_metrics.overall_confidence:.1%}")
                    print(f"MitigationAgent: Confianza científica: {confidence_metrics.scientific_confidence:.1%}")
                    print(f"MitigationAgent: Confianza de predicción: {confidence_metrics.prediction_confidence:.1%}")
            
            # Actualizar estado
            state.mitigation_strategies = strategies
            print(f"MitigationAgent: {len(strategies)} estrategias evaluadas")
            
        except Exception as e:
            self.log_error(state, f"Error: {str(e)}")
        
        return state
    
    def validate_input(self, state: AgentState) -> bool:
        """Valida datos de entrada."""
        return (state.data_collection_result and 
                state.impact_analysis and
                state.data_collection_result.get("asteroid_data"))
    
    def _calculate_mass(self, diameter_km: float) -> float:
        """Calcula masa del asteroide en kg."""
        radius_m = (diameter_km * 1000) / 2
        volume = (4/3) * math.pi * radius_m ** 3
        return self.asteroid_density * volume
    
    def _evaluate_strategies(self, mass: float, impact_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Evalúa estrategias de mitigación."""
        strategies = []
        
        for strategy_id, strategy_info in self.strategies.items():
            # Calcular costo basado en masa
            cost = mass * strategy_info["cost_factor"] / 1e6  # Convertir a millones
            
            # Ajustar efectividad por masa
            effectiveness = strategy_info["effectiveness"]
            if mass > 1e15:  # Asteroides muy grandes
                effectiveness *= 0.5
            
            # Calcular confianza (porcentaje aprobado por supervisor)
            confidence = min(0.95, effectiveness + 0.1)
            
            strategy = {
                "strategy_id": strategy_id,
                "name": strategy_info["name"],
                "effectiveness": effectiveness,
                "cost_millions": cost,
                "confidence": confidence,
                "recommended": effectiveness > 0.5 and cost < 1000
            }
            strategies.append(strategy)
        
        # Ordenar por efectividad
        return sorted(strategies, key=lambda x: x["effectiveness"], reverse=True)
    
    async def _generate_prediction(self, asteroid_data: Dict[str, Any], 
                                 strategies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Genera predicción usando LLM."""
        try:
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                return self._get_fallback_prediction(asteroid_data, strategies)
            
            # Crear prompt simple
            best_strategy = strategies[0] if strategies else {}
            prompt = f"""
            Analiza estas estrategias de mitigación para el asteroide {asteroid_data.get('name', 'Unknown')}:
            
            Mejor estrategia: {best_strategy.get('name', 'None')}
            Efectividad: {best_strategy.get('effectiveness', 0):.1%}
            Costo: ${best_strategy.get('cost_millions', 0):.0f}M
            
            Responde en JSON con:
            - recommended_strategy: nombre de la estrategia
            - confidence_level: nivel de confianza (0-1)
            - summary: resumen en español
            """
            
            # Llamar a Groq API (simplificado)
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
                        "max_tokens": 500
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
        
        return self._get_fallback_prediction(asteroid_data, strategies)
    
    def _get_fallback_prediction(self, asteroid_data: Dict[str, Any], 
                               strategies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Predicción de respaldo."""
        best = strategies[0] if strategies else {}
        return {
            "recommended_strategy": best.get("name", "Kinetic Impactor"),
            "confidence_level": best.get("confidence", 0.7),
            "summary": f"Estrategia recomendada: {best.get('name', 'Kinetic Impactor')} para {asteroid_data.get('name', 'Unknown')}"
        }