"""
============================================
SERVICIO DE INVENTARIO
============================================
Lógica de negocio para gestión de inventario.
Incluye ajustes, consultas y reportes.
============================================
"""

import logging
from typing import List, Dict, Any
from datetime import datetime, date, timedelta
from repositories import ProductoRepository, MovimientoRepository
from exceptions import ProductoNoEncontradoException, DatosInvalidosException

logger = logging.getLogger(__name__)


class InventarioService:
    """Servicio para gestionar la lógica de negocio de inventario"""
    
    def __init__(self):
        self.producto_repo = ProductoRepository()
        self.movimiento_repo = MovimientoRepository()
    
    def obtener_inventario_actual(self) -> List[Dict[str, Any]]:
        """
        Obtiene el inventario actual de todos los productos.
        
        Returns:
            List[Dict]: Lista de productos con stock
        """
        try:
            productos = self.producto_repo.get_all_with_category()
            
            logger.info(f"Inventario consultado: {len(productos)} productos")
            return productos
        except Exception as e:
            logger.error(f"Error obteniendo inventario actual: {e}")
            raise
    
    def obtener_productos_stock_critico(self) -> List[Dict[str, Any]]:
        """
        Obtiene productos con stock crítico (igual o menor al mínimo).
        
        Returns:
            List[Dict]: Productos con stock crítico
        """
        try:
            productos = self.producto_repo.get_low_stock()
            
            logger.info(f"Productos con stock crítico: {len(productos)}")
            return productos
        except Exception as e:
            logger.error(f"Error obteniendo productos con stock crítico: {e}")
            raise
    
    def ajustar_inventario(
        self,
        producto_id: int,
        nuevo_stock: int,
        motivo: str,
        usuario_id: int,
        observaciones: str = None
    ) -> bool:
        """
        Realiza un ajuste manual de inventario.
        
        Args:
            producto_id (int): ID del producto
            nuevo_stock (int): Nuevo stock
            motivo (str): Motivo del ajuste (ej: 'merma', 'corrección', 'inventario físico')
            usuario_id (int): ID del usuario que realiza el ajuste
            observaciones (str): Observaciones opcionales
            
        Returns:
            bool: True si se realizó correctamente
            
        Raises:
            ProductoNoEncontradoException: Si el producto no existe
            DatosInvalidosException: Si los datos son inválidos
        """
        try:
            # Validar producto
            producto = self.producto_repo.find_by_id(producto_id)
            if not producto:
                raise ProductoNoEncontradoException(str(producto_id), "ID")
            
            # Validar nuevo stock
            if nuevo_stock < 0:
                raise DatosInvalidosException('nuevo_stock', 'No puede ser negativo')
            
            # Obtener stock anterior
            stock_anterior = producto['stock_actual']
            diferencia = nuevo_stock - stock_anterior
            
            # Actualizar stock
            self.producto_repo.update(producto_id, {'stock_actual': nuevo_stock})
            
            # Registrar movimiento
            movimiento_data = {
                'producto_id': producto_id,
                'tipo_movimiento': 'ajuste',
                'cantidad': abs(diferencia),
                'motivo': motivo,
                'referencia_id': None,
                'stock_anterior': stock_anterior,
                'stock_nuevo': nuevo_stock,
                'usuario_id': usuario_id,
                'observaciones': observaciones or f"Ajuste de inventario: {motivo}"
            }
            
            self.movimiento_repo.registrar_movimiento(movimiento_data)
            
            logger.info(
                f"Inventario ajustado: Producto {producto['nombre']}, "
                f"Stock anterior: {stock_anterior}, Nuevo stock: {nuevo_stock}"
            )
            
            return True
            
        except (ProductoNoEncontradoException, DatosInvalidosException):
            raise
        except Exception as e:
            logger.error(f"Error ajustando inventario: {e}")
            raise
    
    def obtener_historial_movimientos(
        self,
        producto_id: int = None,
        tipo_movimiento: str = None,
        fecha_inicio: date = None,
        fecha_fin: date = None,
        limite: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Obtiene el historial de movimientos de inventario.
        
        Args:
            producto_id (int): Filtrar por producto específico
            tipo_movimiento (str): Filtrar por tipo ('entrada', 'salida', 'ajuste')
            fecha_inicio (date): Fecha inicial
            fecha_fin (date): Fecha final
            limite (int): Cantidad máxima de registros
            
        Returns:
            List[Dict]: Movimientos de inventario
        """
        try:
            if fecha_inicio and fecha_fin:
                movimientos = self.movimiento_repo.get_by_date_range(fecha_inicio, fecha_fin)
            elif tipo_movimiento:
                movimientos = self.movimiento_repo.get_by_tipo(tipo_movimiento)
            elif producto_id:
                movimientos = self.movimiento_repo.get_by_producto(producto_id)
            else:
                movimientos = self.movimiento_repo.get_movimientos_recientes(limite)
            
            logger.info(f"Historial de movimientos consultado: {len(movimientos)} registros")
            return movimientos
        except Exception as e:
            logger.error(f"Error obteniendo historial de movimientos: {e}")
            raise
    
    def calcular_valor_total_inventario(self) -> Dict[str, Any]:
        """
        Calcula el valor total del inventario actual.
        
        Returns:
            Dict: Valor del inventario
        """
        try:
            productos = self.producto_repo.find_all(conditions="activo = TRUE")
            
            valor_compra = 0
            valor_venta = 0
            total_unidades = 0
            
            for producto in productos:
                stock = producto['stock_actual']
                total_unidades += stock
                valor_compra += stock * producto['precio_compra']
                valor_venta += stock * producto['precio_venta']
            
            ganancia_potencial = valor_venta - valor_compra
            margen_porcentaje = (ganancia_potencial / valor_compra * 100) if valor_compra > 0 else 0
            
            resultado = {
                'total_productos': len(productos),
                'total_unidades': total_unidades,
                'valor_compra': round(valor_compra, 2),
                'valor_venta': round(valor_venta, 2),
                'ganancia_potencial': round(ganancia_potencial, 2),
                'margen_porcentaje': round(margen_porcentaje, 2)
            }
            
            logger.info(
                f"Valor de inventario calculado: "
                f"Compra S/. {resultado['valor_compra']:.2f}, "
                f"Venta S/. {resultado['valor_venta']:.2f}"
            )
            
            return resultado
            
        except Exception as e:
            logger.error(f"Error calculando valor de inventario: {e}")
            raise
    
    def generar_reporte_rotacion(self, dias: int = 30) -> List[Dict[str, Any]]:
        """
        Genera un reporte de rotación de productos.
        
        Args:
            dias (int): Período en días para calcular la rotación
            
        Returns:
            List[Dict]: Productos con su rotación
        """
        try:
            fecha_inicio = datetime.now().date() - timedelta(days=dias)
            fecha_fin = datetime.now().date()
            
            # Obtener movimientos de salida del período
            movimientos = self.movimiento_repo.get_by_date_range(fecha_inicio, fecha_fin)
            salidas = [m for m in movimientos if m['tipo_movimiento'] == 'salida']
            
            # Agrupar por producto
            rotacion_por_producto = {}
            for movimiento in salidas:
                producto_id = movimiento['producto_id']
                if producto_id not in rotacion_por_producto:
                    rotacion_por_producto[producto_id] = {
                        'producto_codigo': movimiento.get('producto_codigo', ''),
                        'producto_nombre': movimiento.get('producto_nombre', ''),
                        'cantidad_vendida': 0,
                        'numero_ventas': 0
                    }
                rotacion_por_producto[producto_id]['cantidad_vendida'] += movimiento['cantidad']
                rotacion_por_producto[producto_id]['numero_ventas'] += 1
            
            # Obtener stock actual y calcular rotación
            resultado = []
            for producto_id, datos in rotacion_por_producto.items():
                producto = self.producto_repo.find_by_id(producto_id)
                if producto:
                    stock_actual = producto['stock_actual']
                    cantidad_vendida = datos['cantidad_vendida']
                    
                    # Tasa de rotación = cantidad vendida / stock promedio
                    # Simplificado: cantidad vendida / stock actual
                    rotacion = (cantidad_vendida / stock_actual) if stock_actual > 0 else 0
                    
                    resultado.append({
                        'producto_id': producto_id,
                        'codigo': datos['producto_codigo'],
                        'nombre': datos['producto_nombre'],
                        'stock_actual': stock_actual,
                        'cantidad_vendida': cantidad_vendida,
                        'numero_ventas': datos['numero_ventas'],
                        'tasa_rotacion': round(rotacion, 2),
                        'dias_inventario': round(dias / rotacion, 2) if rotacion > 0 else 0
                    })
            
            # Ordenar por tasa de rotación descendente
            resultado.sort(key=lambda x: x['tasa_rotacion'], reverse=True)
            
            logger.info(f"Reporte de rotación generado: {len(resultado)} productos")
            return resultado
            
        except Exception as e:
            logger.error(f"Error generando reporte de rotación: {e}")
            raise
    
    def obtener_productos_sin_movimiento(self, dias: int = 60) -> List[Dict[str, Any]]:
        """
        Obtiene productos sin movimientos en un período.
        
        Args:
            dias (int): Período en días
            
        Returns:
            List[Dict]: Productos sin movimiento
        """
        try:
            fecha_limite = datetime.now().date() - timedelta(days=dias)
            
            # Obtener todos los productos activos
            productos = self.producto_repo.get_all_with_category()
            
            productos_sin_movimiento = []
            
            for producto in productos:
                # Obtener movimientos del producto
                movimientos = self.movimiento_repo.get_by_producto(producto['id'])
                
                # Filtrar movimientos recientes
                movimientos_recientes = [
                    m for m in movimientos
                    if m['fecha_movimiento'].date() >= fecha_limite
                ]
                
                if not movimientos_recientes:
                    ultimo_movimiento = movimientos[0] if movimientos else None
                    
                    productos_sin_movimiento.append({
                        'producto_id': producto['id'],
                        'codigo': producto['codigo'],
                        'nombre': producto['nombre'],
                        'categoria': producto.get('categoria_nombre', ''),
                        'stock_actual': producto['stock_actual'],
                        'valor_inventario': producto['stock_actual'] * producto['precio_venta'],
                        'ultimo_movimiento': ultimo_movimiento['fecha_movimiento'] if ultimo_movimiento else None
                    })
            
            logger.info(f"Productos sin movimiento ({dias} días): {len(productos_sin_movimiento)}")
            return productos_sin_movimiento
            
        except Exception as e:
            logger.error(f"Error obteniendo productos sin movimiento: {e}")
            raise