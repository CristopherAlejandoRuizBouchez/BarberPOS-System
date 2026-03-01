import os
import sys
import sqlite3
import json
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
import webbrowser
from threading import Timer


if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")
# --- CONFIGURACIÓN PARA EL EJECUTABLE (.EXE) ---
def resource_path(relative_path):
    """ Obtiene la ruta absoluta a los recursos, funciona para dev y para PyInstaller """
    try:
        # PyInstaller crea una carpeta temporal en _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Iniciamos Flask diciéndole dónde buscar las carpetas dentro del EXE
app = Flask(__name__, 
            template_folder=resource_path('templates'),
            static_folder=resource_path('static'))

app.secret_key = 'barberia_043_segura' # Clave para las alertas

# --- CONEXIÓN A BASE DE DATOS ---
def conectar_db():
    # Busca la base de datos siempre en la misma carpeta donde está el .exe
    base_dir = os.path.dirname(os.path.abspath(sys.argv[0])) if getattr(sys, 'frozen', False) else os.path.abspath(".")
    db_path = os.path.join(base_dir, 'barberia.db')
    conexion = sqlite3.connect(db_path)
    return conexion

@app.route('/')
def index():
    conexion = conectar_db()
    cursor = conexion.cursor()
    
    # Traemos el catálogo
    cursor.execute("SELECT id, nombre, precio, categoria, stock FROM catalogo")
    catalogo = cursor.fetchall()
    
    cursor.execute("SELECT * FROM barberos")
    barberos = cursor.fetchall()
    
    # Ventas del día (no cerradas)
    cursor.execute("""
        SELECT catalogo.nombre, ventas.monto 
        FROM ventas 
        JOIN catalogo ON ventas.producto_id = catalogo.id 
        WHERE ventas.cerrado = 0
        ORDER BY ventas.fecha DESC
    """)
    ventas_dia = cursor.fetchall()
    total_dia = sum(v[1] for v in ventas_dia) if ventas_dia else 0
    
    conexion.close()
    return render_template('index.html', catalogo=catalogo, barberos=barberos, ventas=ventas_dia, total=total_dia)

@app.route('/registrar/<int:id>')
def registrar(id):
    barbero = request.args.get('barbero')
    conexion = conectar_db()
    cursor = conexion.cursor()
    
    cursor.execute("SELECT nombre, precio, categoria, stock FROM catalogo WHERE id = ?", (id,))
    item = cursor.fetchone()
    
    if not item:
        conexion.close()
        flash("❌ Error: Producto no encontrado.", "error")
        return redirect(url_for('index'))

    nombre_item, precio, categoria, stock_actual = item[0], item[1], item[2], item[3]

    # VALIDACIÓN DE STOCK
    if categoria.lower() == 'producto':
        if stock_actual > 0:
            cursor.execute("UPDATE catalogo SET stock = stock - 1 WHERE id = ?", (id,))
        else:
            conexion.close()
            flash(f"⚠️ ¡AGOTADO! No hay stock disponible de {nombre_item}.", "error")
            return redirect(url_for('index'))

    # REGISTRAR VENTA
    cursor.execute("""
        INSERT INTO ventas (producto_id, monto, fecha, barbero_nombre, cerrado, metodo_pago) 
        VALUES (?, ?, datetime('now', 'localtime'), ?, 0, 'Efectivo')
    """, (id, precio, barbero))
    
    conexion.commit()
    conexion.close()
    return redirect(url_for('index'))

# --- ADMINISTRACIÓN ---
@app.route('/admin')
def admin():
    conexion = conectar_db()
    cursor = conexion.cursor()
    cursor.execute("SELECT id, nombre, precio, categoria, stock FROM catalogo")
    catalogo = cursor.fetchall()
    cursor.execute("SELECT * FROM barberos")
    barberos = cursor.fetchall()
    cursor.execute("SELECT id, descripcion, monto, categoria, fecha FROM egresos WHERE strftime('%m', fecha) = strftime('%m', 'now')")
    egresos = cursor.fetchall()
    conexion.close()
    
    # Limpieza de datos para evitar errores en HTML
    catalogo_limpio = [(i[0], i[1], float(i[2]), i[3], int(i[4] or 0)) for i in catalogo]
    
    return render_template('admin.html', catalogo=catalogo_limpio, barberos=barberos, egresos=egresos)

# --- FUNCIONES DE STOCK Y CATALOGO ---
@app.route('/surtir_stock/<int:id>', methods=['POST'])
def surtir_stock(id):
    try:
        cantidad = int(request.form.get('cantidad_nueva', 0))
        if cantidad > 0:
            con = conectar_db(); cur = con.cursor()
            cur.execute("UPDATE catalogo SET stock = stock + ? WHERE id = ?", (cantidad, id))
            con.commit(); con.close()
            flash(f"✅ Se agregaron {cantidad} unidades al inventario.", "success")
    except:
        flash("❌ Error al actualizar inventario.", "error")
    return redirect(url_for('admin'))

@app.route('/agregar', methods=['POST'])
def agregar_producto():
    nombre = request.form['nombre']
    precio = request.form['precio']
    categoria = request.form['categoria']
    stock = request.form.get('stock', 0)
    
    con = conectar_db(); cur = con.cursor()
    cur.execute("INSERT INTO catalogo (nombre, precio, categoria, stock) VALUES (?, ?, ?, ?)", (nombre, precio, categoria, stock))
    con.commit(); con.close()
    flash("✅ Producto agregado correctamente.", "success")
    return redirect(url_for('admin'))

# --- FUNCIONES RESTANTES (Barberos, Egresos, Reportes, Cierre) ---
@app.route('/agregar_barbero', methods=['POST'])
def agregar_barbero():
    con = conectar_db(); cur = con.cursor()
    cur.execute("INSERT INTO barberos (nombre, comision_porcentaje) VALUES (?, ?)", (request.form['nombre'], request.form['comision']))
    con.commit(); con.close()
    return redirect(url_for('admin'))

@app.route('/editar_comision/<int:id>', methods=['POST'])
def editar_comision(id):
    nueva_comision = request.form.get('nueva_comision')
    
    if nueva_comision:
        con = conectar_db()
        cur = con.cursor()
        # Actualizamos solo el porcentaje del barbero seleccionado
        cur.execute("UPDATE barberos SET comision_porcentaje = ? WHERE id = ?", (nueva_comision, id))
        con.commit()
        con.close()
        flash("✅ Comisión actualizada correctamente.", "success")
        
    return redirect(url_for('admin'))

@app.route('/agregar_egreso', methods=['POST'])
def agregar_egreso():
    con = conectar_db(); cur = con.cursor()
    cur.execute("INSERT INTO egresos (descripcion, monto, categoria, fecha) VALUES (?, ?, ?, datetime('now', 'localtime'))", 
                (request.form['descripcion'], request.form['monto'], request.form['categoria']))
    con.commit(); con.close()
    return redirect(url_for('admin'))

@app.route('/eliminar_item/<int:id>')
def eliminar_item(id):
    con = conectar_db(); cur = con.cursor(); cur.execute("DELETE FROM catalogo WHERE id = ?", (id,)); con.commit(); con.close()
    return redirect(url_for('admin'))

@app.route('/eliminar_barbero/<int:id>')
def eliminar_barbero(id):
    con = conectar_db(); cur = con.cursor(); cur.execute("DELETE FROM barberos WHERE id = ?", (id,)); con.commit(); con.close()
    return redirect(url_for('admin'))

@app.route('/eliminar_egreso/<int:id>')
def eliminar_egreso(id):
    con = conectar_db(); cur = con.cursor(); cur.execute("DELETE FROM egresos WHERE id = ?", (id,)); con.commit(); con.close()
    return redirect(url_for('admin'))

@app.route('/cerrar_caja', methods=['POST'])
def cerrar_caja():
    con = conectar_db(); cur = con.cursor()
    cur.execute("SELECT SUM(monto) FROM ventas WHERE cerrado = 0")
    total = cur.fetchone()[0] or 0
    cur.execute("UPDATE ventas SET cerrado = 1 WHERE cerrado = 0")
    con.commit(); con.close()
    return f"Caja cerrada. Total corte: ${total:,.2f}"

@app.route('/reportes')
def reportes():
    mes = request.args.get('mes', datetime.now().strftime('%m'))
    anio = request.args.get('anio', datetime.now().strftime('%Y'))
    con = conectar_db(); cur = con.cursor()
    
    cur.execute("SELECT SUM(monto) FROM ventas WHERE strftime('%m', fecha)=? AND strftime('%Y', fecha)=?", (mes, anio))
    total_mes = cur.fetchone()[0] or 0
    
    cur.execute("SELECT SUM(monto) FROM egresos WHERE strftime('%m', fecha)=? AND strftime('%Y', fecha)=?", (mes, anio))
    total_egresos = cur.fetchone()[0] or 0
    
    cur.execute("""SELECT v.barbero_nombre, COUNT(v.id), SUM(v.monto), COALESCE(b.comision_porcentaje, 50) 
                   FROM ventas v JOIN catalogo c ON v.producto_id = c.id LEFT JOIN barberos b ON v.barbero_nombre = b.nombre 
                   WHERE c.categoria='Servicio' AND strftime('%m', v.fecha)=? AND strftime('%Y', v.fecha)=? GROUP BY v.barbero_nombre""", (mes, anio))
    datos_nomina = cur.fetchall()
    
    lista_pagos = [{'nombre': b[0], 'cantidad': b[1], 'generado': b[2], 'pago': b[2]*(b[3]/100)} for b in datos_nomina]
    pago_barberos = sum(p['pago'] for p in lista_pagos)
    ganancia_neta = total_mes - (total_egresos + pago_barberos)
    
    # Gráficas
    cur.execute("SELECT date(fecha), SUM(monto) FROM ventas WHERE strftime('%m', fecha)=? AND strftime('%Y', fecha)=? GROUP BY date(fecha) ORDER BY date(fecha)", (mes, anio))
    dv = cur.fetchall(); lb, vb = [d[0] for d in dv], [d[1] for d in dv]
    
    cur.execute("SELECT c.nombre, SUM(v.monto) FROM ventas v JOIN catalogo c ON v.producto_id = c.id WHERE strftime('%m', v.fecha)=? AND strftime('%Y', v.fecha)=? GROUP BY c.nombre ORDER BY SUM(v.monto) DESC", (mes, anio))
    dp = cur.fetchall(); lp, vp = [d[0] for d in dp], [d[1] for d in dp]
    
    con.close()
    return render_template('reportes.html', total_mes=total_mes, total_egresos=total_egresos, pago_barberos=pago_barberos, 
                           ganancia_neta=ganancia_neta, lista_pagos=lista_pagos, labels_barras=json.dumps(lb), valores_barras=json.dumps(vb), 
                           labels_pie=json.dumps(lp), valores_pie=json.dumps(vp), mes_actual=mes, anio_actual=anio)

@app.route('/apagar')
def apagar_servidor():

    html_despedida = """
    <div style="font-family: Arial; text-align: center; margin-top: 100px;">
        <h1 style="color: #28a745;">✅ Sistema apagado correctamente</h1>
        <p style="font-size: 18px; color: #666;">El motor de la base de datos se ha detenido.</p>
        <p style="font-size: 20px;"><b>Ya puedes cerrar esta ventana con seguridad. ¡Buen trabajo hoy!</b></p>
    </div>
    """
    from threading import Timer
    def apagar_proceso():
        os._exit(0) 
        
    Timer(1.0, apagar_proceso).start()
    
    return html_despedida

def abrir_navegador():
    webbrowser.open_new("http://127.0.0.1:5000")

    
if __name__ == '__main__':
    # Esperamos 1.5 segundos para asegurar que el servidor ya arrancó, y abrimos Chrome/Edge
    Timer(1.5, abrir_navegador).start()
    
    # Arrancamos Flask
    app.run(host='0.0.0.0', port=5000)