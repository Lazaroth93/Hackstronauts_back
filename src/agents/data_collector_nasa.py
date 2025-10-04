"""
DataCollectorAgent - Recolecta datos reales de asteroides desde NASA API.

Funcionalidad:
- Obtiene datos reales de asteroides de la NASA
- Procesa información orbital y física
- Genera predicciones con confianza
- Incluye manejo de errores y fallback
"""

import httpx
import os
from typing import Dict, Any, Optional, List
from .base_agent import BaseAgent, AgentState
from ..supervisors.hybrid_supervisor import HybridSupervisor
from ..database.postgres_connector import PostgreSQLConnector
from dotenv import load_dotenv

load_dotenv()


class DataCollectorAgentNASA(BaseAgent):
    """Agente que recolecta datos reales de asteroides desde NASA API."""
    
    def __init__(self, supervisor: Optional[HybridSupervisor] = None):
        super().__init__(
            name="DataCollectorAgent",
            description="Recolecta datos de PostgreSQL con fallback a NASA API"
        )
        self.supervisor = supervisor
        self.api_key = os.getenv("NASA_API_KEY", "DEMO_KEY")
        self.base_url = "https://api.nasa.gov/neo/rest/v1"
        
        # Conector PostgreSQL
        try:
            self.db = PostgreSQLConnector()
            print("✅ Conector PostgreSQL inicializado")
        except Exception as e:
            print(f"⚠️ Error inicializando PostgreSQL: {e}")
            self.db = None
    
    async def execute(self, state: AgentState) -> AgentState:
        """Ejecuta la recolección híbrida de datos."""
        print("DataCollectorAgent: Iniciando recolección híbrida...")
        
        try:
            if not self.validate_input(state):
                self.log_error(state, "Datos inválidos")
                return state
            
            # Obtener ID del asteroide
            asteroid_id = state.asteroid_data.get("id")
            if not asteroid_id:
                self.log_error(state, "ID de asteroide no encontrado")
                return state
            
            # 1. Intentar obtener datos de PostgreSQL primero
            asteroid_data = None
            data_source = "unknown"
            
            if self.db:
                print(f"DataCollectorAgent: Buscando datos en PostgreSQL para {asteroid_id}")
                postgres_data = self.db.get_neo_by_id(asteroid_id)
                if postgres_data:
                    print("DataCollectorAgent: Datos encontrados en PostgreSQL")
                    asteroid_data = self._format_postgres_data(postgres_data)
                    data_source = "postgresql"
            
            # 2. Si no hay datos en PostgreSQL, usar NASA API
            if not asteroid_data:
                print(f"DataCollectorAgent: Recolectando datos de NASA API para {asteroid_id}")
                asteroid_data = await self._collect_real_data(asteroid_id)
                data_source = "nasa_api"
            
            if not asteroid_data:
                self.log_error(state, "No se pudieron obtener datos del asteroide")
                return state
            
            # 3. Obtener aproximaciones cercanas
            close_approach_data = []
            if self.db and data_source == "postgresql":
                close_approach_data = self.db.get_close_approaches(asteroid_id)
            
            if not close_approach_data:
                close_approach_data = self._process_close_approaches(asteroid_data)
            
            # 4. Procesar datos orbitales
            orbital_data = self._process_orbital_data(asteroid_data)
            
            # Generar predicción LLM
            prediction = await self._generate_prediction(asteroid_data, {
                "orbital_data": orbital_data,
                "close_approach_data": close_approach_data
            })
            
            # Supervisión híbrida con confianza mejorada
            if self.supervisor:
                collection_data = {
                    "asteroid_data": asteroid_data,
                    "orbital_data": orbital_data,
                    "close_approach_data": close_approach_data,
                    "prediction": prediction
                }
                supervision_result = await self.supervisor.supervise_agent_execution(
                    self.name, collection_data, {"agent_name": self.name}
                )
                state.supervision_results = supervision_result
                
                # Calcular confianzas específicas usando el sistema mejorado
                if hasattr(self.supervisor, 'confidence_system'):
                    confidence_metrics = self.supervisor.confidence_system.update_confidence(
                        validation_reports=supervision_result.get("validation_reports", []),
                        asteroid_data=asteroid_data,
                        prediction_data=prediction
                    )
                    
                    # Agregar confianzas específicas al resultado
                    state.data_collection_result["confidence_metrics"] = {
                        "overall_confidence": confidence_metrics.overall_confidence,
                        "scientific_confidence": confidence_metrics.scientific_confidence,
                        "rag_confidence": confidence_metrics.rag_confidence,
                        "orbital_confidence": confidence_metrics.orbital_confidence,
                        "data_quality_confidence": confidence_metrics.data_quality_confidence,
                        "prediction_confidence": confidence_metrics.prediction_confidence,
                        "trend": confidence_metrics.trend,
                        "alert_level": confidence_metrics.alert_level
                    }
                    
                    # Mostrar confianzas en consola
                    print(f"DataCollectorAgent: Confianza general: {confidence_metrics.overall_confidence:.1%}")
                    print(f"DataCollectorAgent: Confianza orbital: {confidence_metrics.orbital_confidence:.1%}")
                    print(f"DataCollectorAgent: Confianza de datos: {confidence_metrics.data_quality_confidence:.1%}")
                    print(f"DataCollectorAgent: Confianza de predicción: {confidence_metrics.prediction_confidence:.1%}")
            
            # Actualizar estado (preservando confianzas si existen)
            state.data_collection_result.update({
                "asteroid_data": asteroid_data,
                "orbital_data": orbital_data,
                "close_approach_data": close_approach_data,
                "prediction": prediction,
                "data_source": data_source,
                "status": "success"
            })
            
            print(f"DataCollectorAgent: Datos recolectados exitosamente desde {data_source}")
            print(f"DataCollectorAgent: Asteroide: {asteroid_data.get('name', 'Unknown')}")
            print(f"DataCollectorAgent: Diámetro: {asteroid_data.get('diameter_min', 0):.1f} - {asteroid_data.get('diameter_max', 0):.1f} km")
            print(f"DataCollectorAgent: Peligroso: {asteroid_data.get('is_potentially_hazardous_asteroid', False)}")
            
        except Exception as e:
            self.log_error(state, f"Error: {str(e)}")
        
        return state
    
    def validate_input(self, state: AgentState) -> bool:
        """Valida datos de entrada."""
        return (state.asteroid_data and 
                state.asteroid_data.get("id"))
    
    async def _collect_real_data(self, asteroid_id: str) -> Optional[Dict[str, Any]]:
        """Recolecta datos reales del asteroide desde NASA API."""
        try:
            url = f"{self.base_url}/neo/{asteroid_id}"
            params = {"api_key": self.api_key}
            
            print(f"DataCollectorAgent: Llamando a NASA API: {url}")
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=30.0)
            
            if response.status_code == 200:
                data = response.json()
                print(f"DataCollectorAgent: Datos reales obtenidos exitosamente para {asteroid_id}")
                return self._extract_asteroid_data(data)
            else:
                print(f"DataCollectorAgent: Error en API: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"DataCollectorAgent: Error en recolección: {e}")
            return None
    
    def _extract_asteroid_data(self, api_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extrae y procesa datos relevantes del asteroide."""
        # Datos básicos
        name = api_data.get("name", "Unknown")
        diameter = api_data.get("estimated_diameter", {})
        diameter_km = diameter.get("kilometers", {})
        
        # Datos orbitales
        orbital_data = api_data.get("orbital_data", {})
        
        # Datos de aproximaciones cercanas
        close_approaches = api_data.get("close_approach_data", [])
        
        return {
            "id": api_data.get("neo_reference_id", "Unknown"),
            "name": name,
            "diameter_min": diameter_km.get("estimated_diameter_min", 0),
            "diameter_max": diameter_km.get("estimated_diameter_max", 0),
            "is_potentially_hazardous_asteroid": api_data.get("is_potentially_hazardous_asteroid", False),
            "orbital_data": orbital_data,
            "close_approach_data": close_approaches,
            "absolute_magnitude_h": api_data.get("absolute_magnitude_h", 0),
            "nasa_jpl_url": api_data.get("nasa_jpl_url", ""),
            "orbital_period": orbital_data.get("orbital_period", 0),
            "eccentricity": orbital_data.get("eccentricity", 0),
            "inclination": orbital_data.get("inclination", 0),
            "semi_major_axis": orbital_data.get("semi_major_axis", 0)
        }
    
    def _process_orbital_data(self, asteroid_data: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa datos orbitales del asteroide."""
        orbital_data = asteroid_data.get("orbital_data", {})
        
        return {
            "eccentricity": float(orbital_data.get("eccentricity", 0)),
            "inclination": float(orbital_data.get("inclination", 0)),
            "semi_major_axis": float(orbital_data.get("semi_major_axis", 0)),
            "orbital_period": float(orbital_data.get("orbital_period", 0)),
            "perihelion_distance": float(orbital_data.get("perihelion_distance", 0)),
            "aphelion_distance": float(orbital_data.get("aphelion_distance", 0)),
            "orbital_classification": orbital_data.get("orbit_class", "Unknown")
        }
    
    def _process_close_approaches(self, asteroid_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Procesa datos de aproximaciones cercanas."""
        approaches = []
        close_approach_data = asteroid_data.get("close_approach_data", [])
        
        for approach in close_approach_data:
            approach_info = {
                "date": approach.get("close_approach_date", "Unknown"),
                "miss_distance_km": float(approach.get("miss_distance", {}).get("kilometers", "0")),
                "miss_distance_au": float(approach.get("miss_distance", {}).get("astronomical", "0")),
                "relative_velocity_kmh": float(approach.get("relative_velocity", {}).get("kilometers_per_hour", "0")),
                "relative_velocity_ms": float(approach.get("relative_velocity", {}).get("kilometers_per_hour", "0")) / 3.6,
                "orbiting_body": approach.get("orbiting_body", "Earth")
            }
            approaches.append(approach_info)
        
        # Ordenar por fecha (más recientes primero)
        return sorted(approaches, key=lambda x: x["date"], reverse=True)
    
    async def _generate_prediction(self, asteroid_data: Dict[str, Any], 
                                 collection_data: Dict[str, Any]) -> Dict[str, Any]:
        """Genera predicción usando LLM."""
        try:
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                return self._get_fallback_prediction(asteroid_data, collection_data)
            
            # Crear prompt simple
            name = asteroid_data.get("name", "Unknown")
            diameter = asteroid_data.get("diameter_min", 0)
            hazardous = asteroid_data.get("is_potentially_hazardous_asteroid", False)
            approaches = len(collection_data.get("close_approach_data", []))
            
            prompt = f"""
            Analiza estos datos del asteroide {name}:
            
            Diámetro: {diameter:.1f} km
            Peligroso: {'Sí' if hazardous else 'No'}
            Aproximaciones cercanas: {approaches}
            
            Responde en JSON con:
            - risk_assessment: "Bajo", "Medio", "Alto", o "Extremo"
            - monitoring_priority: "Baja", "Media", "Alta", o "Crítica"
            - key_characteristics: lista de características clave
            - confidence_level: nivel de confianza (0-1)
            - summary: resumen en español
            """
            
            # Llamar a Groq API
            import httpx
            import json
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                    json={
                        "model": "llama-3.1-8b-instant",
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.3,
                        "max_tokens": 600
                    },
                    timeout=30.0
                )
            
            if response.status_code == 200:
                content = response.json()["choices"][0]["message"]["content"]
                try:
                    return json.loads(content)
                except:
                    pass
            
        except Exception as e:
            print(f"Error LLM: {e}")
        
        return self._get_fallback_prediction(asteroid_data, collection_data)
    
    def _get_fallback_prediction(self, asteroid_data: Dict[str, Any], 
                               collection_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predicción de respaldo."""
        hazardous = asteroid_data.get("is_potentially_hazardous_asteroid", False)
        diameter = asteroid_data.get("diameter_min", 0)
        
        # Determinar nivel de riesgo
        if hazardous and diameter > 1:
            risk_assessment = "Alto"
            monitoring_priority = "Alta"
        elif hazardous or diameter > 0.5:
            risk_assessment = "Medio"
            monitoring_priority = "Media"
        else:
            risk_assessment = "Bajo"
            monitoring_priority = "Baja"
        
        return {
            "risk_assessment": risk_assessment,
            "monitoring_priority": monitoring_priority,
            "key_characteristics": [
                f"Diámetro: {diameter:.1f} km",
                f"Peligroso: {'Sí' if hazardous else 'No'}",
                f"Aproximaciones: {len(collection_data.get('close_approach_data', []))}"
            ],
            "confidence_level": 0.6,
            "summary": f"Análisis de datos para {asteroid_data.get('name', 'Unknown')}. Riesgo: {risk_assessment}"
        }
    
    def _format_postgres_data(self, postgres_data: Dict[str, Any]) -> Dict[str, Any]:
        """Formatear datos de PostgreSQL al formato esperado"""
        return {
            "id": postgres_data.get("neo_id"),
            "name": postgres_data.get("name"),
            "diameter_min": postgres_data.get("estimated_diameter_min_m"),
            "diameter_max": postgres_data.get("estimated_diameter_max_m"),
            "is_potentially_hazardous_asteroid": postgres_data.get("is_potentially_hazardous", False),
            "absolute_magnitude_h": postgres_data.get("absolute_magnitude_h"),
            "nasa_jpl_url": postgres_data.get("nasa_jpl_url"),
            "raw_data": postgres_data.get("raw_data", {})
        }