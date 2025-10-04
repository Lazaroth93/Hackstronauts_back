"""
Supervisor Híbrido
Coordina los diferentes agentes del sistema
"""

class HybridSupervisor:
    """Supervisor híbrido que coordina todos los agentes"""
    
    def __init__(self):
        """Inicializar el supervisor híbrido"""
        self.agents = {}
        self.status = "inactive"
    
    async def start(self):
        """Iniciar el supervisor"""
        self.status = "active"
        return True
    
    async def stop(self):
        """Detener el supervisor"""
        self.status = "inactive"
        return True
    
    def get_status(self):
        """Obtener el estado del supervisor"""
        return {
            "status": self.status,
            "agents": list(self.agents.keys())
        }
