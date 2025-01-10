# Flask App Template Integrado con Gestión de Inventario

from flask import Flask, render_template, request, jsonify, redirect, url_for  # Este es el módulo principal de Flask que importa las funciones necesarias para crear la aplicación, renderizar plantillas HTML, manejar solicitudes y responder con JSON.
import sqlite3  # Importamos el módulo sqlite3

# Crear Flask app
app = Flask(__name__)  # Crea una instancia de la aplicación Flask. '__name__' indica el módulo actual, lo cual ayuda a Flask a encontrar recursos.

# Configuración
app.config['SECRET_KEY'] = 'your_secret_key_here'  # Establece una clave secreta utilizada para la seguridad de la aplicación, como firmar cookies o manejar sesiones.
app.config['DEBUG'] = True  # Activa el modo de depuración para desarrollo. Cambiar a False en producción.

# Funciones de gestión de inventario
def create_table_inventario():
    conn = sqlite3.connect("inventario.db")  # Conexión a la base de datos
    cursor = conn.cursor()
    query = f"""CREATE TABLE IF NOT EXISTS inventario (
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

def registrar_item(nombre, sku, descripcion, cantidad, precio, categoria):
    conn = sqlite3.connect("inventario.db")
    cursor = conn.cursor()
    query = f"INSERT INTO inventario (nombre, sku, descripcion, cantidad, precio, categoria) VALUES(?, ?, ?, ?, ?, ?)"
    cursor.execute(query, (nombre, sku, descripcion, cantidad, precio, categoria))
    conn.commit()
    conn.close()

def get_inventario():
    conn = sqlite3.connect("inventario.db")
    cursor = conn.cursor()
    query = f"SELECT * FROM inventario"
    cursor.execute(query)
    inventario = cursor.fetchall()
    conn.close()
    return inventario

def buscar_item(sku):
    conn = sqlite3.connect("inventario.db")
    cursor = conn.cursor()
    query = f"SELECT * FROM inventario WHERE sku = ?"
    cursor.execute(query, (sku,))
    item = cursor.fetchone()
    conn.close()
    return item

def modificar_item(sku, nombre=None, descripcion=None, cantidad=None, precio=None, categoria=None):
    conn = sqlite3.connect("inventario.db")
    cursor = conn.cursor()
    updates = []
    if nombre: updates.append(f"nombre = '{nombre}'")
    if descripcion: updates.append(f"descripcion = '{descripcion}'")
    if cantidad is not None: updates.append(f"cantidad = {cantidad}")
    if precio is not None: updates.append(f"precio = {precio}")
    if categoria: updates.append(f"categoria = '{categoria}'")
    if updates:
        update_query = ", ".join(updates)
        query = f"UPDATE inventario SET {update_query} WHERE sku = ?"
        cursor.execute(query, (sku,))
        conn.commit()
    conn.close()

def borrar_item(sku):
    conn = sqlite3.connect("inventario.db")
    cursor = conn.cursor()
    query = f"DELETE FROM inventario WHERE sku = ?"
    cursor.execute(query, (sku,))
    conn.commit()
    conn.close()

# Crear tabla al iniciar
create_table_inventario()

# Rutas
@app.route('/')
def home():
    inventario = get_inventario()
    return render_template('index.html', inventario=inventario)

@app.route('/add', methods=['POST'])
def add_item():
    nombre = request.form['nombre']
    sku = request.form['sku']
    descripcion = request.form['descripcion']
    cantidad = int(request.form['cantidad'])
    precio = int(request.form['precio'])
    categoria = request.form['categoria']
    registrar_item(nombre, sku, descripcion, cantidad, precio, categoria)
    return redirect(url_for('home'))

@app.route('/delete/<sku>', methods=['POST'])
def delete_item(sku):
    borrar_item(sku)
    return redirect(url_for('home'))

@app.route('/edit/<sku>', methods=['GET', 'POST'])
def edit_item(sku):
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion')
        cantidad = request.form.get('cantidad')
        cantidad = int(cantidad) if cantidad else None
        precio = request.form.get('precio')
        precio = int(precio) if precio else None
        categoria = request.form.get('categoria')
        modificar_item(sku, nombre, descripcion, cantidad, precio, categoria)
        return redirect(url_for('home'))
    item = buscar_item(sku)
    return render_template('edit.html', item=item)

# Error handling
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal Server Error"}), 500

# Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)




