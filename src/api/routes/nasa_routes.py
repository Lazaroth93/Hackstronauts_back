"""
Rutas para integración con NASA API
Obtiene datos reales de NEOs directamente de la NASA
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta

from ...services.nasa_service import nasa_service

# Crear el router para NASA
nasa_router = APIRouter(prefix="/nasa", tags=["NASA API"])

class NEOSearchRequest(BaseModel):
    """Request para búsqueda de NEOs en NASA"""
    page: int = 0
    size: int = 20
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class NEOResponse(BaseModel):
    """Response de NEO de la NASA"""
    neo_id: str
    name: str
    absolute_magnitude_h: Optional[float]
    is_potentially_hazardous: bool
    close_approach_date: Optional[str]
    miss_distance_km: Optional[float]
    velocity_km_s: Optional[float]
    diameter_min_m: Optional[float]
    diameter_max_m: Optional[float]
    orbit_class: Optional[str]
    source: str
    last_updated: str

@nasa_router.get("/neos", response_model=Dict[str, Any])
async def get_nasa_neos(
    page: int = Query(0, ge=0, description="Número de página"),
    size: int = Query(20, ge=1, le=20, description="Número de NEOs por página"),
    transform: bool = Query(True, description="Transformar datos al formato interno")
):
    """
    Obtiene NEOs directamente de la NASA API
    
    Args:
        page: Número de página (0-indexed)
        size: Número de NEOs por página (máximo 20)
        transform: Si transformar los datos al formato interno
        
    Returns:
        Lista de NEOs de la NASA
    """
    try:
        # Obtener datos de la NASA
        nasa_data = await nasa_service.get_neos_browse(page=page, size=size)
        
        if transform:
            # Transformar al formato interno
            neos = nasa_service.transform_nasa_data(nasa_data)
            
            return {
                "neos": neos,
                "pagination": {
                    "page": page,
                    "size": size,
                    "total": len(neos),
                    "source": "nasa_api"
                },
                "timestamp": datetime.now().isoformat()
            }
        else:
            # Devolver datos crudos de la NASA
            return {
                "nasa_data": nasa_data,
                "pagination": {
                    "page": page,
                    "size": size,
                    "source": "nasa_api"
                },
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo NEOs de NASA: {str(e)}")

@nasa_router.get("/neos/{neo_id}", response_model=Dict[str, Any])
async def get_nasa_neo_by_id(
    neo_id: str,
    transform: bool = Query(True, description="Transformar datos al formato interno")
):
    """
    Obtiene un NEO específico de la NASA API por ID
    
    Args:
        neo_id: ID del NEO en la NASA
        transform: Si transformar los datos al formato interno
        
    Returns:
        Datos del NEO de la NASA
    """
    try:
        # Obtener datos del NEO de la NASA
        nasa_neo = await nasa_service.get_neo_by_id(neo_id)
        
        if not nasa_neo:
            raise HTTPException(status_code=404, detail=f"NEO {neo_id} no encontrado en NASA API")
        
        if transform:
            # Transformar al formato interno
            transformed_data = nasa_service.transform_nasa_data({"near_earth_objects": [nasa_neo]})
            neo = transformed_data[0] if transformed_data else None
            
            if not neo:
                raise HTTPException(status_code=404, detail=f"Error transformando datos del NEO {neo_id}")
            
            return {
                "neo": neo,
                "source": "nasa_api",
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "nasa_neo": nasa_neo,
                "source": "nasa_api",
                "timestamp": datetime.now().isoformat()
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo NEO {neo_id} de NASA: {str(e)}")

@nasa_router.get("/feed", response_model=Dict[str, Any])
async def get_nasa_feed(
    start_date: Optional[str] = Query(None, description="Fecha de inicio (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Fecha de fin (YYYY-MM-DD)"),
    transform: bool = Query(True, description="Transformar datos al formato interno")
):
    """
    Obtiene feed de NEOs de la NASA para un rango de fechas
    
    Args:
        start_date: Fecha de inicio (por defecto: hoy)
        end_date: Fecha de fin (por defecto: hoy + 7 días)
        transform: Si transformar los datos al formato interno
        
    Returns:
        Feed de NEOs de la NASA
    """
    try:
        # Obtener feed de la NASA
        nasa_feed = await nasa_service.get_feed(start_date=start_date, end_date=end_date)
        
        if transform:
            # Transformar al formato interno
            all_neos = []
            for date_str, neos_data in nasa_feed.get("near_earth_objects", {}).items():
                neos = nasa_service.transform_nasa_data({"near_earth_objects": neos_data})
                for neo in neos:
                    neo["approach_date"] = date_str
                all_neos.extend(neos)
            
            return {
                "neos": all_neos,
                "date_range": {
                    "start_date": start_date or datetime.now().strftime("%Y-%m-%d"),
                    "end_date": end_date or (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
                },
                "source": "nasa_api",
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "nasa_feed": nasa_feed,
                "date_range": {
                    "start_date": start_date or datetime.now().strftime("%Y-%m-%d"),
                    "end_date": end_date or (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
                },
                "source": "nasa_api",
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo feed de NASA: {str(e)}")

@nasa_router.get("/status", response_model=Dict[str, Any])
async def get_nasa_status():
    """
    Obtiene el estado de la conexión con NASA API
    
    Returns:
        Estado de la API de la NASA
    """
    try:
        # Probar conexión con NASA
        test_data = await nasa_service.get_neos_browse(page=0, size=1)
        
        has_api_key = nasa_service.api_key is not None
        neos_count = len(test_data.get("near_earth_objects", []))
        
        return {
            "status": "online" if has_api_key else "offline",
            "has_api_key": has_api_key,
            "test_neos_count": neos_count,
            "api_base_url": nasa_service.base_url,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "error",
            "has_api_key": nasa_service.api_key is not None,
            "error": str(e),
            "api_base_url": nasa_service.base_url,
            "timestamp": datetime.now().isoformat()
        }