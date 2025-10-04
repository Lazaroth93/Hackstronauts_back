
"""
Data Ingestor para obtener y almacenar datos de NEOs de la NASA API
Integrado desde workspace/prototipo1/ingestor/neo_ingest.py
"""

import os
import requests
import psycopg2
from psycopg2.extras import execute_values
import time
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

load_dotenv()

logger = logging.getLogger(__name__)

class DataIngestor:
    """
    Ingestor de datos para obtener y almacenar información de NEOs
    de la NASA API en la base de datos
    """
    
    def __init__(self):
        self.nasa_api_key = os.getenv("NASA_API_KEY")
        self.database_url = os.getenv("DATABASE_URL")
        self.api_base_url = "https://api.nasa.gov/neo/rest/v1"
        self.timeout = 30
        
        if not self.nasa_api_key:
            logger.warning("NASA_API_KEY no encontrada. Usando datos de prueba.")
        if not self.database_url:
            raise RuntimeError("DATABASE_URL no encontrada")
    
    def _get_connection(self, retries: int = 5, delay: int = 5):
        """Intentos de conexión a la base de datos con reintentos."""
        for i in range(retries):
            try:
                conn = psycopg2.connect(
                    self.database_url, 
                    cursor_factory=psycopg2.extras.RealDictCursor
                )
                return conn
            except psycopg2.OperationalError:
                logger.warning(f"[Data Ingestor] DB no disponible, reintentando ({i+1}/{retries})...")
                time.sleep(delay)
        raise Exception("[Data Ingestor] No se pudo conectar a la DB")
    
    def get_neo_data(self, max_neos: int = 1000) -> List[Dict[str, Any]]:
        """
        Obtiene datos de NEOs de la NASA API
        
        Args:
            max_neos: Número máximo de NEOs a obtener
            
        Returns:
            Lista de datos de NEOs
        """
        if not self.nasa_api_key:
            logger.warning("NASA_API_KEY no encontrada, usando datos de prueba")
            return self._get_mock_neo_data()
        
        try:
            logger.info(f"[Data Ingestor] Obteniendo datos de {max_neos} NEOs...")
            neos_data = []
            page = 0
            per_page = 50  # NASA API limita a 50 por página
            
            while len(neos_data) < max_neos and page < 50:  # Máximo 50 páginas
                try:
                    response = requests.get(
                        f"{self.api_base_url}/neo/browse",
                        params={
                            "api_key": self.nasa_api_key,
                            "page": page,
                            "size": per_page
                        },
                        timeout=self.timeout
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        page_neos = data.get("near_earth_objects", [])
                        
                        if not page_neos:
                            logger.info(f"[Data Ingestor] No más NEOs disponibles en página {page}")
                            break
                        
                        for neo in page_neos:
                            # Filtrar por proximidad a la Tierra (menos de 10 millones de km)
                            if neo.get("close_approach_data"):
                                closest_approach = min(
                                    neo["close_approach_data"],
                                    key=lambda x: float(x["miss_distance"]["kilometers"])
                                )
                                miss_distance = float(closest_approach["miss_distance"]["kilometers"])
                                
                                if miss_distance < 10000000:  # 10 millones de km
                                    processed_neo = self._process_neo_data(neo)
                                    if processed_neo:
                                        neos_data.append(processed_neo)
                                        
                                        if len(neos_data) >= max_neos:
                                            break
                        
                        page += 1
                        logger.info(f"[Data Ingestor] Página {page} procesada, {len(neos_data)} NEOs obtenidos")
                        
                    else:
                        logger.error(f"[Data Ingestor] Error en API: {response.status_code}")
                        break
                        
                except requests.exceptions.RequestException as e:
                    logger.error(f"[Data Ingestor] Error en petición: {e}")
                    break
                except Exception as e:
                    logger.error(f"[Data Ingestor] Error procesando página {page}: {e}")
                    break
            
            logger.info(f"[Data Ingestor] Obtenidos {len(neos_data)} NEOs de la NASA API")
            return neos_data
            
        except Exception as e:
            logger.error(f"[Data Ingestor] Error obteniendo datos de NEOs: {e}")
            return self._get_mock_neo_data()
    
    def _process_neo_data(self, neo: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Procesa datos de un NEO individual de la NASA API
        
        Args:
            neo: Datos crudos del NEO de la NASA
            
        Returns:
            Datos procesados del NEO o None si no es válido
        """
        try:
            # Obtener aproximación más cercana
            closest_approach = None
            if neo.get("close_approach_data"):
                closest_approach = min(
                    neo["close_approach_data"],
                    key=lambda x: float(x["miss_distance"]["kilometers"])
                )
            
            if not closest_approach:
                return None
            
            # Obtener datos de diámetro
            diameter_data = neo.get("estimated_diameter", {}).get("meters", {})
            diameter_min = diameter_data.get("estimated_diameter_min")
            diameter_max = diameter_data.get("estimated_diameter_max")
            
            # Obtener datos orbitales
            orbital_data = neo.get("orbital_data", {})
            orbit_class = orbital_data.get("orbit_class", {}).get("orbit_class_type")
            
            processed_neo = {
                "neo_id": neo["id"],
                "name": neo["name"],
                "absolute_magnitude_h": neo.get("absolute_magnitude_h"),
                "is_potentially_hazardous": neo.get("is_potentially_hazardous_asteroid", False),
                "close_approach_date": closest_approach["close_approach_date"],
                "miss_distance_km": float(closest_approach["miss_distance"]["kilometers"]),
                "velocity_km_s": float(closest_approach["relative_velocity"]["kilometers_per_second"]),
                "diameter_min_m": diameter_min,
                "diameter_max_m": diameter_max,
                "orbit_class": orbit_class,
                "nasa_jpl_url": neo.get("nasa_jpl_url"),
                "orbital_period": orbital_data.get("orbital_period"),
                "eccentricity": orbital_data.get("eccentricity"),
                "inclination": orbital_data.get("inclination"),
                "semi_major_axis": orbital_data.get("semi_major_axis"),
                "created_at": datetime.now().isoformat()
            }
            
            return processed_neo
            
        except Exception as e:
            logger.error(f"[Data Ingestor] Error procesando NEO {neo.get('id', 'unknown')}: {e}")
            return None
    
    def _get_mock_neo_data(self) -> List[Dict[str, Any]]:
        """Datos de prueba cuando no hay acceso a NASA API"""
        return [
            {
                "neo_id": "2000433",
                "name": "433 Eros (A898 PA)",
                "absolute_magnitude_h": 11.16,
                "is_potentially_hazardous": False,
                "close_approach_date": "2024-12-25",
                "miss_distance_km": 200000.0,
                "velocity_km_s": 3.43,
                "diameter_min_m": 16840.0,
                "diameter_max_m": 16840.0,
                "orbit_class": "Amor",
                "nasa_jpl_url": "https://ssd.jpl.nasa.gov/tools/sbdb_lookup.html#/?sstr=2000433",
                "orbital_period": 643.115,
                "eccentricity": 0.2228,
                "inclination": 10.828,
                "semi_major_axis": 1.458,
                "created_at": datetime.now().isoformat()
            },
            {
                "neo_id": "99942",
                "name": "99942 Apophis (2004 MN4)",
                "absolute_magnitude_h": 19.7,
                "is_potentially_hazardous": True,
                "close_approach_date": "2029-04-13",
                "miss_distance_km": 300.0,
                "velocity_km_s": 12.6,
                "diameter_min_m": 370.0,
                "diameter_max_m": 370.0,
                "orbit_class": "Aten",
                "nasa_jpl_url": "https://ssd.jpl.nasa.gov/tools/sbdb_lookup.html#/?sstr=99942",
                "orbital_period": 323.596,
                "eccentricity": 0.1912,
                "inclination": 3.331,
                "semi_major_axis": 0.922,
                "created_at": datetime.now().isoformat()
            }
        ]
    
    def store_neo_data(self, neos_data: List[Dict[str, Any]]) -> bool:
        """
        Almacena datos de NEOs en la base de datos
        
        Args:
            neos_data: Lista de datos de NEOs
            
        Returns:
            True si se almacenaron correctamente, False en caso contrario
        """
        if not neos_data:
            logger.warning("[Data Ingestor] No hay datos de NEOs para almacenar")
            return False
        
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            
            # Crear tabla si no existe
            cur.execute("""
            CREATE TABLE IF NOT EXISTS neos_dangerous (
                id SERIAL PRIMARY KEY,
                neo_id VARCHAR(64) UNIQUE NOT NULL,
                name VARCHAR(255) NOT NULL,
                absolute_magnitude_h DECIMAL(10,2),
                is_potentially_hazardous BOOLEAN DEFAULT FALSE,
                close_approach_date DATE,
                miss_distance_km DECIMAL(20,6),
                velocity_km_s DECIMAL(10,6),
                diameter_min_m DECIMAL(10,2),
                diameter_max_m DECIMAL(10,2),
                orbit_class VARCHAR(100),
                nasa_jpl_url TEXT,
                orbital_period DECIMAL(10,6),
                eccentricity DECIMAL(10,6),
                inclination DECIMAL(10,6),
                semi_major_axis DECIMAL(10,6),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Preparar datos para inserción
            insert_data = []
            for neo in neos_data:
                insert_data.append((
                    neo["neo_id"],
                    neo["name"],
                    neo.get("absolute_magnitude_h"),
                    neo.get("is_potentially_hazardous", False),
                    neo.get("close_approach_date"),
                    neo.get("miss_distance_km"),
                    neo.get("velocity_km_s"),
                    neo.get("diameter_min_m"),
                    neo.get("diameter_max_m"),
                    neo.get("orbit_class"),
                    neo.get("nasa_jpl_url"),
                    neo.get("orbital_period"),
                    neo.get("eccentricity"),
                    neo.get("inclination"),
                    neo.get("semi_major_axis")
                ))
            
            # Insertar datos (upsert)
            insert_query = """
            INSERT INTO neos_dangerous (
                neo_id, name, absolute_magnitude_h, is_potentially_hazardous,
                close_approach_date, miss_distance_km, velocity_km_s,
                diameter_min_m, diameter_max_m, orbit_class, nasa_jpl_url,
                orbital_period, eccentricity, inclination, semi_major_axis
            ) VALUES %s
            ON CONFLICT (neo_id) DO UPDATE SET
                name = EXCLUDED.name,
                absolute_magnitude_h = EXCLUDED.absolute_magnitude_h,
                is_potentially_hazardous = EXCLUDED.is_potentially_hazardous,
                close_approach_date = EXCLUDED.close_approach_date,
                miss_distance_km = EXCLUDED.miss_distance_km,
                velocity_km_s = EXCLUDED.velocity_km_s,
                diameter_min_m = EXCLUDED.diameter_min_m,
                diameter_max_m = EXCLUDED.diameter_max_m,
                orbit_class = EXCLUDED.orbit_class,
                nasa_jpl_url = EXCLUDED.nasa_jpl_url,
                orbital_period = EXCLUDED.orbital_period,
                eccentricity = EXCLUDED.eccentricity,
                inclination = EXCLUDED.inclination,
                semi_major_axis = EXCLUDED.semi_major_axis,
                created_at = CURRENT_TIMESTAMP
            """
            
            execute_values(
                cur, insert_query, insert_data, 
                template=None, page_size=100
            )
            
            conn.commit()
            logger.info(f"[Data Ingestor] {len(neos_data)} NEOs almacenados en la base de datos")
            return True
            
        except Exception as e:
            logger.error(f"[Data Ingestor] Error almacenando datos: {e}")
            conn.rollback()
            return False
        finally:
            cur.close()
            conn.close()
    
    def ingest_data(self, max_neos: int = 1000) -> Dict[str, Any]:
        """
        Proceso completo de ingesta de datos
        
        Args:
            max_neos: Número máximo de NEOs a obtener
            
        Returns:
            Resumen del proceso de ingesta
        """
        try:
            logger.info(f"[Data Ingestor] Iniciando ingesta de datos (máximo {max_neos} NEOs)...")
            
            # Obtener datos de NEOs
            neos_data = self.get_neo_data(max_neos)
            
            if not neos_data:
                return {
                    "success": False,
                    "error": "No se pudieron obtener datos de NEOs",
                    "neos_processed": 0,
                    "timestamp": datetime.now().isoformat()
                }
            
            # Almacenar en base de datos
            storage_success = self.store_neo_data(neos_data)
            
            if not storage_success:
                return {
                    "success": False,
                    "error": "Error almacenando datos en la base de datos",
                    "neos_processed": len(neos_data),
                    "timestamp": datetime.now().isoformat()
                }
            
            # Estadísticas
            hazardous_count = sum(1 for neo in neos_data if neo.get("is_potentially_hazardous", False))
            avg_diameter = sum(
                (neo.get("diameter_min_m", 0) + neo.get("diameter_max_m", 0)) / 2 
                for neo in neos_data 
                if neo.get("diameter_min_m") and neo.get("diameter_max_m")
            ) / len(neos_data) if neos_data else 0
            
            return {
                "success": True,
                "neos_processed": len(neos_data),
                "hazardous_count": hazardous_count,
                "avg_diameter_m": avg_diameter,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"[Data Ingestor] Error en ingesta de datos: {e}")
            return {
                "success": False,
                "error": str(e),
                "neos_processed": 0,
                "timestamp": datetime.now().isoformat()
            }

# Instancia global del ingestor
data_ingestor = DataIngestor()
