-- =====================================================
-- INVENTARIO APP - ESQUEMA DE BASE DE DATOS
-- =====================================================
-- Este archivo contiene todo el esquema necesario para
-- replicar la base de datos en Supabase
-- =====================================================

-- Tabla de Categorias
CREATE TABLE IF NOT EXISTS categorias (
    id BIGSERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    descripcion TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW())
);

-- Tabla de Proveedores
CREATE TABLE IF NOT EXISTS proveedores (
    id BIGSERIAL PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    contacto VARCHAR(100),
    telefono VARCHAR(20),
    email VARCHAR(100),
    direccion TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW())
);

-- Tabla de Productos
CREATE TABLE IF NOT EXISTS productos (
    id BIGSERIAL PRIMARY KEY,
    sku VARCHAR(50) UNIQUE,
    nombre VARCHAR(200) NOT NULL,
    descripcion TEXT,
    precio DECIMAL(10, 2) NOT NULL CHECK (precio >= 0),
    cantidad INTEGER NOT NULL DEFAULT 0 CHECK (cantidad >= 0),
    cantidad_minima INTEGER DEFAULT 5,
    categoria_id BIGINT REFERENCES categorias(id) ON DELETE SET NULL,
    proveedor_id BIGINT REFERENCES proveedores(id) ON DELETE SET NULL,
    imagen_url TEXT,
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW())
);

-- Tabla de Movimientos de Inventario
CREATE TABLE IF NOT EXISTS movimientos_inventario (
    id BIGSERIAL PRIMARY KEY,
    producto_id BIGINT NOT NULL REFERENCES productos(id) ON DELETE CASCADE,
    tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('entrada', 'salida', 'ajuste')),
    cantidad INTEGER NOT NULL,
    cantidad_anterior INTEGER NOT NULL,
    cantidad_nueva INTEGER NOT NULL,
    motivo TEXT,
    referencia VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW())
);

-- Indices para mejorar el rendimiento
CREATE INDEX IF NOT EXISTS idx_productos_categoria ON productos(categoria_id);
CREATE INDEX IF NOT EXISTS idx_productos_proveedor ON productos(proveedor_id);
CREATE INDEX IF NOT EXISTS idx_productos_sku ON productos(sku);
CREATE INDEX IF NOT EXISTS idx_productos_activo ON productos(activo);
CREATE INDEX IF NOT EXISTS idx_movimientos_producto ON movimientos_inventario(producto_id);
CREATE INDEX IF NOT EXISTS idx_movimientos_tipo ON movimientos_inventario(tipo);
CREATE INDEX IF NOT EXISTS idx_movimientos_fecha ON movimientos_inventario(created_at);

-- Funcion para actualizar updated_at automaticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = TIMEZONE('utc', NOW());
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers para actualizar updated_at
CREATE TRIGGER update_categorias_updated_at BEFORE UPDATE ON categorias
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_proveedores_updated_at BEFORE UPDATE ON proveedores
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_productos_updated_at BEFORE UPDATE ON productos
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Funcion para registrar movimientos de inventario automaticamente
CREATE OR REPLACE FUNCTION registrar_movimiento_inventario()
RETURNS TRIGGER AS $$
BEGIN
    IF (TG_OP = 'UPDATE' AND OLD.cantidad != NEW.cantidad) THEN
        INSERT INTO movimientos_inventario (
            producto_id,
            tipo,
            cantidad,
            cantidad_anterior,
            cantidad_nueva,
            motivo
        ) VALUES (
            NEW.id,
            CASE
                WHEN NEW.cantidad > OLD.cantidad THEN 'entrada'
                WHEN NEW.cantidad < OLD.cantidad THEN 'salida'
                ELSE 'ajuste'
            END,
            ABS(NEW.cantidad - OLD.cantidad),
            OLD.cantidad,
            NEW.cantidad,
            'Actualizacion automatica'
        );
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger para registrar cambios en cantidad de productos
CREATE TRIGGER producto_cantidad_change AFTER UPDATE ON productos
    FOR EACH ROW EXECUTE FUNCTION registrar_movimiento_inventario();

-- Insertar categorias iniciales
INSERT INTO categorias (nombre, descripcion) VALUES
    ('General', 'Productos sin categoria especifica'),
    ('Electronica', 'Dispositivos y accesorios electronicos'),
    ('Alimentos', 'Productos alimenticios'),
    ('Bebidas', 'Bebidas de todo tipo'),
    ('Limpieza', 'Productos de limpieza e higiene'),
    ('Papeleria', 'Articulos de oficina y papeleria')
ON CONFLICT (nombre) DO NOTHING;

-- Vista para productos con bajo stock
CREATE OR REPLACE VIEW productos_bajo_stock AS
SELECT
    p.id,
    p.sku,
    p.nombre,
    p.cantidad,
    p.cantidad_minima,
    c.nombre as categoria
FROM productos p
LEFT JOIN categorias c ON p.categoria_id = c.id
WHERE p.cantidad <= p.cantidad_minima AND p.activo = TRUE;

-- Vista para resumen de inventario
CREATE OR REPLACE VIEW resumen_inventario AS
SELECT
    c.nombre as categoria,
    COUNT(p.id) as total_productos,
    SUM(p.cantidad) as total_items,
    SUM(p.precio * p.cantidad) as valor_total
FROM productos p
LEFT JOIN categorias c ON p.categoria_id = c.id
WHERE p.activo = TRUE
GROUP BY c.nombre;
