"""
Base agent class for all specialized agents in the AsteroidDefender AI system.

Este archivo define la clase base que todos los agentes especializados van a heredar.
Es importante porque:
1. Establece una interfaz común para todos los agentes
2. Evita duplicar código entre agentes
3. Facilita el mantenimiento y la consistencia
4. Permite agregar funcionalidad común a todos los agentes de una vez
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
from pydantic import BaseModel


class AgentState(BaseModel):
    """
    Estado compartido entre todos los agentes del sistema.
    
    Esta clase es crucial porque:
    - Mantiene el estado de la simulación en un solo lugar
    - Permite que los agentes compartan información entre ellos
    - Facilita el debugging y el seguimiento del flujo de datos
    - Usa Pydantic para validación automática de tipos
    """
    
    # Datos de entrada del asteroide
    asteroid_data: Dict[str, Any] = {}
    simulation_parameters: Dict[str, Any] = {}
    
    # Resultados de cada agente (se van llenando conforme avanza la simulación)
    data_collection_result: Dict[str, Any] = {}
    trajectory_analysis: Dict[str, Any] = {}
    impact_analysis: Dict[str, Any] = {}
    mitigation_strategies: List[Dict[str, Any]] = []
    mitigation_analysis: Dict[str, Any] = {}  # Análisis completo de mitigación con confianzas
    visualization_data: Dict[str, Any] = {}
    explanation_data: Dict[str, Any] = {}  # Explicaciones científicas comprensibles
    ml_predictions: Dict[str, Any] = {}
    explanation: str = ""
    
    # Control del flujo de ejecución
    current_step: str = "data_collection"  # Indica en qué paso estamos
    status: str = "running"  # Estado de la simulación: running, failed, completed
    errors: List[str] = []  # Lista de errores encontrados
    warnings: List[str] = []  # Lista de advertencias
    supervision_results: Dict[str, Any] = {}  # Resultados de supervisión


class BaseAgent(ABC):
    """
    Clase base abstracta para todos los agentes especializados.
    
    Esta clase es fundamental porque:
    - Define la interfaz común que todos los agentes deben implementar
    - Proporciona funcionalidad común (logging, validación, etc.)
    - Facilita el testing y el mantenimiento
    - Permite agregar funcionalidad a todos los agentes de una vez
    """
    
    def __init__(self, name: str, description: str):
        """
        Inicializa el agente base.
        
        Args:
            name: Nombre único del agente
            description: Descripción de qué hace el agente
        """
        self.name = name
        self.description = description
    
    @abstractmethod
    async def execute(self, state: AgentState) -> AgentState:
        """
        Método principal que ejecuta la lógica del agente.
        
        Este método DEBE ser implementado por cada agente especializado.
        Es el corazón de cada agente - aquí es donde se hace el trabajo real.
        
        Args:
            state: Estado actual de la simulación
            
        Returns:
            Estado actualizado después de ejecutar el agente
        """
        pass
    
    def validate_input(self, state: AgentState) -> bool:
        """
        Valida que los datos de entrada sean correctos para este agente.
        
        Este método puede ser sobrescrito por cada agente para validaciones específicas.
        Es importante validar los datos antes de procesarlos para evitar errores.
        
        Args:
            state: Estado actual de la simulación
            
        Returns:
            True si los datos son válidos, False en caso contrario
        """
        return True
    
    def log_error(self, state: AgentState, error: str) -> None:
        """
        Registra un error en el estado de la simulación.
        
        Es importante registrar errores para:
        - Debugging y resolución de problemas
        - Monitoreo del sistema
        - Mejora continua del código
        
        Args:
            state: Estado actual de la simulación
            error: Mensaje de error a registrar
        """
        state.errors.append(f"[{self.name}] {error}")
    
    def log_warning(self, state: AgentState, warning: str) -> None:
        """
        Registra una advertencia en el estado de la simulación.
        
        Las advertencias son menos críticas que los errores pero importantes para:
        - Alertar sobre situaciones potencialmente problemáticas
        - Mejorar la calidad de los resultados
        - Facilitar el debugging
        
        Args:
            state: Estado actual de la simulación
            warning: Mensaje de advertencia a registrar
        """
        state.warnings.append(f"[{self.name}] {warning}")
    
    def __str__(self) -> str:
        """
        Representación en string del agente.
        
        Útil para debugging y logging.
        """
        return f"{self.name}: {self.description}"
