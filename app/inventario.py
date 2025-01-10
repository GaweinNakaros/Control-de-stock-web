# app/inventario.py
from flask import Blueprint, render_template, request
from app_stock import safe_query

inventario_bp = Blueprint('inventario', __name__)

@inventario_bp.route('/view')
def view_inventory():
    
    page = request.args.get('page', 1, type=int)  # Página actual
    per_page = 10  # Cantidad de items por página
    offset = (page - 1) * per_page  # Cálculo del desplazamiento

    cursor = safe_query("SELECT * FROM inventario LIMIT ? OFFSET ?", (per_page, offset))
    if cursor:
        inventario = cursor.fetchall()

    # Obtener el total de items en el inventario para calcular las páginas
    cursor = safe_query("SELECT COUNT(*) FROM inventario")
    total_items = cursor.fetchone()[0]
    total_pages = (total_items // per_page) + (1 if total_items % per_page > 0 else 0)

    return render_template('view_inventory.html', inventario=inventario, page=page, total_pages=total_pages)


