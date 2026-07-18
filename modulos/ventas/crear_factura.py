import os
import datetime
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from tkinter import messagebox
from data.models import get_connection
from modulos.ventas.obtener_numero_factura import obtener_numero_factura_actual
from modulos.configuracion.gestor_configuracion import obtener_configuracion


def generar_factura(total_venta, cliente, productos_seleccionados=None, venta_id=None):
    """
    Genera una factura en PDF con los datos de la venta.
    
    Args:
        total_venta (float): Total de la venta.
        cliente (str): Nombre del cliente.
        productos_seleccionados (list): Lista de tuplas (producto, cantidad, precio_unitario, subtotal).
        venta_id (int): ID de la venta para obtener detalles desde la BD (opcional).
    """
    if productos_seleccionados is None:
        productos_seleccionados = []
    
    # Si no se pasan productos pero se tiene venta_id, obtener desde la BD
    if not productos_seleccionados and venta_id:
        productos_seleccionados = obtener_detalle_venta(venta_id)
    
    if not productos_seleccionados:
        messagebox.showerror("Error", "No hay productos para la factura")
        return
    
    numero_factura = obtener_numero_factura_actual()
    
    try:
        # Crear carpeta de facturas si no existe
        factura_dir = os.path.abspath("facturas")
        if not os.path.exists(factura_dir):
            os.makedirs(factura_dir)
        
        factura_nombre = f"Factura_{numero_factura}.pdf"
        factura_path = os.path.join(factura_dir, factura_nombre)
        
        # Configurar página A4
        c = canvas.Canvas(factura_path, pagesize=A4)
        ancho, alto = A4  # 595 x 842 puntos
        
        # ==================== DATOS DE LA EMPRESA ====================
        empresa_nombre = obtener_configuracion('nombre_empresa', 'Mi Tienda')
        empresa_direccion = obtener_configuracion('direccion_empresa', 'Caracas, Venezuela')
        empresa_telefono = obtener_configuracion('telefono_empresa', '+58-212-1234567')
        empresa_rif = obtener_configuracion('rif_empresa', 'J-00000000-0')
        empresa_email = "info@marketsystem.com"
        empresa_website = "www.marketsystem.com"
        
        # ==================== ENCABEZADO ====================
        c.setFont("Helvetica-Bold", 18)
        c.setFillColor(colors.darkblue)
        c.drawCentredString(ancho/2, alto - 80, "FACTURA DE SERVICIOS")
        
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, alto - 120, f"{empresa_nombre}")
        c.setFont("Helvetica", 11)
        c.drawString(50, alto - 140, f"RIF: {empresa_rif}")
        c.drawString(50, alto - 160, f"Dirección: {empresa_direccion}")
        c.drawString(50, alto - 180, f"Teléfono: {empresa_telefono}")
        c.drawString(50, alto - 200, f"Email: {empresa_email}")
        c.drawString(50, alto - 220, f"Website: {empresa_website}")
        
        # Línea separadora
        c.setLineWidth(0.5)
        c.setStrokeColor(colors.gray)
        c.line(50, alto - 230, ancho - 50, alto - 230)
        
        # Número de factura y fecha
        c.setFont("Helvetica", 11)
        c.drawString(50, alto - 255, f"Número de Factura: {numero_factura}")
        c.drawString(350, alto - 255, f"Fecha: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        # Cliente
        c.drawString(50, alto - 275, f"Cliente: {cliente}")
        
        # Línea separadora
        c.line(50, alto - 285, ancho - 50, alto - 285)
        
        # ==================== TABLA DE PRODUCTOS ====================
        y_offset = alto - 315
        c.setFont("Helvetica-Bold", 12)
        c.drawString(70, y_offset, "Producto")
        c.drawString(270, y_offset, "Cantidad")
        c.drawString(370, y_offset, "Precio")
        c.drawString(470, y_offset, "Total")
        
        c.line(50, y_offset - 10, ancho - 50, y_offset - 10)
        y_offset -= 30
        c.setFont("Helvetica", 11)
        
        # Dibujar cada producto
        for item in productos_seleccionados:
            # item puede ser tupla con diferentes formatos según cómo se llame
            if len(item) == 4:
                # (producto, cantidad, precio_unitario, subtotal)
                producto, cantidad, precio_unitario, subtotal = item
            elif len(item) == 5:
                # (id, producto, cantidad, precio_unitario, subtotal)
                _, producto, cantidad, precio_unitario, subtotal = item
            else:
                # Si viene de detalle_ventas: (producto, precio_unitario, cantidad, subtotal)
                producto, precio_unitario, cantidad, subtotal = item
            
            # Truncar nombre si es muy largo
            if len(producto) > 30:
                producto = producto[:27] + "..."
            
            c.drawString(70, y_offset, producto)
            c.drawString(270, y_offset, str(cantidad))
            c.drawString(370, y_offset, f"${precio_unitario:,.2f}")
            c.drawString(470, y_offset, f"${subtotal:,.2f}")
            y_offset -= 22
            
            # Si nos salimos de la página, agregar nueva página
            if y_offset < 100:
                c.showPage()
                y_offset = alto - 100
                c.setFont("Helvetica", 11)
        
        # Línea final
        c.line(50, y_offset, ancho - 50, y_offset)
        y_offset -= 30
        
        # ==================== TOTAL ====================
        c.setFont("Helvetica-Bold", 14)
        c.setFillColor(colors.darkblue)
        c.drawString(50, y_offset, f"Total a Pagar: ${total_venta:,.2f}")
        c.setFillColor(colors.black)
        
        y_offset -= 20
        c.line(50, y_offset, ancho - 50, y_offset)
        
        # ==================== PIE DE PÁGINA ====================
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(ancho/2, y_offset - 60, "¡Gracias por tu compra, vuelve pronto!")
        
        y_offset -= 100
        c.setFont("Helvetica", 9)
        c.drawString(50, y_offset, "Términos y Condiciones:")
        c.drawString(50, y_offset - 20, "1. Los productos comprados no tienen devolución.")
        c.drawString(50, y_offset - 40, "2. Conserve esta factura como comprobante de su compra.")
        c.drawString(50, y_offset - 60, "3. Para más información visite nuestro sitio web o contacte a servicio al cliente.")
        
        # ==================== GUARDAR ====================
        c.save()
        messagebox.showinfo("✅ Factura Generada", f"Factura guardada en:\n{factura_path}")
        os.startfile(factura_path)
        
    except Exception as e:
        messagebox.showerror("❌ Error", f"No se pudo generar la factura: {e}")


def obtener_detalle_venta(venta_id):
    """
    Obtiene los productos de una venta desde la base de datos MySQL.
    
    Args:
        venta_id (int): ID de la venta.
    
    Returns:
        list: Lista de tuplas (producto, precio_unitario, cantidad, subtotal)
    """
    conn = get_connection()
    if not conn:
        return []
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT producto, precio_unitario, cantidad, subtotal
            FROM detalle_ventas
            WHERE venta_id = %s
        """, (venta_id,))
        resultados = cursor.fetchall()
        return resultados
    except Exception as e:
        print(f"Error al obtener detalle de venta: {e}")
        return []
    finally:
        cursor.close()
        conn.close()


def actualizar_numero_factura(nuevo_numero):
    """
    Actualiza el número de factura en la base de datos (si se usa una tabla de secuencia).
    Esta función es opcional; se puede implementar si se necesita.
    """
    conn = get_connection()
    if not conn:
        return
    cursor = conn.cursor()
    try:
        # Asumiendo que existe una tabla 'configuracion' con clave 'ultima_factura'
        cursor.execute("""
            INSERT INTO configuracion_sistema (clave, valor, descripcion)
            VALUES ('ultima_factura', %s, 'Último número de factura generado')
            ON DUPLICATE KEY UPDATE valor = VALUES(valor)
        """, (str(nuevo_numero),))
        conn.commit()
    except Exception as e:
        print(f"Error al actualizar número de factura: {e}")
    finally:
        cursor.close()
        conn.close()