"""
============================================
REPOSITORIO DE PROVEEDORES
============================================
"""

import logging
from typing import List, Dict, Any, Optional
from .base_repository import BaseRepository
from config.database import execute_query

logger = logging.getLogger(__name__)


class ProveedorRepository(BaseRepository):
    """Repositorio para gestionar proveedores"""
    
    def __init__(self):
        super().__init__('proveedores')
    
    def get_all_active(self) -> List[Dict[str, Any]]:
        """Obtiene todos los proveedores activos"""
        try:
            return self.find_all(
                conditions="activo = TRUE",
                order_by="razon_social ASC"
            )
        except Exception as e:
            logger.error(f"Error obteniendo proveedores activos: {e}")
            raise
    
    def find_by_ruc(self, ruc: str) -> Optional[Dict[str, Any]]:
        """
        Busca un proveedor por RUC.
        
        Args:
            ruc (str): RUC del proveedor
            
        Returns:
            Dict|None: Proveedor encontrado o None
        """
        try:
            query = "SELECT * FROM proveedores WHERE ruc = %s"
            return execute_query(query, (ruc,), fetch='one')
        except Exception as e:
            logger.error(f"Error buscando proveedor por RUC: {e}")
            raise
    
    def search(self, term: str) -> List[Dict[str, Any]]:
        """
        Busca proveedores por RUC o razón social.
        
        Args:
            term (str): Término de búsqueda
            
        Returns:
            List[Dict]: Proveedores encontrados
        """
        try:
            query = """
                SELECT * FROM proveedores
                WHERE (ruc LIKE %s OR razon_social LIKE %s)
                  AND activo = TRUE
                ORDER BY razon_social ASC
                LIMIT 50
            """
            search_term = f"%{term}%"
            return execute_query(query, (search_term, search_term)) or []
        except Exception as e:
            logger.error(f"Error buscando proveedores: {e}")
            raise