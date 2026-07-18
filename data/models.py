# data/models.py
import mysql.connector
import sys

# Configuración de la base de datos
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '12345',
    'database': 'punto_venta',
    'raise_on_warnings': True
}

def get_connection():
    """Devuelve una conexión a MySQL"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as e:
        print(f"Error de conexión MySQL: {e}")
        return None

def crear_base_de_datos():
    try:
        # Conectar sin seleccionar base de datos
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="12345"
        )
        cursor = conn.cursor()

        # Crear la base de datos si no existe
        cursor.execute("CREATE DATABASE IF NOT EXISTS punto_venta")
        cursor.execute("USE punto_venta")

        # ==================== TABLAS PRINCIPALES ====================

        # 1. Usuarios (login)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        # 2. Configuración del sistema
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS configuracion_sistema (
                id INT AUTO_INCREMENT PRIMARY KEY,
                clave VARCHAR(50) NOT NULL UNIQUE,
                valor TEXT NOT NULL,
                descripcion VARCHAR(255),
                fecha_modificacion DATETIME DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        # 3. Historial de actividades
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS historial_actividades (
                id INT AUTO_INCREMENT PRIMARY KEY,
                fecha DATE NOT NULL,
                hora TIME NOT NULL,
                usuario VARCHAR(50) DEFAULT 'Sistema',
                modulo VARCHAR(50) NOT NULL,
                accion VARCHAR(100) NOT NULL,
                descripcion TEXT,
                detalles TEXT,
                tipo VARCHAR(10) DEFAULT 'INFO'
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        # 4. Artículos / Inventario
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS articulos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                codigo VARCHAR(50) UNIQUE,
                articulo VARCHAR(255) NOT NULL,
                precio DECIMAL(10,2) NOT NULL,
                costo DECIMAL(10,2) NOT NULL,
                stock INT NOT NULL DEFAULT 0,
                estado VARCHAR(20) DEFAULT 'activo',
                imagen_path VARCHAR(255)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        # 5. Clientes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clientes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(255) NOT NULL,
                cedula VARCHAR(20) UNIQUE,
                celular VARCHAR(20),
                direccion TEXT,
                correo VARCHAR(255)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        # 6. Proveedores
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS proveedores (
                id INT AUTO_INCREMENT PRIMARY KEY,
                empresa VARCHAR(255) NOT NULL,
                rif VARCHAR(50) UNIQUE NOT NULL,
                celular VARCHAR(20),
                direccion TEXT,
                correo VARCHAR(255)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        # 7. Pedidos a proveedores (cabecera)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pedidos_proveedor (
                id INT AUTO_INCREMENT PRIMARY KEY,
                proveedor_nombre VARCHAR(255) NOT NULL,
                fecha DATETIME NOT NULL,
                estado VARCHAR(20) DEFAULT 'Pendiente',
                total DECIMAL(10,2) DEFAULT 0.00,
                observaciones TEXT
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        # 8. Detalle de pedidos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pedidos_detalle (
                id INT AUTO_INCREMENT PRIMARY KEY,
                pedido_id INT NOT NULL,
                producto_codigo VARCHAR(50) NOT NULL,
                producto_nombre VARCHAR(255) NOT NULL,
                cantidad INT NOT NULL,
                precio_unitario DECIMAL(10,2) DEFAULT 0.00,
                subtotal DECIMAL(10,2) DEFAULT 0.00,
                FOREIGN KEY (pedido_id) REFERENCES pedidos_proveedor(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        # 9. Ventas (cabecera) - ESTRUCTURA MODERNA
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ventas (
                id INT AUTO_INCREMENT PRIMARY KEY,
                numero_factura INT NOT NULL,
                cliente VARCHAR(255) NOT NULL,
                fecha DATE NOT NULL,
                hora TIME NOT NULL,
                subtotal DECIMAL(10,2) DEFAULT 0.00,
                iva DECIMAL(10,2) DEFAULT 0.00,
                total DECIMAL(10,2) DEFAULT 0.00,
                monto_recibido DECIMAL(10,2) DEFAULT 0.00,
                cambio DECIMAL(10,2) DEFAULT 0.00,
                estado VARCHAR(20) DEFAULT 'completada'
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        # 10. Detalle de ventas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS detalle_ventas (
                id INT AUTO_INCREMENT PRIMARY KEY,
                venta_id INT NOT NULL,
                producto VARCHAR(255) NOT NULL,
                precio_unitario DECIMAL(10,2) NOT NULL,
                cantidad INT NOT NULL,
                subtotal DECIMAL(10,2) NOT NULL,
                FOREIGN KEY (venta_id) REFERENCES ventas(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        # ==================== DATOS POR DEFECTO ====================

        # Usuario administrador (admin / admin123)
        cursor.execute("""
            INSERT INTO usuarios (username, password)
            SELECT 'admin', SHA2('admin123', 256)
            WHERE NOT EXISTS (SELECT 1 FROM usuarios WHERE username = 'admin')
        """)

        # Configuraciones por defecto
        config_defaults = [
            ('moneda_principal', 'USD', 'Moneda principal del sistema (USD/VES)'),
            ('tasa_cambio', '36.50', 'Tasa de cambio USD a VES'),
            ('simbolo_ves', 'Bs.', 'Símbolo para Bolívares'),
            ('simbolo_usd', '$', 'Símbolo para Dólares'),
            ('mostrar_ambas_monedas', '1', 'Mostrar precios en ambas monedas (1=Sí, 0=No)'),
            ('nombre_empresa', 'Mi Tienda', 'Nombre de la empresa'),
            ('direccion_empresa', 'Caracas, Venezuela', 'Dirección de la empresa'),
            ('telefono_empresa', '+58-212-1234567', 'Teléfono de la empresa'),
            ('rif_empresa', 'J-00000000-0', 'RIF de la empresa')
        ]
        for clave, valor, desc in config_defaults:
            cursor.execute("""
                INSERT INTO configuracion_sistema (clave, valor, descripcion)
                SELECT %s, %s, %s
                WHERE NOT EXISTS (SELECT 1 FROM configuracion_sistema WHERE clave = %s)
            """, (clave, valor, desc, clave))

        conn.commit()
        conn.close()
        print("✅ Base de datos MySQL creada/actualizada correctamente.")

    except mysql.connector.Error as e:
        print(f"❌ Error: {e}")
        sys.exit()
        

if __name__ == "__main__":
    print("Creando base de datos MySQL...")
    crear_base_de_datos()