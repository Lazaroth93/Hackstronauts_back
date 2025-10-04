"""
Rutas para Métricas del Sistema
Maneja las peticiones HTTP para métricas y estadísticas
Siguiendo principios SOLID - Responsabilidad única
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime

from ..controllers.metrics_controller import MetricsController
from ..models.metrics_models import (
    SizeMetricsResponse,
    VelocityMetricsResponse,
    MagnitudeMetricsResponse,
    SystemStatistics,
    SystemStatusResponse
)

# Crear el router para métricas
metrics_router = APIRouter(prefix="/metrics", tags=["Métricas del Sistema"])

# Instancia del controlador (se inicializa solo cuando se necesita)
def get_metrics_controller():
    """Obtiene una instancia del controlador de métricas"""
    return MetricsController()


@metrics_router.get("/size", response_model=SizeMetricsResponse)
async def get_size_metrics():
    """
    Obtiene métricas de tamaño de todos los NEOs
    
    Returns:
        Métricas de tamaño incluyendo:
        - Conteo total de NEOs
        - Diámetros promedio, mínimo y máximo
        - Desviación estándar
        - Distribución por rangos de tamaño
    """
    try:
        metrics_controller = get_metrics_controller()
        result = metrics_controller.get_size_metrics()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener métricas de tamaño: {str(e)}")


@metrics_router.get("/velocity", response_model=VelocityMetricsResponse)
async def get_velocity_metrics():
    """
    Obtiene métricas de velocidad de todos los NEOs
    
    Returns:
        Métricas de velocidad incluyendo:
        - Conteo total de NEOs
        - Velocidades promedio, mínima y máxima
        - Desviación estándar
        - Distribución por rangos de velocidad
    """
    try:
        metrics_controller = get_metrics_controller()
        result = metrics_controller.get_velocity_metrics()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener métricas de velocidad: {str(e)}")


@metrics_router.get("/magnitude", response_model=MagnitudeMetricsResponse)
async def get_magnitude_metrics():
    """
    Obtiene métricas de magnitud absoluta de todos los NEOs
    
    Returns:
        Métricas de magnitud incluyendo:
        - Conteo total de NEOs
        - Magnitudes promedio, mínima y máxima
        - Desviación estándar
        - Distribución por rangos de magnitud
    """
    try:
        metrics_controller = get_metrics_controller()
        result = metrics_controller.get_magnitude_metrics()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener métricas de magnitud: {str(e)}")


@metrics_router.get("/system", response_model=SystemStatusResponse)
async def get_system_status():
    """
    Obtiene el estado completo del sistema híbrido
    
    Returns:
        Estado del sistema incluyendo:
        - Estado de todos los agentes
        - Estadísticas del sistema
        - Métricas de rendimiento
        - Estado de la base de datos
        - Tiempo de respuesta promedio
    """
    try:
        metrics_controller = get_metrics_controller()
        result = metrics_controller.get_system_status()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener estado del sistema: {str(e)}")


@metrics_router.get("/statistics", response_model=SystemStatistics)
async def get_system_statistics():
    """
    Obtiene estadísticas detalladas del sistema
    
    Returns:
        Estadísticas del sistema incluyendo:
        - Total de NEOs en la base de datos
        - NEOs peligrosos
        - Análisis realizados
        - Predicciones generadas
        - Tiempo de respuesta promedio
        - Uso de memoria y CPU
    """
    try:
        metrics_controller = get_metrics_controller()
        result = metrics_controller.get_system_statistics()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener estadísticas del sistema: {str(e)}")


# Endpoint de salud específico para métricas
@metrics_router.get("/health")
async def metrics_health_check():
    """
    Verifica el estado del servicio de métricas
    
    Returns:
        Estado del servicio y estadísticas básicas
    """
    try:
        # Obtener estadísticas básicas
        metrics_controller = get_metrics_controller()
        stats = metrics_controller.get_basic_stats()
        
        return {
            "status": "healthy",
            "service": "Métricas del Sistema",
            "total_neos": stats.get("total_neos", 0),
            "dangerous_neos": stats.get("dangerous_neos", 0),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Servicio de métricas no disponible: {str(e)}")