"""
============================================
REPOSITORIO DE COMPRAS - POSTGRESQL (CORREGIDO Y VALIDADO)
============================================
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from config.database import execute_query, get_db_cursor

logger = logging.getLogger(__name__)


class CompraRepository:
    """Repositorio para gestionar compras - PostgreSQL"""
    
    def __init__(self):
        self.table_name = 'compras'
    
    def get_all_with_details(self) -> List[Dict[str, Any]]:
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
    
    def find_by_id(self, compra_id: int) -> Optional[Dict[str, Any]]:
        try:
            query = f"SELECT * FROM {self.table_name} WHERE id = %s"
            return execute_query(query, (compra_id,), fetch='one')
        except Exception as e:
            logger.error(f"Error buscando compra por ID: {e}")
            raise
    
    def find_by_numero(self, numero_compra: str) -> Optional[Dict[str, Any]]:
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
        try:
            query = f"""
                SELECT * FROM {self.table_name}
                WHERE estado = %s
                ORDER BY fecha_compra DESC
            """
            return execute_query(query, (estado,)) or []
        except Exception as e:
            logger.error(f"Error obteniendo compras por estado: {e}")
            raise
    
    def get_by_date_range(self, fecha_inicio: date, fecha_fin: date) -> List[Dict[str, Any]]:
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
    
    # ✅ CORREGIDO: Método insert() con validación robusta
    def insert(self, datos_compra: Dict[str, Any]) -> int:
        """
        Inserta compra y retorna ID REAL usando RETURNING (PostgreSQL)
        """
        # ✅ Validar campos obligatorios ANTES de intentar insertar
        campos_obligatorios = [
            'numero_compra', 'proveedor_id', 'usuario_id', 'fecha_compra',
            'tipo_comprobante', 'subtotal', 'impuesto', 'total', 'estado'
        ]
        for campo in campos_obligatorios:
            if campo not in datos_compra or datos_compra[campo] is None:
                raise ValueError(f"Campo obligatorio faltante: {campo}")
        
        query = """
            INSERT INTO compras (
                numero_compra,
                proveedor_id,
                usuario_id,
                fecha_compra,
                subtotal,
                impuesto,
                total,
                estado,
                observaciones
            ) VALUES (
                %(numero_compra)s,
                %(proveedor_id)s,
                %(usuario_id)s,
                %(fecha_compra)s,
                %(subtotal)s,
                %(impuesto)s,
                %(total)s,
                %(estado)s,
                %(observaciones)s
            ) RETURNING id
        """
        
        try:
            with get_db_cursor(dictionary=False) as (cursor, conn):
                cursor.execute(query, datos_compra)
                result = cursor.fetchone()
                
                if not result or result[0] is None:
                    raise RuntimeError("No se obtuvo ID de la compra insertada")
                
                compra_id = result[0]
                conn.commit()
                
                if not isinstance(compra_id, int) or compra_id <= 0:
                    raise ValueError(f"ID de compra inválido retornado por PostgreSQL: {compra_id}")
                
                logger.info(f"✅ Compra insertada exitosamente con ID REAL: {compra_id}")
                return compra_id
                
        except Exception as e:
            logger.error(f"❌ Error CRÍTICO insertando compra: {str(e)}")
            if 'conn' in locals() and conn:
                conn.rollback()
            raise
    
    # ✅ CORREGIDO: Sintaxis del parámetro + validación estricta
    def insert_detalle(self, detalle_data: Dict[str, Any]) -> int:  # ← ¡CORREGIDO: detalle_data: Dict!
        """
        Inserta detalle de compra con validación estricta de compra_id
        """
        # ✅ VALIDACIÓN 1: compra_id existe y es entero positivo
        if 'compra_id' not in detalle_data:
            raise ValueError("El campo 'compra_id' es obligatorio en detalle_data")
        
        compra_id = detalle_data['compra_id']
        if not isinstance(compra_id, int) or compra_id <= 0:
            raise ValueError(f"compra_id inválido: debe ser entero > 0, recibido: {compra_id} (tipo: {type(compra_id).__name__})")
        
        # ✅ VALIDACIÓN 2: Otros campos obligatorios
        campos_obligatorios = ['producto_id', 'cantidad', 'precio_unitario', 'subtotal']
        for campo in campos_obligatorios:
            if campo not in detalle_data or detalle_data[campo] is None:
                raise ValueError(f"Campo obligatorio faltante en detalle: {campo}")
        
        try:
            columns = ', '.join(detalle_data.keys())
            placeholders = ', '.join([f"%({k})s" for k in detalle_data.keys()])
            
            query = f"""
                INSERT INTO detalle_compras ({columns}) 
                VALUES ({placeholders})
                RETURNING id
            """
            
            with get_db_cursor(dictionary=False) as (cursor, conn):
                cursor.execute(query, detalle_data)
                result = cursor.fetchone()
                
                if not result or result[0] is None:
                    raise RuntimeError("No se obtuvo ID del detalle insertado")
                
                detalle_id = result[0]
                conn.commit()
                
                logger.info(
                    f"✅ Detalle insertado exitosamente | "
                    f"Detalle ID: {detalle_id} | "
                    f"Compra ID: {compra_id} | "
                    f"Producto ID: {detalle_data['producto_id']}"
                )
                return detalle_id
                
        except Exception as e:
            logger.error(f"❌ Error CRÍTICO insertando detalle (compra_id={compra_id}): {str(e)}")
            if 'conn' in locals() and conn:
                conn.rollback()
            raise
    
    def update(self, compra_id: int, datos: Dict[str, Any]) -> bool:
        try:
            set_clause = ', '.join([f"{k} = %({k})s" for k in datos.keys()])
            query = f"UPDATE {self.table_name} SET {set_clause} WHERE id = %(id)s"
            
            datos_completos = datos.copy()
            datos_completos['id'] = compra_id
            
            with get_db_cursor() as (cursor, conn):
                cursor.execute(query, datos_completos)
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            logger.error(f"Error actualizando compra: {e}")
            raise
    
    def update_estado(self, compra_id: int, nuevo_estado: str, fecha_recepcion: date = None) -> bool:
        try:
            datos = {'estado': nuevo_estado}
            if fecha_recepcion:
                datos['fecha_recepcion'] = fecha_recepcion
            
            return self.update(compra_id, datos)
        except Exception as e:
            logger.error(f"Error actualizando estado: {e}")
            raise
    
    def generate_numero_compra(self) -> str:
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
            
            new_number = int(result['numero_compra'].split('-')[-1]) + 1 if result else 1
            numero_compra = f"COM-{current_year}-{new_number:03d}"
            logger.info(f"Número de compra generado: {numero_compra}")
            return numero_compra
        except Exception as e:
            logger.error(f"Error generando número: {e}")
            raise