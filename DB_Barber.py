import sqlite3

def inicializar_db():
    conexion = sqlite3.connect('barberia.db')
    cursor = conexion.cursor()

    # 1. TABLA CATÁLOGO (Servicios y Productos)
    # Agregamos stock directamente en la definición inicial
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS catalogo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            precio REAL NOT NULL,
            categoria TEXT NOT NULL,
            stock INTEGER DEFAULT 0
        )
    ''')

    # 2. TABLA VENTAS (Incluye Cierre de Caja y Método de Pago)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            producto_id INTEGER,
            monto REAL,
            fecha TEXT,
            barbero_nombre TEXT,
            cerrado INTEGER DEFAULT 0,
            metodo_pago TEXT DEFAULT 'Efectivo'
        )
    ''')

    # 3. TABLA EGRESOS (Gastos como Luz, Renta, Insumos)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS egresos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descripcion TEXT,
            monto REAL,
            categoria TEXT,
            fecha TEXT
        )
    ''')

    # 4. TABLA BARBEROS (Donde están Richy y Cristo con sus comisiones)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS barberos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            comision_porcentaje INTEGER DEFAULT 50
        )
    ''')

    # --- SECCIÓN DE ACTUALIZACIÓN DE COLUMNAS (MANTENIMIENTO) ---
    # Mantenemos tu lógica de bucle para VENTAS y añadimos CATÁLOGO
    
    # Actualización para VENTAS
    columnas_ventas = [
        ("barbero_nombre", "TEXT DEFAULT 'General'"),
        ("cerrado", "INTEGER DEFAULT 0"),
        ("metodo_pago", "TEXT DEFAULT 'Efectivo'")
    ]

    for columna, tipo in columnas_ventas:
        try:
            cursor.execute(f"ALTER TABLE ventas ADD COLUMN {columna} {tipo}")
        except sqlite3.OperationalError:
            pass # La columna ya existe

    # Actualización para CATÁLOGO (Punto 3: Stock)
    try:
        cursor.execute("ALTER TABLE catalogo ADD COLUMN stock INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass # La columna ya existe
    
    conexion.commit()
    conexion.close()
    print("🚀 Base de datos lista, actualizada y con soporte de Stock.")

if __name__ == "__main__":
    inicializar_db()