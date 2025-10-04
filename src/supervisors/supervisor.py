"""
Supervisor principal del sistema anti-alucinación.

Coordina todos los validadores especializados y mantiene la integridad
científica de todo el sistema de agentes.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from .agent_supervisor import AgentSupervisor
from ..validators import PhysicsValidator, DataValidator, ConfidenceSystem
from ..agents.base_agent import AgentState


class Supervisor:
    """
    Supervisor principal del sistema anti-alucinación.
    
    Coordina:
    - Validadores especializados por dominio
    - Sistema de confianza y alertas
    - Supervisión de agentes individuales
    - Toma de decisiones sobre continuidad
    """
    
    def __init__(self):
        """Inicializa el supervisor principal."""
        print("=" * 60)
        print("INICIALIZANDO SISTEMA DE SUPERVISIÓN ANTI-ALUCINACIÓN")
        print("=" * 60)
        
        # Inicializar validadores especializados
        self.physics_validator = PhysicsValidator()
        self.data_validator = DataValidator()
        self.confidence_system = ConfidenceSystem()
        
        # Inicializar supervisores de agentes
        self.agent_supervisors = {
            "DataCollectorAgent": AgentSupervisor("DataCollectorAgent", [self.data_validator]),
            "TrajectoryAgent": AgentSupervisor("TrajectoryAgent", [self.physics_validator]),
            "ImpactAnalyzerAgent": AgentSupervisor("ImpactAnalyzerAgent", [self.physics_validator]),
            "MitigationAgent": AgentSupervisor("MitigationAgent", [self.physics_validator]),
            "VisualizationAgent": AgentSupervisor("VisualizationAgent", [self.data_validator]),
            "MLPredictorAgent": AgentSupervisor("MLPredictorAgent", [self.data_validator]),
            "ExplainerAgent": AgentSupervisor("ExplainerAgent", [self.data_validator])
        }
        
        print("Supervisor principal inicializado correctamente")
        print("=" * 60)
    
    async def supervise_agent_execution(
        self, 
        agent_name: str, 
        agent_data: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Supervisa la ejecución de un agente específico.
        
        Args:
            agent_name: Nombre del agente a supervisar
            agent_data: Datos producidos por el agente
            context: Contexto de la ejecución
            
        Returns:
            Resultado de la supervisión con recomendaciones
        """
        print("=" * 60)
        print(f"SUPERVISANDO EJECUCIÓN DE {agent_name.upper()}")
        print("=" * 60)
        
        # Obtener supervisor del agente
        agent_supervisor = self.agent_supervisors.get(agent_name)
        if not agent_supervisor:
            print(f"ERROR: No se encontró supervisor para {agent_name}")
            return {
                "supervised": False,
                "error": f"No supervisor found for {agent_name}",
                "recommendation": "stop"
            }
        
        # Supervisar el agente
        supervision_result = await agent_supervisor.supervise(agent_data, context)
        
        # Actualizar sistema de confianza
        if supervision_result["validation_reports"]:
            metrics = self.confidence_system.update_confidence(supervision_result["validation_reports"])
            supervision_result["confidence_metrics"] = metrics
        
        # Generar recomendación final
        recommendation = self._generate_recommendation(supervision_result)
        supervision_result["recommendation"] = recommendation
        
        print(f"Supervisión completada - Recomendación: {recommendation}")
        print("=" * 60)
        
        return supervision_result
    
    async def supervise_full_simulation(
        self, 
        simulation_state: AgentState
    ) -> Dict[str, Any]:
        """
        Supervisa una simulación completa.
        
        Args:
            simulation_state: Estado completo de la simulación
            
        Returns:
            Reporte de supervisión de la simulación completa
        """
        print("=" * 60)
        print("SUPERVISANDO SIMULACIÓN COMPLETA")
        print("=" * 60)
        
        simulation_report = {
            "simulation_id": f"sim_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "agent_reports": {},
            "overall_confidence": 0.0,
            "simulation_valid": True,
            "recommendations": [],
            "alerts": []
        }
        
        # Supervisar cada componente del estado
        components_to_supervise = [
            ("asteroid_data", "DataCollectorAgent", "asteroid"),
            ("trajectory_analysis", "TrajectoryAgent", "trajectory"),
            ("impact_analysis", "ImpactAnalyzerAgent", "impact"),
            ("mitigation_strategies", "MitigationAgent", "mitigation"),
            ("visualization_data", "VisualizationAgent", "visualization"),
            ("ml_predictions", "MLPredictorAgent", "ml"),
            ("explanation", "ExplainerAgent", "explanation")
        ]
        
        all_validation_reports = []
        
        for component, agent_name, data_type in components_to_supervise:
            if hasattr(simulation_state, component):
                component_data = getattr(simulation_state, component)
                if component_data:
                    context = {
                        "agent_name": agent_name,
                        "data_type": data_type,
                        "simulation_id": simulation_report["simulation_id"]
                    }
                    
                    supervision_result = await self.supervise_agent_execution(
                        agent_name, component_data, context
                    )
                    
                    simulation_report["agent_reports"][agent_name] = supervision_result
                    
                    if supervision_result.get("validation_reports"):
                        all_validation_reports.extend(supervision_result["validation_reports"])
        
        # Calcular métricas generales
        if all_validation_reports:
            metrics = self.confidence_system.update_confidence(all_validation_reports)
            simulation_report["overall_confidence"] = metrics.overall_confidence
            simulation_report["simulation_valid"] = metrics.overall_confidence >= 0.7
        
        # Obtener alertas activas
        simulation_report["alerts"] = [
            {
                "level": alert.level,
                "message": alert.message,
                "agent": alert.agent_name,
                "timestamp": alert.timestamp.isoformat()
            }
            for alert in self.confidence_system.get_active_alerts()
        ]
        
        # Generar recomendaciones generales
        simulation_report["recommendations"] = self._generate_simulation_recommendations(simulation_report)
        
        print(f"Supervisión de simulación completada")
        print(f"Confianza general: {simulation_report['overall_confidence']:.2f}")
        print(f"Simulación válida: {simulation_report['simulation_valid']}")
        print("=" * 60)
        
        return simulation_report
    
    def _generate_recommendation(self, supervision_result: Dict[str, Any]) -> str:
        """
        Genera una recomendación basada en los resultados de supervisión.
        
        Args:
            supervision_result: Resultado de la supervisión
            
        Returns:
            Recomendación: "continue", "retry", "stop", "investigate"
        """
        validation_reports = supervision_result.get("validation_reports", [])
        confidence_metrics = supervision_result.get("confidence_metrics")
        
        if not validation_reports:
            return "investigate"
        
        # Contar errores críticos
        critical_errors = sum(
            len(report.get_errors()) for report in validation_reports
        )
        
        # Contar advertencias
        warnings = sum(
            len(report.get_warnings()) for report in validation_reports
        )
        
        # Determinar recomendación
        if critical_errors > 3:
            return "stop"
        elif critical_errors > 0 or warnings > 5:
            return "retry"
        elif confidence_metrics and confidence_metrics.overall_confidence < 0.6:
            return "investigate"
        else:
            return "continue"
    
    def _generate_simulation_recommendations(self, simulation_report: Dict[str, Any]) -> List[str]:
        """
        Genera recomendaciones para la simulación completa.
        
        Args:
            simulation_report: Reporte de la simulación
            
        Returns:
            Lista de recomendaciones
        """
        recommendations = []
        
        confidence = simulation_report.get("overall_confidence", 0.0)
        alerts = simulation_report.get("alerts", [])
        
        if confidence < 0.5:
            recommendations.append("CRÍTICO: Confianza muy baja, revisar todos los agentes")
        elif confidence < 0.7:
            recommendations.append("ADVERTENCIA: Confianza baja, verificar cálculos")
        
        if len(alerts) > 5:
            recommendations.append("ADVERTENCIA: Muchas alertas activas, revisar sistema")
        
        critical_alerts = [a for a in alerts if a["level"] == "critical"]
        if critical_alerts:
            recommendations.append("CRÍTICO: Alertas críticas activas, detener simulación")
        
        if not recommendations:
            recommendations.append("ÉXITO: Simulación válida, continuar")
        
        return recommendations
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Obtiene el estado actual del sistema de supervisión.
        
        Returns:
            Estado del sistema
        """
        health_report = self.confidence_system.get_system_health_report()
        active_alerts = self.confidence_system.get_active_alerts()
        trend = self.confidence_system.get_confidence_trend()
        
        return {
            "system_health": health_report,
            "active_alerts": len(active_alerts),
            "confidence_trend": trend,
            "supervisors_active": len(self.agent_supervisors),
            "validators_active": 3,  # Physics, Data, Confidence
            "last_updated": datetime.now().isoformat()
        }
    
    def should_continue_simulation(self) -> bool:
        """
        Determina si la simulación debe continuar.
        
        Returns:
            True si debe continuar, False si debe detenerse
        """
        return self.confidence_system.should_continue_simulation()
    
    def get_agent_health(self, agent_name: str) -> Dict[str, Any]:
        """
        Obtiene el estado de salud de un agente específico.
        
        Args:
            agent_name: Nombre del agente
            
        Returns:
            Estado de salud del agente
        """
        return self.confidence_system.get_agent_performance(agent_name)