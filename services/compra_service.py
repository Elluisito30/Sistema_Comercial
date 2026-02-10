"""
============================================
SERVICIO DE COMPRAS
============================================
Lógica de negocio para el proceso de compras.
Incluye registro de compras y actualización de inventario.
============================================
"""

import logging
from typing import List, Dict, Any
from datetime import datetime, date
from repositories import (
    CompraRepository, 
    ProductoRepository, 
    ProveedorRepository,
    MovimientoRepository
)
from exceptions import (
    ProveedorNoEncontradoException,
    ProductoNoEncontradoException,
    CompraNoEncontradaException,
    EstadoInvalidoException,
    DatosInvalidosException
)
from config.database import get_db_cursor

logger = logging.getLogger(__name__)


class CompraService:
    """Servicio para gestionar la lógica de negocio de compras"""
    
    def __init__(self):
        self.compra_repo = CompraRepository()
        self.producto_repo = ProductoRepository()
        self.proveedor_repo = ProveedorRepository()
        self.movimiento_repo = MovimientoRepository()
    
    def registrar_compra(
        self, 
        proveedor_id: int,
        usuario_id: int,
        productos: List[Dict[str, Any]],
        fecha_compra: date = None,
        impuesto_porcentaje: float = 0.18,
        observaciones: str = None
    ) -> Dict[str, Any]:
        """
        Registra una nueva compra con sus detalles.
        
        Args:
            proveedor_id (int): ID del proveedor
            usuario_id (int): ID del usuario que registra
            productos (List[Dict]): Lista de productos con estructura:
                [{'producto_id': int, 'cantidad': int, 'precio_unitario': float}]
            fecha_compra (date): Fecha de la compra (hoy si no se especifica)
            impuesto_porcentaje (float): Porcentaje de impuesto (default 18%)
            observaciones (str): Observaciones opcionales
            
        Returns:
            Dict: Información de la compra registrada
            
        Raises:
            ProveedorNoEncontradoException: Si el proveedor no existe
            ProductoNoEncontradoException: Si algún producto no existe
            DatosInvalidosException: Si los datos son inválidos
        """
        try:
            # Validar proveedor
            proveedor = self.proveedor_repo.find_by_id(proveedor_id)
            if not proveedor:
                raise ProveedorNoEncontradoException(str(proveedor_id))
            
            # Validar que hay productos
            if not productos or len(productos) == 0:
                raise DatosInvalidosException('productos', 'Debe incluir al menos un producto')
            
            # Validar cada producto y calcular totales
            subtotal = 0
            for item in productos:
                # Validar producto existe
                producto = self.producto_repo.find_by_id(item['producto_id'])
                if not producto:
                    raise ProductoNoEncontradoException(str(item['producto_id']), "ID")
                
                # Validar datos del item
                if item['cantidad'] <= 0:
                    raise DatosInvalidosException('cantidad', 'Debe ser mayor a 0')
                
                if item['precio_unitario'] <= 0:
                    raise DatosInvalidosException('precio_unitario', 'Debe ser mayor a 0')
                
                # Calcular subtotal del item
                item['subtotal'] = item['cantidad'] * item['precio_unitario']
                subtotal += item['subtotal']
            
            # Calcular impuesto y total
            impuesto = subtotal * impuesto_porcentaje
            total = subtotal + impuesto
            
            # Fecha de compra
            if fecha_compra is None:
                fecha_compra = datetime.now().date()
            
            # Generar número de compra
            numero_compra = self.compra_repo.generate_numero_compra()
            
            # TRANSACCIÓN: Insertar compra y detalles
            compra_id = None
            
            with get_db_cursor() as (cursor, conn):
                try:
                    # 1. Insertar compra
                    datos_compra = {
                        'numero_compra': numero_compra,
                        'proveedor_id': proveedor_id,
                        'usuario_id': usuario_id,
                        'fecha_compra': fecha_compra,
                        'estado': 'pendiente',
                        'subtotal': round(subtotal, 2),
                        'impuesto': round(impuesto, 2),
                        'total': round(total, 2),
                        'observaciones': observaciones
                    }
                    
                    compra_id = self.compra_repo.insert(datos_compra)
                    
                    # 2. Insertar detalles
                    for item in productos:
                        detalle_data = {
                            'compra_id': compra_id,
                            'producto_id': item['producto_id'],
                            'cantidad': item['cantidad'],
                            'precio_unitario': item['precio_unitario'],
                            'subtotal': item['subtotal']
                        }
                        self.compra_repo.insert_detalle(detalle_data)
                    
                    conn.commit()
                    
                    logger.info(
                        f"Compra registrada: {numero_compra}, "
                        f"Proveedor: {proveedor['razon_social']}, "
                        f"Total: S/. {total:.2f}"
                    )
                    
                except Exception as e:
                    conn.rollback()
                    logger.error(f"Error en transacción de compra: {e}")
                    raise
            
            # Retornar información de la compra
            return {
                'compra_id': compra_id,
                'numero_compra': numero_compra,
                'proveedor': proveedor['razon_social'],
                'fecha_compra': fecha_compra,
                'subtotal': round(subtotal, 2),
                'impuesto': round(impuesto, 2),
                'total': round(total, 2),
                'cantidad_productos': len(productos),
                'estado': 'pendiente'
            }
            
        except (ProveedorNoEncontradoException, ProductoNoEncontradoException, DatosInvalidosException):
            raise
        except Exception as e:
            logger.error(f"Error registrando compra: {e}")
            raise
    
    def recibir_compra(self, compra_id: int, usuario_id: int, fecha_recepcion: date = None) -> bool:
        """
        Marca una compra como recibida y actualiza el inventario.
        
        Args:
            compra_id (int): ID de la compra
            usuario_id (int): ID del usuario que recibe
            fecha_recepcion (date): Fecha de recepción (hoy si no se especifica)
            
        Returns:
            bool: True si se procesó correctamente
            
        Raises:
            CompraNoEncontradaException: Si la compra no existe
            EstadoInvalidoException: Si la compra no está en estado pendiente
        """
        try:
            # Obtener la compra
            compra = self.compra_repo.find_by_id(compra_id)
            if not compra:
                raise CompraNoEncontradaException(str(compra_id))
            
            # Validar estado
            if compra['estado'] != 'pendiente':
                raise EstadoInvalidoException(
                    'Compra',
                    compra['estado'],
                    'recibir compra'
                )
            
            # Fecha de recepción
            if fecha_recepcion is None:
                fecha_recepcion = datetime.now().date()
            
            # Obtener detalles de la compra
            detalles = self.compra_repo.get_detalle(compra_id)
            
            # TRANSACCIÓN: Actualizar stock y registrar movimientos
            with get_db_cursor() as (cursor, conn):
                try:
                    for detalle in detalles:
                        producto_id = detalle['producto_id']
                        cantidad = detalle['cantidad']
                        
                        # Obtener stock anterior
                        stock_anterior = self.producto_repo.get_stock_actual(producto_id)
                        stock_nuevo = stock_anterior + cantidad
                        
                        # Actualizar stock
                        self.producto_repo.update_stock(producto_id, cantidad, 'sumar')
                        
                        # Registrar movimiento
                        movimiento_data = {
                            'producto_id': producto_id,
                            'tipo_movimiento': 'entrada',
                            'cantidad': cantidad,
                            'motivo': 'compra',
                            'referencia_id': compra_id,
                            'stock_anterior': stock_anterior,
                            'stock_nuevo': stock_nuevo,
                            'usuario_id': usuario_id,
                            'observaciones': f"Entrada por compra {compra['numero_compra']}"
                        }
                        self.movimiento_repo.registrar_movimiento(movimiento_data)
                    
                    # Actualizar estado de la compra
                    self.compra_repo.update_estado(compra_id, 'recibida', fecha_recepcion)
                    
                    conn.commit()
                    
                    logger.info(
                        f"Compra recibida: {compra['numero_compra']}, "
                        f"{len(detalles)} productos actualizados"
                    )
                    
                    return True
                    
                except Exception as e:
                    conn.rollback()
                    logger.error(f"Error en transacción de recepción de compra: {e}")
                    raise
            
        except (CompraNoEncontradaException, EstadoInvalidoException):
            raise
        except Exception as e:
            logger.error(f"Error recibiendo compra {compra_id}: {e}")
            raise
    
    def cancelar_compra(self, compra_id: int) -> bool:
        """
        Cancela una compra pendiente.
        
        Args:
            compra_id (int): ID de la compra
            
        Returns:
            bool: True si se canceló correctamente
        """
        try:
            compra = self.compra_repo.find_by_id(compra_id)
            if not compra:
                raise CompraNoEncontradaException(str(compra_id))
            
            if compra['estado'] != 'pendiente':
                raise EstadoInvalidoException(
                    'Compra',
                    compra['estado'],
                    'cancelar compra'
                )
            
            resultado = self.compra_repo.update_estado(compra_id, 'cancelada')
            
            if resultado:
                logger.info(f"Compra cancelada: {compra['numero_compra']}")
            
            return resultado
            
        except (CompraNoEncontradaException, EstadoInvalidoException):
            raise
        except Exception as e:
            logger.error(f"Error cancelando compra {compra_id}: {e}")
            raise
    
    def listar_compras(self, estado: str = None) -> List[Dict[str, Any]]:
        """
        Lista compras, opcionalmente filtradas por estado.
        
        Args:
            estado (str): Estado a filtrar ('pendiente', 'recibida', 'cancelada')
            
        Returns:
            List[Dict]: Lista de compras
        """
        try:
            if estado:
                compras = self.compra_repo.get_by_estado(estado)
            else:
                compras = self.compra_repo.get_all_with_details()
            
            logger.info(f"Compras listadas: {len(compras)}")
            return compras
        except Exception as e:
            logger.error(f"Error listando compras: {e}")
            raise
    
    def obtener_compra_completa(self, compra_id: int) -> Dict[str, Any]:
        """
        Obtiene una compra con todos sus detalles.
        
        Args:
            compra_id (int): ID de la compra
            
        Returns:
            Dict: Compra con detalles
        """
        try:
            compra = self.compra_repo.find_by_id(compra_id)
            if not compra:
                raise CompraNoEncontradaException(str(compra_id))
            
            detalles = self.compra_repo.get_detalle(compra_id)
            
            compra['detalles'] = detalles
            return compra
            
        except CompraNoEncontradaException:
            raise
        except Exception as e:
            logger.error(f"Error obteniendo compra completa {compra_id}: {e}")
            raise
    
    def calcular_total_compras_periodo(
        self, 
        fecha_inicio: date, 
        fecha_fin: date
    ) -> Dict[str, Any]:
        """
        Calcula estadísticas de compras en un período.
        
        Args:
            fecha_inicio (date): Fecha inicial
            fecha_fin (date): Fecha final
            
        Returns:
            Dict: Estadísticas de compras
        """
        try:
            compras = self.compra_repo.get_by_date_range(fecha_inicio, fecha_fin)
            
            compras_recibidas = [c for c in compras if c['estado'] == 'recibida']
            
            total_gastado = sum(c['total'] for c in compras_recibidas)
            
            resultado = {
                'total_compras': len(compras),
                'compras_recibidas': len(compras_recibidas),
                'compras_pendientes': len([c for c in compras if c['estado'] == 'pendiente']),
                'total_gastado': round(total_gastado, 2),
                'promedio_por_compra': round(total_gastado / len(compras_recibidas), 2) if compras_recibidas else 0,
                'fecha_inicio': fecha_inicio,
                'fecha_fin': fecha_fin
            }
            
            logger.info(f"Estadísticas de compras calculadas: S/. {resultado['total_gastado']:.2f}")
            return resultado
            
        except Exception as e:
            logger.error(f"Error calculando total de compras: {e}")
            raise