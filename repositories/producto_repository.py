"""
============================================
REPOSITORIO DE PRODUCTOS
============================================
"""

import logging
from typing import List, Dict, Any, Optional
from .base_repository import BaseRepository
from config.database import execute_query, get_db_cursor

logger = logging.getLogger(__name__)


class ProductoRepository(BaseRepository):
    """Repositorio para gestionar productos"""
    
    def __init__(self):
        super().__init__('productos')
    
    def get_all_with_category(self) -> List[Dict[str, Any]]:
        """
        Obtiene todos los productos con información de categoría.
        
        Returns:
            List[Dict]: Lista de productos con categoría
        """
        try:
            query = """
                SELECT 
                    p.*,
                    c.nombre as categoria_nombre
                FROM productos p
                INNER JOIN categorias c ON p.categoria_id = c.id
                WHERE p.activo = TRUE
                ORDER BY p.nombre ASC
            """
            return execute_query(query) or []
        except Exception as e:
            logger.error(f"Error obteniendo productos con categoría: {e}")
            raise
    
    def find_by_codigo(self, codigo: str) -> Optional[Dict[str, Any]]:
        """
        Busca un producto por su código.
        
        Args:
            codigo (str): Código del producto
            
        Returns:
            Dict|None: Producto encontrado o None
        """
        try:
            query = "SELECT * FROM productos WHERE codigo = %s"
            return execute_query(query, (codigo,), fetch='one')
        except Exception as e:
            logger.error(f"Error buscando producto por código: {e}")
            raise
    
    def get_by_category(self, categoria_id: int) -> List[Dict[str, Any]]:
        """
        Obtiene productos de una categoría específica.
        
        Args:
            categoria_id (int): ID de la categoría
            
        Returns:
            List[Dict]: Lista de productos
        """
        try:
            return self.find_all(
                conditions="categoria_id = %s AND activo = TRUE",
                params=(categoria_id,),
                order_by="nombre ASC"
            )
        except Exception as e:
            logger.error(f"Error obteniendo productos por categoría: {e}")
            raise
    
    def get_low_stock(self) -> List[Dict[str, Any]]:
        """
        Obtiene productos con stock bajo o igual al mínimo.
        
        Returns:
            List[Dict]: Lista de productos con stock bajo
        """
        try:
            query = """
                SELECT 
                    p.*,
                    c.nombre as categoria_nombre,
                    (p.stock_minimo - p.stock_actual) as cantidad_requerida
                FROM productos p
                INNER JOIN categorias c ON p.categoria_id = c.id
                WHERE p.stock_actual <= p.stock_minimo 
                  AND p.activo = TRUE
                ORDER BY cantidad_requerida DESC
            """
            return execute_query(query) or []
        except Exception as e:
            logger.error(f"Error obteniendo productos con stock bajo: {e}")
            raise
    
    def update_stock(self, producto_id: int, cantidad: int, operacion: str = 'sumar') -> bool:
        """
        Actualiza el stock de un producto.
        
        Args:
            producto_id (int): ID del producto
            cantidad (int): Cantidad a sumar o restar
            operacion (str): 'sumar' o 'restar'
            
        Returns:
            bool: True si se actualizó correctamente
        """
        try:
            if operacion == 'sumar':
                query = "UPDATE productos SET stock_actual = stock_actual + %s WHERE id = %s"
            else:  # restar
                query = "UPDATE productos SET stock_actual = stock_actual - %s WHERE id = %s"
            
            with get_db_cursor() as (cursor, conn):
                cursor.execute(query, (cantidad, producto_id))
                conn.commit()
                
                if cursor.rowcount > 0:
                    logger.info(f"Stock actualizado: Producto {producto_id}, {operacion} {cantidad}")
                    return True
                return False
                
        except Exception as e:
            logger.error(f"Error actualizando stock: {e}")
            raise
    
    def get_stock_actual(self, producto_id: int) -> Optional[int]:
        """
        Obtiene el stock actual de un producto.
        
        Args:
            producto_id (int): ID del producto
            
        Returns:
            int|None: Stock actual o None
        """
        try:
            query = "SELECT stock_actual FROM productos WHERE id = %s"
            result = execute_query(query, (producto_id,), fetch='one')
            return result['stock_actual'] if result else None
        except Exception as e:
            logger.error(f"Error obteniendo stock actual: {e}")
            raise
    
    def search(self, term: str) -> List[Dict[str, Any]]:
        """
        Busca productos por código o nombre.
        
        Args:
            term (str): Término de búsqueda
            
        Returns:
            List[Dict]: Productos encontrados
        """
        try:
            query = """
                SELECT 
                    p.*,
                    c.nombre as categoria_nombre
                FROM productos p
                INNER JOIN categorias c ON p.categoria_id = c.id
                WHERE (p.codigo LIKE %s OR p.nombre LIKE %s)
                  AND p.activo = TRUE
                ORDER BY p.nombre ASC
                LIMIT 50
            """
            search_term = f"%{term}%"
            return execute_query(query, (search_term, search_term)) or []
        except Exception as e:
            logger.error(f"Error buscando productos: {e}")
            raise