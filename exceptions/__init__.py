"""
Paquete de excepciones personalizadas
"""

from .business_exceptions import (
    BusinessException,
    StockInsuficienteException,
    ProductoNoEncontradoException,
    ClienteNoEncontradoException,
    ProveedorNoEncontradoException,
    CompraNoEncontradaException,
    VentaNoEncontradaException,
    EstadoInvalidoException,
    DatosInvalidosException
)

__all__ = [
    'BusinessException',
    'StockInsuficienteException',
    'ProductoNoEncontradoException',
    'ClienteNoEncontradoException',
    'ProveedorNoEncontradoException',
    'CompraNoEncontradaException',
    'VentaNoEncontradaException',
    'EstadoInvalidoException',
    'DatosInvalidosException'
]