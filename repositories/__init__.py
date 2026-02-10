"""
Paquete de repositorios - Capa de acceso a datos
"""

from .producto_repository import ProductoRepository
from .categoria_repository import CategoriaRepository
from .proveedor_repository import ProveedorRepository
from .cliente_repository import ClienteRepository
from .compra_repository import CompraRepository
from .venta_repository import VentaRepository
from .movimiento_repository import MovimientoRepository
from .usuario_repository import UsuarioRepository

__all__ = [
    'ProductoRepository',
    'CategoriaRepository',
    'ProveedorRepository',
    'ClienteRepository',
    'CompraRepository',
    'VentaRepository',
    'MovimientoRepository',
    'UsuarioRepository'
]