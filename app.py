from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Configuración de Supabase
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


@app.route('/')
def index():
    """Página principal - Dashboard del inventario"""
    try:
        # Obtener todos los productos activos
        productos_response = supabase.table('productos').select('*').eq('activo', True).execute()
        productos = productos_response.data

        # Calcular estadísticas
        total_productos = len(productos)
        total_items = sum(p['cantidad'] for p in productos)
        valor_total = sum(p['precio'] * p['cantidad'] for p in productos)

        # Productos con bajo stock (cantidad <= cantidad_minima)
        productos_bajo_stock = [p for p in productos if p['cantidad'] <= p.get('cantidad_minima', 5)]
        total_bajo_stock = len(productos_bajo_stock)

        # Obtener resumen por categorías
        categorias_response = supabase.table('categorias').select('*').order('nombre').execute()
        categorias = categorias_response.data

        resumen_categorias = []
        for categoria in categorias:
            productos_cat = [p for p in productos if p.get('categoria_id') == categoria['id']]
            if productos_cat:
                resumen_categorias.append({
                    'nombre': categoria['nombre'],
                    'total_productos': len(productos_cat),
                    'total_items': sum(p['cantidad'] for p in productos_cat),
                    'valor_total': sum(p['precio'] * p['cantidad'] for p in productos_cat)
                })

        # Productos sin categoría
        productos_sin_cat = [p for p in productos if p.get('categoria_id') is None]
        if productos_sin_cat:
            resumen_categorias.append({
                'nombre': 'Sin categoría',
                'total_productos': len(productos_sin_cat),
                'total_items': sum(p['cantidad'] for p in productos_sin_cat),
                'valor_total': sum(p['precio'] * p['cantidad'] for p in productos_sin_cat)
            })

        # Obtener últimos movimientos
        movimientos_response = supabase.table('movimientos_inventario').select(
            '*, productos(id, nombre, sku)'
        ).order('created_at', desc=True).limit(10).execute()
        ultimos_movimientos = movimientos_response.data

        return render_template('index.html',
                             total_productos=total_productos,
                             total_items=total_items,
                             valor_total=valor_total,
                             total_bajo_stock=total_bajo_stock,
                             productos_bajo_stock=productos_bajo_stock,
                             resumen_categorias=resumen_categorias,
                             ultimos_movimientos=ultimos_movimientos)
    except Exception as e:
        flash(f'Error al cargar el dashboard: {str(e)}', 'danger')
        return render_template('index.html',
                             total_productos=0,
                             total_items=0,
                             valor_total=0,
                             total_bajo_stock=0,
                             productos_bajo_stock=[],
                             resumen_categorias=[],
                             ultimos_movimientos=[])


@app.route('/productos')
def productos():
    """Lista todos los productos del inventario"""
    try:
        # Obtener productos con información de categoría
        response = supabase.table('productos').select('*, categorias(nombre)').execute()
        productos = response.data
        return render_template('productos.html', productos=productos)
    except Exception as e:
        flash(f'Error al cargar productos: {str(e)}', 'danger')
        return render_template('productos.html', productos=[])


@app.route('/producto/nuevo', methods=['GET', 'POST'])
def nuevo_producto():
    """Crear un nuevo producto"""
    if request.method == 'POST':
        try:
            # Preparar datos del producto
            categoria_id = request.form.get('categoria_id')
            data = {
                'nombre': request.form['nombre'],
                'descripcion': request.form.get('descripcion', ''),
                'precio': float(request.form['precio']),
                'cantidad': int(request.form['cantidad']),
                'categoria_id': int(categoria_id) if categoria_id else None,
                'sku': request.form.get('sku', '')
            }
            supabase.table('productos').insert(data).execute()
            flash('Producto creado exitosamente', 'success')
            return redirect(url_for('productos'))
        except Exception as e:
            flash(f'Error al crear producto: {str(e)}', 'danger')

    # Cargar categorías para el formulario
    try:
        categorias_response = supabase.table('categorias').select('*').order('nombre').execute()
        categorias = categorias_response.data
    except Exception as e:
        categorias = []
        flash(f'Advertencia: No se pudieron cargar las categorías: {str(e)}', 'warning')

    return render_template('producto_form.html', producto=None, categorias=categorias)


@app.route('/producto/<int:id>/editar', methods=['GET', 'POST'])
def editar_producto(id):
    """Editar un producto existente"""
    if request.method == 'POST':
        try:
            # Preparar datos del producto
            categoria_id = request.form.get('categoria_id')
            data = {
                'nombre': request.form['nombre'],
                'descripcion': request.form.get('descripcion', ''),
                'precio': float(request.form['precio']),
                'cantidad': int(request.form['cantidad']),
                'categoria_id': int(categoria_id) if categoria_id else None,
                'sku': request.form.get('sku', '')
            }
            supabase.table('productos').update(data).eq('id', id).execute()
            flash('Producto actualizado exitosamente', 'success')
            return redirect(url_for('productos'))
        except Exception as e:
            flash(f'Error al actualizar producto: {str(e)}', 'danger')

    # Obtener datos del producto
    try:
        response = supabase.table('productos').select('*').eq('id', id).execute()
        producto = response.data[0] if response.data else None

        # Cargar categorías para el formulario
        categorias_response = supabase.table('categorias').select('*').order('nombre').execute()
        categorias = categorias_response.data

        return render_template('producto_form.html', producto=producto, categorias=categorias)
    except Exception as e:
        flash(f'Error al cargar producto: {str(e)}', 'danger')
        return redirect(url_for('productos'))


@app.route('/producto/<int:id>/eliminar', methods=['POST'])
def eliminar_producto(id):
    """Eliminar un producto"""
    try:
        supabase.table('productos').delete().eq('id', id).execute()
        flash('Producto eliminado exitosamente', 'success')
    except Exception as e:
        flash(f'Error al eliminar producto: {str(e)}', 'danger')

    return redirect(url_for('productos'))


# ==================== RUTAS DE CATEGORÍAS ====================

@app.route('/categorias')
def categorias():
    """Lista todas las categorías"""
    try:
        response = supabase.table('categorias').select('*').order('nombre').execute()
        categorias = response.data

        # Contar productos por categoría
        for categoria in categorias:
            productos_response = supabase.table('productos').select('id', count='exact').eq('categoria_id', categoria['id']).execute()
            categoria['total_productos'] = productos_response.count if productos_response.count else 0

        return render_template('categorias.html', categorias=categorias)
    except Exception as e:
        flash(f'Error al cargar categorías: {str(e)}', 'danger')
        return render_template('categorias.html', categorias=[])


@app.route('/categoria/nueva', methods=['GET', 'POST'])
def nueva_categoria():
    """Crear una nueva categoría"""
    if request.method == 'POST':
        try:
            data = {
                'nombre': request.form['nombre'],
                'descripcion': request.form.get('descripcion', '')
            }
            supabase.table('categorias').insert(data).execute()
            flash('Categoría creada exitosamente', 'success')
            return redirect(url_for('categorias'))
        except Exception as e:
            flash(f'Error al crear categoría: {str(e)}', 'danger')

    return render_template('categoria_form.html', categoria=None)


@app.route('/categoria/<int:id>/editar', methods=['GET', 'POST'])
def editar_categoria(id):
    """Editar una categoría existente"""
    if request.method == 'POST':
        try:
            data = {
                'nombre': request.form['nombre'],
                'descripcion': request.form.get('descripcion', '')
            }
            supabase.table('categorias').update(data).eq('id', id).execute()
            flash('Categoría actualizada exitosamente', 'success')
            return redirect(url_for('categorias'))
        except Exception as e:
            flash(f'Error al actualizar categoría: {str(e)}', 'danger')

    # Obtener datos de la categoría
    try:
        response = supabase.table('categorias').select('*').eq('id', id).execute()
        categoria = response.data[0] if response.data else None
        return render_template('categoria_form.html', categoria=categoria)
    except Exception as e:
        flash(f'Error al cargar categoría: {str(e)}', 'danger')
        return redirect(url_for('categorias'))


@app.route('/categoria/<int:id>/eliminar', methods=['POST'])
def eliminar_categoria(id):
    """Eliminar una categoría"""
    try:
        # Verificar si hay productos con esta categoría
        productos_response = supabase.table('productos').select('id', count='exact').eq('categoria_id', id).execute()
        total_productos = productos_response.count if productos_response.count else 0

        if total_productos > 0:
            flash(f'No se puede eliminar la categoría porque tiene {total_productos} producto(s) asociado(s). Primero reasigna o elimina los productos.', 'warning')
        else:
            supabase.table('categorias').delete().eq('id', id).execute()
            flash('Categoría eliminada exitosamente', 'success')
    except Exception as e:
        flash(f'Error al eliminar categoría: {str(e)}', 'danger')

    return redirect(url_for('categorias'))


# ==================== RUTAS DE MOVIMIENTOS DE INVENTARIO ====================

@app.route('/movimientos')
def movimientos():
    """Lista todos los movimientos de inventario"""
    try:
        # Obtener filtro de producto si existe
        producto_id = request.args.get('producto_id', type=int)

        # Construir la consulta
        query = supabase.table('movimientos_inventario').select(
            '*, productos(id, nombre, sku)'
        ).order('created_at', desc=True)

        # Aplicar filtro si existe
        if producto_id:
            query = query.eq('producto_id', producto_id)

        # Limitar a los últimos 100 movimientos
        response = query.limit(100).execute()
        movimientos = response.data

        # Obtener lista de productos para el filtro
        productos_response = supabase.table('productos').select('id, nombre, sku').order('nombre').execute()
        productos = productos_response.data

        return render_template('movimientos.html',
                             movimientos=movimientos,
                             productos=productos,
                             producto_id_filtro=producto_id)
    except Exception as e:
        flash(f'Error al cargar movimientos: {str(e)}', 'danger')
        return render_template('movimientos.html', movimientos=[], productos=[])


@app.route('/movimiento/nuevo', methods=['GET', 'POST'])
def nuevo_movimiento():
    """Registrar un nuevo movimiento de inventario manualmente"""
    if request.method == 'POST':
        try:
            producto_id = int(request.form['producto_id'])
            tipo = request.form['tipo']
            cantidad = int(request.form['cantidad'])
            motivo = request.form.get('motivo', '')
            referencia = request.form.get('referencia', '')

            # Obtener el producto actual
            producto_response = supabase.table('productos').select('*').eq('id', producto_id).execute()
            if not producto_response.data:
                flash('Producto no encontrado', 'danger')
                return redirect(url_for('nuevo_movimiento'))

            producto = producto_response.data[0]
            cantidad_anterior = producto['cantidad']

            # Calcular nueva cantidad según el tipo de movimiento
            if tipo == 'entrada':
                cantidad_nueva = cantidad_anterior + cantidad
            elif tipo == 'salida':
                cantidad_nueva = cantidad_anterior - cantidad
                if cantidad_nueva < 0:
                    flash('No hay suficiente stock para realizar esta salida', 'danger')
                    return redirect(url_for('nuevo_movimiento'))
            else:  # ajuste
                cantidad_nueva = cantidad
                cantidad = abs(cantidad_nueva - cantidad_anterior)

            # Registrar el movimiento
            movimiento_data = {
                'producto_id': producto_id,
                'tipo': tipo,
                'cantidad': cantidad,
                'cantidad_anterior': cantidad_anterior,
                'cantidad_nueva': cantidad_nueva,
                'motivo': motivo,
                'referencia': referencia
            }
            supabase.table('movimientos_inventario').insert(movimiento_data).execute()

            # Actualizar la cantidad del producto
            supabase.table('productos').update({'cantidad': cantidad_nueva}).eq('id', producto_id).execute()

            flash('Movimiento registrado exitosamente', 'success')
            return redirect(url_for('movimientos'))
        except Exception as e:
            flash(f'Error al registrar movimiento: {str(e)}', 'danger')

    # Cargar productos para el formulario
    try:
        productos_response = supabase.table('productos').select('*').order('nombre').execute()
        productos = productos_response.data
    except Exception as e:
        productos = []
        flash(f'Advertencia: No se pudieron cargar los productos: {str(e)}', 'warning')

    return render_template('movimiento_form.html', productos=productos)


if __name__ == '__main__':
    app.run(debug=True)
