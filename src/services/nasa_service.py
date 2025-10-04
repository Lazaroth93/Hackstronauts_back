"""
Servicio para integración con NASA API
Obtiene datos reales de NEOs directamente de la NASA
"""

import os
import requests
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class NASAService:
    """Servicio para obtener datos de NEOs de la NASA API"""
    
    def __init__(self):
        self.api_key = os.getenv("NASA_API_KEY")
        self.base_url = "https://api.nasa.gov/neo/rest/v1"
        self.timeout = 30
        
        if not self.api_key:
            logger.warning("NASA_API_KEY no encontrada. Usando datos de prueba.")
    
    async def get_neos_browse(self, page: int = 0, size: int = 20) -> Dict[str, Any]:
        """
        Obtiene lista de NEOs usando el endpoint browse de la NASA
        
        Args:
            page: Número de página (0-indexed)
            size: Número de NEOs por página (máximo 20)
            
        Returns:
            Dict con datos de NEOs de la NASA
        """
        if not self.api_key:
            return self._get_mock_data()
        
        try:
            url = f"{self.base_url}/neo/browse"
            params = {
                "api_key": self.api_key,
                "page": page,
                "size": min(size, 20)  # NASA limita a 20 por página
            }
            
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Obtenidos {len(data.get('near_earth_objects', []))} NEOs de la NASA")
            
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error obteniendo datos de NASA: {e}")
            return self._get_mock_data()
        except Exception as e:
            logger.error(f"Error inesperado: {e}")
            return self._get_mock_data()
    
    async def get_neo_by_id(self, neo_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene datos específicos de un NEO por ID
        
        Args:
            neo_id: ID del NEO
            
        Returns:
            Dict con datos del NEO o None si no se encuentra
        """
        if not self.api_key:
            return self._get_mock_neo_by_id(neo_id)
        
        try:
            url = f"{self.base_url}/neo/{neo_id}"
            params = {"api_key": self.api_key}
            
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Obtenidos datos del NEO {neo_id} de la NASA")
            
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error obteniendo NEO {neo_id} de NASA: {e}")
            return self._get_mock_neo_by_id(neo_id)
        except Exception as e:
            logger.error(f"Error inesperado: {e}")
            return self._get_mock_neo_by_id(neo_id)
    
    async def get_feed(self, start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """
        Obtiene feed de NEOs para un rango de fechas
        
        Args:
            start_date: Fecha de inicio (YYYY-MM-DD)
            end_date: Fecha de fin (YYYY-MM-DD)
            
        Returns:
            Dict con datos del feed de NEOs
        """
        if not self.api_key:
            return self._get_mock_feed()
        
        # Si no se proporcionan fechas, usar los próximos 7 días
        if not start_date:
            start_date = datetime.now().strftime("%Y-%m-%d")
        if not end_date:
            end_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        
        try:
            url = f"{self.base_url}/feed"
            params = {
                "api_key": self.api_key,
                "start_date": start_date,
                "end_date": end_date
            }
            
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Obtenido feed de NEOs del {start_date} al {end_date}")
            
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error obteniendo feed de NASA: {e}")
            return self._get_mock_feed()
        except Exception as e:
            logger.error(f"Error inesperado: {e}")
            return self._get_mock_feed()
    
    def _get_mock_data(self) -> Dict[str, Any]:
        """Datos de prueba cuando no hay API key de NASA"""
        return {
            "near_earth_objects": [
                {
                    "id": "2000433",
                    "name": "433 Eros (A898 PA)",
                    "absolute_magnitude_h": 11.16,
                    "is_potentially_hazardous_asteroid": False,
                    "close_approach_data": [
                        {
                            "close_approach_date": "2024-12-25",
                            "miss_distance": {"kilometers": "200000.0"},
                            "relative_velocity": {"kilometers_per_second": "3.43"}
                        }
                    ],
                    "estimated_diameter": {
                        "meters": {
                            "estimated_diameter_min": 16840.0,
                            "estimated_diameter_max": 16840.0
                        }
                    },
                    "orbital_data": {
                        "orbit_class": {
                            "orbit_class_type": "Amor"
                        }
                    }
                },
                {
                    "id": "99942",
                    "name": "99942 Apophis (2004 MN4)",
                    "absolute_magnitude_h": 19.7,
                    "is_potentially_hazardous_asteroid": True,
                    "close_approach_data": [
                        {
                            "close_approach_date": "2029-04-13",
                            "miss_distance": {"kilometers": "300.0"},
                            "relative_velocity": {"kilometers_per_second": "12.6"}
                        }
                    ],
                    "estimated_diameter": {
                        "meters": {
                            "estimated_diameter_min": 370.0,
                            "estimated_diameter_max": 370.0
                        }
                    },
                    "orbital_data": {
                        "orbit_class": {
                            "orbit_class_type": "Aten"
                        }
                    }
                }
            ]
        }
    
    def _get_mock_neo_by_id(self, neo_id: str) -> Optional[Dict[str, Any]]:
        """Datos de prueba para un NEO específico"""
        mock_data = self._get_mock_data()
        for neo in mock_data["near_earth_objects"]:
            if neo["id"] == neo_id:
                return neo
        return None
    
    def _get_mock_feed(self) -> Dict[str, Any]:
        """Feed de prueba"""
        return {
            "near_earth_objects": {
                datetime.now().strftime("%Y-%m-%d"): self._get_mock_data()["near_earth_objects"]
            }
        }
    
    def transform_nasa_data(self, nasa_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Transforma datos de la NASA al formato interno
        
        Args:
            nasa_data: Datos crudos de la NASA API
            
        Returns:
            Lista de NEOs en formato interno
        """
        neos = []
        
        for neo_data in nasa_data.get("near_earth_objects", []):
            # Obtener el acercamiento más cercano
            closest_approach = None
            if neo_data.get("close_approach_data"):
                closest_approach = min(
                    neo_data["close_approach_data"],
                    key=lambda x: float(x["miss_distance"]["kilometers"])
                )
            
            neo = {
                "neo_id": neo_data["id"],
                "name": neo_data["name"],
                "absolute_magnitude_h": neo_data.get("absolute_magnitude_h"),
                "is_potentially_hazardous": neo_data.get("is_potentially_hazardous_asteroid", False),
                "close_approach_date": closest_approach["close_approach_date"] if closest_approach else None,
                "miss_distance_km": float(closest_approach["miss_distance"]["kilometers"]) if closest_approach else None,
                "velocity_km_s": float(closest_approach["relative_velocity"]["kilometers_per_second"]) if closest_approach else None,
                "diameter_min_m": neo_data.get("estimated_diameter", {}).get("meters", {}).get("estimated_diameter_min"),
                "diameter_max_m": neo_data.get("estimated_diameter", {}).get("meters", {}).get("estimated_diameter_max"),
                "orbit_class": neo_data.get("orbital_data", {}).get("orbit_class", {}).get("orbit_class_type"),
                "source": "nasa_api",
                "last_updated": datetime.now().isoformat()
            }
            
            neos.append(neo)
        
        return neos

# Instancia global del servicio
nasa_service = NASAService()