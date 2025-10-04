"""
Conector de PostgreSQL
Maneja la conexión a la base de datos PostgreSQL
"""

import os
import psycopg2
import psycopg2.extras
from typing import Optional, Dict, Any, List

class PostgreSQLConnector:
    """Conector para la base de datos PostgreSQL"""
    
    def __init__(self):
        """Inicializar el conector"""
        self.connection = None
        self.cursor = None
        self.connect()
    
    def connect(self):
        """Conectar a la base de datos"""
        try:
            # Configuración de la base de datos desde variables de entorno
            db_config = {
                'host': os.getenv('DB_HOST', 'localhost'),
                'port': os.getenv('DB_PORT', '5432'),
                'database': os.getenv('DB_NAME', 'hackstronauts'),
                'user': os.getenv('DB_USER', 'postgres'),
                'password': os.getenv('DB_PASSWORD', 'password')
            }
            
            self.connection = psycopg2.connect(**db_config)
            self.cursor = self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            return True
        except Exception as e:
            print(f"Error conectando a la base de datos: {e}")
            return False
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Ejecutar una consulta SQL"""
        try:
            if not self.connection or self.connection.closed:
                self.connect()
            
            self.cursor.execute(query, params)
            
            if query.strip().upper().startswith('SELECT'):
                return self.cursor.fetchall()
            else:
                self.connection.commit()
                return []
        except Exception as e:
            print(f"Error ejecutando consulta: {e}")
            return []
    
    def close(self):
        """Cerrar la conexión"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
    
    async def close_async(self):
        """Cerrar la conexión de forma asíncrona"""
        self.close()
