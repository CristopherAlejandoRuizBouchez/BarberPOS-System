import sqlite3

def visualizar_base_de_datos():
    # Nos conectamos a la base de datos de la barbería
    conexion = sqlite3.connect('barberia.db')
    cursor = conexion.cursor()
    
    # Lista de las tablas que creaste en tu sistema
    tablas = ['catalogo', 'barberos', 'ventas', 'egresos']
    
    for tabla in tablas:
        print(f"\n{'='*40}")
        print(f"📦 TABLA: {tabla.upper()}")
        print(f"{'='*40}")
        
        try:
            cursor.execute(f"SELECT * FROM {tabla}")
            filas = cursor.fetchall()
            
            # Sacamos los nombres de las columnas automáticamente
            columnas = [descripcion[0] for descripcion in cursor.description]
            print(f"Columnas: {columnas}\n")
            
            if not filas:
                print("La tabla está vacía.")
            else:
                for fila in filas:
                    print(fila)
        except Exception as e:
            print(f"No se pudo leer la tabla {tabla} (quizás aún no la creas bien). Error: {e}")
            
    conexion.close()

if __name__ == '__main__':
    visualizar_base_de_datos()