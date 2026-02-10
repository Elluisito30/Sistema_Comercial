"""
============================================
REPOSITORIO DE USUARIOS
============================================
"""

import logging
from typing import List, Dict, Any, Optional
from .base_repository import BaseRepository
from config.database import execute_query

logger = logging.getLogger(__name__)


class UsuarioRepository(BaseRepository):
    """Repositorio para gestionar usuarios"""
    
    def __init__(self):
        super().__init__('usuarios')
    
    def get_all_active(self) -> List[Dict[str, Any]]:
        """Obtiene todos los usuarios activos"""
        try:
            return self.find_all(
                conditions="activo = TRUE",
                order_by="nombre_completo ASC"
            )
        except Exception as e:
            logger.error(f"Error obteniendo usuarios activos: {e}")
            raise
    
    def find_by_username(self, nombre_usuario: str) -> Optional[Dict[str, Any]]:
        """
        Busca un usuario por nombre de usuario.
        
        Args:
            nombre_usuario (str): Nombre de usuario
            
        Returns:
            Dict|None: Usuario encontrado o None
        """
        try:
            query = "SELECT * FROM usuarios WHERE nombre_usuario = %s"
            return execute_query(query, (nombre_usuario,), fetch='one')
        except Exception as e:
            logger.error(f"Error buscando usuario por username: {e}")
            raise
    
    def find_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Busca un usuario por email.
        
        Args:
            email (str): Email del usuario
            
        Returns:
            Dict|None: Usuario encontrado o None
        """
        try:
            query = "SELECT * FROM usuarios WHERE email = %s"
            return execute_query(query, (email,), fetch='one')
        except Exception as e:
            logger.error(f"Error buscando usuario por email: {e}")
            raise
    
    def get_by_rol(self, rol: str) -> List[Dict[str, Any]]:
        """
        Obtiene usuarios por rol.
        
        Args:
            rol (str): Rol ('admin', 'vendedor', 'almacenero')
            
        Returns:
            List[Dict]: Lista de usuarios
        """
        try:
            return self.find_all(
                conditions="rol = %s AND activo = TRUE",
                params=(rol,),
                order_by="nombre_completo ASC"
            )
        except Exception as e:
            logger.error(f"Error obteniendo usuarios por rol: {e}")
            raise