"""
============================================
REPOSITORIO BASE
============================================
Clase abstracta con métodos comunes para todos los repositorios.
Proporciona operaciones CRUD genéricas.
============================================
"""

import logging
from typing import Optional, List, Dict, Any, Tuple
from config.database import get_db_cursor, execute_query, execute_transaction

logger = logging.getLogger(__name__)


class BaseRepository:
    """
    Clase base para todos los repositorios.
    Proporciona métodos CRUD genéricos que pueden ser reutilizados.
    """
    
    def __init__(self, table_name: str):
        """
        Inicializa el repositorio base.
        
        Args:
            table_name (str): Nombre de la tabla en la base de datos
        """
        self.table_name = table_name
    
    def find_all(self, conditions: str = "", params: tuple = None, 
                 order_by: str = "id ASC") -> List[Dict[str, Any]]:
        """
        Obtiene todos los registros de la tabla.
        
        Args:
            conditions (str): Condiciones WHERE opcionales
            params (tuple): Parámetros para las condiciones
            order_by (str): Ordenamiento
            
        Returns:
            List[Dict]: Lista de registros
        """
        try:
            query = f"SELECT * FROM {self.table_name}"
            
            if conditions:
                query += f" WHERE {conditions}"
            
            query += f" ORDER BY {order_by}"
            
            result = execute_query(query, params)
            logger.info(f"find_all en {self.table_name}: {len(result)} registros")
            return result if result else []
            
        except Exception as e:
            logger.error(f"Error en find_all de {self.table_name}: {e}")
            raise
    
    def find_by_id(self, id: int) -> Optional[Dict[str, Any]]:
        """
        Busca un registro por su ID.
        
        Args:
            id (int): ID del registro
            
        Returns:
            Dict|None: Registro encontrado o None
        """
        try:
            query = f"SELECT * FROM {self.table_name} WHERE id = %s"
            result = execute_query(query, (id,), fetch='one')
            
            if result:
                logger.debug(f"find_by_id en {self.table_name}: ID {id} encontrado")
            else:
                logger.warning(f"find_by_id en {self.table_name}: ID {id} no encontrado")
            
            return result
            
        except Exception as e:
            logger.error(f"Error en find_by_id de {self.table_name}: {e}")
            raise
    
    def insert(self, data: Dict[str, Any]) -> Optional[int]:
        """
        Inserta un nuevo registro.
        
        Args:
            data (Dict): Diccionario con los datos a insertar
            
        Returns:
            int|None: ID del registro insertado
        """
        try:
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['%s'] * len(data))
            values = tuple(data.values())
            
            query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"
            
            with get_db_cursor() as (cursor, conn):
                cursor.execute(query, values)
                conn.commit()
                inserted_id = cursor.lastrowid
                
                logger.info(f"insert en {self.table_name}: ID {inserted_id} creado")
                return inserted_id
                
        except Exception as e:
            logger.error(f"Error en insert de {self.table_name}: {e}")
            raise
    
    def update(self, id: int, data: Dict[str, Any]) -> bool:
        """
        Actualiza un registro existente.
        
        Args:
            id (int): ID del registro a actualizar
            data (Dict): Diccionario con los datos a actualizar
            
        Returns:
            bool: True si se actualizó correctamente
        """
        try:
            set_clause = ', '.join([f"{key} = %s" for key in data.keys()])
            values = tuple(data.values()) + (id,)
            
            query = f"UPDATE {self.table_name} SET {set_clause} WHERE id = %s"
            
            with get_db_cursor() as (cursor, conn):
                cursor.execute(query, values)
                conn.commit()
                affected_rows = cursor.rowcount
                
                if affected_rows > 0:
                    logger.info(f"update en {self.table_name}: ID {id} actualizado")
                    return True
                else:
                    logger.warning(f"update en {self.table_name}: ID {id} no encontrado")
                    return False
                    
        except Exception as e:
            logger.error(f"Error en update de {self.table_name}: {e}")
            raise
    
    def delete(self, id: int) -> bool:
        """
        Elimina un registro por su ID (hard delete).
        
        Args:
            id (int): ID del registro a eliminar
            
        Returns:
            bool: True si se eliminó correctamente
        """
        try:
            query = f"DELETE FROM {self.table_name} WHERE id = %s"
            
            with get_db_cursor() as (cursor, conn):
                cursor.execute(query, (id,))
                conn.commit()
                affected_rows = cursor.rowcount
                
                if affected_rows > 0:
                    logger.info(f"delete en {self.table_name}: ID {id} eliminado")
                    return True
                else:
                    logger.warning(f"delete en {self.table_name}: ID {id} no encontrado")
                    return False
                    
        except Exception as e:
            logger.error(f"Error en delete de {self.table_name}: {e}")
            raise
    
    def soft_delete(self, id: int) -> bool:
        """
        Desactiva un registro (soft delete) marcando activo = False.
        
        Args:
            id (int): ID del registro a desactivar
            
        Returns:
            bool: True si se desactivó correctamente
        """
        try:
            return self.update(id, {'activo': False})
        except Exception as e:
            logger.error(f"Error en soft_delete de {self.table_name}: {e}")
            raise
    
    def count(self, conditions: str = "", params: tuple = None) -> int:
        """
        Cuenta registros en la tabla.
        
        Args:
            conditions (str): Condiciones WHERE opcionales
            params (tuple): Parámetros para las condiciones
            
        Returns:
            int: Cantidad de registros
        """
        try:
            query = f"SELECT COUNT(*) as total FROM {self.table_name}"
            
            if conditions:
                query += f" WHERE {conditions}"
            
            result = execute_query(query, params, fetch='one')
            total = result['total'] if result else 0
            
            logger.debug(f"count en {self.table_name}: {total} registros")
            return total
            
        except Exception as e:
            logger.error(f"Error en count de {self.table_name}: {e}")
            raise