"""
Sistema de confianza para monitoreo continuo.

Mantiene un registro de la confianza del sistema y genera alertas
cuando la confianza cae por debajo de umbrales críticos.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from .base_validator import ValidationReport


@dataclass
class ConfidenceMetrics:
    """Métricas de confianza del sistema."""
    overall_confidence: float
    scientific_confidence: float
    rag_confidence: float
    orbital_confidence: float  # Nueva: confianza basada en incertidumbre orbital
    data_quality_confidence: float  # Nueva: confianza basada en calidad de datos
    prediction_confidence: float  # Nueva: confianza basada en predicciones LLM
    trend: str  # "improving", "stable", "declining"
    alert_level: str  # "low", "medium", "high", "critical"
    timestamp: datetime


@dataclass
class Alert:
    """Alerta del sistema de confianza."""
    level: str  # "low", "medium", "high", "critical"
    message: str
    agent_name: str
    timestamp: datetime
    resolved: bool = False


class ConfidenceSystem:
    """
    Sistema de monitoreo de confianza del sistema.
    
    Mantiene:
    - Historial de confianza por agente
    - Tendencias de confianza
    - Alertas automáticas
    - Recomendaciones de acción
    """
    
    def __init__(self):
        """Inicializa el sistema de confianza."""
        self.confidence_history: List[ConfidenceMetrics] = []
        self.agent_performance: Dict[str, List[float]] = {}
        self.active_alerts: List[Alert] = []
        self.max_history = 100  # Mantener últimos 100 registros
        
        # Umbrales de alerta
        self.alert_thresholds = {
            "critical": 0.3,
            "high": 0.5,
            "medium": 0.7,
            "low": 0.8
        }
    
    def update_confidence(self, validation_reports: List[ValidationReport], 
                         asteroid_data: Dict[str, Any] = None, 
                         prediction_data: Dict[str, Any] = None) -> ConfidenceMetrics:
        """
        Actualiza las métricas de confianza basadas en reportes de validación y datos adicionales.
        
        Args:
            validation_reports: Lista de reportes de validación
            asteroid_data: Datos del asteroide de NASA API (opcional)
            prediction_data: Datos de predicción LLM (opcional)
            
        Returns:
            Métricas de confianza actualizadas
        """
        if not validation_reports:
            return self._create_default_metrics()
        
        # Calcular confianza científica (validadores base)
        scientific_confidence = self._calculate_scientific_confidence(validation_reports)
        
        # Calcular confianza RAG (si está disponible)
        rag_confidence = self._calculate_rag_confidence(validation_reports)
        
        # Calcular nuevas confianzas si hay datos disponibles
        orbital_confidence = 0.5  # Valor por defecto
        data_quality_confidence = 0.5  # Valor por defecto
        prediction_confidence = 0.6  # Valor por defecto
        
        if asteroid_data:
            orbital_confidence = self.calculate_orbital_confidence(asteroid_data)
            data_quality_confidence = self.calculate_data_quality_confidence(asteroid_data)
        
        if prediction_data:
            prediction_confidence = self.calculate_prediction_confidence(prediction_data)
        
        # Calcular confianza general con nueva ponderación
        # 30% científico + 20% RAG + 20% orbital + 15% datos + 15% predicción
        overall_confidence = (
            scientific_confidence * 0.30 +
            rag_confidence * 0.20 +
            orbital_confidence * 0.20 +
            data_quality_confidence * 0.15 +
            prediction_confidence * 0.15
        )
        
        # Determinar tendencia
        trend = self._calculate_trend(overall_confidence)
        
        # Determinar nivel de alerta
        alert_level = self._determine_alert_level(overall_confidence)
        
        # Crear métricas con todas las confianzas
        metrics = ConfidenceMetrics(
            overall_confidence=overall_confidence,
            scientific_confidence=scientific_confidence,
            rag_confidence=rag_confidence,
            orbital_confidence=orbital_confidence,
            data_quality_confidence=data_quality_confidence,
            prediction_confidence=prediction_confidence,
            trend=trend,
            alert_level=alert_level,
            timestamp=datetime.now()
        )
        
        # Guardar en historial
        self.confidence_history.append(metrics)
        
        # Limitar historial
        if len(self.confidence_history) > self.max_history:
            self.confidence_history.pop(0)
        
        # Generar alertas si es necesario
        self._check_for_alerts(metrics, validation_reports)
        
        return metrics
    
    def _calculate_scientific_confidence(self, reports: List[ValidationReport]) -> float:
        """Calcula confianza científica promedio."""
        if not reports:
            return 0.0
        
        # Filtrar reportes científicos (no RAG)
        scientific_reports = [r for r in reports if not hasattr(r, 'validation_type') or r.validation_type != 'rag']
        
        if not scientific_reports:
            return 0.0
        
        total_confidence = sum(r.overall_confidence for r in scientific_reports)
        return total_confidence / len(scientific_reports)
    
    def _calculate_rag_confidence(self, reports: List[ValidationReport]) -> float:
        """Calcula confianza RAG promedio."""
        if not reports:
            return 0.0
        
        # Filtrar reportes RAG
        rag_reports = [r for r in reports if hasattr(r, 'validation_type') and r.validation_type == 'rag']
        
        if not rag_reports:
            return 1.0  # Si no hay RAG, asumir confianza alta
        
        total_confidence = sum(r.overall_confidence for r in rag_reports)
        return total_confidence / len(rag_reports)
    
    def _calculate_trend(self, current_confidence: float) -> str:
        """Calcula la tendencia de confianza."""
        if len(self.confidence_history) < 2:
            return "stable"
        
        recent_confidence = [m.overall_confidence for m in self.confidence_history[-5:]]
        if len(recent_confidence) < 2:
            return "stable"
        
        # Calcular tendencia simple
        first_half = sum(recent_confidence[:len(recent_confidence)//2]) / (len(recent_confidence)//2)
        second_half = sum(recent_confidence[len(recent_confidence)//2:]) / (len(recent_confidence) - len(recent_confidence)//2)
        
        diff = second_half - first_half
        
        if diff > 0.05:
            return "improving"
        elif diff < -0.05:
            return "declining"
        else:
            return "stable"
    
    def _determine_alert_level(self, confidence: float) -> str:
        """Determina el nivel de alerta basado en la confianza."""
        if confidence < self.alert_thresholds["critical"]:
            return "critical"
        elif confidence < self.alert_thresholds["high"]:
            return "high"
        elif confidence < self.alert_thresholds["medium"]:
            return "medium"
        else:
            return "low"
    
    def _check_for_alerts(self, metrics: ConfidenceMetrics, reports: List[ValidationReport]) -> None:
        """Verifica si se deben generar alertas."""
        # Alerta por confianza baja
        if metrics.alert_level in ["critical", "high"]:
            alert = Alert(
                level=metrics.alert_level,
                message=f"Confianza del sistema {metrics.alert_level}: {metrics.overall_confidence:.2f}",
                agent_name="system",
                timestamp=datetime.now()
            )
            self.active_alerts.append(alert)
        
        # Alerta por tendencia declinante
        if metrics.trend == "declining" and metrics.overall_confidence < 0.8:
            alert = Alert(
                level="medium",
                message=f"Tendencia declinante detectada: {metrics.overall_confidence:.2f}",
                agent_name="system",
                timestamp=datetime.now()
            )
            self.active_alerts.append(alert)
        
        # Alerta por errores críticos
        critical_errors = sum(len(r.get_errors()) for r in reports)
        if critical_errors > 0:
            alert = Alert(
                level="critical",
                message=f"Errores críticos detectados: {critical_errors}",
                agent_name="system",
                timestamp=datetime.now()
            )
            self.active_alerts.append(alert)
    
    def _create_default_metrics(self) -> ConfidenceMetrics:
        """Crea métricas por defecto cuando no hay datos."""
        return ConfidenceMetrics(
            overall_confidence=0.5,
            scientific_confidence=0.5,
            rag_confidence=0.5,
            orbital_confidence=0.5,
            data_quality_confidence=0.5,
            prediction_confidence=0.6,
            trend="stable",
            alert_level="medium",
            timestamp=datetime.now()
        )
    
    def get_active_alerts(self) -> List[Alert]:
        """Obtiene alertas activas no resueltas."""
        return [a for a in self.active_alerts if not a.resolved]
    
    def resolve_alert(self, alert_index: int) -> bool:
        """Marca una alerta como resuelta."""
        if 0 <= alert_index < len(self.active_alerts):
            self.active_alerts[alert_index].resolved = True
            return True
        return False
    
    def get_confidence_trend(self) -> Dict[str, Any]:
        """Obtiene la tendencia de confianza."""
        if len(self.confidence_history) < 2:
            return {"trend": "insufficient_data", "change": 0.0}
        
        recent = self.confidence_history[-1]
        previous = self.confidence_history[-2]
        
        change = recent.overall_confidence - previous.overall_confidence
        
        return {
            "trend": recent.trend,
            "change": change,
            "current_confidence": recent.overall_confidence,
            "previous_confidence": previous.overall_confidence
        }
    
    def get_system_health_report(self) -> Dict[str, Any]:
        """Obtiene reporte de salud del sistema."""
        if not self.confidence_history:
            return {"status": "no_data", "confidence": 0.0}
        
        latest = self.confidence_history[-1]
        active_alerts = self.get_active_alerts()
        
        return {
            "status": "healthy" if latest.alert_level == "low" else "degraded",
            "confidence": latest.overall_confidence,
            "scientific_confidence": latest.scientific_confidence,
            "rag_confidence": latest.rag_confidence,
            "orbital_confidence": latest.orbital_confidence,
            "data_quality_confidence": latest.data_quality_confidence,
            "prediction_confidence": latest.prediction_confidence,
            "trend": latest.trend,
            "alert_level": latest.alert_level,
            "active_alerts": len(active_alerts),
            "last_updated": latest.timestamp.isoformat()
        }
    
    def get_agent_performance(self, agent_name: str) -> Dict[str, Any]:
        """Obtiene rendimiento de un agente específico."""
        if agent_name not in self.agent_performance:
            return {"error": f"No data for agent {agent_name}"}
        
        confidences = self.agent_performance[agent_name]
        
        return {
            "agent_name": agent_name,
            "average_confidence": sum(confidences) / len(confidences),
            "min_confidence": min(confidences),
            "max_confidence": max(confidences),
            "total_measurements": len(confidences),
            "trend": "improving" if len(confidences) > 1 and confidences[-1] > confidences[0] else "stable"
        }
    
    def should_continue_simulation(self) -> bool:
        """Determina si la simulación debe continuar."""
        if not self.confidence_history:
            return True
        
        latest = self.confidence_history[-1]
        
        # No continuar si hay alertas críticas
        critical_alerts = [a for a in self.active_alerts if a.level == "critical" and not a.resolved]
        if critical_alerts:
            return False
        
        # No continuar si la confianza es muy baja
        if latest.overall_confidence < 0.3:
            return False
        
        return True
    
    def calculate_orbital_confidence(self, asteroid_data: Dict[str, Any]) -> float:
        """
        Calcula confianza basada en incertidumbre orbital de datos de NASA.
        
        Args:
            asteroid_data: Datos del asteroide de NASA API
            
        Returns:
            Confianza orbital (0.0 - 1.0)
        """
        try:
            # Obtener rango de diámetro (incertidumbre física)
            diameter_min = asteroid_data.get("diameter_min", 0)
            diameter_max = asteroid_data.get("diameter_max", 0)
            
            if diameter_min == 0 or diameter_max == 0:
                return 0.5  # Confianza media si no hay datos
            
            # Calcular incertidumbre relativa
            diameter_uncertainty = (diameter_max - diameter_min) / diameter_min
            
            # Confianza inversamente proporcional a incertidumbre
            # Menos incertidumbre = más confianza
            orbital_confidence = max(0.1, 1.0 - min(diameter_uncertainty, 0.9))
            
            # Ajustar por magnitud absoluta (objetos más brillantes = más confianza)
            absolute_magnitude = asteroid_data.get("absolute_magnitude_h", 20)
            if absolute_magnitude < 15:  # Objetos brillantes
                orbital_confidence *= 1.1
            elif absolute_magnitude > 25:  # Objetos muy débiles
                orbital_confidence *= 0.8
            
            return min(1.0, orbital_confidence)
            
        except Exception:
            return 0.5  # Confianza media en caso de error
    
    def calculate_data_quality_confidence(self, asteroid_data: Dict[str, Any]) -> float:
        """
        Calcula confianza basada en calidad y completitud de datos.
        
        Args:
            asteroid_data: Datos del asteroide
            
        Returns:
            Confianza de calidad de datos (0.0 - 1.0)
        """
        try:
            # Campos requeridos para alta confianza
            required_fields = [
                "id", "name", "diameter_min", "diameter_max", 
                "absolute_magnitude_h", "orbital_data"
            ]
            
            # Contar campos presentes
            present_fields = sum(1 for field in required_fields if asteroid_data.get(field) is not None)
            completeness = present_fields / len(required_fields)
            
            # Verificar calidad de datos orbitales
            orbital_data = asteroid_data.get("orbital_data", {})
            orbital_fields = ["eccentricity", "inclination", "semi_major_axis"]
            orbital_completeness = sum(1 for field in orbital_fields if orbital_data.get(field) is not None)
            orbital_quality = orbital_completeness / len(orbital_fields)
            
            # Verificar consistencia de datos
            consistency = self._check_data_consistency(asteroid_data)
            
            # Combinar métricas
            data_confidence = (completeness * 0.4 + orbital_quality * 0.4 + consistency * 0.2)
            
            return min(1.0, data_confidence)
            
        except Exception:
            return 0.5  # Confianza media en caso de error
    
    def calculate_prediction_confidence(self, prediction_data: Dict[str, Any]) -> float:
        """
        Calcula confianza basada en predicciones LLM.
        
        Args:
            prediction_data: Datos de predicción del LLM
            
        Returns:
            Confianza de predicción (0.0 - 1.0)
        """
        try:
            # Obtener confianza del LLM si está disponible
            llm_confidence = prediction_data.get("confidence_level", 0.6)
            
            # Verificar consistencia de la predicción
            consistency = self._check_prediction_consistency(prediction_data)
            
            # Verificar completitud de la predicción
            completeness = self._check_prediction_completeness(prediction_data)
            
            # Combinar métricas
            prediction_confidence = (llm_confidence * 0.5 + consistency * 0.3 + completeness * 0.2)
            
            return min(1.0, prediction_confidence)
            
        except Exception:
            return 0.6  # Confianza media en caso de error
    
    def _check_data_consistency(self, asteroid_data: Dict[str, Any]) -> float:
        """Verifica consistencia interna de los datos."""
        try:
            # Verificar que el diámetro mínimo sea menor que el máximo
            diameter_min = asteroid_data.get("diameter_min", 0)
            diameter_max = asteroid_data.get("diameter_max", 0)
            diameter_consistent = diameter_min <= diameter_max if diameter_min > 0 and diameter_max > 0 else 0.5
            
            # Verificar que la magnitud absoluta esté en rango razonable
            absolute_magnitude = asteroid_data.get("absolute_magnitude_h", 15)
            magnitude_consistent = 0.5 if 5 <= absolute_magnitude <= 30 else 0.2
            
            # Verificar datos orbitales
            orbital_data = asteroid_data.get("orbital_data", {})
            eccentricity = float(orbital_data.get("eccentricity", 0.5))
            eccentricity_consistent = 0.5 if 0 <= eccentricity <= 1 else 0.2
            
            return (diameter_consistent + magnitude_consistent + eccentricity_consistent) / 3
            
        except Exception:
            return 0.5
    
    def _check_prediction_consistency(self, prediction_data: Dict[str, Any]) -> float:
        """Verifica consistencia de la predicción LLM."""
        try:
            # Verificar que los campos requeridos estén presentes
            required_fields = ["summary", "confidence_level"]
            present_fields = sum(1 for field in required_fields if prediction_data.get(field) is not None)
            
            return present_fields / len(required_fields)
            
        except Exception:
            return 0.5
    
    def _check_prediction_completeness(self, prediction_data: Dict[str, Any]) -> float:
        """Verifica completitud de la predicción LLM."""
        try:
            # Verificar longitud del resumen (más largo = más completo)
            summary = prediction_data.get("summary", "")
            summary_length = len(summary.split())
            
            if summary_length > 20:
                return 1.0
            elif summary_length > 10:
                return 0.7
            elif summary_length > 5:
                return 0.4
            else:
                return 0.1
                
        except Exception:
            return 0.5