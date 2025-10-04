"""
DataCollectorAgent - Recolecta y valida datos de asteroides.

Este agente es el primero en ejecutarse y se encarga de:
- Obtener datos del asteroide (por ahora hardcodeados)
- Recolectar datos contextuales (terremotos, elevación, etc.)
- Validar y limpiar los datos obtenidos

¿Por qué es importante?
- Es el punto de entrada de datos reales
- Sin datos buenos, todo lo demás falla
- Maneja la integración con APIs externas (cuando se implemente)
- Valida que los datos sean correctos
"""

from typing import Dict, Any, Optional
from .base_agent import BaseAgent, AgentState
from ..supervisors.hybrid_supervisor import HybridSupervisor


class DataCollectorAgent(BaseAgent):
    """
    Agente responsable de recolectar datos de asteroides.
    
    Este agente es fundamental porque:
    - Es el primer paso en la simulación
    - Proporciona los datos base para todos los demás agentes
    - Valida que los datos sean correctos antes de continuar
    - Maneja la integración con fuentes de datos externas
    """
    
    def __init__(self, supervisor: Optional[HybridSupervisor] = None):
        super().__init__(
            name="DataCollectorAgent",
            description="Recolecta y valida datos de asteroides de fuentes externas"
        )
        self.supervisor = supervisor
        
        # URLs de las APIs (para uso futuro)
        self.nasa_base_url = "https://api.nasa.gov/neo/rest/v1"
        self.usgs_earthquake_url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
        
        # Datos hardcodeados para testing (simulan datos reales de la NASA)
        self.mock_asteroid_data = {
            "2000433": {  # Eros
                "id": "2000433",
                "name": "Eros",
                "diameter_min": 16.84,
                "diameter_max": 16.84,
                "hazardous": False,
                "close_approach_data": [
                    {
                        "close_approach_date": "2024-12-25",
                        "miss_distance": {"kilometers": "0.2"},
                        "relative_velocity": {"kilometers_per_hour": "12345.67"},
                        "orbiting_body": "Earth"
                    }
                ],
                "orbital_data": {
                    "eccentricity": "0.2227",
                    "inclination": "10.829",
                    "semi_major_axis": "1.458",
                    "perihelion_distance": "1.133",
                    "aphelion_distance": "1.783"
                },
                "physical_characteristics": {
                    "absolute_magnitude": 11.16,
                    "albedo": 0.25,
                    "spectral_type": "S"
                }
            },
            "2001862": {  # Apollo
                "id": "2001862",
                "name": "Apollo",
                "diameter_min": 1.5,
                "diameter_max": 1.5,
                "hazardous": True,
                "close_approach_data": [
                    {
                        "close_approach_date": "2024-02-20",
                        "miss_distance": {"kilometers": "0.05"},
                        "relative_velocity": {"kilometers_per_hour": "15678.90"},
                        "orbiting_body": "Earth"
                    }
                ],
                "orbital_data": {
                    "eccentricity": "0.5599",
                    "inclination": "6.353",
                    "semi_major_axis": "1.471",
                    "perihelion_distance": "0.647",
                    "aphelion_distance": "2.295"
                },
                "physical_characteristics": {
                    "absolute_magnitude": 16.25,
                    "albedo": 0.15,
                    "spectral_type": "Sq"
                }
            }
        }
    
    async def execute(self, state: AgentState) -> AgentState:
        """
        Ejecuta la recolección de datos del asteroide.
        
        Este método es el corazón del agente. Aquí es donde:
        - Se obtienen los datos del asteroide
        - Se validan los datos
        - Se procesan y limpian los datos
        - Se almacenan en el estado compartido
        
        Args:
            state: Estado actual de la simulación
            
        Returns:
            Estado actualizado con los datos recolectados
        """
        print("=" * 50)
        print("DataCollectorAgent: Iniciando recolección de datos...")
        
        try:
            # Validar que tenemos datos de entrada
            if not self.validate_input(state):
                self.log_error(state, "Datos de entrada inválidos")
                return state
            
            # Obtener ID del asteroide
            asteroid_id = state.asteroid_data.get("id", "unknown")
            print(f"DataCollectorAgent: Recolectando datos para asteroide {asteroid_id}")
            
            # Recolectar datos del asteroide (hardcodeados por ahora)
            asteroid_data = await self._collect_asteroid_data(asteroid_id)
            
            # Recolectar datos contextuales
            context_data = await self._collect_context_data(asteroid_id)
            
            # Preparar datos para supervisión
            collected_data = {
                "asteroid_data": asteroid_data,
                "context_data": context_data,
                "collection_timestamp": "2024-01-01T00:00:00Z",  # TODO: Usar timestamp real
                "status": "success",
                "source": "mock_data"  # Indica que son datos de prueba
            }
            
            # SUPERVISIÓN ANTI-ALUCINACIÓN
            if self.supervisor:
                print("DataCollectorAgent: Iniciando supervisión anti-alucinación...")
                supervision_context = {
                    "agent_name": self.name,
                    "data_type": "asteroid",
                    "simulation_id": getattr(state, 'simulation_id', 'unknown')
                }
                
                # Validar solo los datos del asteroide (no la estructura completa)
                supervision_result = await self.supervisor.supervise_agent_execution(
                    self.name, asteroid_data, supervision_context
                )
                
                # Verificar si la supervisión fue exitosa
                if supervision_result.get("recommendation") == "stop":
                    self.log_error(state, "Supervisión detectó errores críticos, deteniendo ejecución")
                    state.status = "failed"
                    return state
                elif supervision_result.get("recommendation") == "retry":
                    self.log_warning(state, "Supervisión detectó problemas, considerando reintento")
                
                # Agregar resultados de supervisión al estado
                state.supervision_results = supervision_result
            
            # Actualizar el estado con los datos recolectados
            state.data_collection_result = collected_data
            
            print("DataCollectorAgent: Datos recolectados exitosamente")
            print(f"DataCollectorAgent: Asteroide: {asteroid_data.get('name', 'Unknown')}")
            print(f"DataCollectorAgent: Diámetro: {asteroid_data.get('diameter_min', 'Unknown')} km")
            print(f"DataCollectorAgent: Peligroso: {asteroid_data.get('hazardous', 'Unknown')}")
            print("=" * 50)
            
        except Exception as e:
            error_msg = f"Error en recolección de datos: {str(e)}"
            self.log_error(state, error_msg)
            print(f"DataCollectorAgent: {error_msg}")
            print("=" * 50)
        
        return state
    
    def validate_input(self, state: AgentState) -> bool:
        """
        Valida que los datos de entrada sean correctos.
        
        Este método verifica que:
        - Tengamos datos del asteroide
        - El ID del asteroide sea válido
        - Los parámetros de simulación sean correctos
        
        Args:
            state: Estado actual de la simulación
            
        Returns:
            True si los datos son válidos, False en caso contrario
        """
        if not state.asteroid_data:
            self.log_warning(state, "No hay datos del asteroide")
            return False
        
        # Verificar que tenemos un ID válido
        asteroid_id = state.asteroid_data.get("id")
        if not asteroid_id:
            self.log_warning(state, "No hay ID del asteroide")
            return False
        
        # Verificar que el ID existe en nuestros datos mock
        if asteroid_id not in self.mock_asteroid_data:
            self.log_warning(state, f"ID de asteroide {asteroid_id} no encontrado en datos mock")
            return False
        
        return True
    
    async def _collect_asteroid_data(self, asteroid_id: str) -> Dict[str, Any]:
        """
        Recolecta datos detallados del asteroide.
        
        Por ahora usa datos hardcodeados, pero en el futuro aquí se conectaría
        con la NASA API para obtener datos reales.
        
        Args:
            asteroid_id: ID único del asteroide
            
        Returns:
            Datos detallados del asteroide
        """
        print(f"DataCollectorAgent: Obteniendo datos para asteroide {asteroid_id}")
        
        # Por ahora, usar datos mock
        # TODO: Implementar conexión real con NASA API
        asteroid_data = self.mock_asteroid_data.get(asteroid_id, {})
        
        if not asteroid_data:
            raise ValueError(f"No se encontraron datos para el asteroide {asteroid_id}")
        
        return asteroid_data
    
    async def _collect_context_data(self, asteroid_id: str) -> Dict[str, Any]:
        """
        Recolecta datos contextuales adicionales.
        
        Esto incluye datos como:
        - Terremotos recientes en la zona
        - Datos de elevación
        - Densidad poblacional
        - Infraestructura crítica
        
        Args:
            asteroid_id: ID del asteroide
            
        Returns:
            Datos contextuales
        """
        print(f"DataCollectorAgent: Recolectando datos contextuales para {asteroid_id}")
        
        # Por ahora, datos mock
    
        context_data = {
            "recent_earthquakes": [
                {
                    "magnitude": 4.2,
                    "location": "Madrid, Spain",
                    "date": "2024-01-01",
                    "depth": 10.5
                }
            ],
            "elevation_data": {
                "average_elevation": 650,  # metros
                "terrain_type": "urban"
            },
            "population_density": {
                "affected_area": 1000000,  # personas
                "density_per_km2": 5000
            },
            "infrastructure_data": {
                "hospitals": 15,
                "schools": 200,
                "airports": 1,
                "power_plants": 3
            }
        }
        
        return context_data
