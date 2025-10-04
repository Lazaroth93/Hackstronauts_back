"""
Controlador para NEOs (Near Earth Objects)
Contiene la lógica de negocio para operaciones con NEOs
Siguiendo principios SOLID - Responsabilidad única
"""

import os
import psycopg2
import psycopg2.extras
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..models.neo_models import (
    NEOSearchQuery,
    NEOResponse,
    NEOSListResponse,
    DangerousNEOResponse,
    SearchResponse,
    ApproachResponse,
    UpcomingApproachesResponse,
    RiskCategory
)


class NEOController:
    """
    Controlador para operaciones con NEOs
    
    Responsabilidades:
    - Obtener NEOs de la base de datos
    - Filtrar y buscar NEOs
    - Procesar datos de NEOs
    - Manejar paginación
    """
    
    def __init__(self):
        """Inicializa la conexión a la base de datos"""
        self.database_url = os.getenv("DATABASE_URL")
        if not self.database_url:
            raise ValueError("DATABASE_URL no está configurada")
    
    def _get_connection(self):
        """
        Obtiene una conexión a la base de datos
        
        Returns:
            psycopg2.connection: Conexión a PostgreSQL
        """
        return psycopg2.connect(
            self.database_url, 
            cursor_factory=psycopg2.extras.RealDictCursor
        )
    
    def get_all_neos(
        self, 
        page: int = 1, 
        limit: int = 20, 
        hazardous_only: bool = False,
        sort_by: str = "name",
        sort_order: str = "asc"
    ) -> NEOSListResponse:
        """
        Obtiene todos los NEOs con paginación y filtros
        
        Args:
            page: Número de página (empezando en 1)
            limit: Elementos por página
            hazardous_only: Solo NEOs peligrosos
            sort_by: Campo para ordenar
            sort_order: Orden (asc/desc)
            
        Returns:
            NEOSListResponse: Lista de NEOs con paginación
        """
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            
            # Construir query base con JOIN para obtener predicciones
            base_query = """
            SELECT 
                nd.neo_id,
                nd.name,
                nd.close_approach_date,
                nd.miss_distance_km,
                nd.diameter_min_m,
                nd.diameter_max_m,
                nd.velocity_km_s,
                nd.is_potentially_hazardous,
                np.risk_score,
                NULL as risk_category,
                NULL as impact_energy_mt,
                NULL as crater_diameter_km,
                NULL as damage_radius_km
            FROM neos_dangerous nd
            LEFT JOIN neo_predictions np ON nd.neo_id = np.neo_id
            """
            
            # Construir condiciones WHERE
            where_conditions = []
            params = []
            
            if hazardous_only:
                where_conditions.append("nd.is_potentially_hazardous = TRUE")
            
            if where_conditions:
                base_query += " WHERE " + " AND ".join(where_conditions)
            
            # Validar y aplicar ordenamiento
            valid_sort_fields = ["name", "close_approach_date", "miss_distance_km", "velocity_km_s", "risk_score"]
            if sort_by not in valid_sort_fields:
                sort_by = "name"
            
            sort_order = "ASC" if sort_order.lower() == "asc" else "DESC"
            base_query += f" ORDER BY {sort_by} {sort_order}"
            
            # Aplicar paginación
            offset = (page - 1) * limit
            base_query += f" LIMIT {limit} OFFSET {offset}"
            
            # Ejecutar query
            cur.execute(base_query, params)
            rows = cur.fetchall()
            
            # Contar total para paginación
            count_query = "SELECT COUNT(*) FROM neos_dangerous nd"
            if where_conditions:
                count_query += " WHERE " + " AND ".join(where_conditions)
            
            cur.execute(count_query, params)
            total_count = cur.fetchone()["count"]
            
            # Convertir filas a objetos NEOResponse
            neos = [self._row_to_neo_response(row) for row in rows]
            
            return NEOSListResponse(
                neos=neos,
                pagination={
                    "page": page,
                    "limit": limit,
                    "total": total_count,
                    "pages": (total_count + limit - 1) // limit
                }
            )
            
        finally:
            cur.close()
            conn.close()
    
    def get_neo_by_id(self, neo_id: str) -> Optional[NEOResponse]:
        """
        Obtiene un NEO específico por su ID
        
        Args:
            neo_id: ID del NEO
            
        Returns:
            NEOResponse o None si no se encuentra
        """
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            
            cur.execute("""
            SELECT 
                n.*,
                np.risk_score,
                NULL as risk_category,
                NULL as impact_energy_mt,
                NULL as crater_diameter_km,
                NULL as damage_radius_km,
                np.impact_area_km2,
                np.impact_probability
            FROM neos n
            LEFT JOIN neo_predictions np ON n.neo_id = np.neo_id
            WHERE n.neo_id = %s
            ORDER BY np.created_at DESC
            LIMIT 1
            """, (neo_id,))
            
            row = cur.fetchone()
            if not row:
                return None
            
            return self._row_to_neo_response(row)
            
        finally:
            cur.close()
            conn.close()
    
    def get_dangerous_neos(self, limit: int = 50) -> DangerousNEOResponse:
        """
        Obtiene NEOs potencialmente peligrosos
        
        Args:
            limit: Número máximo de NEOs
            
        Returns:
            DangerousNEOResponse: Lista de NEOs peligrosos
        """
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            
            cur.execute("""
            SELECT 
                nd.*,
                np.risk_score,
                NULL as risk_category,
                NULL as impact_energy_mt,
                NULL as crater_diameter_km,
                NULL as damage_radius_km
            FROM neos_dangerous nd
            LEFT JOIN neo_predictions np ON nd.neo_id = np.neo_id
            WHERE nd.is_potentially_hazardous = TRUE
            ORDER BY np.risk_score DESC NULLS LAST, nd.miss_distance_km ASC
            LIMIT %s
            """, (limit,))
            
            rows = cur.fetchall()
            neos = [self._row_to_neo_response(row) for row in rows]
            
            return DangerousNEOResponse(
                dangerous_neos=neos,
                count=len(neos)
            )
            
        finally:
            cur.close()
            conn.close()
    
    def search_neos(self, search_query: NEOSearchQuery) -> SearchResponse:
        """
        Busca NEOs con filtros avanzados
        
        Args:
            search_query: Parámetros de búsqueda
            
        Returns:
            SearchResponse: Resultados de la búsqueda
        """
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            
            base_query = """
            SELECT 
                nd.*,
                np.risk_score,
                NULL as impact_energy_mt
            FROM neos_dangerous nd
            LEFT JOIN neo_predictions np ON nd.neo_id = np.neo_id
            WHERE 1=1
            """
            
            params = []
            
            # Búsqueda por nombre
            if search_query.query:
                base_query += " AND LOWER(nd.name) LIKE LOWER(%s)"
                params.append(f"%{search_query.query}%")
            
            # Filtros adicionales
            if search_query.hazardous_only:
                base_query += " AND nd.is_potentially_hazardous = TRUE"
            
            if search_query.min_diameter:
                base_query += " AND nd.diameter_min_m >= %s"
                params.append(search_query.min_diameter)
            
            if search_query.max_diameter:
                base_query += " AND nd.diameter_max_m <= %s"
                params.append(search_query.max_diameter)
            
            if search_query.min_velocity:
                base_query += " AND nd.velocity_km_s >= %s"
                params.append(search_query.min_velocity)
            
            if search_query.max_velocity:
                base_query += " AND nd.velocity_km_s <= %s"
                params.append(search_query.max_velocity)
            
            base_query += " ORDER BY nd.miss_distance_km ASC LIMIT %s"
            params.append(search_query.limit)
            
            cur.execute(base_query, params)
            rows = cur.fetchall()
            
            neos = [self._row_to_neo_response(row) for row in rows]
            
            return SearchResponse(
                results=neos,
                count=len(neos),
                query=search_query.dict()
            )
            
        finally:
            cur.close()
            conn.close()
    
    def get_neo_approaches(self, neo_id: str) -> Optional[ApproachResponse]:
        """
        Obtiene todas las aproximaciones de un NEO
        
        Args:
            neo_id: ID del NEO
            
        Returns:
            ApproachResponse o None si no se encuentra
        """
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            
            cur.execute("""
            SELECT 
                close_approach_date,
                miss_distance_km,
                velocity_km_s,
                is_potentially_hazardous
            FROM neos_dangerous 
            WHERE neo_id = %s
            ORDER BY close_approach_date ASC
            """, (neo_id,))
            
            approaches = cur.fetchall()
            
            if not approaches:
                return None
            
            return ApproachResponse(
                neo_id=neo_id,
                approaches=[dict(approach) for approach in approaches],
                total_approaches=len(approaches)
            )
            
        finally:
            cur.close()
            conn.close()
    
    def get_upcoming_approaches(self, days: int = 30, limit: int = 50) -> UpcomingApproachesResponse:
        """
        Obtiene próximas aproximaciones cercanas
        
        Args:
            days: Días hacia adelante
            limit: Número máximo de aproximaciones
            
        Returns:
            UpcomingApproachesResponse: Próximas aproximaciones
        """
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            
            cur.execute("""
            SELECT 
                nd.neo_id,
                nd.name,
                nd.close_approach_date,
                nd.miss_distance_km,
                nd.velocity_km_s,
                nd.is_potentially_hazardous,
                np.risk_score,
                np.risk_category
            FROM neos_dangerous nd
            LEFT JOIN neo_predictions np ON nd.neo_id = np.neo_id
            WHERE nd.close_approach_date >= CURRENT_DATE 
            AND nd.close_approach_date <= CURRENT_DATE + INTERVAL '%s days'
            ORDER BY nd.close_approach_date ASC, nd.miss_distance_km ASC
            LIMIT %s
            """, (days, limit))
            
            approaches = cur.fetchall()
            neos = [self._row_to_neo_response(row) for row in approaches]
            
            return UpcomingApproachesResponse(
                upcoming_approaches=neos,
                count=len(neos),
                days_ahead=days
            )
            
        finally:
            cur.close()
            conn.close()
    
    def _row_to_neo_response(self, row: Dict[str, Any]) -> NEOResponse:
        """
        Convierte una fila de la base de datos a NEOResponse
        
        Args:
            row: Fila de la base de datos
            
        Returns:
            NEOResponse: Objeto de respuesta
        """
        return NEOResponse(
            neo_id=row["neo_id"],
            name=row["name"],
            close_approach_date=row.get("close_approach_date"),
            miss_distance_km=row.get("miss_distance_km"),
            diameter_min_m=row.get("estimated_diameter_min_m"),
            diameter_max_m=row.get("estimated_diameter_max_m"),
            velocity_km_s=row.get("velocity_km_s"),
            is_potentially_hazardous=row["is_potentially_hazardous"],
            risk_score=row.get("risk_score"),
            risk_category=self._map_risk_category(row.get("risk_category")),
            impact_energy_mt=row.get("impact_energy_mt"),
            crater_diameter_km=row.get("crater_diameter_km"),
            damage_radius_km=row.get("damage_radius_km")
        )
    
    def _map_risk_category(self, category: str) -> Optional[RiskCategory]:
        """Mapea categorías de riesgo de la base de datos al enum"""
        if not category:
            return None
        
        mapping = {
            "very_low": RiskCategory.VERY_LOW,
            "low": RiskCategory.LOW,
            "medium": RiskCategory.MODERATE,
            "moderate": RiskCategory.MODERATE,
            "high": RiskCategory.HIGH,
            "critical": RiskCategory.CRITICAL,
            "Muy Bajo": RiskCategory.VERY_LOW,
            "Bajo": RiskCategory.LOW,
            "Moderado": RiskCategory.MODERATE,
            "Alto": RiskCategory.HIGH,
            "Crítico": RiskCategory.CRITICAL
        }
        
        return mapping.get(category.lower(), None)