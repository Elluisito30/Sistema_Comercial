"""
============================================
REPOSITORIO DE CATEGORÍAS
============================================
"""

import logging
from typing import List, Dict, Any, Optional
from .base_repository import BaseRepository
from config.database import execute_query

logger = logging.getLogger(__name__)


class CategoriaRepository(BaseRepository):
    """Repositorio para gestionar categorías de productos"""
    
    def __init__(self):
        super().__init__('categorias')
    
    def get_all_active(self) -> List[Dict[str, Any]]:
        """
        Obtiene todas las categorías activas.
        
        Returns:
            List[Dict]: Lista de categorías activas
        """
        try:
            return self.find_all(conditions="activo = TRUE", order_by="nombre ASC")
        except Exception as e:
            logger.error(f"Error obteniendo categorías activas: {e}")
            raise
    
    def find_by_name(self, nombre: str) -> Optional[Dict[str, Any]]:
        """
        Busca una categoría por nombre.
        
        Args:
            nombre (str): Nombre de la categoría
            
        Returns:
            Dict|None: Categoría encontrada o None
        """
        try:
            query = "SELECT * FROM categorias WHERE nombre = %s"
            return execute_query(query, (nombre,), fetch='one')
        except Exception as e:
            logger.error(f"Error buscando categoría por nombre: {e}")
            raise