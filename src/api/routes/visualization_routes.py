"""
Rutas para Visualizaciones
Maneja las peticiones HTTP para generar gráficos y visualizaciones
"""

from fastapi import APIRouter, HTTPException, Path, Depends
from typing import Optional
from datetime import datetime

from ..controllers.visualization_controller import VisualizationController
from ..models.visualization_models import (
    OrbitalTrajectoryResponse,
    ImpactMapResponse,
    ConfidenceChartResponse,
    RiskTimelineResponse,
    Orbit3DResponse
)

# Crear el router para visualizaciones
visualization_router = APIRouter(prefix="/visualize", tags=["Visualizaciones"])

# Instancia del controlador (se inicializa solo cuando se necesita)
def get_visualization_controller():
    """Obtiene una instancia del controlador de visualizaciones"""
    return VisualizationController()

@visualization_router.get("/asteroid/{neo_id}/trajectory", response_model=OrbitalTrajectoryResponse)
async def get_orbital_trajectory(
    neo_id: str = Path(..., description="ID único del NEO")
):
    """
    Genera gráfico de trayectoria orbital de un asteroide
    
    - **neo_id**: ID único del NEO
    
    Returns:
        Gráfico de trayectoria orbital con datos de posición y tiempo
    """
    try:
        controller = get_visualization_controller()
        result = controller.get_orbital_trajectory(neo_id)
        if not result:
            raise HTTPException(status_code=404, detail=f"No se encontraron datos para el NEO {neo_id}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando trayectoria orbital: {str(e)}")

@visualization_router.get("/asteroid/{neo_id}/impact-map", response_model=ImpactMapResponse)
async def get_impact_map(
    neo_id: str = Path(..., description="ID único del NEO")
):
    """
    Genera mapa de impacto con zonas de daño
    
    - **neo_id**: ID único del NEO
    
    Returns:
        Mapa de impacto con zonas de daño, ondas sísmicas y tsunamis
    """
    try:
        controller = get_visualization_controller()
        result = controller.get_impact_map(neo_id)
        if not result:
            raise HTTPException(status_code=404, detail=f"No se encontraron datos para el NEO {neo_id}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando mapa de impacto: {str(e)}")

@visualization_router.get("/asteroid/{neo_id}/confidence", response_model=ConfidenceChartResponse)
async def get_confidence_chart(
    neo_id: str = Path(..., description="ID único del NEO")
):
    """
    Genera gráfico de métricas de confianza
    
    - **neo_id**: ID único del NEO
    
    Returns:
        Gráfico de métricas de confianza del sistema
    """
    try:
        controller = get_visualization_controller()
        result = controller.get_confidence_chart(neo_id)
        if not result:
            raise HTTPException(status_code=404, detail=f"No se encontraron métricas para el NEO {neo_id}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando gráfico de confianza: {str(e)}")

@visualization_router.get("/asteroid/{neo_id}/risk-timeline", response_model=RiskTimelineResponse)
async def get_risk_timeline(
    neo_id: str = Path(..., description="ID único del NEO")
):
    """
    Genera timeline de riesgo temporal
    
    - **neo_id**: ID único del NEO
    
    Returns:
        Timeline de riesgo con eventos temporales y niveles de amenaza
    """
    try:
        controller = get_visualization_controller()
        result = controller.get_risk_timeline(neo_id)
        if not result:
            raise HTTPException(status_code=404, detail=f"No se encontraron datos temporales para el NEO {neo_id}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando timeline de riesgo: {str(e)}")

@visualization_router.get("/asteroid/{neo_id}/orbit-3d", response_model=Orbit3DResponse)
async def get_orbit_3d(
    neo_id: str = Path(..., description="ID único del NEO")
):
    """
    Genera visualización 3D de órbita
    
    - **neo_id**: ID único del NEO
    
    Returns:
        Visualización 3D de la órbita del asteroide
    """
    try:
        controller = get_visualization_controller()
        result = controller.get_orbit_3d(neo_id)
        if not result:
            raise HTTPException(status_code=404, detail=f"No se encontraron datos orbitales para el NEO {neo_id}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando visualización 3D: {str(e)}")

# Endpoint de salud específico para visualizaciones
@visualization_router.get("/health")
async def visualization_health_check():
    """
    Verifica el estado del servicio de visualizaciones
    
    Returns:
        Estado del servicio y estadísticas de visualizaciones
    """
    try:
        controller = get_visualization_controller()
        stats = controller.get_service_stats()
        
        return {
            "status": "healthy",
            "service": "Visualizaciones",
            "total_visualizations": stats.get("total_visualizations", 0),
            "supported_types": [
                "orbital_trajectory",
                "impact_map", 
                "confidence_chart",
                "risk_timeline",
                "orbit_3d"
            ],
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Servicio de visualizaciones no disponible: {str(e)}")