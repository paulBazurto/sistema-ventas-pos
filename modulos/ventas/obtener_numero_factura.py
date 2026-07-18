from data.models import get_connection

def obtener_numero_factura_actual():
    """
    Obtiene el número de factura más reciente y devuelve el siguiente.
    Si no hay facturas, devuelve 1.
    """
    conn = get_connection()
    if not conn:
        return 1

    cursor = conn.cursor()
    try:
        # La tabla 'ventas' tiene la columna 'numero_factura'
        cursor.execute("SELECT MAX(numero_factura) FROM ventas")
        resultado = cursor.fetchone()
        ultimo = resultado[0] if resultado and resultado[0] is not None else 0
        return ultimo + 1
    except Exception as e:
        print(f"Error obteniendo el número de factura: {e}")
        return 1
    finally:
        cursor.close()
        conn.close()