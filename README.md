# 🛒 Sistema de Comercialización

Sistema integral de gestión comercial desarrollado en Python con Streamlit para la interfaz gráfica y MySQL como base de datos.

## 📋 Características

### Módulos Implementados

- **📦 Gestión de Productos**
  - CRUD completo de productos
  - Categorización
  - Control de stock mínimo
  - Búsqueda y filtros avanzados

- **🛍️ Ventas**
  - Registro de ventas con carrito
  - Validación automática de stock
  - Múltiples tipos de comprobante (boleta, factura, ticket)
  - Métodos de pago (efectivo, tarjeta, transferencia)
  - Aplicación de descuentos
  - Historial de ventas
  - Anulación de ventas

- **📥 Compras**
  - Registro de órdenes de compra
  - Recepción de mercancía
  - Actualización automática de inventario
  - Control de estados (pendiente, recibida, cancelada)
  - Historial de compras

- **📊 Inventario**
  - Consulta general de inventario
  - Alertas de stock crítico
  - Ajustes manuales de inventario
  - Historial de movimientos (entradas/salidas/ajustes)
  - Valorización de inventario

- **🏠 Dashboard**
  - Métricas generales
  - Alertas de stock crítico
  - Valorización de inventario
  - Accesos rápidos

## 🛠️ Tecnologías

- **Backend:** Python 3.x
- **Base de Datos:** MySQL 5.7+ / MariaDB
- **Framework UI:** Streamlit
- **ORM/Connector:** mysql-connector-python
- **Visualización:** Plotly, Pandas
- **Seguridad:** bcrypt

## 📦 Instalación

### 1. Requisitos Previos

- Python 3.8 o superior
- MySQL 5.7+ o MariaDB 10.x
- XAMPP (opcional, para MySQL local)

### 2. Clonar el Repositorio

```bash
git clone <url-repositorio>
cd Sistema_Comercial
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar Base de Datos

1. Crear la base de datos ejecutando el script SQL:

```bash
mysql -u root -p < sql/schema.sql
```

2. Copiar el archivo de configuración:

```bash
copy .env.example .env
```

3. Editar el archivo `.env` con tus credenciales:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=tu_password
DB_NAME=sistema_comercializacion
```

### 5. Verificar Conexión

```bash
python test_connection.py
```

## 🚀 Ejecución

### Iniciar la aplicación:

```bash
streamlit run app.py
```

La aplicación se abrirá automáticamente en tu navegador en `http://localhost:8501`

## 👤 Usuarios por Defecto

El sistema viene con usuarios predefinidos (contraseña: `admin123`):

- **admin** - Administrador (acceso completo)
- **vendedor1** - Vendedor
- **almacen1** - Almacenero

## 📁 Estructura del Proyecto

```
Sistema_Comercial/
├── app.py                      # Punto de entrada principal
├── config/                     # Configuración
│   ├── database.py            # Gestión de conexiones
│   └── settings.py            # Variables de entorno
├── models/                     # Modelos de datos (ORM futuro)
├── repositories/              # Capa de acceso a datos
│   ├── base_repository.py
│   ├── producto_repository.py
│   ├── venta_repository.py
│   ├── compra_repository.py
│   └── ...
├── services/                  # Lógica de negocio
│   ├── producto_service.py
│   ├── venta_service.py
│   ├── compra_service.py
│   ├── inventario_service.py
│   └── ...
├── ui/                        # Interfaz gráfica
│   ├── pages/                # Páginas de la aplicación
│   │   ├── dashboard.py
│   │   ├── productos.py
│   │   ├── ventas.py
│   │   ├── compras.py
│   │   └── inventario.py
│   └── components/           # Componentes reutilizables
├── exceptions/               # Excepciones personalizadas
├── utils/                    # Utilidades
├── sql/                      # Scripts SQL
│   └── schema.sql
├── logs/                     # Archivos de log
├── reports/                  # Reportes generados
└── requirements.txt          # Dependencias
```

## 🔑 Funcionalidades Clave

### Validaciones Automáticas
- ✅ Stock suficiente antes de vender
- ✅ Integridad referencial de datos
- ✅ Precios y cantidades válidos
- ✅ Estados válidos para operaciones

### Transacciones Atómicas
- ✅ Venta completa (venta + detalles + actualización stock + movimientos)
- ✅ Compra completa (compra + detalles)
- ✅ Recepción de mercancía (actualización estado + stock + movimientos)

### Trazabilidad
- ✅ Historial completo de movimientos de inventario
- ✅ Registro de usuario en cada operación
- ✅ Fechas de creación y modificación
- ✅ Logs de todas las operaciones

## 📊 Reportes y Consultas

El sistema incluye vistas SQL predefinidas para:
- Productos con stock bajo
- Ventas diarias
- Top 10 productos más vendidos
- Compras por proveedor
- Inventario valorizado
- Clientes top
- Movimientos recientes

## ⚙️ Configuración Avanzada

### Connection Pooling

El sistema utiliza connection pooling para optimizar el rendimiento:

```python
DB_POOL_NAME=mypool
DB_POOL_SIZE=5  # Número de conexiones en el pool
```

### Logging

Los logs se guardan en `logs/database.log` con información detallada de todas las operaciones.

## 🔐 Seguridad

- Contraseñas hasheadas con bcrypt
- Control de acceso por roles
- Validaciones en capa de servicios
- Protección contra SQL injection (prepared statements)
- Soft delete para mantener historial

## 🐛 Troubleshooting

### Error de conexión a MySQL

```bash
# Verificar que MySQL esté corriendo
mysql -u root -p

# Verificar credenciales en .env
```

### Error al importar módulos

```bash
# Reinstalar dependencias
pip install -r requirements.txt --upgrade
```

### Puerto 8501 ocupado

```bash
# Usar otro puerto
streamlit run app.py --server.port 8502
```

## 🚧 Próximas Funcionalidades

- [ ] Generación de reportes PDF
- [ ] Dashboard con gráficos avanzados
- [ ] Gestión de usuarios desde la UI
- [ ] Exportación de datos a Excel
- [ ] Notificaciones de stock crítico
- [ ] Sistema de autenticación robusto
- [ ] API REST para integraciones

## 👥 Contribución

Para contribuir al proyecto:

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/NuevaFuncionalidad`)
3. Commit tus cambios (`git commit -am 'Agrega nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/NuevaFuncionalidad`)
5. Crea un Pull Request

## 📄 Licencia

Este proyecto es de uso educativo y demostrativo.

## 📧 Contacto

Para soporte o consultas sobre el sistema, contactar al administrador del proyecto.

---

**Desarrollado con ❤️ en Python + Streamlit**
