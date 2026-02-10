"""
============================================
REPOSITORIO DE VENTAS
============================================
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from .base_repository import BaseRepository
from config.database import execute_query, get_db_cursor

logger = logging.getLogger(__name__)


class VentaRepository(BaseRepository):
    """Repositorio para gestionar ventas y sus detalles"""
    
    def __init__(self):
        super().__init__('ventas')
    
    def get_all_with_details(self) -> List[Dict[str, Any]]:
        """
        Obtiene todas las ventas con información de cliente.
        
        Returns:
            List[Dict]: Lista de ventas
        """
        try:
            query = """
                SELECT 
                    v.*,
                    c.numero_documento,
                    CONCAT(c.nombres, ' ', COALESCE(c.apellidos, '')) as cliente_nombre,
                    u.nombre_completo as vendedor_nombre
                FROM ventas v
                INNER JOIN clientes c ON v.cliente_id = c.id
                INNER JOIN usuarios u ON v.usuario_id = u.id
                ORDER BY v.fecha_venta DESC, v.id DESC
            """
            return execute_query(query) or []
        except Exception as e:
            logger.error(f"Error obteniendo ventas con detalles: {e}")
            raise
    
    def find_by_numero(self, numero_venta: str) -> Optional[Dict[str, Any]]:
        """
        Busca una venta por su número.
        
        Args:
            numero_venta (str): Número de venta
            
        Returns:
            Dict|None: Venta encontrada o None
        """
        try:
            query = """
                SELECT 
                    v.*,
                    c.numero_documento,
                    CONCAT(c.nombres, ' ', COALESCE(c.apellidos, '')) as cliente_nombre,
                    u.nombre_completo as vendedor_nombre
                FROM ventas v
                INNER JOIN clientes c ON v.cliente_id = c.id
                INNER JOIN usuarios u ON v.usuario_id = u.id
                WHERE v.numero_venta = %s
            """
            return execute_query(query, (numero_venta,), fetch='one')
        except Exception as e:
            logger.error(f"Error buscando venta por número: {e}")
            raise
    
    def get_by_cliente(self, cliente_id: int) -> List[Dict[str, Any]]:
        """
        Obtiene ventas de un cliente específico.
        
        Args:
            cliente_id (int): ID del cliente
            
        Returns:
            List[Dict]: Lista de ventas
        """
        try:
            return self.find_all(
                conditions="cliente_id = %s AND estado = 'completada'",
                params=(cliente_id,),
                order_by="fecha_venta DESC"
            )
        except Exception as e:
            logger.error(f"Error obteniendo ventas por cliente: {e}")
            raise
    
    def get_by_estado(self, estado: str) -> List[Dict[str, Any]]:
        """
        Obtiene ventas por estado.
        
        Args:
            estado (str): Estado ('completada', 'anulada')
            
        Returns:
            List[Dict]: Lista de ventas
        """
        try:
            return self.find_all(
                conditions="estado = %s",
                params=(estado,),
                order_by="fecha_venta DESC"
            )
        except Exception as e:
            logger.error(f"Error obteniendo ventas por estado: {e}")
            raise
    
    def get_by_date_range(self, fecha_inicio: date, fecha_fin: date) -> List[Dict[str, Any]]:
        """
        Obtiene ventas en un rango de fechas.
        
        Args:
            fecha_inicio (date): Fecha inicial
            fecha_fin (date): Fecha final
            
        Returns:
            List[Dict]: Lista de ventas
        """
        try:
            query = """
                SELECT 
                    v.*,
                    CONCAT(c.nombres, ' ', COALESCE(c.apellidos, '')) as cliente_nombre
                FROM ventas v
                INNER JOIN clientes c ON v.cliente_id = c.id
                WHERE v.fecha_venta BETWEEN %s AND %s
                  AND v.estado = 'completada'
                ORDER BY v.fecha_venta DESC
            """
            return execute_query(query, (fecha_inicio, fecha_fin)) or []
        except Exception as e:
            logger.error(f"Error obteniendo ventas por rango de fechas: {e}")
            raise
    
    def get_detalle(self, venta_id: int) -> List[Dict[str, Any]]:
        """
        Obtiene el detalle de productos de una venta.
        
        Args:
            venta_id (int): ID de la venta
            
        Returns:
            List[Dict]: Lista de productos vendidos
        """
        try:
            query = """
                SELECT 
                    dv.*,
                    p.codigo as producto_codigo,
                    p.nombre as producto_nombre,
                    p.unidad_medida
                FROM detalle_ventas dv
                INNER JOIN productos p ON dv.producto_id = p.id
                WHERE dv.venta_id = %s
                ORDER BY dv.id
            """
            return execute_query(query, (venta_id,)) or []
        except Exception as e:
            logger.error(f"Error obteniendo detalle de venta: {e}")
            raise
    
    def insert_detalle(self, detalle_data: Dict[str, Any]) -> Optional[int]:
        """
        Inserta un detalle de venta.
        
        Args:
            detalle_data (Dict): Datos del detalle
            
        Returns:
            int|None: ID del detalle insertado
        """
        try:
            columns = ', '.join(detalle_data.keys())
            placeholders = ', '.join(['%s'] * len(detalle_data))
            values = tuple(detalle_data.values())
            
            query = f"INSERT INTO detalle_ventas ({columns}) VALUES ({placeholders})"
            
            with get_db_cursor() as (cursor, conn):
                cursor.execute(query, values)
                conn.commit()
                inserted_id = cursor.lastrowid
                logger.info(f"Detalle de venta insertado: ID {inserted_id}")
                return inserted_id
                
        except Exception as e:
            logger.error(f"Error insertando detalle de venta: {e}")
            raise
    
    def anular_venta(self, venta_id: int) -> bool:
        """
        Anula una venta.
        
        Args:
            venta_id (int): ID de la venta
            
        Returns:
            bool: True si se anuló correctamente
        """
        try:
            return self.update(venta_id, {'estado': 'anulada'})
        except Exception as e:
            logger.error(f"Error anulando venta: {e}")
            raise
    
    def generate_numero_venta(self, tipo_comprobante: str) -> str:
        """
        Genera un número de venta único según el tipo de comprobante.
        
        Args:
            tipo_comprobante (str): Tipo ('boleta', 'factura', 'ticket')
            
        Returns:
            str: Número de venta (ej: BOL-2024-001, FAC-2024-001)
        """
        try:
            current_year = datetime.now().year
            
            # Prefijo según tipo de comprobante
            prefijos = {
                'boleta': 'BOL',
                'factura': 'FAC',
                'ticket': 'TIC'
            }
            
            prefijo = prefijos.get(tipo_comprobante, 'VEN')
            
            query = """
                SELECT numero_venta 
                FROM ventas 
                WHERE numero_venta LIKE %s
                ORDER BY id DESC 
                LIMIT 1
            """
            
            result = execute_query(query, (f"{prefijo}-{current_year}-%",), fetch='one')
            
            if result:
                last_number = int(result['numero_venta'].split('-')[-1])
                new_number = last_number + 1
            else:
                new_number = 1
            
            numero_venta = f"{prefijo}-{current_year}-{new_number:04d}"
            logger.info(f"Número de venta generado: {numero_venta}")
            return numero_venta
            
        except Exception as e:
            logger.error(f"Error generando número de venta: {e}")
            raise
    
    def get_ventas_del_dia(self, fecha: date = None) -> List[Dict[str, Any]]:
        """
        Obtiene las ventas de un día específico.
        
        Args:
            fecha (date): Fecha a consultar (hoy si no se especifica)
            
        Returns:
            List[Dict]: Lista de ventas del día
        """
        try:
            if fecha is None:
                fecha = datetime.now().date()
            
            query = """
                SELECT 
                    v.*,
                    CONCAT(c.nombres, ' ', COALESCE(c.apellidos, '')) as cliente_nombre
                FROM ventas v
                INNER JOIN clientes c ON v.cliente_id = c.id
                WHERE v.fecha_venta = %s
                  AND v.estado = 'completada'
                ORDER BY v.id DESC
            """
            return execute_query(query, (fecha,)) or []
        except Exception as e:
            logger.error(f"Error obteniendo ventas del día: {e}")
            raise
    
    def get_total_ventas_periodo(self, fecha_inicio: date, fecha_fin: date) -> float:
        """
        Obtiene el total de ventas en un período.
        
        Args:
            fecha_inicio (date): Fecha inicial
            fecha_fin (date): Fecha final
            
        Returns:
            float: Total vendido
        """
        try:
            query = """
                SELECT COALESCE(SUM(total), 0) as total_vendido
                FROM ventas
                WHERE fecha_venta BETWEEN %s AND %s
                  AND estado = 'completada'
            """
            result = execute_query(query, (fecha_inicio, fecha_fin), fetch='one')
            return float(result['total_vendido']) if result else 0.0
        except Exception as e:
            logger.error(f"Error obteniendo total de ventas: {e}")
            raise