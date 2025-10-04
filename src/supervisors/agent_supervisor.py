"""
Supervisor individual para cada agente.

Maneja la supervisión específica de un agente, coordinando
múltiples validadores y generando reportes detallados.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from ..validators.base_validator import BaseValidator, ValidationReport


class AgentSupervisor:
    """
    Supervisor individual para un agente específico.
    
    Coordina múltiples validadores especializados para verificar
    la veracidad y precisión de los resultados de un agente.
    """
    
    def __init__(self, agent_name: str, validators: List[BaseValidator]):
        """
        Inicializa el supervisor del agente.
        
        Args:
            agent_name: Nombre del agente a supervisar
            validators: Lista de validadores especializados
        """
        self.agent_name = agent_name
        self.validators = validators
        self.supervision_history: List[Dict[str, Any]] = []
        self.max_history = 50  # Mantener solo los últimos 50 registros
        
        print(f"AgentSupervisor creado para {agent_name} con {len(validators)} validadores")
    
    async def supervise(self, agent_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Supervisa la ejecución del agente.
        
        Args:
            agent_data: Datos producidos por el agente
            context: Contexto de la ejecución
            
        Returns:
            Resultado de la supervisión
        """
        print("=" * 50)
        print(f"AgentSupervisor: Supervisando {self.agent_name}...")
        
        supervision_result = {
            "agent_name": self.agent_name,
            "timestamp": datetime.now().isoformat(),
            "supervised": True,
            "validation_reports": [],
            "overall_confidence": 0.0,
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "recommendations": []
        }
        
        # Ejecutar cada validador
        for validator in self.validators:
            try:
                print(f"AgentSupervisor: Ejecutando {validator.name}...")
                
                # Preparar contexto específico para el validador
                validator_context = {
                    **context,
                    "agent_type": self._get_agent_type(),
                    "validator_name": validator.name
                }
                
                # Ejecutar validación
                validation_report = validator.validate(agent_data, validator_context)
                supervision_result["validation_reports"].append(validation_report)
                
                print(f"AgentSupervisor: {validator.name} completado - {len(validation_report.results)} validaciones")
                
            except Exception as e:
                print(f"AgentSupervisor: ERROR en {validator.name}: {str(e)}")
                
                # Crear reporte de error
                error_report = ValidationReport(
                    agent_name=self.agent_name,
                    overall_confidence=0.0,
                    is_valid=False,
                    validation_count=0,
                    results=[]
                )
                error_report.add_result(validator.create_validation_result(
                    level="critical",
                    message=f"Error en validador {validator.name}: {str(e)}",
                    confidence=0.0
                ))
                supervision_result["validation_reports"].append(error_report)
        
        # Consolidar resultados
        self._consolidate_results(supervision_result)
        
        # Generar recomendaciones
        supervision_result["recommendations"] = self._generate_recommendations(supervision_result)
        
        # Guardar en historial
        self._save_to_history(supervision_result)
        
        print(f"AgentSupervisor: Supervisión de {self.agent_name} completada")
        print(f"AgentSupervisor: Confianza: {supervision_result['overall_confidence']:.2f}")
        print(f"AgentSupervisor: Válido: {supervision_result['is_valid']}")
        print("=" * 50)
        
        return supervision_result
    
    def _get_agent_type(self) -> str:
        """Determina el tipo de agente basado en su nombre."""
        agent_type_mapping = {
            "DataCollectorAgent": "data_collection",
            "TrajectoryAgent": "trajectory",
            "ImpactAnalyzerAgent": "impact",
            "MitigationAgent": "mitigation",
            "VisualizationAgent": "visualization",
            "MLPredictorAgent": "ml",
            "ExplainerAgent": "explanation"
        }
        return agent_type_mapping.get(self.agent_name, "unknown")
    
    def _consolidate_results(self, supervision_result: Dict[str, Any]) -> None:
        """Consolida los resultados de todos los validadores."""
        validation_reports = supervision_result["validation_reports"]
        
        if not validation_reports:
            return
        
        # Calcular confianza general
        total_confidence = sum(report.overall_confidence for report in validation_reports)
        supervision_result["overall_confidence"] = total_confidence / len(validation_reports)
        
        # Determinar si es válido (sin errores críticos)
        has_critical_errors = any(
            len(report.get_errors()) > 0 for report in validation_reports
        )
        supervision_result["is_valid"] = not has_critical_errors
        
        # Consolidar errores y advertencias
        all_errors = []
        all_warnings = []
        
        for report in validation_reports:
            all_errors.extend(report.get_errors())
            all_warnings.extend(report.get_warnings())
        
        supervision_result["errors"] = [
            {
                "message": error.message,
                "field": error.field,
                "validator": "unknown"  # TODO: Track validator source
            }
            for error in all_errors
        ]
        
        supervision_result["warnings"] = [
            {
                "message": warning.message,
                "field": warning.field,
                "validator": "unknown"  # TODO: Track validator source
            }
            for warning in all_warnings
        ]
    
    def _generate_recommendations(self, supervision_result: Dict[str, Any]) -> List[str]:
        """Genera recomendaciones basadas en los resultados de supervisión."""
        recommendations = []
        
        confidence = supervision_result["overall_confidence"]
        errors = supervision_result["errors"]
        warnings = supervision_result["warnings"]
        
        # Recomendaciones basadas en confianza
        if confidence < 0.3:
            recommendations.append("CRÍTICO: Confianza extremadamente baja, revisar completamente")
        elif confidence < 0.5:
            recommendations.append("ALTO: Confianza baja, verificar cálculos principales")
        elif confidence < 0.7:
            recommendations.append("MEDIO: Confianza moderada, revisar advertencias")
        elif confidence < 0.9:
            recommendations.append("BAJO: Confianza buena, optimizar detalles")
        else:
            recommendations.append("EXCELENTE: Confianza alta, continuar")
        
        # Recomendaciones basadas en errores
        if len(errors) > 5:
            recommendations.append("CRÍTICO: Demasiados errores, detener ejecución")
        elif len(errors) > 2:
            recommendations.append("ALTO: Múltiples errores, revisar antes de continuar")
        elif len(errors) > 0:
            recommendations.append("MEDIO: Errores detectados, corregir antes de continuar")
        
        # Recomendaciones basadas en advertencias
        if len(warnings) > 10:
            recommendations.append("MEDIO: Muchas advertencias, revisar calidad de datos")
        elif len(warnings) > 5:
            recommendations.append("BAJO: Varias advertencias, verificar entradas")
        
        # Recomendaciones específicas por tipo de agente
        agent_specific = self._get_agent_specific_recommendations(supervision_result)
        recommendations.extend(agent_specific)
        
        return recommendations
    
    def _get_agent_specific_recommendations(self, supervision_result: Dict[str, Any]) -> List[str]:
        """Genera recomendaciones específicas para el tipo de agente."""
        recommendations = []
        
        if self.agent_name == "DataCollectorAgent":
            recommendations.append("Verificar conectividad con APIs externas")
            recommendations.append("Validar formato de datos recibidos")
        
        elif self.agent_name == "TrajectoryAgent":
            recommendations.append("Verificar constantes astronómicas")
            recommendations.append("Validar conservación de energía")
        
        elif self.agent_name == "ImpactAnalyzerAgent":
            recommendations.append("Verificar cálculos de energía de impacto")
            recommendations.append("Validar rangos de valores físicos")
        
        elif self.agent_name == "MitigationAgent":
            recommendations.append("Verificar viabilidad de estrategias")
            recommendations.append("Validar cálculos de costo-beneficio")
        
        elif self.agent_name == "VisualizationAgent":
            recommendations.append("Verificar integridad de datos de visualización")
            recommendations.append("Validar rangos de coordenadas")
        
        elif self.agent_name == "MLPredictorAgent":
            recommendations.append("Verificar calidad de datos de entrenamiento")
            recommendations.append("Validar rangos de predicción")
        
        elif self.agent_name == "ExplainerAgent":
            recommendations.append("Verificar coherencia del lenguaje")
            recommendations.append("Validar adaptación a la audiencia")
        
        return recommendations
    
    def _save_to_history(self, supervision_result: Dict[str, Any]) -> None:
        """Guarda el resultado en el historial de supervisión."""
        self.supervision_history.append(supervision_result)
        
        # Mantener solo los últimos N registros
        if len(self.supervision_history) > self.max_history:
            self.supervision_history.pop(0)
    
    def get_supervision_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Obtiene el historial de supervisión del agente.
        
        Args:
            limit: Número máximo de registros a retornar
            
        Returns:
            Lista de resultados de supervisión históricos
        """
        return self.supervision_history[-limit:] if self.supervision_history else []
    
    def get_agent_performance_summary(self) -> Dict[str, Any]:
        """
        Obtiene un resumen del rendimiento del agente.
        
        Returns:
            Resumen del rendimiento
        """
        if not self.supervision_history:
            return {"error": "No supervision history available"}
        
        # Calcular métricas
        total_supervisions = len(self.supervision_history)
        valid_supervisions = sum(1 for s in self.supervision_history if s["is_valid"])
        avg_confidence = sum(s["overall_confidence"] for s in self.supervision_history) / total_supervisions
        
        # Contar errores y advertencias
        total_errors = sum(len(s["errors"]) for s in self.supervision_history)
        total_warnings = sum(len(s["warnings"]) for s in self.supervision_history)
        
        return {
            "agent_name": self.agent_name,
            "total_supervisions": total_supervisions,
            "valid_supervisions": valid_supervisions,
            "success_rate": valid_supervisions / total_supervisions,
            "average_confidence": avg_confidence,
            "total_errors": total_errors,
            "total_warnings": total_warnings,
            "error_rate": total_errors / total_supervisions,
            "warning_rate": total_warnings / total_supervisions
        }