from flask import Flask, render_template, request, redirect, url_for
import sqlite3  # Para manejar la base de datos SQLite

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

# Ruta para el menú principal
@app.route('/')
def menu():
    """Renderiza el menú principal"""
    return render_template('menu.html')

# Ruta para agregar un nuevo item al inventario
@app.route('/add', methods=['GET', 'POST'])
def add_item():
    """Permite agregar un nuevo item al inventario mediante un formulario"""
    if request.method == 'POST':
        nombre = request.form['nombre']
        sku = request.form['sku']
        descripcion = request.form['descripcion']
        cantidad = int(request.form['cantidad'])
        precio = float(request.form['precio'])
        categoria = request.form['categoria']

        conn = sqlite3.connect("inventario.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO inventario (nombre, sku, descripcion, cantidad, precio, categoria)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (nombre, sku, descripcion, cantidad, precio, categoria))
        conn.commit()
        conn.close()

        return redirect(url_for('menu'))

    return render_template('add_item.html')

# Ruta para visualizar el inventario
@app.route('/view')
def view_inventory():
    """Muestra el inventario completo en una tabla"""
    conn = sqlite3.connect("inventario.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM inventario")
    inventario = cursor.fetchall()
    conn.close()
    return render_template('view_inventory.html', inventario=inventario)

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








