"""
Validador base para el sistema anti-alucinación.

Define la interfaz común para todos los validadores especializados
que verifican la veracidad científica de los resultados de los agentes.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Tuple, Optional
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime


class ValidationLevel(str, Enum):
    """Niveles de validación disponibles."""
    CRITICAL = "critical"      # Errores que invalidan el resultado
    WARNING = "warning"        # Advertencias que requieren atención
    INFO = "info"             # Información adicional
    SUCCESS = "success"       # Validación exitosa


class ValidationResult(BaseModel):
    """Resultado de una validación individual."""
    level: ValidationLevel = Field(description="Nivel de severidad")
    message: str = Field(description="Mensaje descriptivo del problema")
    field: Optional[str] = Field(default=None, description="Campo específico que falló")
    expected_value: Optional[Any] = Field(default=None, description="Valor esperado")
    actual_value: Optional[Any] = Field(default=None, description="Valor actual")
    confidence: float = Field(ge=0.0, le=1.0, description="Nivel de confianza (0-1)")
    timestamp: datetime = Field(default_factory=datetime.now, description="Momento de la validación")
    
    class Config:
        json_schema_extra = {
            "example": {
                "level": "warning",
                "message": "El valor de energía cinética está fuera del rango esperado",
                "field": "kinetic_energy",
                "expected_value": "1e15 - 1e20 J",
                "actual_value": "1e25 J",
                "confidence": 0.85
            }
        }


class ValidationReport(BaseModel):
    """Reporte completo de validación para un agente."""
    agent_name: str = Field(description="Nombre del agente validado")
    overall_confidence: float = Field(ge=0.0, le=1.0, description="Confianza general (0-1)")
    is_valid: bool = Field(description="Si el resultado es válido")
    validation_count: int = Field(description="Número total de validaciones")
    results: List[ValidationResult] = Field(default_factory=list, description="Resultados individuales")
    timestamp: datetime = Field(default_factory=datetime.now, description="Momento del reporte")
    
    def add_result(self, result: ValidationResult) -> None:
        """Agrega un resultado de validación al reporte."""
        self.results.append(result)
        self.validation_count = len(self.results)
        
        # Recalcular confianza general
        if self.results:
            total_confidence = sum(r.confidence for r in self.results)
            self.overall_confidence = total_confidence / len(self.results)
            
            # Determinar si es válido (sin errores críticos)
            critical_errors = [r for r in self.results if r.level == ValidationLevel.CRITICAL]
            self.is_valid = len(critical_errors) == 0
    
    def get_errors(self) -> List[ValidationResult]:
        """Obtiene solo los errores críticos."""
        return [r for r in self.results if r.level == ValidationLevel.CRITICAL]
    
    def get_warnings(self) -> List[ValidationResult]:
        """Obtiene solo las advertencias."""
        return [r for r in self.results if r.level == ValidationLevel.WARNING]
    
    def get_summary(self) -> Dict[str, Any]:
        """Obtiene un resumen del reporte."""
        return {
            "agent": self.agent_name,
            "valid": self.is_valid,
            "confidence": self.overall_confidence,
            "total_validations": self.validation_count,
            "errors": len(self.get_errors()),
            "warnings": len(self.get_warnings()),
            "timestamp": self.timestamp.isoformat()
        }


class BaseValidator(ABC):
    """
    Validador base abstracto para verificar resultados de agentes.
    
    Cada validador especializado debe heredar de esta clase e implementar
    los métodos de validación específicos para su dominio científico.
    """
    
    def __init__(self, name: str, description: str):
        """
        Inicializa el validador base.
        
        Args:
            name: Nombre del validador (ej. "PhysicsValidator")
            description: Descripción de qué valida
        """
        self.name = name
        self.description = description
        self.validation_rules = self._load_validation_rules()
    
    @abstractmethod
    def _load_validation_rules(self) -> Dict[str, Any]:
        """
        Carga las reglas de validación específicas del dominio.
        
        Returns:
            Diccionario con reglas de validación
        """
        pass
    
    @abstractmethod
    def validate(self, agent_data: Dict[str, Any], context: Dict[str, Any]) -> ValidationReport:
        """
        Valida los datos de un agente específico.
        
        Args:
            agent_data: Datos producidos por el agente
            context: Contexto adicional para la validación
            
        Returns:
            Reporte de validación completo
        """
        pass
    
    def create_validation_result(
        self,
        level: ValidationLevel,
        message: str,
        field: Optional[str] = None,
        expected_value: Optional[Any] = None,
        actual_value: Optional[Any] = None,
        confidence: float = 1.0
    ) -> ValidationResult:
        """
        Crea un resultado de validación estandarizado.
        
        Args:
            level: Nivel de severidad
            message: Mensaje descriptivo
            field: Campo específico (opcional)
            expected_value: Valor esperado (opcional)
            actual_value: Valor actual (opcional)
            confidence: Nivel de confianza (0-1)
            
        Returns:
            Resultado de validación
        """
        return ValidationResult(
            level=level,
            message=message,
            field=field,
            expected_value=expected_value,
            actual_value=actual_value,
            confidence=confidence
        )
    
    def validate_range(
        self,
        value: float,
        min_val: float,
        max_val: float,
        field_name: str,
        unit: str = ""
    ) -> ValidationResult:
        """
        Valida que un valor esté dentro de un rango esperado.
        
        Args:
            value: Valor a validar
            min_val: Valor mínimo esperado
            max_val: Valor máximo esperado
            field_name: Nombre del campo
            unit: Unidad de medida (opcional)
            
        Returns:
            Resultado de validación
        """
        if min_val <= value <= max_val:
            return self.create_validation_result(
                level=ValidationLevel.SUCCESS,
                message=f"Valor de {field_name} dentro del rango esperado",
                field=field_name,
                actual_value=f"{value} {unit}".strip(),
                confidence=1.0
            )
        else:
            level = ValidationLevel.CRITICAL if value < min_val * 0.1 or value > max_val * 10 else ValidationLevel.WARNING
            return self.create_validation_result(
                level=level,
                message=f"Valor de {field_name} fuera del rango esperado",
                field=field_name,
                expected_value=f"{min_val} - {max_val} {unit}".strip(),
                actual_value=f"{value} {unit}".strip(),
                confidence=0.3
            )
    
    def validate_physics_constant(
        self,
        value: float,
        expected: float,
        tolerance: float,
        constant_name: str
    ) -> ValidationResult:
        """
        Valida constantes físicas contra valores conocidos.
        
        Args:
            value: Valor calculado
            expected: Valor esperado de la constante
            tolerance: Tolerancia permitida (0-1)
            constant_name: Nombre de la constante
            
        Returns:
            Resultado de validación
        """
        relative_error = abs(value - expected) / expected
        
        if relative_error <= tolerance:
            return self.create_validation_result(
                level=ValidationLevel.SUCCESS,
                message=f"Constante {constant_name} calculada correctamente",
                field=constant_name,
                actual_value=value,
                confidence=1.0
            )
        else:
            return self.create_validation_result(
                level=ValidationLevel.CRITICAL,
                message=f"Constante {constant_name} con error excesivo",
                field=constant_name,
                expected_value=expected,
                actual_value=value,
                confidence=0.1
            )
    
    def validate_data_consistency(
        self,
        data: Dict[str, Any],
        required_fields: List[str]
    ) -> List[ValidationResult]:
        """
        Valida que los datos tengan los campos requeridos.
        
        Args:
            data: Datos a validar
            required_fields: Lista de campos requeridos
            
        Returns:
            Lista de resultados de validación
        """
        results = []
        
        for field in required_fields:
            if field not in data:
                results.append(self.create_validation_result(
                    level=ValidationLevel.CRITICAL,
                    message=f"Campo requerido '{field}' no encontrado",
                    field=field,
                    confidence=0.0
                ))
            elif data[field] is None:
                results.append(self.create_validation_result(
                    level=ValidationLevel.CRITICAL,
                    message=f"Campo requerido '{field}' es nulo",
                    field=field,
                    confidence=0.0
                ))
            else:
                results.append(self.create_validation_result(
                    level=ValidationLevel.SUCCESS,
                    message=f"Campo '{field}' presente y válido",
                    field=field,
                    confidence=1.0
                ))
        
        return results