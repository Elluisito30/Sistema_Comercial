"""
============================================
REPOSITORIO DE MOVIMIENTOS DE INVENTARIO
============================================
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from .base_repository import BaseRepository
from config.database import execute_query

logger = logging.getLogger(__name__)


class MovimientoRepository(BaseRepository):
    """Repositorio para gestionar movimientos de inventario"""
    
    def __init__(self):
        super().__init__('movimientos_inventario')
    
    def get_all_with_details(self) -> List[Dict[str, Any]]:
        """
        Obtiene todos los movimientos con detalles de producto y usuario.
        
        Returns:
            List[Dict]: Lista de movimientos
        """
        try:
            query = """
                SELECT 
                    mi.*,
                    p.codigo as producto_codigo,
                    p.nombre as producto_nombre,
                    u.nombre_completo as usuario_nombre
                FROM movimientos_inventario mi
                INNER JOIN productos p ON mi.producto_id = p.id
                INNER JOIN usuarios u ON mi.usuario_id = u.id
                ORDER BY mi.fecha_movimiento DESC
                LIMIT 100
            """
            return execute_query(query) or []
        except Exception as e:
            logger.error(f"Error obteniendo movimientos con detalles: {e}")
            raise
    
    def get_by_producto(self, producto_id: int) -> List[Dict[str, Any]]:
        """
        Obtiene movimientos de un producto específico.
        
        Args:
            producto_id (int): ID del producto
            
        Returns:
            List[Dict]: Lista de movimientos
        """
        try:
            query = """
                SELECT 
                    mi.*,
                    u.nombre_completo as usuario_nombre
                FROM movimientos_inventario mi
                INNER JOIN usuarios u ON mi.usuario_id = u.id
                WHERE mi.producto_id = %s
                ORDER BY mi.fecha_movimiento DESC
            """
            return execute_query(query, (producto_id,)) or []
        except Exception as e:
            logger.error(f"Error obteniendo movimientos por producto: {e}")
            raise
    
    def get_by_tipo(self, tipo_movimiento: str) -> List[Dict[str, Any]]:
        """
        Obtiene movimientos por tipo.
        
        Args:
            tipo_movimiento (str): Tipo ('entrada', 'salida', 'ajuste')
            
        Returns:
            List[Dict]: Lista de movimientos
        """
        try:
            return self.find_all(
                conditions="tipo_movimiento = %s",
                params=(tipo_movimiento,),
                order_by="fecha_movimiento DESC"
            )
        except Exception as e:
            logger.error(f"Error obteniendo movimientos por tipo: {e}")
            raise
    
    def get_by_date_range(self, fecha_inicio: date, fecha_fin: date) -> List[Dict[str, Any]]:
        """
        Obtiene movimientos en un rango de fechas.
        
        Args:
            fecha_inicio (date): Fecha inicial
            fecha_fin (date): Fecha final
            
        Returns:
            List[Dict]: Lista de movimientos
        """
        try:
            query = """
                SELECT 
                    mi.*,
                    p.codigo as producto_codigo,
                    p.nombre as producto_nombre,
                    u.nombre_completo as usuario_nombre
                FROM movimientos_inventario mi
                INNER JOIN productos p ON mi.producto_id = p.id
                INNER JOIN usuarios u ON mi.usuario_id = u.id
                WHERE DATE(mi.fecha_movimiento) BETWEEN %s AND %s
                ORDER BY mi.fecha_movimiento DESC
            """
            return execute_query(query, (fecha_inicio, fecha_fin)) or []
        except Exception as e:
            logger.error(f"Error obteniendo movimientos por rango de fechas: {e}")
            raise
    
    def get_movimientos_recientes(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Obtiene los movimientos más recientes.
        
        Args:
            limit (int): Cantidad de registros a retornar
            
        Returns:
            List[Dict]: Lista de movimientos recientes
        """
        try:
            query = f"""
                SELECT 
                    mi.*,
                    p.codigo as producto_codigo,
                    p.nombre as producto_nombre,
                    u.nombre_completo as usuario_nombre
                FROM movimientos_inventario mi
                INNER JOIN productos p ON mi.producto_id = p.id
                INNER JOIN usuarios u ON mi.usuario_id = u.id
                ORDER BY mi.fecha_movimiento DESC
                LIMIT {limit}
            """
            return execute_query(query) or []
        except Exception as e:
            logger.error(f"Error obteniendo movimientos recientes: {e}")
            raise
    
    def registrar_movimiento(self, movimiento_data: Dict[str, Any]) -> Optional[int]:
        """
        Registra un nuevo movimiento de inventario.
        Esta función es un alias de insert() con logging específico.
        
        Args:
            movimiento_data (Dict): Datos del movimiento
            
        Returns:
            int|None: ID del movimiento registrado
        """
        try:
            movimiento_id = self.insert(movimiento_data)
            
            if movimiento_id:
                logger.info(
                    f"Movimiento registrado: Producto {movimiento_data['producto_id']}, "
                    f"Tipo {movimiento_data['tipo_movimiento']}, "
                    f"Cantidad {movimiento_data['cantidad']}"
                )
            
            return movimiento_id
        except Exception as e:
            logger.error(f"Error registrando movimiento: {e}")
            raise