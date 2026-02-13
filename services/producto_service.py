"""
============================================
SERVICIO DE PRODUCTOS
============================================
Lógica de negocio relacionada con productos.
============================================
"""

import logging
from typing import List, Dict, Any, Optional
from repositories import ProductoRepository, CategoriaRepository
from exceptions import ProductoNoEncontradoException, DatosInvalidosException

logger = logging.getLogger(__name__)


class ProductoService:
    """Servicio para gestionar la lógica de negocio de productos"""
    
    def __init__(self):
        self.producto_repo = ProductoRepository()
        self.categoria_repo = CategoriaRepository()
    
    def listar_productos_activos(self) -> List[Dict[str, Any]]:
        """
        Lista todos los productos activos con información de categoría.
        
        Returns:
            List[Dict]: Lista de productos
        """
        try:
            productos = self.producto_repo.get_all_with_category()
            logger.info(f"Productos activos listados: {len(productos)}")
            return productos
        except Exception as e:
            logger.error(f"Error listando productos: {e}")
            raise
    
    def obtener_producto_por_id(self, producto_id: int) -> Dict[str, Any]:
        """
        Obtiene un producto por su ID.
        
        Args:
            producto_id (int): ID del producto
            
        Returns:
            Dict: Información del producto
            
        Raises:
            ProductoNoEncontradoException: Si el producto no existe
        """
        try:
            producto = self.producto_repo.find_by_id(producto_id)
            
            if not producto:
                raise ProductoNoEncontradoException(str(producto_id), "ID")
            
            return producto
        except ProductoNoEncontradoException:
            raise
        except Exception as e:
            logger.error(f"Error obteniendo producto {producto_id}: {e}")
            raise
    
    def obtener_producto_por_codigo(self, codigo: str) -> Dict[str, Any]:
        """
        Obtiene un producto por su código.
        
        Args:
            codigo (str): Código del producto
            
        Returns:
            Dict: Información del producto
            
        Raises:
            ProductoNoEncontradoException: Si el producto no existe
        """
        try:
            producto = self.producto_repo.find_by_codigo(codigo)
            
            if not producto:
                raise ProductoNoEncontradoException(codigo, "CÓDIGO")
            
            return producto
        except ProductoNoEncontradoException:
            raise
        except Exception as e:
            logger.error(f"Error obteniendo producto por código {codigo}: {e}")
            raise
    
    def buscar_productos(self, termino: str) -> List[Dict[str, Any]]:
        """
        Busca productos por código o nombre.
        
        Args:
            termino (str): Término de búsqueda
            
        Returns:
            List[Dict]: Productos encontrados
        """
        try:
            if not termino or len(termino.strip()) < 2:
                raise DatosInvalidosException(
                    "término de búsqueda",
                    "Debe tener al menos 2 caracteres"
                )
            
            productos = self.producto_repo.search(termino.strip())
            logger.info(f"Búsqueda '{termino}': {len(productos)} resultados")
            return productos
        except DatosInvalidosException:
            raise
        except Exception as e:
            logger.error(f"Error buscando productos: {e}")
            raise
    
    def crear_producto(self, datos_producto: Optional[Dict[str, Any]] = None, **kwargs) -> int:
        """
        Crea un nuevo producto.
        Acepta múltiples formas de entrada:
         - crear_producto({'codigo': 'P001', 'nombre': 'Producto', ...})
         - crear_producto(codigo='P001', nombre='Producto', ...)
         - crear_producto(codigo_producto='P001', nombre_producto='Producto', ...)  # Variantes de nombres
        
        Args:
            datos_producto (Optional[Dict]): Datos del producto como diccionario
            **kwargs: Parámetros nombrados con flexibilidad en nombres de campos
            
        Returns:
            int: ID del producto creado
            
        Raises:
            DatosInvalidosException: Si los datos son inválidos o faltan campos requeridos
        """
        try:
            # Si recibimos kwargs, construir el dict de datos con mapeo flexible de nombres
            if kwargs:
                datos_producto = {
                    'codigo': kwargs.get('codigo') or kwargs.get('codigo_producto') or kwargs.get('code'),
                    'nombre': kwargs.get('nombre') or kwargs.get('nombre_producto'),
                    'categoria_id': kwargs.get('categoria_id') or kwargs.get('categoria') or kwargs.get('categoriaId'),
                    'precio_compra': kwargs.get('precio_compra') or kwargs.get('precioCompra'),
                    'precio_venta': kwargs.get('precio_venta') or kwargs.get('precioVenta'),
                    'stock_actual': kwargs.get('stock_actual') or kwargs.get('stock') or 0,
                    'stock_minimo': kwargs.get('stock_minimo') or kwargs.get('stockMinimo') or 0,
                    'unidad_medida': kwargs.get('unidad_medida') or kwargs.get('unidad') or kwargs.get('unidadMedida'),
                    'descripcion': kwargs.get('descripcion') or kwargs.get('descripcion_producto') or kwargs.get('description')
                }
            elif datos_producto is None or not isinstance(datos_producto, dict):
                # Validación defensiva: evitar errores como 'int' object is not subscriptable
                raise DatosInvalidosException(
                    'datos_producto',
                    f"Se esperaba un diccionario con los datos del producto, pero se recibió: {type(datos_producto).__name__ if datos_producto is not None else 'None'}"
                )

            # Eliminar claves con valor None para evitar sobrescribir valores por defecto
            datos_producto = {k: v for k, v in datos_producto.items() if v is not None}

            # Validar datos obligatorios
            self._validar_datos_producto(datos_producto)

            # Validar que el código no exista
            if self.producto_repo.find_by_codigo(datos_producto['codigo']):
                raise DatosInvalidosException(
                    'codigo',
                    f"El código '{datos_producto['codigo']}' ya existe"
                )

            # Validar que la categoría exista
            categoria = self.categoria_repo.find_by_id(datos_producto['categoria_id'])
            if not categoria:
                raise DatosInvalidosException(
                    'categoria_id',
                    'La categoría especificada no existe'
                )

            # Validar coherencia de precios
            if datos_producto['precio_venta'] < datos_producto['precio_compra']:
                raise DatosInvalidosException(
                    'precio_venta',
                    'El precio de venta no puede ser menor al precio de compra'
                )

            producto_id = self.producto_repo.insert(datos_producto)
            logger.info(f"Producto creado: ID {producto_id}, Código {datos_producto['codigo']}")
            return producto_id

        except DatosInvalidosException:
            raise
        except Exception as e:
            logger.error(f"Error creando producto: {e}")
            raise
    
    def actualizar_producto(self, producto_id: int, datos: Dict[str, Any]) -> bool:
        """
        Actualiza un producto existente.
        
        Args:
            producto_id (int): ID del producto
            datos (Dict): Datos a actualizar
            
        Returns:
            bool: True si se actualizó correctamente
        """
        try:
            # Verificar que el producto existe
            producto = self.obtener_producto_por_id(producto_id)
            
            # Si se actualiza el código, validar que no exista
            if 'codigo' in datos and datos['codigo'] != producto['codigo']:
                if self.producto_repo.find_by_codigo(datos['codigo']):
                    raise DatosInvalidosException(
                        'codigo',
                        f"El código '{datos['codigo']}' ya existe"
                    )
            
            # Validar precios si se están actualizando
            precio_compra = datos.get('precio_compra', producto['precio_compra'])
            precio_venta = datos.get('precio_venta', producto['precio_venta'])
            
            if precio_venta < precio_compra:
                raise DatosInvalidosException(
                    'precio_venta',
                    'El precio de venta no puede ser menor al precio de compra'
                )
            
            resultado = self.producto_repo.update(producto_id, datos)
            
            if resultado:
                logger.info(f"Producto actualizado: ID {producto_id}")
            
            return resultado
            
        except (ProductoNoEncontradoException, DatosInvalidosException):
            raise
        except Exception as e:
            logger.error(f"Error actualizando producto {producto_id}: {e}")
            raise
    
    def desactivar_producto(self, producto_id: int) -> bool:
        """
        Desactiva un producto (soft delete).
        
        Args:
            producto_id (int): ID del producto
            
        Returns:
            bool: True si se desactivó correctamente
        """
        try:
            # Verificar que el producto existe
            self.obtener_producto_por_id(producto_id)
            
            resultado = self.producto_repo.soft_delete(producto_id)
            
            if resultado:
                logger.info(f"Producto desactivado: ID {producto_id}")
            
            return resultado
            
        except ProductoNoEncontradoException:
            raise
        except Exception as e:
            logger.error(f"Error desactivando producto {producto_id}: {e}")
            raise
    
    def obtener_productos_stock_bajo(self) -> List[Dict[str, Any]]:
        """
        Obtiene productos con stock bajo o igual al mínimo.
        
        Returns:
            List[Dict]: Productos con stock bajo
        """
        try:
            productos = self.producto_repo.get_low_stock()
            logger.info(f"Productos con stock bajo: {len(productos)}")
            return productos
        except Exception as e:
            logger.error(f"Error obteniendo productos con stock bajo: {e}")
            raise
    
    def calcular_valor_inventario(self) -> Dict[str, float]:
        """
        Calcula el valor total del inventario.
        
        Returns:
            Dict: Valor en precio de compra y precio de venta
        """
        try:
            productos = self.producto_repo.find_all(conditions="activo = TRUE")
            
            valor_compra = sum(
                p['stock_actual'] * p['precio_compra'] 
                for p in productos
            )
            
            valor_venta = sum(
                p['stock_actual'] * p['precio_venta'] 
                for p in productos
            )
            
            resultado = {
                'valor_compra': round(valor_compra, 2),
                'valor_venta': round(valor_venta, 2),
                'ganancia_potencial': round(valor_venta - valor_compra, 2),
                'total_productos': len(productos)
            }
            
            logger.info(f"Valor de inventario calculado: S/. {resultado['valor_venta']:.2f}")
            return resultado
            
        except Exception as e:
            logger.error(f"Error calculando valor de inventario: {e}")
            raise
    
    def listar_productos_inactivos(self) -> List[Dict[str, Any]]:
        """
        Lista todos los productos INACTIVOS con información de categoría.
        
        Returns:
            List[Dict]: Lista de productos desactivados
        """
        try:
            productos = self.producto_repo.get_all_inactive()
            logger.info(f"Productos inactivos listados: {len(productos)}")
            return productos
        except Exception as e:
            logger.error(f"Error listando productos inactivos: {e}")
            raise
    
    def _validar_datos_producto(self, datos: Dict[str, Any]) -> None:
        """
        Valida los datos de un producto.
        
        Args:
            datos (Dict): Datos a validar
            
        Raises:
            DatosInvalidosException: Si algún dato es inválido
        """
        campos_requeridos = [
            'codigo', 'nombre', 'categoria_id', 
            'precio_compra', 'precio_venta', 'unidad_medida'
        ]
        
        for campo in campos_requeridos:
            if campo not in datos or not datos[campo]:
                raise DatosInvalidosException(campo, "Campo requerido")
        
        # ✅ Validación adicional para código
        if not datos['codigo'] or not datos['codigo'].strip():
            raise DatosInvalidosException('codigo', 'El código no puede estar vacío')
        
        # Validar precios positivos
        if datos['precio_compra'] <= 0:
            raise DatosInvalidosException('precio_compra', 'Debe ser mayor a 0')
        
        if datos['precio_venta'] <= 0:
            raise DatosInvalidosException('precio_venta', 'Debe ser mayor a 0')
        
        # Validar stock si está presente
        if 'stock_actual' in datos and datos['stock_actual'] < 0:
            raise DatosInvalidosException('stock_actual', 'No puede ser negativo')
        
        if 'stock_minimo' in datos and datos['stock_minimo'] < 0:
            raise DatosInvalidosException('stock_minimo', 'No puede ser negativo')
    
    def obtener_productos_stock_critico(self) -> List[Dict[str, Any]]:
        """
        Retorna productos con stock crítico (alias de stock bajo).
        """
        productos = self.obtener_productos_stock_bajo()
        logger.info(f"Productos con stock crítico: {len(productos)}")
        return productos