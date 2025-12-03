# py-ventory - Sistema de Gestión de Inventario

Aplicación web completa para gestión de inventario de tiendas pequeñas, desarrollada con Flask/Python, Supabase y desplegada en Vercel.

## Stack Tecnológico

- **Backend**: Flask (Python)
- **Base de Datos**: Supabase (PostgreSQL)
- **Frontend**: Bootstrap 5 + CSS personalizado
- **Despliegue**: Vercel (Serverless)

## Funcionalidades Implementadas

### 1. Gestión de Productos
- CRUD completo (Crear, Leer, Actualizar, Eliminar)
- Campos: SKU, nombre, descripción, precio, cantidad, categoría, proveedor
- Alertas visuales de stock (bajo, medio, suficiente)
- Búsqueda y filtrado en tiempo real
- Indicadores de estado (activo/inactivo)

### 2. Gestión de Categorías
- Sistema dinámico de categorías
- Vista en tarjetas con contador de productos
- Protección contra eliminación de categorías con productos asociados
- Resumen de valor por categoría

### 3. Movimientos de Inventario
- Registro automático de cambios en cantidades
- Tres tipos de movimientos:
  - **Entrada**: Incrementa stock (compras, devoluciones)
  - **Salida**: Disminuye stock (ventas, pérdidas)
  - **Ajuste**: Establece valor exacto (inventario físico)
- Historial completo con filtros por producto
- Registro manual con validaciones

### 4. Dashboard Inteligente
- Estadísticas en tiempo real:
  - Total de productos y items en stock
  - Valor total del inventario
  - Número de categorías activas
  - Productos con bajo stock
- Alertas de productos que requieren reabastecimiento
- Resumen por categorías con valores
- Últimos 10 movimientos de inventario
- Acciones rápidas para funciones principales

### 5. Interfaz de Usuario
- Diseño responsive con Bootstrap 5
- Colores personalizados en `static/css/variables.css`
- Iconos de Bootstrap Icons
- Navegación intuitiva con breadcrumbs
- Mensajes flash para feedback del usuario
- Confirmaciones para acciones destructivas

## Estructura del Proyecto

```
py-ventory/
├── api/
│   └── index.py              # Handler para Vercel serverless
├── static/
│   └── css/
│       └── variables.css     # Variables CSS personalizadas
├── templates/
│   ├── base.html             # Template base
│   ├── index.html            # Dashboard principal
│   ├── productos.html        # Lista de productos
│   ├── producto_form.html    # Formulario de productos
│   ├── categorias.html       # Lista de categorías
│   ├── categoria_form.html   # Formulario de categorías
│   ├── movimientos.html      # Historial de movimientos
│   └── movimiento_form.html  # Registro de movimientos
├── app.py                    # Aplicación Flask principal
├── SUPABASE.sql             # Esquema completo de base de datos
├── requirements.txt          # Dependencias Python
├── vercel.json              # Configuración de Vercel
├── .env                     # Variables de entorno (local)
├── .gitignore               # Archivos ignorados
└── README.md                # Documentación

```

## Esquema de Base de Datos

### Tablas Principales

1. **productos**
   - Información completa de productos
   - Relaciones con categorías y proveedores
   - Campos de auditoría (created_at, updated_at)

2. **categorias**
   - Sistema de clasificación de productos
   - Nombre único con descripción

3. **proveedores**
   - Información de proveedores (preparado para futuro)

4. **movimientos_inventario**
   - Historial completo de cambios
   - Registro automático vía triggers
   - Campos: tipo, cantidad, stock anterior/nuevo, motivo, referencia

### Características del Esquema

- **Triggers automáticos**:
  - Actualización de timestamps
  - Registro automático de movimientos al cambiar cantidades
- **Vistas optimizadas**:
  - productos_bajo_stock
  - resumen_inventario
- **Índices** para mejorar rendimiento
- **Constraints** para integridad de datos

## Configuración y Despliegue

### Variables de Entorno Requeridas

```env
SUPABASE_URL=tu_url_de_supabase
SUPABASE_KEY=tu_anon_key_de_supabase
SECRET_KEY=clave_secreta_para_flask
```

### Despliegue en Vercel

1. Configuración en `vercel.json` con rewrites a `/api/index`
2. Handler en `api/index.py` que importa la app Flask
3. Lazy initialization del cliente Supabase para compatibilidad serverless
4. Variables de entorno configuradas en Vercel Dashboard

### Dependencias

- Flask 3.0.0
- supabase 1.0.3 (versión estable para serverless)
- python-dotenv 1.0.0

## Características Técnicas

### Inicialización Lazy de Supabase

Para evitar problemas en entornos serverless, el cliente de Supabase se inicializa solo cuando se usa por primera vez, no al importar el módulo.

### Manejo de Errores

- Validación de variables de entorno al inicio
- Try-catch en todas las operaciones de base de datos
- Mensajes flash informativos para el usuario
- Logging de errores para debugging

### Seguridad

- Variables de entorno protegidas (.env no se sube a Git)
- SECRET_KEY para sesiones Flask
- Validación de datos en formularios
- Confirmaciones para operaciones destructivas

## Patrones de Desarrollo

### Rutas Organizadas

- `/` - Dashboard
- `/productos` - Gestión de productos
- `/categorias` - Gestión de categorías
- `/movimientos` - Historial de inventario

### Templates Reutilizables

- Template base con navegación y mensajes flash
- Bloques de contenido personalizables
- Estilos consistentes con variables CSS

### Base de Datos Replicable

El archivo `SUPABASE.sql` contiene TODO el esquema necesario para replicar la base de datos completa en cualquier entorno, incluyendo:
- Definición de tablas
- Índices
- Triggers y funciones
- Vistas
- Datos iniciales de categorías

## Mejoras Futuras Planificadas

- Sistema de autenticación de usuarios
- Gestión de proveedores
- Reportes y gráficos avanzados
- Exportación a Excel/PDF
- API REST para integraciones
- Sistema de alertas por email
- Códigos de barras y QR
- Multi-tienda

## Notas de Desarrollo

- El proyecto usa lazy initialization para Supabase client para evitar errores en import time
- La versión 1.0.3 de supabase es más estable en entornos serverless que las versiones 2.x
- Los triggers de PostgreSQL automatizan el registro de movimientos
- Bootstrap 5 proporciona responsive design sin JavaScript adicional