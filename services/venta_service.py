"""
============================================
SERVICIO DE VENTAS
============================================
Lógica de negocio para el proceso de ventas.
Incluye validación de stock y registro de ventas.
============================================
"""

import logging
from typing import List, Dict, Any
from datetime import datetime, date
from repositories import (
    VentaRepository,
    ProductoRepository,
    ClienteRepository,
    MovimientoRepository
)
from exceptions import (
    ClienteNoEncontradoException,
    ProductoNoEncontradoException,
    VentaNoEncontradaException,
    StockInsuficienteException,
    EstadoInvalidoException,
    DatosInvalidosException
)
from config.database import get_db_cursor

logger = logging.getLogger(__name__)


class VentaService:
    """Servicio para gestionar la lógica de negocio de ventas"""
    
    def __init__(self):
        self.venta_repo = VentaRepository()
        self.producto_repo = ProductoRepository()
        self.cliente_repo = ClienteRepository()
        self.movimiento_repo = MovimientoRepository()
    
    def registrar_venta(
        self,
        cliente_id: int,
        usuario_id: int,
        productos: List[Dict[str, Any]],
        tipo_comprobante: str = 'boleta',
        metodo_pago: str = 'efectivo',
        fecha_venta: date = None,
        descuento_global: float = 0,
        impuesto_porcentaje: float = 0.18,
        observaciones: str = None
    ) -> Dict[str, Any]:
        """
        Registra una nueva venta validando stock disponible.
        
        Args:
            cliente_id (int): ID del cliente
            usuario_id (int): ID del usuario vendedor
            productos (List[Dict]): Lista de productos:
                [{'producto_id': int, 'cantidad': int, 'precio_unitario': float, 'descuento': float}]
            tipo_comprobante (str): 'boleta', 'factura' o 'ticket'
            metodo_pago (str): 'efectivo', 'tarjeta' o 'transferencia'
            fecha_venta (date): Fecha de la venta (hoy si no se especifica)
            descuento_global (float): Descuento aplicado al total
            impuesto_porcentaje (float): Porcentaje de impuesto (default 18%)
            observaciones (str): Observaciones opcionales
            
        Returns:
            Dict: Información de la venta registrada
            
        Raises:
            ClienteNoEncontradoException: Si el cliente no existe
            ProductoNoEncontradoException: Si algún producto no existe
            StockInsuficienteException: Si no hay stock suficiente
            DatosInvalidosException: Si los datos son inválidos
        """
        try:
            # Validar cliente
            cliente = self.cliente_repo.find_by_id(cliente_id)
            if not cliente:
                raise ClienteNoEncontradoException(str(cliente_id))
            
            # Validar que hay productos
            if not productos or len(productos) == 0:
                raise DatosInvalidosException('productos', 'Debe incluir al menos un producto')
            
            # Validar tipo de comprobante
            if tipo_comprobante not in ['boleta', 'factura', 'ticket']:
                raise DatosInvalidosException('tipo_comprobante', 'Tipo inválido')
            
            # Validar método de pago
            if metodo_pago not in ['efectivo', 'tarjeta', 'transferencia']:
                raise DatosInvalidosException('metodo_pago', 'Método inválido')
            
            # Validar stock y calcular totales
            subtotal = 0
            
            for item in productos:
                # Validar producto existe
                producto = self.producto_repo.find_by_id(item['producto_id'])
                if not producto:
                    raise ProductoNoEncontradoException(str(item['producto_id']), "ID")
                
                # Validar cantidad
                if item['cantidad'] <= 0:
                    raise DatosInvalidosException('cantidad', 'Debe ser mayor a 0')
                
                # Validar stock disponible
                stock_disponible = producto['stock_actual']
                if stock_disponible < item['cantidad']:
                    raise StockInsuficienteException(
                        producto['nombre'],
                        stock_disponible,
                        item['cantidad']
                    )
                
                # Validar precio
                if item['precio_unitario'] <= 0:
                    raise DatosInvalidosException('precio_unitario', 'Debe ser mayor a 0')
                
                # Calcular subtotal del item (con descuento por producto)
                descuento_item = item.get('descuento', 0)
                subtotal_item = (item['cantidad'] * item['precio_unitario']) - descuento_item
                item['subtotal'] = subtotal_item
                subtotal += subtotal_item
            
            # Aplicar descuento global
            subtotal_con_descuento = subtotal - descuento_global
            
            # Calcular impuesto y total
            impuesto = subtotal_con_descuento * impuesto_porcentaje
            total = subtotal_con_descuento + impuesto
            
            # Fecha de venta
            if fecha_venta is None:
                fecha_venta = datetime.now().date()
            
            # Generar número de venta
            numero_venta = self.venta_repo.generate_numero_venta(tipo_comprobante)
            
            # TRANSACCIÓN: Insertar venta, detalles, actualizar stock y registrar movimientos
            venta_id = None
            
            with get_db_cursor() as (cursor, conn):
                try:
                    # 1. Insertar venta
                    datos_venta = {
                        'numero_venta': numero_venta,
                        'cliente_id': cliente_id,
                        'usuario_id': usuario_id,
                        'fecha_venta': fecha_venta,
                        'tipo_comprobante': tipo_comprobante,
                        'estado': 'completada',
                        'subtotal': round(subtotal, 2),
                        'descuento': round(descuento_global, 2),
                        'impuesto': round(impuesto, 2),
                        'total': round(total, 2),
                        'metodo_pago': metodo_pago,
                        'observaciones': observaciones
                    }
                    
                    venta_id = self.venta_repo.insert(datos_venta)
                    
                    # 2. Insertar detalles, actualizar stock y registrar movimientos
                    for item in productos:
                        producto_id = item['producto_id']
                        cantidad = item['cantidad']
                        
                        # Insertar detalle
                        detalle_data = {
                            'venta_id': venta_id,
                            'producto_id': producto_id,
                            'cantidad': cantidad,
                            'precio_unitario': item['precio_unitario'],
                            'descuento': item.get('descuento', 0),
                            'subtotal': item['subtotal']
                        }
                        self.venta_repo.insert_detalle(detalle_data)
                        
                        # Obtener stock anterior
                        stock_anterior = self.producto_repo.get_stock_actual(producto_id)
                        stock_nuevo = stock_anterior - cantidad
                        
                        # Actualizar stock
                        self.producto_repo.update_stock(producto_id, cantidad, 'restar')
                        
                        # Registrar movimiento
                        movimiento_data = {
                            'producto_id': producto_id,
                            'tipo_movimiento': 'salida',
                            'cantidad': cantidad,
                            'motivo': 'venta',
                            'referencia_id': venta_id,
                            'stock_anterior': stock_anterior,
                            'stock_nuevo': stock_nuevo,
                            'usuario_id': usuario_id,
                            'observaciones': f"Salida por venta {numero_venta}"
                        }
                        self.movimiento_repo.registrar_movimiento(movimiento_data)
                    
                    conn.commit()
                    
                    cliente_nombre = f"{cliente['nombres']} {cliente.get('apellidos', '')}".strip()
                    
                    logger.info(
                        f"Venta registrada: {numero_venta}, "
                        f"Cliente: {cliente_nombre}, "
                        f"Total: S/. {total:.2f}"
                    )
                    
                except Exception as e:
                    conn.rollback()
                    logger.error(f"Error en transacción de venta: {e}")
                    raise
            
            # Retornar información de la venta
            return {
                'venta_id': venta_id,
                'numero_venta': numero_venta,
                'cliente': f"{cliente['nombres']} {cliente.get('apellidos', '')}".strip(),
                'fecha_venta': fecha_venta,
                'tipo_comprobante': tipo_comprobante,
                'subtotal': round(subtotal, 2),
                'descuento': round(descuento_global, 2),
                'impuesto': round(impuesto, 2),
                'total': round(total, 2),
                'metodo_pago': metodo_pago,
                'cantidad_productos': len(productos),
                'estado': 'completada'
            }
            
        except (
            ClienteNoEncontradoException,
            ProductoNoEncontradoException,
            StockInsuficienteException,
            DatosInvalidosException
        ):
            raise
        except Exception as e:
            logger.error(f"Error registrando venta: {e}")
            raise
    
    def anular_venta(self, venta_id: int, usuario_id: int) -> bool:
        """
        Anula una venta y devuelve el stock.
        
        Args:
            venta_id (int): ID de la venta
            usuario_id (int): ID del usuario que anula
            
        Returns:
            bool: True si se anuló correctamente
            
        Raises:
            VentaNoEncontradaException: Si la venta no existe
            EstadoInvalidoException: Si la venta ya está anulada
        """
        try:
            # Obtener la venta
            venta = self.venta_repo.find_by_id(venta_id)
            if not venta:
                raise VentaNoEncontradaException(str(venta_id))
            
            # Validar estado
            if venta['estado'] == 'anulada':
                raise EstadoInvalidoException(
                    'Venta',
                    venta['estado'],
                    'anular venta'
                )
            
            # Obtener detalles
            detalles = self.venta_repo.get_detalle(venta_id)
            
            # TRANSACCIÓN: Devolver stock y anular venta
            with get_db_cursor() as (cursor, conn):
                try:
                    for detalle in detalles:
                        producto_id = detalle['producto_id']
                        cantidad = detalle['cantidad']
                        
                        # Obtener stock anterior
                        stock_anterior = self.producto_repo.get_stock_actual(producto_id)
                        stock_nuevo = stock_anterior + cantidad
                        
                        # Devolver stock
                        self.producto_repo.update_stock(producto_id, cantidad, 'sumar')
                        
                        # Registrar movimiento
                        movimiento_data = {
                            'producto_id': producto_id,
                            'tipo_movimiento': 'entrada',
                            'cantidad': cantidad,
                            'motivo': 'anulación de venta',
                            'referencia_id': venta_id,
                            'stock_anterior': stock_anterior,
                            'stock_nuevo': stock_nuevo,
                            'usuario_id': usuario_id,
                            'observaciones': f"Devolución por anulación de venta {venta['numero_venta']}"
                        }
                        self.movimiento_repo.registrar_movimiento(movimiento_data)
                    
                    # Anular venta
                    self.venta_repo.anular_venta(venta_id)
                    
                    conn.commit()
                    
                    logger.info(
                        f"Venta anulada: {venta['numero_venta']}, "
                        f"Stock devuelto para {len(detalles)} productos"
                    )
                    
                    return True
                    
                except Exception as e:
                    conn.rollback()
                    logger.error(f"Error en transacción de anulación de venta: {e}")
                    raise
            
        except (VentaNoEncontradaException, EstadoInvalidoException):
            raise
        except Exception as e:
            logger.error(f"Error anulando venta {venta_id}: {e}")
            raise
    
    def listar_ventas(self, estado: str = None) -> List[Dict[str, Any]]:
        """
        Lista ventas, opcionalmente filtradas por estado.
        
        Args:
            estado (str): Estado a filtrar ('completada', 'anulada')
            
        Returns:
            List[Dict]: Lista de ventas
        """
        try:
            if estado:
                ventas = self.venta_repo.get_by_estado(estado)
            else:
                ventas = self.venta_repo.get_all_with_details()
            
            logger.info(f"Ventas listadas: {len(ventas)}")
            return ventas
        except Exception as e:
            logger.error(f"Error listando ventas: {e}")
            raise
    
    def obtener_venta_completa(self, venta_id: int) -> Dict[str, Any]:
        """
        Obtiene una venta con todos sus detalles.
        
        Args:
            venta_id (int): ID de la venta
            
        Returns:
            Dict: Venta con detalles
        """
        try:
            venta = self.venta_repo.find_by_id(venta_id)
            if not venta:
                raise VentaNoEncontradaException(str(venta_id))
            
            detalles = self.venta_repo.get_detalle(venta_id)
            
            venta['detalles'] = detalles
            return venta
            
        except VentaNoEncontradaException:
            raise
        except Exception as e:
            logger.error(f"Error obteniendo venta completa {venta_id}: {e}")
            raise
    
    def obtener_ventas_del_dia(self, fecha: date = None) -> List[Dict[str, Any]]:
        """
        Obtiene las ventas de un día específico.
        
        Args:
            fecha (date): Fecha a consultar (hoy si no se especifica)
            
        Returns:
            List[Dict]: Ventas del día
        """
        try:
            ventas = self.venta_repo.get_ventas_del_dia(fecha)
            logger.info(f"Ventas del día: {len(ventas)}")
            return ventas
        except Exception as e:
            logger.error(f"Error obteniendo ventas del día: {e}")
            raise
    
    def calcular_total_ventas_periodo(
        self,
        fecha_inicio: date,
        fecha_fin: date
    ) -> Dict[str, Any]:
        """
        Calcula estadísticas de ventas en un período.
        
        Args:
            fecha_inicio (date): Fecha inicial
            fecha_fin (date): Fecha final
            
        Returns:
            Dict: Estadísticas de ventas
        """
        try:
            ventas = self.venta_repo.get_by_date_range(fecha_inicio, fecha_fin)
            
            total_vendido = sum(v['total'] for v in ventas)
            total_descuentos = sum(v['descuento'] for v in ventas)
            
            # Agrupar por método de pago
            por_metodo = {}
            for venta in ventas:
                metodo = venta['metodo_pago']
                if metodo not in por_metodo:
                    por_metodo[metodo] = {'cantidad': 0, 'monto': 0}
                por_metodo[metodo]['cantidad'] += 1
                por_metodo[metodo]['monto'] += venta['total']
            
            resultado = {
                'total_ventas': len(ventas),
                'total_vendido': round(total_vendido, 2),
                'total_descuentos': round(total_descuentos, 2),
                'promedio_por_venta': round(total_vendido / len(ventas), 2) if ventas else 0,
                'ticket_minimo': round(min((v['total'] for v in ventas), default=0), 2),
                'ticket_maximo': round(max((v['total'] for v in ventas), default=0), 2),
                'por_metodo_pago': por_metodo,
                'fecha_inicio': fecha_inicio,
                'fecha_fin': fecha_fin
            }
            
            logger.info(f"Estadísticas de ventas calculadas: S/. {resultado['total_vendido']:.2f}")
            return resultado
            
        except Exception as e:
            logger.error(f"Error calculando total de ventas: {e}")
            raise