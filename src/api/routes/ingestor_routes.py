"""
Rutas para el ingestor de datos de NEOs
Permite obtener y almacenar datos de la NASA API
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime

from ...services.data_ingestor import data_ingestor

# Crear el router para ingestor
ingestor_router = APIRouter(prefix="/ingestor", tags=["Data Ingestor"])

class IngestRequest(BaseModel):
    """Request para ingesta de datos"""
    max_neos: int = 1000
    force_refresh: bool = False

class IngestResponse(BaseModel):
    """Response de ingesta de datos"""
    success: bool
    neos_processed: int
    hazardous_count: int
    avg_diameter_m: float
    timestamp: str
    error: Optional[str] = None

@ingestor_router.post("/ingest", response_model=IngestResponse)
async def ingest_neo_data(request: IngestRequest):
    """
    Ingesta datos de NEOs de la NASA API
    
    Args:
        request: Parámetros de ingesta
        
    Returns:
        Resultado del proceso de ingesta
    """
    try:
        # Realizar ingesta de datos
        result = data_ingestor.ingest_data(max_neos=request.max_neos)
        
        if result["success"]:
            return IngestResponse(
                success=True,
                neos_processed=result["neos_processed"],
                hazardous_count=result["hazardous_count"],
                avg_diameter_m=result["avg_diameter_m"],
                timestamp=result["timestamp"]
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Error desconocido en ingesta de datos")
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error en ingesta de datos: {str(e)}"
        )

@ingestor_router.get("/status", response_model=Dict[str, Any])
async def get_ingestor_status():
    """
    Obtiene el estado del ingestor de datos
    
    Returns:
        Estado del ingestor
    """
    try:
        # Verificar conexión a la base de datos
        conn = data_ingestor._get_connection()
        cur = conn.cursor()
        
        # Contar NEOs en la base de datos
        cur.execute("SELECT COUNT(*) FROM neos_dangerous")
        total_neos = cur.fetchone()["count"]
        
        cur.execute("SELECT COUNT(*) FROM neos_dangerous WHERE is_potentially_hazardous = TRUE")
        hazardous_neos = cur.fetchone()["count"]
        
        cur.close()
        conn.close()
        
        return {
            "status": "online",
            "database_connected": True,
            "total_neos": total_neos,
            "hazardous_neos": hazardous_neos,
            "nasa_api_available": data_ingestor.nasa_api_key is not None,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "error",
            "database_connected": False,
            "error": str(e),
            "nasa_api_available": data_ingestor.nasa_api_key is not None,
            "timestamp": datetime.now().isoformat()
        }

@ingestor_router.get("/neos/count", response_model=Dict[str, Any])
async def get_neo_count():
    """
    Obtiene el número de NEOs almacenados en la base de datos
    
    Returns:
        Conteo de NEOs
    """
    try:
        conn = data_ingestor._get_connection()
        cur = conn.cursor()
        
        # Contar NEOs totales
        cur.execute("SELECT COUNT(*) FROM neos_dangerous")
        total_neos = cur.fetchone()["count"]
        
        # Contar NEOs peligrosos
        cur.execute("SELECT COUNT(*) FROM neos_dangerous WHERE is_potentially_hazardous = TRUE")
        hazardous_neos = cur.fetchone()["count"]
        
        # Contar por clase orbital (si la columna existe)
        try:
            cur.execute("""
            SELECT orbit_class, COUNT(*) as count
            FROM neos_dangerous
            WHERE orbit_class IS NOT NULL
            GROUP BY orbit_class
            ORDER BY count DESC
            """)
            orbital_distribution = cur.fetchall()
        except psycopg2.Error:
            # Si la columna no existe, usar distribución simple
            orbital_distribution = []
        
        cur.close()
        conn.close()
        
        return {
            "total_neos": total_neos,
            "hazardous_neos": hazardous_neos,
            "safe_neos": total_neos - hazardous_neos,
            "orbital_distribution": [
                {"orbit_class": row["orbit_class"], "count": row["count"]}
                for row in orbital_distribution
            ],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo conteo de NEOs: {str(e)}"
        )

@ingestor_router.delete("/neos", response_model=Dict[str, Any])
async def clear_neo_data():
    """
    Limpia todos los datos de NEOs de la base de datos
    
    Returns:
        Resultado de la limpieza
    """
    try:
        conn = data_ingestor._get_connection()
        cur = conn.cursor()
        
        # Contar NEOs antes de eliminar
        cur.execute("SELECT COUNT(*) FROM neos_dangerous")
        neos_before = cur.fetchone()["count"]
        
        # Eliminar todos los NEOs
        cur.execute("DELETE FROM neos_dangerous")
        
        conn.commit()
        
        cur.close()
        conn.close()
        
        return {
            "success": True,
            "neos_deleted": neos_before,
            "message": f"Se eliminaron {neos_before} NEOs de la base de datos",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error limpiando datos de NEOs: {str(e)}"
        )