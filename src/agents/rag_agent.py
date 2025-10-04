"""
RAG Agent para búsqueda vectorial y análisis de documentos
Integrado desde workspace/prototipo1/agents/neo_rag_agent/
"""

import os
import time
import psycopg2
import psycopg2.extras
import requests
import json
from datetime import datetime
import numpy as np
from typing import List, Dict, Any, Optional
import logging

from .base_agent import BaseAgent, AgentState

logger = logging.getLogger(__name__)

class RAGAgent(BaseAgent):
    """
    Agente RAG (Retrieval-Augmented Generation) para búsqueda vectorial
    y análisis de documentos relacionados con asteroides
    """
    
    def __init__(self):
        super().__init__()
        self.name = "RAGAgent"
        self.description = "Agente RAG para búsqueda vectorial y análisis de documentos"
        self.database_url = os.getenv("DATABASE_URL")
        self.nasa_api_key = os.getenv("NASA_API_KEY")
    
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
                logger.warning(f"[RAG Agent] DB no disponible, reintentando ({i+1}/{retries})...")
                time.sleep(delay)
        raise Exception("[RAG Agent] No se pudo conectar a la DB")
    
    def _get_neo_data(self) -> List[Dict[str, Any]]:
        """Obtiene datos reales de NEOs de la NASA API."""
        if not self.nasa_api_key:
            logger.warning("NASA_API_KEY no encontrada, usando datos de prueba")
            return self._get_mock_neo_data()
        
        try:
            response = requests.get(
                "https://api.nasa.gov/neo/rest/v1/neo/browse",
                params={
                    "api_key": self.nasa_api_key,
                    "page": 0,
                    "size": 20
                },
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            neos = []
            for neo_data in data.get("near_earth_objects", []):
                neo = {
                    "neo_id": neo_data["id"],
                    "name": neo_data["name"],
                    "absolute_magnitude": neo_data.get("absolute_magnitude_h"),
                    "is_potentially_hazardous": neo_data.get("is_potentially_hazardous_asteroid", False),
                    "close_approach_date": None,
                    "miss_distance_km": None,
                    "velocity_km_s": None,
                    "diameter_min_m": None,
                    "diameter_max_m": None,
                    "orbit_class": neo_data.get("orbital_data", {}).get("orbit_class", {}).get("orbit_class_type")
                }
                
                # Obtener datos de aproximación más cercana
                if neo_data.get("close_approach_data"):
                    closest_approach = min(
                        neo_data["close_approach_data"],
                        key=lambda x: float(x["miss_distance"]["kilometers"])
                    )
                    neo["close_approach_date"] = closest_approach["close_approach_date"]
                    neo["miss_distance_km"] = float(closest_approach["miss_distance"]["kilometers"])
                    neo["velocity_km_s"] = float(closest_approach["relative_velocity"]["kilometers_per_second"])
                
                # Obtener datos de diámetro
                if neo_data.get("estimated_diameter", {}).get("meters"):
                    diameter_data = neo_data["estimated_diameter"]["meters"]
                    neo["diameter_min_m"] = diameter_data.get("estimated_diameter_min")
                    neo["diameter_max_m"] = diameter_data.get("estimated_diameter_max")
                
                neos.append(neo)
            
            logger.info(f"[RAG Agent] Obtenidos {len(neos)} NEOs de la NASA API")
            return neos
            
        except Exception as e:
            logger.error(f"[RAG Agent] Error obteniendo datos de NASA: {e}")
            return self._get_mock_neo_data()
    
    def _get_mock_neo_data(self) -> List[Dict[str, Any]]:
        """Datos de prueba cuando no hay acceso a NASA API"""
        return [
            {
                "neo_id": "2000433",
                "name": "433 Eros (A898 PA)",
                "absolute_magnitude": 11.16,
                "is_potentially_hazardous": False,
                "close_approach_date": "2024-12-25",
                "miss_distance_km": 200000.0,
                "velocity_km_s": 3.43,
                "diameter_min_m": 16840.0,
                "diameter_max_m": 16840.0,
                "orbit_class": "Amor"
            },
            {
                "neo_id": "99942",
                "name": "99942 Apophis (2004 MN4)",
                "absolute_magnitude": 19.7,
                "is_potentially_hazardous": True,
                "close_approach_date": "2029-04-13",
                "miss_distance_km": 300.0,
                "velocity_km_s": 12.6,
                "diameter_min_m": 370.0,
                "diameter_max_m": 370.0,
                "orbit_class": "Aten"
            }
        ]
    
    def _store_documents(self, neos: List[Dict[str, Any]]) -> int:
        """Almacena documentos en la base de datos para búsqueda vectorial"""
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            
            # Limpiar documentos existentes
            cur.execute("DELETE FROM documents WHERE source = 'nasa_api'")
            
            documents = []
            for neo in neos:
                # Crear contenido del documento
                content = f"""
                Asteroide: {neo['name']}
                ID: {neo['neo_id']}
                Diámetro: {neo.get('diameter_min_m', 'N/A')} - {neo.get('diameter_max_m', 'N/A')} metros
                Velocidad: {neo.get('velocity_km_s', 'N/A')} km/s
                Distancia de fallo: {neo.get('miss_distance_km', 'N/A')} km
                Peligroso: {'Sí' if neo.get('is_potentially_hazardous') else 'No'}
                Clase orbital: {neo.get('orbit_class', 'N/A')}
                Fecha de aproximación: {neo.get('close_approach_date', 'N/A')}
                """
                
                # Crear embedding simple (en producción usar un modelo real)
                embedding = self._create_simple_embedding(content)
                
                documents.append((
                    f"neo_{neo['neo_id']}",
                    "nasa_api",
                    content.strip(),
                    json.dumps({
                        "neo_id": neo["neo_id"],
                        "name": neo["name"],
                        "is_potentially_hazardous": neo.get("is_potentially_hazardous", False),
                        "diameter_min": neo.get("diameter_min_m"),
                        "diameter_max": neo.get("diameter_max_m"),
                        "velocity": neo.get("velocity_km_s"),
                        "miss_distance": neo.get("miss_distance_km"),
                        "orbit_class": neo.get("orbit_class"),
                        "approach_date": neo.get("close_approach_date")
                    }),
                    embedding
                ))
            
            # Insertar documentos
            insert_query = """
            INSERT INTO documents (id, source, content, metadata, embedding)
            VALUES %s
            """
            psycopg2.extras.execute_values(
                cur, insert_query, documents, template=None, page_size=100
            )
            
            conn.commit()
            logger.info(f"[RAG Agent] Almacenados {len(documents)} documentos")
            return len(documents)
            
        except Exception as e:
            logger.error(f"[RAG Agent] Error almacenando documentos: {e}")
            conn.rollback()
            return 0
        finally:
            cur.close()
            conn.close()
    
    def _create_simple_embedding(self, text: str) -> List[float]:
        """Crea un embedding simple basado en características del texto"""
        # Embedding simple basado en características del texto
        # En producción, usar un modelo real como sentence-transformers
        
        # Normalizar texto
        text_lower = text.lower()
        
        # Características básicas
        features = [
            len(text),  # Longitud del texto
            text_lower.count("peligroso"),  # Palabras de peligro
            text_lower.count("asteroide"),  # Palabras relacionadas con asteroides
            text_lower.count("km"),  # Unidades de distancia
            text_lower.count("metros"),  # Unidades de tamaño
            text_lower.count("sí") if "peligroso: sí" in text_lower else 0,  # Es peligroso
            text_lower.count("no") if "peligroso: no" in text_lower else 0,  # No es peligroso
        ]
        
        # Crear embedding de 1536 dimensiones (compatible con pgvector)
        embedding = [0.0] * 1536
        for i, feature in enumerate(features):
            if i < 1536:
                embedding[i] = float(feature) / 1000.0  # Normalizar
        
        # Rellenar con valores aleatorios basados en el hash del texto
        import hashlib
        text_hash = int(hashlib.md5(text.encode()).hexdigest()[:8], 16)
        for i in range(len(features), 1536):
            embedding[i] = (text_hash % 1000) / 1000.0
            text_hash = text_hash // 1000
        
        return embedding
    
    def _search_documents(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Busca documentos similares usando búsqueda vectorial"""
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            
            # Crear embedding de la consulta
            query_embedding = self._create_simple_embedding(query)
            query_vector = "[" + ",".join(map(str, query_embedding)) + "]"
            
            # Búsqueda vectorial
            search_query = """
            SELECT id, source, content, metadata, 
                   (embedding <-> %s::vector) AS distance
            FROM documents
            ORDER BY embedding <-> %s::vector
            LIMIT %s
            """
            
            cur.execute(search_query, (query_vector, query_vector, top_k))
            results = cur.fetchall()
            
            logger.info(f"[RAG Agent] Encontrados {len(results)} documentos para consulta: {query}")
            return results
            
        except Exception as e:
            logger.error(f"[RAG Agent] Error en búsqueda vectorial: {e}")
            return []
        finally:
            cur.close()
            conn.close()
    
    async def execute(self, state: AgentState) -> AgentState:
        """
        Ejecuta el agente RAG para búsqueda vectorial y análisis de documentos
        """
        try:
            logger.info(f"[RAG Agent] Iniciando análisis RAG...")
            
            # Obtener datos de NEOs
            neos = self._get_neo_data()
            
            # Almacenar documentos
            documents_stored = self._store_documents(neos)
            
            # Realizar búsquedas de ejemplo
            search_queries = [
                "asteroides peligrosos",
                "objetos cercanos a la tierra",
                "impacto potencial",
                "monitoreo de asteroides"
            ]
            
            search_results = {}
            for query in search_queries:
                results = self._search_documents(query, top_k=3)
                search_results[query] = [
                    {
                        "id": row["id"],
                        "source": row["source"],
                        "content": row["content"][:200] + "...",  # Truncar contenido
                        "metadata": row["metadata"],
                        "similarity": 1.0 - float(row["distance"])  # Convertir distancia a similitud
                    }
                    for row in results
                ]
            
            # Actualizar estado
            state.rag_analysis = {
                "documents_stored": documents_stored,
                "search_results": search_results,
                "neos_analyzed": len(neos),
                "status": "success",
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"[RAG Agent] Análisis RAG completado - {documents_stored} documentos almacenados")
            return state
            
        except Exception as e:
            logger.error(f"[RAG Agent] Error en análisis RAG: {e}")
            state.rag_analysis = {
                "error": str(e),
                "status": "error",
                "timestamp": datetime.now().isoformat()
            }
            return state
