import sqlite3
import random
from datetime import datetime, timedelta

def simular():
    conexion = sqlite3.connect('barberia.db')
    cursor = conexion.cursor()

    # Obtenemos los IDs de los productos que ya tienes
    cursor.execute("SELECT id, precio FROM catalogo")
    items = cursor.fetchall()

    if not items:
        print(" Primero agrega productos en el panel de Admin.")
        return

    print(" Generando 50 ventas aleatorias...")

    for _ in range(50):
        item = random.choice(items)
        item_id = item[0]
        precio = item[1]
        
        # Generar una fecha aleatoria en los últimos 15 días
        dias_atras = random.randint(0, 15)
        fecha = (datetime.now() - timedelta(days=dias_atras)).strftime('%Y-%m-%d %H:%M:%S')
        
        metodo = random.choice(['Efectivo', 'Transferencia'])
        
        cursor.execute("""
            INSERT INTO ventas (producto_id, monto, metodo_pago, fecha) 
            VALUES (?, ?, ?, ?)
        """, (item_id, precio, metodo, fecha))

    conexion.commit()
    conexion.close()
    print(" ¡Listo! 50 ventas agregadas. Revisa tus gráficas ahora.")

if __name__ == "__main__":
    simular()