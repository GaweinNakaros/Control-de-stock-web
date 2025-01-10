# Flask App Template Integrado con Gestión de Inventario

from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3

# Crear Flask app
app = Flask(__name__)

# Configuración
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['DEBUG'] = True

# Funciones de gestión de inventario
def create_table_inventario():
    conn = sqlite3.connect("inventario.db")
    cursor = conn.cursor()
    query = """CREATE TABLE IF NOT EXISTS inventario (
                inventario_id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                sku TEXT NOT NULL UNIQUE,
                descripcion TEXT,
                cantidad INTEGER,
                precio INTEGER,
                categoria TEXT
            )"""
    cursor.execute(query)
    conn.commit()
    conn.close()

# Crear tabla inicial
create_table_inventario()

# Rutas
@app.route('/')
def menu():
    return render_template('menu.html')

@app.route('/add', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        nombre = request.form['nombre']
        sku = request.form['sku']
        descripcion = request.form['descripcion']
        cantidad = int(request.form['cantidad'])
        precio = int(request.form['precio'])
        categoria = request.form['categoria']
        conn = sqlite3.connect("inventario.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO inventario (nombre, sku, descripcion, cantidad, precio, categoria) VALUES (?, ?, ?, ?, ?, ?)", (nombre, sku, descripcion, cantidad, precio, categoria))
        conn.commit()
        conn.close()
        return redirect(url_for('menu'))
    return render_template('add_item.html')

@app.route('/view')
def view_inventory():
    conn = sqlite3.connect("inventario.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM inventario")
    inventario = cursor.fetchall()
    conn.close()
    return render_template('view_inventory.html', inventario=inventario)

@app.route('/search', methods=['GET', 'POST'])
def search_item():
    item = None
    if request.method == 'POST':
        sku = request.form['sku']
        conn = sqlite3.connect("inventario.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM inventario WHERE sku = ?", (sku,))
        item = cursor.fetchone()
        conn.close()
    return render_template('search_item.html', item=item)

@app.route('/edit/<sku>', methods=['GET', 'POST'])
def edit_item(sku):
    conn = sqlite3.connect("inventario.db")
    cursor = conn.cursor()
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        cantidad = int(request.form['cantidad'])
        precio = int(request.form['precio'])
        categoria = request.form['categoria']
        cursor.execute("UPDATE inventario SET nombre = ?, descripcion = ?, cantidad = ?, precio = ?, categoria = ? WHERE sku = ?",
                       (nombre, descripcion, cantidad, precio, categoria, sku))
        conn.commit()
        conn.close()
        return redirect(url_for('view_inventory'))
    cursor.execute("SELECT * FROM inventario WHERE sku = ?", (sku,))
    item = cursor.fetchone()
    conn.close()
    return render_template('edit_item.html', item=item)

@app.route('/delete/<sku>', methods=['POST'])
def delete_item(sku):
    conn = sqlite3.connect("inventario.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM inventario WHERE sku = ?", (sku,))
    conn.commit()
    conn.close()
    return redirect(url_for('view_inventory'))

@app.route('/report')
def report_stock():
    conn = sqlite3.connect("inventario.db")
    cursor = conn.cursor()
    cursor.execute("SELECT nombre, cantidad FROM inventario")
    stock = cursor.fetchall()
    conn.close()
    return render_template('report_stock.html', stock=stock)

@app.route('/low-stock', methods=['GET', 'POST'])
def low_stock():
    limite = 5
    if request.method == 'POST':
        limite = int(request.form['limite'])
    conn = sqlite3.connect("inventario.db")
    cursor = conn.cursor()
    cursor.execute("SELECT nombre, cantidad FROM inventario WHERE cantidad <= ?", (limite,))
    stock_bajo = cursor.fetchall()
    conn.close()
    return render_template('low_stock.html', stock_bajo=stock_bajo, limite=limite)

# Error handling
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html', message="La página que buscas no existe."), 404

# Run the app
if __name__ == '__main__':
    app.run(debug=True)







