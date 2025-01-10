from flask import Flask, render_template, request, redirect, url_for, g # Mejorar la gestión de base de datos utilizando un contexto de conexión
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField
from wtforms.validators import DataRequired, NumberRange
from inventario import inventario_bp

import sqlite3  # Para manejar la base de datos SQLite

class ItemForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired()])
    sku = StringField('SKU', validators=[DataRequired()])
    descripcion = StringField('Descripción')
    cantidad = IntegerField('Cantidad', validators=[DataRequired(), NumberRange(min=1)])
    precio = FloatField('Precio', validators=[DataRequired(), NumberRange(min=0.01)])
    categoria = StringField('Categoría')

# Inicializar la aplicación Flask
app = Flask(__name__)

# Configuración inicial de la base de datos
# Crea la tabla "inventario" si no existe

def create_table_inventario():
    conn = sqlite3.connect("inventario.db")  # Conexión a la base de datos
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventario (
            inventario_id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            sku TEXT NOT NULL UNIQUE,
            descripcion TEXT,
            cantidad INTEGER NOT NULL,
            precio REAL NOT NULL,
            categoria TEXT
        )
    """)
    conn.commit()
    conn.close()

# Llamada para asegurar que la tabla exista al inicio
create_table_inventario()

# Usar un hook para gestionar la conexión a la base de datos
# Reemplaza las consultas directas con el uso de get_db()
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect("inventario.db")
        g.db.row_factory = sqlite3.Row  # Permite acceder a las columnas por nombre
    return g.db

@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# Proteccion consultas
def safe_query(query, params=()):
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(query, params)
        return cursor
    except sqlite3.Error as e:
        print(f"Error en la consulta: {e}")
        return None

# Ruta para el menú principal
@app.route('/')
def menu():
    """Renderiza el menú principal"""
    return render_template('menu.html')

# Ruta para agregar un nuevo item al inventario

def validate_item_data(nombre, sku, cantidad, precio):
    if not nombre or not sku or cantidad <= 0 or precio <= 0:
        return False
    return True

@app.route('/add', methods=['GET', 'POST'])
def add_item():
    message = ""
    if request.method == 'POST':
        nombre = request.form['nombre']
        sku = request.form['sku']
        descripcion = request.form['descripcion']
        cantidad = int(request.form['cantidad'])
        precio = float(request.form['precio'])
        categoria = request.form['categoria']

        if not validate_item_data(nombre, sku, cantidad, precio):
            return render_template('add_item.html', error="Datos inválidos")

        db = get_db()
        cursor = db.cursor()
        cursor.execute("""INSERT INTO inventario (nombre, sku, descripcion, cantidad, precio, categoria) 
                          VALUES (?, ?, ?, ?, ?, ?)""",
                       (nombre, sku, descripcion, cantidad, precio, categoria))
        db.commit()

        message = "Item agregado con éxito"
        return render_template('add_item.html', message=message)

    return render_template('add_item.html', message=message)

# Ruta para ver el inventario
# En app_stock.py

app.register_blueprint(inventario_bp)

# Ruta para buscar un item por SKU
@app.route('/search', methods=['GET', 'POST'])
def search_item():
    """Permite buscar un item en el inventario mediante el SKU"""
    item = None
    if request.method == 'POST':
        sku = request.form['sku']
        conn = sqlite3.connect("inventario.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM inventario WHERE sku = ?", (sku,))
        item = cursor.fetchone()
        conn.close()
    return render_template('search_item.html', item=item)

# Ruta para editar un item existente
@app.route('/edit/<sku>', methods=['GET', 'POST'])
def edit_item(sku):
    """Permite editar un item específico del inventario"""
    conn = sqlite3.connect("inventario.db")
    cursor = conn.cursor()

    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        cantidad = int(request.form['cantidad'])
        precio = float(request.form['precio'])
        categoria = request.form['categoria']

        cursor.execute("""
            UPDATE inventario
            SET nombre = ?, descripcion = ?, cantidad = ?, precio = ?, categoria = ?
            WHERE sku = ?
        """, (nombre, descripcion, cantidad, precio, categoria, sku))
        conn.commit()
        conn.close()
        return redirect(url_for('view_inventory'))

    cursor.execute("SELECT * FROM inventario WHERE sku = ?", (sku,))
    item = cursor.fetchone()
    conn.close()
    return render_template('edit_item.html', item=item)

# Ruta para eliminar un item
@app.route('/delete/<sku>', methods=['POST'])
def delete_item(sku):
    """Permite eliminar un item del inventario por SKU"""
    conn = sqlite3.connect("inventario.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM inventario WHERE sku = ?", (sku,))
    conn.commit()
    conn.close()
    return redirect(url_for('view_inventory'))

# Ruta para mostrar el reporte de stock
@app.route('/report')
def report_stock():
    """Muestra un reporte del stock actual"""
    conn = sqlite3.connect("inventario.db")
    cursor = conn.cursor()
    cursor.execute("SELECT nombre, cantidad FROM inventario")
    stock = cursor.fetchall()
    conn.close()
    return render_template('report_stock.html', stock=stock)

# Ruta para el reporte de stock bajo
@app.route('/low-stock', methods=['GET', 'POST'])
def low_stock():
    """Genera un reporte de items con stock bajo basado en un límite"""
    limite = 5
    if request.method == 'POST':
        limite = int(request.form['limite'])

    conn = sqlite3.connect("inventario.db")
    cursor = conn.cursor()
    cursor.execute("SELECT nombre, cantidad FROM inventario WHERE cantidad <= ?", (limite,))
    stock_bajo = cursor.fetchall()
    conn.close()

    return render_template('low_stock.html', stock_bajo=stock_bajo, limite=limite)

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run(debug=True)








