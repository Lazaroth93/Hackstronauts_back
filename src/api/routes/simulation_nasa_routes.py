"""
Rutas para simulación completa usando datos de NASA API
Integra la NASA API con el sistema de agentes para simulación completa
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime

from ...services.nasa_service import nasa_service
from ...graphs.graph_agent import AgentGraph
from ...supervisors.hybrid_supervisor import HybridSupervisor

# Crear el router para simulación NASA
simulation_nasa_router = APIRouter(prefix="/simulate-nasa", tags=["Simulación NASA"])

class NASA_SimulationRequest(BaseModel):
    """Request para simulación usando datos de NASA"""
    neo_id: str
    simulation_params: Optional[Dict[str, Any]] = None

class NASA_SimulationResponse(BaseModel):
    """Response de simulación NASA"""
    success: bool
    neo_id: str
    neo_name: str
    nasa_data: Dict[str, Any]
    simulation_results: Any  # Cambiado a Any para aceptar AgentState
    timestamp: str

@simulation_nasa_router.post("/complete", response_model=NASA_SimulationResponse)
async def simulate_nasa_neo_complete(request: NASA_SimulationRequest):
    """
    Simulación completa de un NEO obtenido de la NASA API
    
    Args:
        request: Datos del NEO a simular
        
    Returns:
        Resultados completos de la simulación
    """
    try:
        # 1. Obtener datos del NEO de la NASA
        nasa_neo = await nasa_service.get_neo_by_id(request.neo_id)
        
        if not nasa_neo:
            raise HTTPException(
                status_code=404, 
                detail=f"NEO {request.neo_id} no encontrado en NASA API"
            )
        
        # 2. Transformar datos de la NASA al formato interno
        transformed_data = nasa_service.transform_nasa_data({"near_earth_objects": [nasa_neo]})
        
        if not transformed_data:
            raise HTTPException(
                status_code=500,
                detail=f"Error transformando datos del NEO {request.neo_id}"
            )
        
        neo_data = transformed_data[0]
        
        # 3. Preparar datos para la simulación
        simulation_data = {
            "id": neo_data["neo_id"],
            "name": neo_data["name"],
            "simulation_id": f"nasa_sim_{neo_data['neo_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "nasa_data": neo_data,
            "simulation_params": request.simulation_params or {}
        }
        
        # 4. Ejecutar simulación completa con agentes
        supervisor = HybridSupervisor()
        agent_graph = AgentGraph(supervisor=supervisor)
        
        # Ejecutar simulación
        result_state = await agent_graph.run_simulation(simulation_data)
        
        # 5. Preparar respuesta
        response = NASA_SimulationResponse(
            success=True,
            neo_id=neo_data["neo_id"],
            neo_name=neo_data["name"],
            nasa_data=neo_data,
            simulation_results=result_state,
            timestamp=datetime.now().isoformat()
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error en simulación NASA: {str(e)}"
        )

@simulation_nasa_router.get("/neos", response_model=Dict[str, Any])
async def get_simulatable_neos(
    page: int = Query(0, ge=0, description="Número de página"),
    size: int = Query(10, ge=1, le=20, description="Número de NEOs por página"),
    hazardous_only: bool = Query(False, description="Solo NEOs peligrosos")
):
    """
    Obtiene lista de NEOs de la NASA que se pueden simular
    
    Args:
        page: Número de página
        size: Número de NEOs por página
        hazardous_only: Si filtrar solo NEOs peligrosos
        
    Returns:
        Lista de NEOs disponibles para simulación
    """
    try:
        # Obtener NEOs de la NASA
        nasa_data = await nasa_service.get_neos_browse(page=page, size=size)
        neos = nasa_service.transform_nasa_data(nasa_data)
        
        # Filtrar NEOs peligrosos si se solicita
        if hazardous_only:
            neos = [neo for neo in neos if neo.get("is_potentially_hazardous", False)]
        
        # Agregar información de simulación
        for neo in neos:
            neo["can_simulate"] = True
            neo["simulation_ready"] = all([
                neo.get("diameter_min_m") is not None,
                neo.get("diameter_max_m") is not None,
                neo.get("velocity_km_s") is not None,
                neo.get("miss_distance_km") is not None
            ])
        
        return {
            "neos": neos,
            "pagination": {
                "page": page,
                "size": size,
                "total": len(neos),
                "hazardous_only": hazardous_only
            },
            "source": "nasa_api",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo NEOs para simulación: {str(e)}"
        )

@simulation_nasa_router.get("/status", response_model=Dict[str, Any])
async def get_simulation_status():
    """
    Obtiene el estado del sistema de simulación NASA
    
    Returns:
        Estado del sistema de simulación
    """
    try:
        # Verificar estado de NASA API
        nasa_status = await nasa_service.get_neos_browse(page=0, size=1)
        nasa_working = len(nasa_status.get("near_earth_objects", [])) > 0
        
        # Verificar estado de agentes
        supervisor = HybridSupervisor()
        agent_graph = AgentGraph(supervisor=supervisor)
        
        return {
            "nasa_api_status": "online" if nasa_working else "offline",
            "agents_status": "ready",
            "simulation_ready": nasa_working,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "nasa_api_status": "error",
            "agents_status": "error",
            "simulation_ready": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }