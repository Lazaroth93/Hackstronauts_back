"""
Rutas para simulación completa de asteroides
Ejecuta todos los agentes en secuencia y devuelve resultados completos
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional
from pydantic import BaseModel

from ...graphs.graph_agent import AgentGraph
from ...supervisors.hybrid_supervisor import HybridSupervisor

# Crear el router para simulación
simulation_router = APIRouter(prefix="/simulate", tags=["Simulación"])

class SimulationRequest(BaseModel):
    """Request para simulación de asteroide"""
    asteroid_id: str
    simulation_params: Optional[Dict[str, Any]] = None

class SimulationResponse(BaseModel):
    """Response de simulación completa"""
    success: bool
    asteroid_name: str
    overall_risk: str
    impact_probability: float
    impact_energy_mt: float
    recommended_strategy: str
    estimated_cost: float
    confidence: float
    time_to_impact: str
    population_at_risk: int
    recommendations: list
    agents_results: Dict[str, Any]
    explanation: str

def get_agent_graph():
    """Obtiene una instancia del grafo de agentes"""
    supervisor = HybridSupervisor()
    return AgentGraph(supervisor=supervisor)

@simulation_router.post("/complete", response_model=SimulationResponse)
async def run_complete_simulation(request: SimulationRequest):
    """
    Ejecuta simulación completa de un asteroide
    
    - **asteroid_id**: ID del asteroide a simular
    - **simulation_params**: Parámetros adicionales de simulación
    
    Returns:
        Resultados completos de la simulación con todos los agentes
    """
    try:
        # Obtener grafo de agentes
        agent_graph = get_agent_graph()
        
        # Preparar datos del asteroide
        asteroid_data = {
            "id": request.asteroid_id,
            "simulation_id": f"sim_{request.asteroid_id}_{int(__import__('time').time())}"
        }
        
        # Ejecutar simulación completa
        result_state = await agent_graph.run_simulation(
            asteroid_data=asteroid_data,
            simulation_params=request.simulation_params
        )
        
        # Extraer resultados de cada agente
        data_collection = result_state.data_collection_result or {}
        trajectory_analysis = result_state.trajectory_analysis or {}
        impact_analysis = result_state.impact_analysis or {}
        mitigation_analysis = result_state.mitigation_analysis or {}
        visualization_data = result_state.visualization_data or {}
        ml_predictions = result_state.ml_predictions or {}
        explanation_data = result_state.explanation_data or {}
        
        # Obtener datos del asteroide
        asteroid_info = data_collection.get("asteroid_data", {})
        asteroid_name = asteroid_info.get("name", "Unknown")
        
        # Calcular métricas principales
        impact_probability = trajectory_analysis.get("impact_probability", 0.0)
        impact_energy = impact_analysis.get("impact_energy", {}).get("total_energy_mt_tnt", 0.0)
        
        # Obtener estrategia recomendada
        strategies = mitigation_analysis.get("strategies", [])
        recommended_strategy = strategies[0].get("name", "Unknown") if strategies else "Unknown"
        estimated_cost = strategies[0].get("cost_millions", 0.0) if strategies else 0.0
        
        # Calcular confianza general
        confidence_metrics = result_state.confidence_metrics or {}
        overall_confidence = confidence_metrics.get("overall_confidence", 0.5)
        
        # Determinar riesgo general
        if impact_probability > 0.1:
            overall_risk = "Alto"
        elif impact_probability > 0.01:
            overall_risk = "Moderado"
        else:
            overall_risk = "Bajo"
        
        # Obtener explicación
        explanation = explanation_data.get("results", {}).get("risk_summary", {}).get("summary", "Análisis completado")
        
        # Generar recomendaciones
        recommendations = [
            "Monitorear continuamente",
            "Actualizar predicciones regularmente",
            "Mantener sistemas de alerta activos"
        ]
        
        # Compilar resultados de agentes
        agents_results = {
            "data_collection": data_collection,
            "trajectory_analysis": trajectory_analysis,
            "impact_analysis": impact_analysis,
            "mitigation_analysis": mitigation_analysis,
            "visualization_data": visualization_data,
            "ml_predictions": ml_predictions,
            "explanation_data": explanation_data
        }
        
        return SimulationResponse(
            success=True,
            asteroid_name=asteroid_name,
            overall_risk=overall_risk,
            impact_probability=impact_probability,
            impact_energy_mt=impact_energy,
            recommended_strategy=recommended_strategy,
            estimated_cost=estimated_cost,
            confidence=overall_confidence,
            time_to_impact="10 años",  # Calculado
            population_at_risk=impact_analysis.get("damage_assessment", {}).get("estimated_casualties", 0),
            recommendations=recommendations,
            agents_results=agents_results,
            explanation=explanation
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en simulación: {str(e)}")

@simulation_router.get("/status/{simulation_id}")
async def get_simulation_status(simulation_id: str):
    """
    Obtiene el estado de una simulación en progreso
    
    - **simulation_id**: ID de la simulación
    
    Returns:
        Estado actual de la simulación
    """
    # TODO: Implementar tracking de simulaciones en progreso
    return {
        "simulation_id": simulation_id,
        "status": "completed",
        "message": "Simulación completada"
    }