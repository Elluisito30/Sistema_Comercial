"""
============================================
REPOSITORIO DE CLIENTES
============================================
"""

import logging
from typing import List, Dict, Any, Optional
from .base_repository import BaseRepository
from config.database import execute_query

logger = logging.getLogger(__name__)


class ClienteRepository(BaseRepository):
    """Repositorio para gestionar clientes"""
    
    def __init__(self):
        super().__init__('clientes')
    
    def get_all_active(self) -> List[Dict[str, Any]]:
        """Obtiene todos los clientes activos"""
        try:
            return self.find_all(
                conditions="activo = TRUE",
                order_by="nombres ASC"
            )
        except Exception as e:
            logger.error(f"Error obteniendo clientes activos: {e}")
            raise
    
    def find_by_documento(self, numero_documento: str) -> Optional[Dict[str, Any]]:
        """
        Busca un cliente por número de documento.
        
        Args:
            numero_documento (str): Número de documento
            
        Returns:
            Dict|None: Cliente encontrado o None
        """
        try:
            query = "SELECT * FROM clientes WHERE numero_documento = %s"
            return execute_query(query, (numero_documento,), fetch='one')
        except Exception as e:
            logger.error(f"Error buscando cliente por documento: {e}")
            raise
    
    def search(self, term: str) -> List[Dict[str, Any]]:
        """
        Busca clientes por documento o nombre.
        
        Args:
            term (str): Término de búsqueda
            
        Returns:
            List[Dict]: Clientes encontrados
        """
        try:
            query = """
                SELECT * FROM clientes
                WHERE (numero_documento LIKE %s 
                   OR nombres LIKE %s 
                   OR apellidos LIKE %s
                   OR razon_social LIKE %s)
                  AND activo = TRUE
                ORDER BY nombres ASC
                LIMIT 50
            """
            search_term = f"%{term}%"
            return execute_query(
                query, 
                (search_term, search_term, search_term, search_term)
            ) or []
        except Exception as e:
            logger.error(f"Error buscando clientes: {e}")
            raise