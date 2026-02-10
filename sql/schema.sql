-- ============================================
-- SISTEMA DE COMERCIALIZACIÓN
-- Base de Datos MySQL
-- Versión: 1.1 (Sin procedimientos almacenados)
-- Compatible con: MySQL 5.7+, MariaDB 10.x, XAMPP
-- ============================================

-- Crear base de datos
DROP DATABASE IF EXISTS sistema_comercializacion;
CREATE DATABASE sistema_comercializacion
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE sistema_comercializacion;

-- ============================================
-- TABLA: usuarios
-- ============================================
CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre_usuario VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    nombre_completo VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    rol ENUM('admin', 'vendedor', 'almacenero') NOT NULL,
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_nombre_usuario (nombre_usuario),
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- TABLA: categorias
-- ============================================
CREATE TABLE categorias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) UNIQUE NOT NULL,
    descripcion TEXT,
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_nombre (nombre)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- TABLA: proveedores
-- ============================================
CREATE TABLE proveedores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ruc VARCHAR(20) UNIQUE NOT NULL,
    razon_social VARCHAR(200) NOT NULL,
    nombre_contacto VARCHAR(100),
    telefono VARCHAR(20),
    email VARCHAR(100),
    direccion TEXT,
    ciudad VARCHAR(100),
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_ruc (ruc),
    INDEX idx_razon_social (razon_social)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- TABLA: productos
-- ============================================
CREATE TABLE productos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE NOT NULL,
    nombre VARCHAR(200) NOT NULL,
    descripcion TEXT,
    categoria_id INT NOT NULL,
    precio_compra DECIMAL(10,2) NOT NULL,
    precio_venta DECIMAL(10,2) NOT NULL,
    stock_actual INT DEFAULT 0,
    stock_minimo INT DEFAULT 5,
    unidad_medida VARCHAR(20) NOT NULL,
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (categoria_id) REFERENCES categorias(id) ON DELETE RESTRICT,
    INDEX idx_codigo (codigo),
    INDEX idx_nombre (nombre),
    INDEX idx_categoria (categoria_id),
    INDEX idx_stock (stock_actual)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- TABLA: compras
-- ============================================
CREATE TABLE compras (
    id INT AUTO_INCREMENT PRIMARY KEY,
    numero_compra VARCHAR(20) UNIQUE NOT NULL,
    proveedor_id INT NOT NULL,
    usuario_id INT NOT NULL,
    fecha_compra DATE NOT NULL,
    fecha_recepcion DATE,
    estado ENUM('pendiente', 'recibida', 'cancelada') NOT NULL DEFAULT 'pendiente',
    subtotal DECIMAL(10,2) NOT NULL,
    impuesto DECIMAL(10,2) DEFAULT 0,
    total DECIMAL(10,2) NOT NULL,
    observaciones TEXT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (proveedor_id) REFERENCES proveedores(id) ON DELETE RESTRICT,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE RESTRICT,
    INDEX idx_numero_compra (numero_compra),
    INDEX idx_proveedor (proveedor_id),
    INDEX idx_fecha_compra (fecha_compra),
    INDEX idx_estado (estado)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- TABLA: detalle_compras
-- ============================================
CREATE TABLE detalle_compras (
    id INT AUTO_INCREMENT PRIMARY KEY,
    compra_id INT NOT NULL,
    producto_id INT NOT NULL,
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (compra_id) REFERENCES compras(id) ON DELETE CASCADE,
    FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE RESTRICT,
    UNIQUE KEY uk_compra_producto (compra_id, producto_id),
    INDEX idx_compra (compra_id),
    INDEX idx_producto (producto_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- TABLA: movimientos_inventario
-- ============================================
CREATE TABLE movimientos_inventario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    producto_id INT NOT NULL,
    tipo_movimiento ENUM('entrada', 'salida', 'ajuste') NOT NULL,
    cantidad INT NOT NULL,
    motivo VARCHAR(100) NOT NULL,
    referencia_id INT,
    stock_anterior INT NOT NULL,
    stock_nuevo INT NOT NULL,
    usuario_id INT NOT NULL,
    observaciones TEXT,
    fecha_movimiento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE RESTRICT,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE RESTRICT,
    INDEX idx_producto (producto_id),
    INDEX idx_fecha (fecha_movimiento),
    INDEX idx_tipo (tipo_movimiento)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- TABLA: clientes
-- ============================================
CREATE TABLE clientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tipo_documento ENUM('DNI', 'RUC', 'CE', 'pasaporte') NOT NULL,
    numero_documento VARCHAR(20) UNIQUE NOT NULL,
    nombres VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100),
    razon_social VARCHAR(200),
    telefono VARCHAR(20),
    email VARCHAR(100),
    direccion TEXT,
    ciudad VARCHAR(100),
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_numero_documento (numero_documento),
    INDEX idx_nombres (nombres)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- TABLA: ventas
-- ============================================
CREATE TABLE ventas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    numero_venta VARCHAR(20) UNIQUE NOT NULL,
    cliente_id INT NOT NULL,
    usuario_id INT NOT NULL,
    fecha_venta DATE NOT NULL,
    tipo_comprobante ENUM('boleta', 'factura', 'ticket') NOT NULL,
    estado ENUM('completada', 'anulada') NOT NULL DEFAULT 'completada',
    subtotal DECIMAL(10,2) NOT NULL,
    descuento DECIMAL(10,2) DEFAULT 0,
    impuesto DECIMAL(10,2) DEFAULT 0,
    total DECIMAL(10,2) NOT NULL,
    metodo_pago ENUM('efectivo', 'tarjeta', 'transferencia') NOT NULL,
    observaciones TEXT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE RESTRICT,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE RESTRICT,
    INDEX idx_numero_venta (numero_venta),
    INDEX idx_cliente (cliente_id),
    INDEX idx_fecha_venta (fecha_venta),
    INDEX idx_estado (estado)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- TABLA: detalle_ventas
-- ============================================
CREATE TABLE detalle_ventas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    venta_id INT NOT NULL,
    producto_id INT NOT NULL,
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    descuento DECIMAL(10,2) DEFAULT 0,
    subtotal DECIMAL(10,2) NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (venta_id) REFERENCES ventas(id) ON DELETE CASCADE,
    FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE RESTRICT,
    UNIQUE KEY uk_venta_producto (venta_id, producto_id),
    INDEX idx_venta (venta_id),
    INDEX idx_producto (producto_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- DATOS DE PRUEBA
-- ============================================

-- Usuario administrador por defecto
-- Usuario: admin
-- Password: admin123 (hasheado con bcrypt)
INSERT INTO usuarios (nombre_usuario, password_hash, nombre_completo, email, rol) VALUES
('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpLaEr8e2', 'Administrador Sistema', 'admin@sistema.com', 'admin'),
('vendedor1', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpLaEr8e2', 'Carlos Vendedor', 'vendedor@sistema.com', 'vendedor'),
('almacen1', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpLaEr8e2', 'Ana Almacén', 'almacen@sistema.com', 'almacenero');

-- Categorías de ejemplo
INSERT INTO categorias (nombre, descripcion) VALUES
('Electrónica', 'Productos electrónicos y tecnología'),
('Alimentos', 'Productos alimenticios y bebidas'),
('Ropa', 'Prendas de vestir y accesorios'),
('Ferretería', 'Herramientas y materiales de construcción'),
('Oficina', 'Artículos de oficina y papelería'),
('Hogar', 'Artículos para el hogar'),
('Deportes', 'Equipamiento deportivo');

-- Proveedores de ejemplo
INSERT INTO proveedores (ruc, razon_social, nombre_contacto, telefono, email, direccion, ciudad) VALUES
('20123456789', 'Distribuidora ABC S.A.C.', 'Juan Pérez', '999888777', 'ventas@abc.com', 'Av. Industrial 123', 'Lima'),
('20987654321', 'Tech Solutions E.I.R.L.', 'María Torres', '988777666', 'contacto@techsol.com', 'Jr. Comercio 456', 'Arequipa'),
('20456789123', 'Alimentos del Norte S.A.', 'Pedro Ramírez', '977666555', 'info@alimnorte.com', 'Calle Principal 789', 'Trujillo');

-- Clientes de ejemplo
INSERT INTO clientes (tipo_documento, numero_documento, nombres, apellidos, telefono, email, ciudad) VALUES
('DNI', '12345678', 'María', 'González López', '987654321', 'maria.gonzalez@email.com', 'Piura'),
('DNI', '87654321', 'José', 'Rodríguez Sánchez', '976543210', 'jose.rodriguez@email.com', 'Chiclayo'),
('RUC', '20111222333', 'Empresa Demo', NULL, '965432109', 'empresa@demo.com', 'Lima'),
('DNI', '11223344', 'Ana', 'Martínez Flores', '954321098', 'ana.martinez@email.com', 'Piura'),
('CE', 'CE123456', 'Carlos', 'Extranjero Smith', '943210987', 'carlos.smith@email.com', 'Lima');

-- Productos de ejemplo (varios por categoría)
INSERT INTO productos (codigo, nombre, descripcion, categoria_id, precio_compra, precio_venta, stock_actual, stock_minimo, unidad_medida) VALUES
-- Electrónica (categoría 1)
('ELEC001', 'Laptop HP 15.6"', 'Laptop HP Core i5, 8GB RAM, 256GB SSD', 1, 1800.00, 2500.00, 15, 5, 'unidad'),
('ELEC002', 'Mouse Logitech Inalámbrico', 'Mouse óptico inalámbrico 2.4GHz', 1, 25.00, 45.00, 50, 10, 'unidad'),
('ELEC003', 'Teclado Mecánico RGB', 'Teclado mecánico retroiluminado', 1, 80.00, 150.00, 30, 8, 'unidad'),
('ELEC004', 'Monitor LED 24"', 'Monitor Full HD IPS', 1, 350.00, 550.00, 20, 5, 'unidad'),

-- Alimentos (categoría 2)
('ALIM001', 'Arroz Superior 5kg', 'Arroz extra de primera calidad', 2, 12.00, 18.00, 200, 50, 'bolsa'),
('ALIM002', 'Aceite Vegetal 1L', 'Aceite vegetal comestible', 2, 8.00, 12.00, 150, 30, 'botella'),
('ALIM003', 'Azúcar Blanca 1kg', 'Azúcar refinada', 2, 2.50, 4.00, 300, 80, 'bolsa'),
('ALIM004', 'Leche Evaporada 400ml', 'Leche evaporada entera', 2, 3.00, 4.50, 180, 40, 'lata'),

-- Ropa (categoría 3)
('ROPA001', 'Polo Deportivo Dri-Fit', 'Polo manga corta material transpirable', 3, 25.00, 50.00, 60, 15, 'unidad'),
('ROPA002', 'Jean Clásico Azul', 'Jean de mezclilla talla 32', 3, 45.00, 85.00, 40, 10, 'unidad'),
('ROPA003', 'Zapatillas Running', 'Zapatillas deportivas para correr', 3, 80.00, 150.00, 35, 8, 'par'),

-- Ferretería (categoría 4)
('FERR001', 'Martillo Carpintero', 'Martillo con mango de madera 500g', 4, 15.00, 28.00, 45, 10, 'unidad'),
('FERR002', 'Destornillador Set 6 Piezas', 'Juego de destornilladores punta plana y estrella', 4, 18.00, 35.00, 55, 12, 'set'),
('FERR003', 'Taladro Eléctrico 600W', 'Taladro percutor con estuche', 4, 120.00, 220.00, 18, 5, 'unidad'),

-- Oficina (categoría 5)
('OFIC001', 'Papel Bond A4 x500', 'Resma papel bond 75g', 5, 10.00, 15.00, 120, 30, 'resma'),
('OFIC002', 'Lapicero Azul x12', 'Caja de lapiceros punta fina', 5, 6.00, 12.00, 80, 20, 'caja'),
('OFIC003', 'Archivador Palanca', 'Archivador tamaño oficio lomo ancho', 5, 5.00, 9.00, 95, 25, 'unidad'),

-- Hogar (categoría 6)
('HOGA001', 'Juego de Ollas 5 Piezas', 'Set de ollas antiadherentes', 6, 80.00, 140.00, 25, 8, 'set'),
('HOGA002', 'Toalla de Baño Premium', 'Toalla 100% algodón 70x140cm', 6, 18.00, 35.00, 70, 15, 'unidad'),

-- Deportes (categoría 7)
('DEPO001', 'Balón Fútbol N°5', 'Balón profesional cosido a mano', 7, 35.00, 65.00, 42, 10, 'unidad'),
('DEPO002', 'Mancuernas 5kg Par', 'Par de mancuernas recubiertas', 7, 40.00, 75.00, 28, 8, 'par');

-- ============================================
-- VISTAS PARA REPORTES
-- ============================================

-- Vista: Productos con stock bajo
CREATE VIEW v_productos_stock_bajo AS
SELECT 
    p.id,
    p.codigo,
    p.nombre,
    c.nombre AS categoria,
    p.stock_actual,
    p.stock_minimo,
    p.precio_venta,
    (p.stock_minimo - p.stock_actual) AS cantidad_requerida
FROM productos p
INNER JOIN categorias c ON p.categoria_id = c.id
WHERE p.stock_actual <= p.stock_minimo AND p.activo = TRUE
ORDER BY (p.stock_minimo - p.stock_actual) DESC;

-- Vista: Resumen de ventas diarias
CREATE VIEW v_ventas_diarias AS
SELECT 
    DATE(v.fecha_venta) AS fecha,
    COUNT(v.id) AS total_ventas,
    SUM(v.total) AS monto_total,
    AVG(v.total) AS ticket_promedio,
    SUM(v.descuento) AS descuentos_totales
FROM ventas v
WHERE v.estado = 'completada'
GROUP BY DATE(v.fecha_venta)
ORDER BY fecha DESC;

-- Vista: Top 10 productos más vendidos
CREATE VIEW v_productos_mas_vendidos AS
SELECT 
    p.id,
    p.codigo,
    p.nombre,
    c.nombre AS categoria,
    SUM(dv.cantidad) AS cantidad_vendida,
    SUM(dv.subtotal) AS ingresos_totales,
    COUNT(DISTINCT dv.venta_id) AS numero_ventas
FROM detalle_ventas dv
INNER JOIN productos p ON dv.producto_id = p.id
INNER JOIN categorias c ON p.categoria_id = c.id
INNER JOIN ventas v ON dv.venta_id = v.id
WHERE v.estado = 'completada'
GROUP BY p.id, p.codigo, p.nombre, c.nombre
ORDER BY cantidad_vendida DESC
LIMIT 10;

-- Vista: Resumen de compras por proveedor
CREATE VIEW v_compras_por_proveedor AS
SELECT 
    prov.id,
    prov.razon_social,
    COUNT(c.id) AS total_compras,
    SUM(c.total) AS monto_total_comprado,
    AVG(c.total) AS ticket_promedio,
    MAX(c.fecha_compra) AS ultima_compra
FROM proveedores prov
LEFT JOIN compras c ON prov.id = c.proveedor_id
WHERE c.estado != 'cancelada' OR c.id IS NULL
GROUP BY prov.id, prov.razon_social
ORDER BY monto_total_comprado DESC;

-- Vista: Inventario valorizado
CREATE VIEW v_inventario_valorizado AS
SELECT 
    p.id,
    p.codigo,
    p.nombre,
    c.nombre AS categoria,
    p.stock_actual,
    p.precio_compra,
    p.precio_venta,
    (p.stock_actual * p.precio_compra) AS valor_inventario_compra,
    (p.stock_actual * p.precio_venta) AS valor_inventario_venta,
    ((p.precio_venta - p.precio_compra) / p.precio_compra * 100) AS margen_porcentaje
FROM productos p
INNER JOIN categorias c ON p.categoria_id = c.id
WHERE p.activo = TRUE
ORDER BY valor_inventario_venta DESC;

-- Vista: Clientes con más compras
CREATE VIEW v_clientes_top AS
SELECT 
    cl.id,
    cl.numero_documento,
    CONCAT(cl.nombres, ' ', COALESCE(cl.apellidos, '')) AS nombre_completo,
    cl.ciudad,
    COUNT(v.id) AS total_compras,
    SUM(v.total) AS monto_total_gastado,
    AVG(v.total) AS ticket_promedio,
    MAX(v.fecha_venta) AS ultima_compra
FROM clientes cl
INNER JOIN ventas v ON cl.id = v.cliente_id
WHERE v.estado = 'completada'
GROUP BY cl.id, cl.numero_documento, nombre_completo, cl.ciudad
ORDER BY monto_total_gastado DESC;

-- Vista: Movimientos de inventario recientes
CREATE VIEW v_movimientos_recientes AS
SELECT 
    mi.id,
    p.codigo,
    p.nombre AS producto,
    mi.tipo_movimiento,
    mi.cantidad,
    mi.motivo,
    mi.stock_anterior,
    mi.stock_nuevo,
    u.nombre_completo AS usuario,
    mi.fecha_movimiento,
    mi.observaciones
FROM movimientos_inventario mi
INNER JOIN productos p ON mi.producto_id = p.id
INNER JOIN usuarios u ON mi.usuario_id = u.id
ORDER BY mi.fecha_movimiento DESC
LIMIT 50;

-- ============================================
-- ÍNDICES ADICIONALES PARA OPTIMIZACIÓN
-- ============================================

-- Índice compuesto para búsquedas de ventas por cliente y fecha
CREATE INDEX idx_ventas_cliente_fecha ON ventas(cliente_id, fecha_venta);

-- Índice compuesto para búsquedas de compras por proveedor y fecha
CREATE INDEX idx_compras_proveedor_fecha ON compras(proveedor_id, fecha_compra);

-- ============================================
-- FIN DEL SCRIPT
-- ============================================

-- Verificación de la instalación
SELECT 'Base de datos creada exitosamente' AS mensaje;
SELECT COUNT(*) AS total_tablas FROM information_schema.tables 
WHERE table_schema = 'sistema_comercializacion' AND table_type = 'BASE TABLE';
SELECT COUNT(*) AS total_vistas FROM information_schema.views 
WHERE table_schema = 'sistema_comercializacion';