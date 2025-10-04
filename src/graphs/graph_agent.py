"""
AgentGraph - Coordinador principal de agentes.

Funcionalidad:
- Coordina la ejecución de todos los agentes especializados
- Maneja el estado compartido entre agentes
- Permite agregar lógica condicional y manejo de errores
- Ejecuta el flujo completo de simulación
"""

from typing import Dict, Any, Optional
from ..agents.base_agent import AgentState
from ..agents.data_collector_nasa import DataCollectorAgentNASA
from ..agents.trajectory_agent import TrajectoryAgent
from ..agents.impact_analyzer import ImpactAnalyzerAgent
from ..agents.mitigation_agent import MitigationAgent
from ..agents.visualization_agent import VisualizationAgent
from ..agents.explainer_agent import ExplainerAgent
from ..agents.ml_predictor import MLPredictorAgent
from ..supervisors.hybrid_supervisor import HybridSupervisor


class AgentGraph:
    """Coordinador principal de agentes usando flujo secuencial."""
    
    def __init__(self, supervisor: Optional[HybridSupervisor] = None):
        """Inicializa el grafo de agentes."""
        self.supervisor = supervisor
        
        # Inicializar agentes reales
        self.data_collector = DataCollectorAgentNASA(supervisor=supervisor)
        self.trajectory_agent = TrajectoryAgent(supervisor=supervisor)
        self.impact_analyzer = ImpactAnalyzerAgent(supervisor=supervisor)
        self.mitigation_agent = MitigationAgent(supervisor=supervisor)
        self.visualization_agent = VisualizationAgent(supervisor=supervisor)
        self.explainer_agent = ExplainerAgent(supervisor=supervisor)
        self.ml_predictor_agent = MLPredictorAgent(supervisor=supervisor)
    
    async def run_simulation(self, asteroid_data: Dict[str, Any], 
                           simulation_params: Optional[Dict[str, Any]] = None) -> AgentState:
        """Ejecuta la simulación completa del asteroide."""
        print("🚀 Iniciando simulación de asteroide...")
        print("=" * 60)
        
        # Crear estado inicial
        state = AgentState(
            asteroid_data=asteroid_data,
            simulation_parameters=simulation_params or {}
        )
        
        try:
            # Ejecutar pipeline de agentes
            state = await self._run_data_collector(state)
            state = await self._run_trajectory_agent(state)
            state = await self._run_impact_analyzer(state)
            state = await self._run_mitigation_agent(state)
            state = await self._run_visualization_agent(state)
            state = await self._run_explainer_agent(state)
            state = await self._run_ml_predictor_agent(state)
            
            # Mostrar resumen final
            self._show_final_summary(state)
            
        except Exception as e:
            print(f"❌ Error en simulación: {str(e)}")
            state.status = "failed"
            state.errors.append(str(e))
        
        return state
    
    async def _run_data_collector(self, state: AgentState) -> AgentState:
        """Ejecuta DataCollectorAgent."""
        print("📊 Fase 1: Recolectando datos del asteroide...")
        result_state = await self.data_collector.execute(state)
        print("✅ Datos recolectados exitosamente")
        return result_state
    
    async def _run_trajectory_agent(self, state: AgentState) -> AgentState:
        """Ejecuta TrajectoryAgent."""
        print("🛰️ Fase 2: Analizando trayectoria orbital...")
        result_state = await self.trajectory_agent.execute(state)
        print("✅ Análisis de trayectoria completado")
        return result_state
    
    async def _run_impact_analyzer(self, state: AgentState) -> AgentState:
        """Ejecuta ImpactAnalyzerAgent."""
        print("💥 Fase 3: Analizando efectos de impacto...")
        result_state = await self.impact_analyzer.execute(state)
        print("✅ Análisis de impacto completado")
        return result_state
    
    async def _run_mitigation_agent(self, state: AgentState) -> AgentState:
        """Ejecuta MitigationAgent."""
        print("🛡️ Fase 4: Evaluando estrategias de mitigación...")
        result_state = await self.mitigation_agent.execute(state)
        print("✅ Evaluación de mitigación completada")
        return result_state
    
    async def _run_visualization_agent(self, state: AgentState) -> AgentState:
        """Ejecuta VisualizationAgent."""
        print("📊 Fase 5: Generando visualizaciones...")
        result_state = await self.visualization_agent.execute(state)
        print("✅ Visualizaciones generadas")
        return result_state
    
    async def _run_explainer_agent(self, state: AgentState) -> AgentState:
        """Ejecuta ExplainerAgent."""
        print("📚 Fase 6: Generando explicaciones científicas...")
        result_state = await self.explainer_agent.execute(state)
        print("✅ Explicaciones generadas")
        return result_state
    
    async def _run_ml_predictor_agent(self, state: AgentState) -> AgentState:
        """Ejecuta MLPredictorAgent."""
        print("🤖 Fase 7: Generando predicciones ML avanzadas...")
        result_state = await self.ml_predictor_agent.execute(state)
        print("✅ Predicciones ML generadas")
        return result_state
    
    def _show_final_summary(self, state: AgentState):
        """Muestra resumen final de la simulación."""
        print("\n" + "=" * 60)
        print("📋 RESUMEN FINAL DE LA SIMULACIÓN")
        print("=" * 60)
        
        # Datos del asteroide
        asteroid_data = state.data_collection_result.get("asteroid_data", {})
        print(f"🪐 Asteroide: {asteroid_data.get('name', 'Unknown')}")
        print(f"📏 Diámetro: {asteroid_data.get('diameter_min', 0):.1f} - {asteroid_data.get('diameter_max', 0):.1f} km")
        print(f"⚠️ Peligroso: {'Sí' if asteroid_data.get('is_potentially_hazardous_asteroid') else 'No'}")
        
        # Análisis de trayectoria
        trajectory_data = state.trajectory_analysis
        if trajectory_data:
            impact_prob = trajectory_data.get("impact_probability", 0)
            print(f"🎯 Probabilidad de impacto: {impact_prob:.1%}")
        
        # Análisis de impacto
        impact_data = state.impact_analysis
        if impact_data:
            energy_data = impact_data.get("impact_energy", {})
            crater_data = impact_data.get("crater_size", {})
            print(f"⚡ Energía del impacto: {energy_data.get('total_energy_mt_tnt', 0):.1f} MT TNT")
            print(f"🕳️ Diámetro del cráter: {crater_data.get('diameter_km', 0):.1f} km")
        
        # Estrategias de mitigación
        mitigation_strategies = state.mitigation_strategies
        if mitigation_strategies:
            print(f"🛡️ Estrategias evaluadas: {len(mitigation_strategies)}")
            if mitigation_strategies:
                best_strategy = mitigation_strategies[0]
                print(f"🥇 Mejor estrategia: {best_strategy.get('name', 'Unknown')}")
                print(f"💰 Costo estimado: ${best_strategy.get('estimated_cost', 0):,.0f}")
        
        # Estado de supervisión
        if state.supervision_results:
            print(f"🔍 Supervisión: {state.supervision_results.get('recommendation', 'Unknown')}")
        
      
        
    def get_agent_status(self) -> Dict[str, Any]:
        """Obtiene el estado de todos los agentes."""
        return {
            "data_collector": "ready",
            "trajectory_agent": "ready", 
            "impact_analyzer": "ready",
            "mitigation_agent": "ready",
            "visualization_agent": "ready",
            "explainer_agent": "ready",
            "ml_predictor_agent": "ready",
            "supervisor": "ready" if self.supervisor else "disabled"
        }
    
    def get_simulation_parameters(self) -> Dict[str, Any]:
        """Obtiene parámetros de simulación por defecto."""
        return {
            "simulation_id": "default",
            "max_execution_time": 300,  # 5 minutos
            "enable_supervision": True,
            "enable_llm_predictions": True,
            "confidence_threshold": 0.7
        }