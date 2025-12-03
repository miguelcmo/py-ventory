# Inventario App

Sistema de gestión de inventario para tiendas pequeñas desarrollado con Flask y Supabase.

## Características

- Gestión completa de productos (CRUD)
- Control de stock en tiempo real
- Alertas de bajo stock
- Categorización de productos
- Historial automático de movimientos de inventario
- Interfaz moderna con Bootstrap 5
- Base de datos en Supabase (PostgreSQL)
- Desplegable en Vercel

## Tecnologías

- **Backend**: Flask (Python)
- **Base de Datos**: Supabase (PostgreSQL)
- **Frontend**: Bootstrap 5 + Custom CSS
- **Despliegue**: Vercel

## Instalación Local

### 1. Clonar el repositorio

```bash
cd S14_inventoryApp
```

### 2. Crear entorno virtual

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Copia el archivo `.env.example` a `.env` y configura tus credenciales de Supabase:

```bash
cp .env.example .env
```

Edita el archivo `.env`:

```env
SUPABASE_URL=tu_url_de_supabase
SUPABASE_KEY=tu_key_de_supabase
SECRET_KEY=tu_clave_secreta_para_flask
```

### 5. Configurar la base de datos en Supabase

1. Crea una cuenta en [Supabase](https://supabase.com)
2. Crea un nuevo proyecto
3. Ve a la sección SQL Editor
4. Copia y ejecuta todo el contenido del archivo `SUPABASE.sql`
5. Copia la URL y la Anon Key de tu proyecto y pégalas en el archivo `.env`

### 6. Ejecutar la aplicación

```bash
python app.py
```

La aplicación estará disponible en `http://localhost:5000`

## Estructura del Proyecto

```
S14_inventoryApp/
├── app.py                  # Aplicación principal Flask
├── requirements.txt        # Dependencias Python
├── vercel.json            # Configuración de Vercel
├── SUPABASE.sql           # Esquema de base de datos
├── .env.example           # Template de variables de entorno
├── static/
│   └── css/
│       └── variables.css  # Variables CSS personalizadas
└── templates/
    ├── base.html          # Template base
    ├── index.html         # Dashboard
    ├── productos.html     # Lista de productos
    └── producto_form.html # Formulario de producto
```

## Esquema de Base de Datos

### Tablas Principales

- **productos**: Almacena información de productos
- **categorias**: Categorías de productos
- **proveedores**: Información de proveedores
- **movimientos_inventario**: Historial de cambios en inventario

### Características del Esquema

- Triggers automáticos para actualizar timestamps
- Registro automático de movimientos de inventario
- Vistas para productos con bajo stock y resumen de inventario
- Índices para mejorar el rendimiento

## Despliegue en Vercel

### 1. Instalar Vercel CLI

```bash
npm i -g vercel
```

### 2. Desplegar

```bash
vercel
```

### 3. Configurar variables de entorno en Vercel

En el dashboard de Vercel, configura las siguientes variables:

- `SUPABASE_URL`
- `SUPABASE_KEY`
- `SECRET_KEY`

## Funcionalidades Principales

### Dashboard

- Vista general del inventario
- Estadísticas rápidas
- Accesos directos a funciones principales

### Productos

- Listar todos los productos
- Crear nuevo producto
- Editar producto existente
- Eliminar producto
- Búsqueda y filtrado
- Indicadores visuales de stock

### Gestión de Stock

- Control automático de cantidades
- Alertas de bajo stock
- Historial de movimientos

## Próximas Mejoras

- Gestión de proveedores
- Reportes y estadísticas avanzadas
- Exportación a Excel/PDF
- Sistema de autenticación
- API REST
- Dashboard con gráficos

## Soporte

Para reportar problemas o sugerencias, crea un issue en el repositorio.

## Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.
