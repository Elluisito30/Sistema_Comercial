"""
============================================
REPOSITORIO DE COMPRAS
============================================
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from .base_repository import BaseRepository
from config.database import execute_query, get_db_cursor

logger = logging.getLogger(__name__)


class CompraRepository(BaseRepository):
    """Repositorio para gestionar compras y sus detalles"""
    
    def __init__(self):
        super().__init__('compras')
    
    def get_all_with_details(self) -> List[Dict[str, Any]]:
        """
        Obtiene todas las compras con información de proveedor.
        
        Returns:
            List[Dict]: Lista de compras
        """
        try:
            query = """
                SELECT 
                    c.*,
                    p.razon_social as proveedor_nombre,
                    u.nombre_completo as usuario_nombre
                FROM compras c
                INNER JOIN proveedores p ON c.proveedor_id = p.id
                INNER JOIN usuarios u ON c.usuario_id = u.id
                ORDER BY c.fecha_compra DESC, c.id DESC
            """
            return execute_query(query) or []
        except Exception as e:
            logger.error(f"Error obteniendo compras con detalles: {e}")
            raise
    
    def find_by_numero(self, numero_compra: str) -> Optional[Dict[str, Any]]:
        """
        Busca una compra por su número.
        
        Args:
            numero_compra (str): Número de compra
            
        Returns:
            Dict|None: Compra encontrada o None
        """
        try:
            query = """
                SELECT 
                    c.*,
                    p.razon_social as proveedor_nombre,
                    u.nombre_completo as usuario_nombre
                FROM compras c
                INNER JOIN proveedores p ON c.proveedor_id = p.id
                INNER JOIN usuarios u ON c.usuario_id = u.id
                WHERE c.numero_compra = %s
            """
            return execute_query(query, (numero_compra,), fetch='one')
        except Exception as e:
            logger.error(f"Error buscando compra por número: {e}")
            raise
    
    def get_by_proveedor(self, proveedor_id: int) -> List[Dict[str, Any]]:
        """
        Obtiene compras de un proveedor específico.
        
        Args:
            proveedor_id (int): ID del proveedor
            
        Returns:
            List[Dict]: Lista de compras
        """
        try:
            query = """
                SELECT c.*, p.razon_social as proveedor_nombre
                FROM compras c
                INNER JOIN proveedores p ON c.proveedor_id = p.id
                WHERE c.proveedor_id = %s
                ORDER BY c.fecha_compra DESC
            """
            return execute_query(query, (proveedor_id,)) or []
        except Exception as e:
            logger.error(f"Error obteniendo compras por proveedor: {e}")
            raise
    
    def get_by_estado(self, estado: str) -> List[Dict[str, Any]]:
        """
        Obtiene compras por estado.
        
        Args:
            estado (str): Estado ('pendiente', 'recibida', 'cancelada')
            
        Returns:
            List[Dict]: Lista de compras
        """
        try:
            return self.find_all(
                conditions="estado = %s",
                params=(estado,),
                order_by="fecha_compra DESC"
            )
        except Exception as e:
            logger.error(f"Error obteniendo compras por estado: {e}")
            raise
    
    def get_by_date_range(self, fecha_inicio: date, fecha_fin: date) -> List[Dict[str, Any]]:
        """
        Obtiene compras en un rango de fechas.
        
        Args:
            fecha_inicio (date): Fecha inicial
            fecha_fin (date): Fecha final
            
        Returns:
            List[Dict]: Lista de compras
        """
        try:
            query = """
                SELECT 
                    c.*,
                    p.razon_social as proveedor_nombre
                FROM compras c
                INNER JOIN proveedores p ON c.proveedor_id = p.id
                WHERE c.fecha_compra BETWEEN %s AND %s
                ORDER BY c.fecha_compra DESC
            """
            return execute_query(query, (fecha_inicio, fecha_fin)) or []
        except Exception as e:
            logger.error(f"Error obteniendo compras por rango de fechas: {e}")
            raise
    
    def get_detalle(self, compra_id: int) -> List[Dict[str, Any]]:
        """
        Obtiene el detalle de productos de una compra.
        
        Args:
            compra_id (int): ID de la compra
            
        Returns:
            List[Dict]: Lista de productos comprados
        """
        try:
            query = """
                SELECT 
                    dc.*,
                    p.codigo as producto_codigo,
                    p.nombre as producto_nombre,
                    p.unidad_medida
                FROM detalle_compras dc
                INNER JOIN productos p ON dc.producto_id = p.id
                WHERE dc.compra_id = %s
                ORDER BY dc.id
            """
            return execute_query(query, (compra_id,)) or []
        except Exception as e:
            logger.error(f"Error obteniendo detalle de compra: {e}")
            raise
    
    def insert_detalle(self, detalle_data: Dict[str, Any]) -> Optional[int]:
        """
        Inserta un detalle de compra.
        
        Args:
            detalle_data (Dict): Datos del detalle
            
        Returns:
            int|None: ID del detalle insertado
        """
        try:
            columns = ', '.join(detalle_data.keys())
            placeholders = ', '.join(['%s'] * len(detalle_data))
            values = tuple(detalle_data.values())
            
            query = f"INSERT INTO detalle_compras ({columns}) VALUES ({placeholders})"
            
            with get_db_cursor() as (cursor, conn):
                cursor.execute(query, values)
                conn.commit()
                inserted_id = cursor.lastrowid
                logger.info(f"Detalle de compra insertado: ID {inserted_id}")
                return inserted_id
                
        except Exception as e:
            logger.error(f"Error insertando detalle de compra: {e}")
            raise
    
    def update_estado(self, compra_id: int, nuevo_estado: str, fecha_recepcion: date = None) -> bool:
        """
        Actualiza el estado de una compra.
        
        Args:
            compra_id (int): ID de la compra
            nuevo_estado (str): Nuevo estado
            fecha_recepcion (date): Fecha de recepción (opcional)
            
        Returns:
            bool: True si se actualizó correctamente
        """
        try:
            data = {'estado': nuevo_estado}
            
            if fecha_recepcion:
                data['fecha_recepcion'] = fecha_recepcion
            
            return self.update(compra_id, data)
        except Exception as e:
            logger.error(f"Error actualizando estado de compra: {e}")
            raise
    
    def generate_numero_compra(self) -> str:
        """
        Genera un número de compra único.
        
        Returns:
            str: Número de compra (ej: COM-2024-001)
        """
        try:
            current_year = datetime.now().year
            
            query = """
                SELECT numero_compra 
                FROM compras 
                WHERE numero_compra LIKE %s
                ORDER BY id DESC 
                LIMIT 1
            """
            
            result = execute_query(query, (f"COM-{current_year}-%",), fetch='one')
            
            if result:
                # Extraer el número secuencial
                last_number = int(result['numero_compra'].split('-')[-1])
                new_number = last_number + 1
            else:
                new_number = 1
            
            numero_compra = f"COM-{current_year}-{new_number:03d}"
            logger.info(f"Número de compra generado: {numero_compra}")
            return numero_compra
            
        except Exception as e:
            logger.error(f"Error generando número de compra: {e}")
            raise