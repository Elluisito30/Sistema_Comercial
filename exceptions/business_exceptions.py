"""
============================================
EXCEPCIONES PERSONALIZADAS DEL NEGOCIO
============================================
Define excepciones específicas para manejar errores
de lógica de negocio de forma clara y consistente.
============================================
"""


class BusinessException(Exception):
    """Excepción base para errores de lógica de negocio"""
    
    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)
    
    def __str__(self):
        if self.details:
            return f"{self.message} - Detalles: {self.details}"
        return self.message


class StockInsuficienteException(BusinessException):
    """Se lanza cuando no hay suficiente stock para una operación"""
    
    def __init__(self, producto_nombre: str, stock_disponible: int, cantidad_solicitada: int):
        message = f"Stock insuficiente para '{producto_nombre}'"
        details = {
            'producto': producto_nombre,
            'stock_disponible': stock_disponible,
            'cantidad_solicitada': cantidad_solicitada,
            'faltante': cantidad_solicitada - stock_disponible
        }
        super().__init__(message, details)


class ProductoNoEncontradoException(BusinessException):
    """Se lanza cuando no se encuentra un producto"""
    
    def __init__(self, identificador: str, tipo: str = "ID"):
        message = f"Producto no encontrado ({tipo}: {identificador})"
        details = {'identificador': identificador, 'tipo': tipo}
        super().__init__(message, details)


class ClienteNoEncontradoException(BusinessException):
    """Se lanza cuando no se encuentra un cliente"""
    
    def __init__(self, identificador: str):
        message = f"Cliente no encontrado (ID/Documento: {identificador})"
        details = {'identificador': identificador}
        super().__init__(message, details)


class ProveedorNoEncontradoException(BusinessException):
    """Se lanza cuando no se encuentra un proveedor"""
    
    def __init__(self, identificador: str):
        message = f"Proveedor no encontrado (ID/RUC: {identificador})"
        details = {'identificador': identificador}
        super().__init__(message, details)


class CompraNoEncontradaException(BusinessException):
    """Se lanza cuando no se encuentra una compra"""
    
    def __init__(self, identificador: str):
        message = f"Compra no encontrada (ID/Número: {identificador})"
        details = {'identificador': identificador}
        super().__init__(message, details)


class VentaNoEncontradaException(BusinessException):
    """Se lanza cuando no se encuentra una venta"""
    
    def __init__(self, identificador: str):
        message = f"Venta no encontrada (ID/Número: {identificador})"
        details = {'identificador': identificador}
        super().__init__(message, details)


class EstadoInvalidoException(BusinessException):
    """Se lanza cuando se intenta una operación con un estado inválido"""
    
    def __init__(self, entidad: str, estado_actual: str, operacion: str):
        message = f"No se puede realizar '{operacion}' en {entidad} con estado '{estado_actual}'"
        details = {
            'entidad': entidad,
            'estado_actual': estado_actual,
            'operacion': operacion
        }
        super().__init__(message, details)


class DatosInvalidosException(BusinessException):
    """Se lanza cuando los datos proporcionados son inválidos"""
    
    def __init__(self, campo: str, razon: str):
        message = f"Datos inválidos en campo '{campo}': {razon}"
        details = {'campo': campo, 'razon': razon}
        super().__init__(message, details)