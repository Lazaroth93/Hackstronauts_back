"""
Rutas para NEOs (Near Earth Objects)
Maneja las peticiones HTTP y conecta con el controlador
Siguiendo principios SOLID - Responsabilidad única
"""

from fastapi import APIRouter, HTTPException, Query, Path, Depends
from typing import Optional, List
from datetime import datetime

from ..controllers.neo_controller import NEOController
from ..models.neo_models import (
    NEOSearchQuery,
    NEOResponse,
    NEOSListResponse,
    DangerousNEOResponse,
    SearchResponse,
    ApproachResponse,
    UpcomingApproachesResponse
)

# Crear el router para NEOs
neo_router = APIRouter(prefix="/neos", tags=["NEOs"])

# Instancia del controlador (se inicializa solo cuando se necesita)
def get_neo_controller():
    """Obtiene una instancia del controlador de NEOs"""
    return NEOController()


@neo_router.get("/", response_model=NEOSListResponse)
async def get_all_neos(
    page: int = Query(1, ge=1, description="Número de página"),
    limit: int = Query(20, ge=1, le=100, description="Elementos por página"),
    hazardous_only: bool = Query(False, description="Solo NEOs peligrosos"),
    sort_by: str = Query("name", description="Campo para ordenar"),
    sort_order: str = Query("asc", regex="^(asc|desc)$", description="Orden de clasificación")
):
    """
    Obtiene todos los NEOs con paginación y filtros
    
    - **page**: Número de página (empezando en 1)
    - **limit**: Elementos por página (máximo 100)
    - **hazardous_only**: Filtrar solo NEOs potencialmente peligrosos
    - **sort_by**: Campo para ordenar (name, close_approach_date, miss_distance_km, velocity_km_s, risk_score)
    - **sort_order**: Orden de clasificación (asc o desc)
    
    Returns:
        Lista paginada de NEOs con metadatos de paginación
    """
    try:
        neo_controller = get_neo_controller()
        result = neo_controller.get_all_neos(
            page=page,
            limit=limit,
            hazardous_only=hazardous_only,
            sort_by=sort_by,
            sort_order=sort_order
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener NEOs: {str(e)}")


@neo_router.get("/dangerous", response_model=DangerousNEOResponse)
async def get_dangerous_neos(
    limit: int = Query(50, ge=1, le=200, description="Número máximo de NEOs peligrosos")
):
    """
    Obtiene NEOs potencialmente peligrosos ordenados por riesgo
    
    - **limit**: Número máximo de NEOs a devolver (máximo 200)
    
    Returns:
        Lista de NEOs peligrosos con sus métricas de riesgo
    """
    try:
        neo_controller = get_neo_controller()
        result = neo_controller.get_dangerous_neos(limit=limit)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener NEOs peligrosos: {str(e)}")


@neo_router.post("/search", response_model=SearchResponse)
async def search_neos(search_query: NEOSearchQuery):
    """
    Busca NEOs con filtros avanzados
    
    - **query**: Término de búsqueda (nombre del NEO)
    - **limit**: Número máximo de resultados (máximo 100)
    - **hazardous_only**: Filtrar solo NEOs peligrosos
    - **min_diameter**: Diámetro mínimo en metros
    - **max_diameter**: Diámetro máximo en metros
    - **min_velocity**: Velocidad mínima en km/s
    - **max_velocity**: Velocidad máxima en km/s
    
    Returns:
        Resultados de la búsqueda con metadatos
    """
    try:
        neo_controller = get_neo_controller()
        result = neo_controller.search_neos(search_query)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en la búsqueda: {str(e)}")


@neo_router.get("/{neo_id}/approaches", response_model=ApproachResponse)
async def get_neo_approaches(
    neo_id: str = Path(..., description="ID único del NEO")
):
    """
    Obtiene todas las aproximaciones históricas y futuras de un NEO
    
    - **neo_id**: ID único del NEO
    
    Returns:
        Lista de todas las aproximaciones del NEO ordenadas por fecha
    """
    try:
        neo_controller = get_neo_controller()
        approaches = neo_controller.get_neo_approaches(neo_id)
        if not approaches:
            raise HTTPException(status_code=404, detail=f"No se encontraron aproximaciones para el NEO {neo_id}")
        return approaches
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener aproximaciones: {str(e)}")


@neo_router.get("/approaches/upcoming", response_model=UpcomingApproachesResponse)
async def get_upcoming_approaches(
    days: int = Query(30, ge=1, le=365, description="Días hacia adelante para buscar"),
    limit: int = Query(50, ge=1, le=200, description="Número máximo de aproximaciones")
):
    """
    Obtiene próximas aproximaciones cercanas a la Tierra
    
    - **days**: Número de días hacia adelante para buscar (máximo 365)
    - **limit**: Número máximo de aproximaciones (máximo 200)
    
    Returns:
        Lista de próximas aproximaciones ordenadas por fecha y distancia
    """
    try:
        neo_controller = get_neo_controller()
        result = neo_controller.get_upcoming_approaches(days=days, limit=limit)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener próximas aproximaciones: {str(e)}")


# Endpoint de salud específico para NEOs
@neo_router.get("/health")
async def neo_health_check():
    """
    Verifica el estado del servicio de NEOs
    
    Returns:
        Estado del servicio y estadísticas básicas
    """
    try:
        # Obtener estadísticas básicas
        neo_controller = get_neo_controller()
        dangerous_count = neo_controller.get_dangerous_neos(limit=1).count
        
        return {
            "status": "healthy",
            "service": "NEOs",
            "dangerous_neos_count": dangerous_count,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Servicio de NEOs no disponible: {str(e)}")


@neo_router.get("/{neo_id}", response_model=NEOResponse)
async def get_neo_by_id(
    neo_id: str = Path(..., description="ID único del NEO")
):
    """
    Obtiene un NEO específico por su ID
    
    - **neo_id**: ID único del NEO
    
    Returns:
        Datos completos del NEO incluyendo predicciones de riesgo
    """
    try:
        neo_controller = get_neo_controller()
        neo = neo_controller.get_neo_by_id(neo_id)
        if not neo:
            raise HTTPException(status_code=404, detail=f"NEO con ID {neo_id} no encontrado")
        return neo
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener NEO: {str(e)}")