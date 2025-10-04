"""
VisualizationAgent - Crea visualizaciones científicas de datos de asteroides.

Funcionalidad:
- Genera gráficos de trayectorias orbitales
- Crea mapas de impacto y zonas de daño
- Visualiza métricas de confianza
- Produce diagramas de riesgo temporal
- Genera representaciones 3D de órbitas

Especialidad: Visualización científica, gráficos, comunicación visual
"""

import math
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from .base_agent import BaseAgent, AgentState
from ..supervisors.hybrid_supervisor import HybridSupervisor
from dotenv import load_dotenv

load_dotenv()


class VisualizationAgent(BaseAgent):
    """
    Agente especializado en visualización científica de datos de asteroides.
    
    Responsabilidades:
    - Crear gráficos de trayectorias orbitales
    - Generar mapas de impacto con zonas de daño
    - Visualizar métricas de confianza del sistema
    - Producir diagramas de riesgo temporal
    - Crear representaciones 3D de órbitas
    """
    
    def __init__(self, supervisor: Optional[HybridSupervisor] = None):
        super().__init__(
            name="VisualizationAgent",
            description="Crea visualizaciones científicas de datos de asteroides"
        )
        self.supervisor = supervisor
        
        # Configuración de visualización
        self.chart_colors = {
            'trajectory': '#2E86AB',
            'impact_zone': '#F24236', 
            'confidence': '#F6AE2D',
            'risk': '#7209B7',
            'safe_zone': '#06D6A0'
        }
    
    async def execute(self, state: AgentState) -> AgentState:
        """
        Ejecuta la generación de visualizaciones.
        
        Args:
            state: Estado actual del sistema con datos de asteroides
            
        Returns:
            AgentState actualizado con visualizaciones generadas
        """
        print("VisualizationAgent: Generando visualizaciones...")
        
        try:
            if not self.validate_input(state):
                self.log_error(state, "Datos inválidos para visualización")
                return state
            
            # Obtener datos de entrada
            asteroid_data = state.data_collection_result.get("asteroid_data", {})
            trajectory_data = state.trajectory_analysis
            impact_data = state.impact_analysis
            mitigation_data = state.mitigation_analysis
            
            # Generar diferentes tipos de visualizaciones
            visualizations = {}
            
            # 1. Gráfico de trayectoria orbital
            if trajectory_data:
                visualizations['orbital_trajectory'] = self._create_orbital_trajectory_chart(
                    asteroid_data, trajectory_data
                )
            
            # 2. Mapa de impacto
            if impact_data:
                visualizations['impact_map'] = self._create_impact_map(
                    asteroid_data, impact_data
                )
            
            # 3. Gráfico de métricas de confianza
            if hasattr(state, 'confidence_metrics'):
                visualizations['confidence_chart'] = self._create_confidence_chart(
                    state.confidence_metrics
                )
            
            # 4. Diagrama de riesgo temporal
            if trajectory_data and impact_data:
                visualizations['risk_timeline'] = self._create_risk_timeline(
                    trajectory_data, impact_data
                )
            
            # 5. Visualización 3D de órbita
            if trajectory_data:
                visualizations['orbit_3d'] = self._create_3d_orbit_visualization(
                    asteroid_data, trajectory_data
                )
            
            # Actualizar estado con visualizaciones
            state.visualization_data = {
                'charts': visualizations,
                'metadata': {
                    'generated_at': datetime.utcnow().isoformat(),
                    'asteroid_id': asteroid_data.get('id', 'unknown'),
                    'total_visualizations': len(visualizations)
                },
                'status': 'success'
            }
            
            # Supervisión y validación
            if self.supervisor:
                supervision_result = await self.supervisor.supervise_agent(
                    agent_name=self.name,
                    input_data=asteroid_data,
                    output_data=visualizations
                )
                
                # Integrar métricas de confianza
                if hasattr(self.supervisor, 'confidence_system'):
                    confidence_metrics = self.supervisor.confidence_system.update_confidence(
                        validation_reports=supervision_result.get("validation_reports", []),
                        asteroid_data=asteroid_data,
                        prediction_data=visualizations
                    )
                    
                    state.visualization_data['confidence_metrics'] = {
                        'overall_confidence': confidence_metrics.overall_confidence,
                        'scientific_confidence': confidence_metrics.scientific_confidence,
                        'rag_confidence': confidence_metrics.rag_confidence,
                        'orbital_confidence': confidence_metrics.orbital_confidence,
                        'data_quality_confidence': confidence_metrics.data_quality_confidence,
                        'prediction_confidence': confidence_metrics.prediction_confidence,
                        'trend': confidence_metrics.trend,
                        'alert_level': confidence_metrics.alert_level
                    }
            
            print(f"VisualizationAgent: {len(visualizations)} visualizaciones generadas")
            return state
            
        except Exception as e:
            self.log_error(state, f"Error generando visualizaciones: {str(e)}")
            return state
    
    def _create_orbital_trajectory_chart(self, asteroid_data: Dict[str, Any], 
                                       trajectory_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crea gráfico de trayectoria orbital.
        
        Args:
            asteroid_data: Datos del asteroide
            trajectory_data: Datos de trayectoria
            
        Returns:
            Diccionario con configuración del gráfico
        """
        # TODO: Implementar lógica de gráfico de trayectoria
        # Por ahora retornamos estructura básica
        return {
            'type': 'orbital_trajectory',
            'title': f"Trayectoria Orbital - {asteroid_data.get('name', 'Unknown')}",
            'data': {
                'x_axis': 'Tiempo (días)',
                'y_axis': 'Distancia (UA)',
                'points': []  # Se llenará con datos reales
            },
            'config': {
                'color': self.chart_colors['trajectory'],
                'width': 800,
                'height': 600
            }
        }
    
    def _create_impact_map(self, asteroid_data: Dict[str, Any], 
                          impact_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crea mapa de impacto con zonas de daño.
        
        Args:
            asteroid_data: Datos del asteroide
            impact_data: Datos de impacto
            
        Returns:
            Diccionario con configuración del mapa
        """
        # TODO: Implementar lógica de mapa de impacto
        return {
            'type': 'impact_map',
            'title': f"Mapa de Impacto - {asteroid_data.get('name', 'Unknown')}",
            'data': {
                'center_lat': 0.0,  # Latitud del impacto
                'center_lon': 0.0,  # Longitud del impacto
                'zones': []  # Zonas de daño
            },
            'config': {
                'map_type': 'satellite',
                'zoom_level': 6
            }
        }
    
    def _create_confidence_chart(self, confidence_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crea gráfico de métricas de confianza.
        
        Args:
            confidence_metrics: Métricas de confianza
            
        Returns:
            Diccionario con configuración del gráfico
        """
        # TODO: Implementar lógica de gráfico de confianza
        return {
            'type': 'confidence_chart',
            'title': "Métricas de Confianza del Sistema",
            'data': {
                'categories': ['Científica', 'RAG', 'Orbital', 'Calidad', 'Predicción'],
                'values': []  # Se llenará con valores reales
            },
            'config': {
                'chart_type': 'radar',
                'colors': list(self.chart_colors.values())
            }
        }
    
    def _create_risk_timeline(self, trajectory_data: Dict[str, Any], 
                             impact_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crea diagrama de riesgo temporal.
        
        Args:
            trajectory_data: Datos de trayectoria
            impact_data: Datos de impacto
            
        Returns:
            Diccionario con configuración del timeline
        """
        # TODO: Implementar lógica de timeline de riesgo
        return {
            'type': 'risk_timeline',
            'title': "Timeline de Riesgo",
            'data': {
                'events': [],  # Eventos temporales
                'risk_levels': []  # Niveles de riesgo por tiempo
            },
            'config': {
                'time_range': '30_days',
                'risk_threshold': 0.5
            }
        }
    
    def _create_3d_orbit_visualization(self, asteroid_data: Dict[str, Any], 
                                     trajectory_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crea visualización 3D de órbita.
        
        Args:
            asteroid_data: Datos del asteroide
            trajectory_data: Datos de trayectoria
            
        Returns:
            Diccionario con configuración 3D
        """
        # TODO: Implementar lógica de visualización 3D
        return {
            'type': 'orbit_3d',
            'title': f"Órbita 3D - {asteroid_data.get('name', 'Unknown')}",
            'data': {
                'orbit_points': [],  # Puntos de la órbita
                'earth_position': [0, 0, 0],
                'asteroid_position': [0, 0, 0]
            },
            'config': {
                'camera_position': [10, 10, 10],
                'animation_speed': 1.0
            }
        }
    
    def validate_input(self, state: AgentState) -> bool:
        """
        Valida que los datos de entrada sean suficientes para visualización.
        
        Args:
            state: Estado del sistema
            
        Returns:
            True si los datos son válidos, False en caso contrario
        """
        # Verificar que hay datos de asteroides
        if not state.data_collection_result:
            return False
        
        # Verificar que hay al menos datos de trayectoria o impacto
        has_trajectory = bool(state.trajectory_analysis)
        has_impact = bool(state.impact_analysis)
        
        return has_trajectory or has_impact
