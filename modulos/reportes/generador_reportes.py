import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk
from modulos.utils.estilos_modernos import estilos
from data.models import get_connection   # <--- Conexión desde data.models
from datetime import datetime, timedelta
import os
import subprocess
import platform
import tempfile

# Configurar CustomTkinter
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class GeneradorReportes:
    def __init__(self, parent):
        self.parent = parent
        self.window = None
        
    def abrir_ventana_reportes(self):
        """Abrir ventana principal de reportes"""
        self.window = tk.Toplevel(self.parent)
        self.window.title("📊 Generador de Reportes")
        self.window.geometry("900x700+300+50")
        self.window.configure(bg=estilos.COLORS['bg_primary'])
        self.window.resizable(True, True)
        self.window.grab_set()
        self.window.focus_set()
        
        # Frame principal
        main_frame = tk.Frame(self.window, bg=estilos.COLORS['bg_primary'])
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Título
        title_label = tk.Label(main_frame, text="📊 Centro de Reportes", 
                              font=('Segoe UI', 20, 'bold'), 
                              bg=estilos.COLORS['bg_primary'],
                              fg=estilos.COLORS['primary'])
        title_label.pack(pady=(0, 20))
        
        # Frame de opciones
        options_frame = tk.LabelFrame(main_frame, text="🎯 Opciones de Reporte", 
                                     font=('Segoe UI', 14, 'bold'), 
                                     bg=estilos.COLORS['white'],
                                     fg=estilos.COLORS['primary'])
        options_frame.pack(fill='x', pady=(0, 20))
        
        # Tipo de reporte
        tk.Label(options_frame, text="📋 Tipo de Reporte:", 
                font=('Segoe UI', 12, 'bold'), 
                bg=estilos.COLORS['white'],
                fg=estilos.COLORS['dark']).grid(row=0, column=0, sticky='w', padx=10, pady=10)
        
        self.tipo_reporte = ttk.Combobox(options_frame, font=('Segoe UI', 11), 
                                        values=["Ventas Diarias", "Ventas por Período", 
                                               "Inventario Actual", "Productos Más Vendidos",
                                               "Clientes Registrados", "Proveedores",
                                               "Reporte Completo"], 
                                        state="readonly", width=25)
        self.tipo_reporte.set("Ventas Diarias")
        self.tipo_reporte.grid(row=0, column=1, padx=10, pady=10)
        
        # Período de fechas
        tk.Label(options_frame, text="📅 Fecha Inicio:", 
                font=('Segoe UI', 12, 'bold'), 
                bg=estilos.COLORS['white'],
                fg=estilos.COLORS['dark']).grid(row=1, column=0, sticky='w', padx=10, pady=5)
        
        self.fecha_inicio = tk.Entry(options_frame, font=('Segoe UI', 11), width=15)
        self.fecha_inicio.insert(0, datetime.now().strftime('%Y-%m-%d'))
        self.fecha_inicio.grid(row=1, column=1, sticky='w', padx=10, pady=5)
        
        tk.Label(options_frame, text="📅 Fecha Fin:", 
                font=('Segoe UI', 12, 'bold'), 
                bg=estilos.COLORS['white'],
                fg=estilos.COLORS['dark']).grid(row=2, column=0, sticky='w', padx=10, pady=5)
        
        self.fecha_fin = tk.Entry(options_frame, font=('Segoe UI', 11), width=15)
        self.fecha_fin.insert(0, datetime.now().strftime('%Y-%m-%d'))
        self.fecha_fin.grid(row=2, column=1, sticky='w', padx=10, pady=5)
        
        # Botones de acción
        buttons_frame = tk.Frame(options_frame, bg=estilos.COLORS['white'])
        buttons_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        btn_generar = ctk.CTkButton(buttons_frame, text="📊 Generar Reporte", 
                                   command=self.generar_reporte,
                                   width=150, height=40,
                                   font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                                   fg_color=estilos.COLORS['primary'],
                                   hover_color=estilos.COLORS['primary_dark'])
        btn_generar.pack(side='left', padx=5)
        
        btn_pdf = ctk.CTkButton(buttons_frame, text="📄 Exportar PDF", 
                               command=self.exportar_pdf,
                               width=150, height=40,
                               font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                               fg_color=estilos.COLORS['danger'],
                               hover_color="#dc3545")
        btn_pdf.pack(side='left', padx=5)
        
        btn_imprimir = ctk.CTkButton(buttons_frame, text="🖨️ Imprimir", 
                                    command=self.imprimir_reporte,
                                    width=150, height=40,
                                    font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                                    fg_color=estilos.COLORS['secondary'],
                                    hover_color="#059669")
        btn_imprimir.pack(side='left', padx=5)
        
        # Frame de vista previa
        preview_frame = tk.LabelFrame(main_frame, text="👁️ Vista Previa del Reporte", 
                                     font=('Segoe UI', 14, 'bold'), 
                                     bg=estilos.COLORS['white'],
                                     fg=estilos.COLORS['primary'])
        preview_frame.pack(fill='both', expand=True)
        
        # Área de texto con scroll
        text_frame = tk.Frame(preview_frame, bg=estilos.COLORS['white'])
        text_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        v_scrollbar = ttk.Scrollbar(text_frame, orient='vertical')
        v_scrollbar.pack(side='right', fill='y')
        
        h_scrollbar = ttk.Scrollbar(text_frame, orient='horizontal')
        h_scrollbar.pack(side='bottom', fill='x')
        
        self.texto_reporte = tk.Text(text_frame, 
                                    font=('Consolas', 10),
                                    bg='white',
                                    fg=estilos.COLORS['dark'],
                                    yscrollcommand=v_scrollbar.set,
                                    xscrollcommand=h_scrollbar.set,
                                    wrap='none')
        self.texto_reporte.pack(fill='both', expand=True)
        
        v_scrollbar.config(command=self.texto_reporte.yview)
        h_scrollbar.config(command=self.texto_reporte.xview)
        
        # Generar reporte inicial
        self.generar_reporte()
    
    # ---------------------------------------------------------------------------------
    def generar_reporte(self):
        """Generar el reporte seleccionado"""
        tipo = self.tipo_reporte.get()
        fecha_inicio = self.fecha_inicio.get()
        fecha_fin = self.fecha_fin.get()
        
        try:
            if tipo == "Ventas Diarias":
                contenido = self.reporte_ventas_diarias(fecha_inicio)
            elif tipo == "Ventas por Período":
                contenido = self.reporte_ventas_periodo(fecha_inicio, fecha_fin)
            elif tipo == "Inventario Actual":
                contenido = self.reporte_inventario()
            elif tipo == "Productos Más Vendidos":
                contenido = self.reporte_productos_vendidos()
            elif tipo == "Clientes Registrados":
                contenido = self.reporte_clientes()
            elif tipo == "Proveedores":
                contenido = self.reporte_proveedores()
            elif tipo == "Reporte Completo":
                contenido = self.reporte_completo()
            else:
                contenido = "Tipo de reporte no implementado"
            
            self.texto_reporte.delete('1.0', 'end')
            self.texto_reporte.insert('1.0', contenido)
            
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al generar reporte: {e}")
    
    # ---------------------------------------------------------------------------------
    def reporte_ventas_diarias(self, fecha):
        """Generar reporte de ventas diarias (usando ventas y detalle_ventas)"""
        conn = get_connection()
        if not conn:
            return "❌ Error de conexión a la base de datos"
        cursor = conn.cursor()
        try:
            # Obtener resumen de ventas del día
            cursor.execute("""
                SELECT v.id, v.numero_factura, v.cliente, v.fecha, v.hora, 
                       v.subtotal, v.iva, v.total, v.monto_recibido, v.cambio
                FROM ventas v
                WHERE v.fecha = %s
                ORDER BY v.hora
            """, (fecha,))
            ventas = cursor.fetchall()
            
            if not ventas:
                return f"No hay ventas registradas para la fecha {fecha}"
            
            total_ventas = sum(v[7] for v in ventas)  # total
            total_iva = sum(v[6] for v in ventas)     # iva
            total_subtotal = sum(v[5] for v in ventas) # subtotal
            
            reporte = f"""
╔══════════════════════════════════════════════════════════════╗
║                    📊 REPORTE DE VENTAS DIARIAS               ║
╠══════════════════════════════════════════════════════════════╣
║ Fecha: {fecha}                                    ║
║ Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}                     ║
╚══════════════════════════════════════════════════════════════╝

📈 RESUMEN EJECUTIVO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Total de Ventas: ${total_ventas:.2f}
• Número de Transacciones: {len(ventas)}
• Subtotal: ${total_subtotal:.2f}
• IVA Total: ${total_iva:.2f}
• Promedio por Venta: ${(total_ventas/len(ventas) if ventas else 0):.2f}

📋 DETALLE DE VENTAS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{'Factura':<10} {'Cliente':<20} {'Hora':<10} {'Subtotal':<12} {'IVA':<10} {'Total':<12}
{'-'*10} {'-'*20} {'-'*10} {'-'*12} {'-'*10} {'-'*12}
"""
            
            for venta in ventas:
                factura = str(venta[1])
                cliente = str(venta[2])[:20]
                hora = str(venta[4])[:5] if venta[4] else '--:--'
                subtotal = venta[5]
                iva = venta[6]
                total = venta[7]
                reporte += f"{factura:<10} {cliente:<20} {hora:<10} ${subtotal:<11.2f} ${iva:<9.2f} ${total:<11.2f}\n"
            
            # Obtener productos más vendidos del día
            cursor.execute("""
                SELECT d.producto, SUM(d.cantidad) as total_cant
                FROM detalle_ventas d
                JOIN ventas v ON d.venta_id = v.id
                WHERE v.fecha = %s
                GROUP BY d.producto
                ORDER BY total_cant DESC
                LIMIT 5
            """, (fecha,))
            top_productos = cursor.fetchall()
            
            if top_productos:
                reporte += f"""
{'-'*88}
🏆 TOP 5 PRODUCTOS MÁS VENDIDOS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{'Producto':<40} {'Cantidad':<15}
{'-'*40} {'-'*15}
"""
                for prod, cant in top_productos:
                    reporte += f"{prod[:40]:<40} {cant:<15}\n"
            
            reporte += f"""
{'-'*88}
📊 ESTADÍSTICAS ADICIONALES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Venta Máxima: ${max([v[7] for v in ventas]) if ventas else 0:.2f}
• Venta Mínima: ${min([v[7] for v in ventas]) if ventas else 0:.2f}
• Hora de Mayor Actividad: {self.obtener_hora_pico(ventas)}

═══════════════════════════════════════════════════════════════
                    Fin del Reporte
═══════════════════════════════════════════════════════════════
"""
            return reporte
            
        except Exception as e:
            return f"❌ Error al generar reporte de ventas: {e}"
        finally:
            cursor.close()
            conn.close()
    
    # ---------------------------------------------------------------------------------
    def reporte_ventas_periodo(self, fecha_inicio, fecha_fin):
        """Generar reporte de ventas por período"""
        conn = get_connection()
        if not conn:
            return "❌ Error de conexión a la base de datos"
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT v.fecha, COUNT(*) as num_ventas, SUM(v.total) as total_dia
                FROM ventas v
                WHERE v.fecha BETWEEN %s AND %s
                GROUP BY v.fecha
                ORDER BY v.fecha
            """, (fecha_inicio, fecha_fin))
            resultados = cursor.fetchall()
            
            if not resultados:
                return f"No hay ventas en el período {fecha_inicio} al {fecha_fin}"
            
            total_general = sum(r[2] for r in resultados)
            promedio_diario = total_general / len(resultados) if resultados else 0
            
            reporte = f"""
╔══════════════════════════════════════════════════════════════╗
║              📊 REPORTE DE VENTAS POR PERÍODO                 ║
╠══════════════════════════════════════════════════════════════╣
║ Período: {fecha_inicio} al {fecha_fin}                 ║
║ Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}                     ║
╚══════════════════════════════════════════════════════════════╝

📈 RESUMEN EJECUTIVO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Total de Ventas en el Período: ${total_general:.2f}
• Número de Días: {len(resultados)}
• Promedio Diario: ${promedio_diario:.2f}
• Día con Mayor Venta: {max(resultados, key=lambda x: x[2])[0] if resultados else 'N/A'}

📋 DETALLE POR DÍA:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{'Fecha':<15} {'Nº Ventas':<12} {'Total':<15}
{'-'*15} {'-'*12} {'-'*15}
"""
            for fecha, num, total in resultados:
                reporte += f"{fecha:<15} {num:<12} ${total:<14.2f}\n"
            
            reporte += f"""
{'-'*42}
TOTAL GENERAL: ${total_general:.2f}
═══════════════════════════════════════════════════════════════
                    Fin del Reporte
═══════════════════════════════════════════════════════════════
"""
            return reporte
        except Exception as e:
            return f"❌ Error al generar reporte: {e}"
        finally:
            cursor.close()
            conn.close()
    
    # ---------------------------------------------------------------------------------
    def reporte_inventario(self):
        """Generar reporte de inventario actual (usando articulos)"""
        conn = get_connection()
        if not conn:
            return "❌ Error de conexión a la base de datos"
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT codigo, articulo, precio, costo, stock, estado
                FROM articulos
                ORDER BY articulo
            """)
            productos = cursor.fetchall()
            
            if not productos:
                return "No hay artículos en el inventario"
            
            valor_total = sum(p[3] * p[4] for p in productos if p[4])  # costo * stock
            productos_bajo_stock = [p for p in productos if p[4] < 10]
            stock_total = sum(p[4] for p in productos if p[4])
            
            reporte = f"""
╔══════════════════════════════════════════════════════════════╗
║                    📦 REPORTE DE INVENTARIO                   ║
╠══════════════════════════════════════════════════════════════╣
║ Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}                     ║
╚══════════════════════════════════════════════════════════════╝

📈 RESUMEN EJECUTIVO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Total de Artículos: {len(productos)}
• Valor Total del Inventario: ${valor_total:.2f}
• Artículos con Stock Bajo (<10): {len(productos_bajo_stock)}
• Stock Total: {stock_total} unidades

📋 INVENTARIO DETALLADO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{'Código':<15} {'Artículo':<30} {'Stock':<8} {'Precio':<12} {'Costo':<12} {'Estado':<10}
{'-'*15} {'-'*30} {'-'*8} {'-'*12} {'-'*12} {'-'*10}
"""
            for codigo, articulo, precio, costo, stock, estado in productos:
                cod = str(codigo) if codigo else 'N/A'
                art = str(articulo)[:30]
                st = stock if stock else 0
                prec = precio if precio else 0
                cos = costo if costo else 0
                est = str(estado) if estado else 'N/A'
                estado_icon = "⚠️ BAJO" if st < 10 else "✅ OK"
                reporte += f"{cod:<15} {art:<30} {st:<8} ${prec:<11.2f} ${cos:<11.2f} {estado_icon:<10}\n"
            
            if productos_bajo_stock:
                reporte += f"""

⚠️ ARTÍCULOS CON STOCK BAJO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
                for p in productos_bajo_stock:
                    reporte += f"• {p[1]} - Stock: {p[4]} unidades\n"
            
            reporte += f"""

═══════════════════════════════════════════════════════════════
                    Fin del Reporte
═══════════════════════════════════════════════════════════════
"""
            return reporte
        except Exception as e:
            return f"❌ Error al generar reporte de inventario: {e}"
        finally:
            cursor.close()
            conn.close()
    
    # ---------------------------------------------------------------------------------
    def reporte_productos_vendidos(self):
        """Generar reporte de productos más vendidos (usando detalle_ventas)"""
        conn = get_connection()
        if not conn:
            return "❌ Error de conexión a la base de datos"
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT d.producto, SUM(d.cantidad) as total_vendido, 
                       SUM(d.subtotal) as total_ingresos
                FROM detalle_ventas d
                GROUP BY d.producto
                ORDER BY total_vendido DESC
                LIMIT 20
            """)
            resultados = cursor.fetchall()
            
            if not resultados:
                return "No hay productos vendidos aún"
            
            total_unidades = sum(r[1] for r in resultados)
            total_ingresos = sum(r[2] for r in resultados)
            
            reporte = f"""
╔══════════════════════════════════════════════════════════════╗
║                📊 PRODUCTOS MÁS VENDIDOS                      ║
╠══════════════════════════════════════════════════════════════╣
║ Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}                     ║
╚══════════════════════════════════════════════════════════════╝

📈 RESUMEN:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Total de Unidades Vendidas: {total_unidades}
• Total de Ingresos: ${total_ingresos:.2f}
• Número de Productos Diferentes: {len(resultados)}

📋 TOP 20 PRODUCTOS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{'#':<4} {'Producto':<40} {'Unidades':<12} {'Ingresos':<15}
{'-'*4} {'-'*40} {'-'*12} {'-'*15}
"""
            for i, (producto, unidades, ingresos) in enumerate(resultados, 1):
                reporte += f"{i:<4} {producto[:40]:<40} {unidades:<12} ${ingresos:<14.2f}\n"
            
            reporte += f"""
═══════════════════════════════════════════════════════════════
                    Fin del Reporte
═══════════════════════════════════════════════════════════════
"""
            return reporte
        except Exception as e:
            return f"❌ Error al generar reporte: {e}"
        finally:
            cursor.close()
            conn.close()
    
    # ---------------------------------------------------------------------------------
    def reporte_clientes(self):
        """Generar reporte de clientes"""
        conn = get_connection()
        if not conn:
            return "❌ Error de conexión a la base de datos"
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM clientes ORDER BY nombre")
            clientes = cursor.fetchall()
            
            if not clientes:
                return "No hay clientes registrados"
            
            reporte = f"""
╔══════════════════════════════════════════════════════════════╗
║                    👥 REPORTE DE CLIENTES                     ║
╠══════════════════════════════════════════════════════════════╣
║ Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}                     ║
╚══════════════════════════════════════════════════════════════╝

📈 RESUMEN:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Total de Clientes Registrados: {len(clientes)}

📋 LISTADO DE CLIENTES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{'ID':<5} {'Nombre':<25} {'Cédula':<15} {'Teléfono':<15} {'Email':<30}
{'-'*5} {'-'*25} {'-'*15} {'-'*15} {'-'*30}
"""
            for cliente in clientes:
                reporte += f"{cliente[0]:<5} {str(cliente[1])[:25]:<25} {str(cliente[2]):<15} {str(cliente[3]):<15} {str(cliente[5])[:30]:<30}\n"
            
            reporte += f"""
═══════════════════════════════════════════════════════════════
                    Fin del Reporte
═══════════════════════════════════════════════════════════════
"""
            return reporte
        except Exception as e:
            return f"❌ Error al generar reporte de clientes: {e}"
        finally:
            cursor.close()
            conn.close()
    
    # ---------------------------------------------------------------------------------
    def reporte_proveedores(self):
        """Generar reporte de proveedores"""
        conn = get_connection()
        if not conn:
            return "❌ Error de conexión a la base de datos"
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM proveedores ORDER BY empresa")
            proveedores = cursor.fetchall()
            
            if not proveedores:
                return "No hay proveedores registrados"
            
            reporte = f"""
╔══════════════════════════════════════════════════════════════╗
║                    🏢 REPORTE DE PROVEEDORES                  ║
╠══════════════════════════════════════════════════════════════╣
║ Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}                     ║
╚══════════════════════════════════════════════════════════════╝

📈 RESUMEN:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Total de Proveedores: {len(proveedores)}

📋 LISTADO DE PROVEEDORES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{'ID':<5} {'Empresa':<30} {'RIF':<15} {'Teléfono':<15} {'Email':<25}
{'-'*5} {'-'*30} {'-'*15} {'-'*15} {'-'*25}
"""
            for proveedor in proveedores:
                reporte += f"{proveedor[0]:<5} {str(proveedor[1])[:30]:<30} {str(proveedor[2]):<15} {str(proveedor[3]):<15} {str(proveedor[5])[:25]:<25}\n"
            
            reporte += f"""
═══════════════════════════════════════════════════════════════
                    Fin del Reporte
═══════════════════════════════════════════════════════════════
"""
            return reporte
        except Exception as e:
            return f"❌ Error al generar reporte de proveedores: {e}"
        finally:
            cursor.close()
            conn.close()
    
    # ---------------------------------------------------------------------------------
    def reporte_completo(self):
        """Generar reporte completo del sistema"""
        fecha_actual = datetime.now().strftime('%Y-%m-%d')
        
        reporte = f"""
╔══════════════════════════════════════════════════════════════╗
║                    📊 REPORTE COMPLETO DEL SISTEMA            ║
╠══════════════════════════════════════════════════════════════╣
║ Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}                     ║
╚══════════════════════════════════════════════════════════════╝

"""
        reporte += "1️⃣ " + "="*60 + "\n"
        reporte += "   VENTAS DEL DÍA\n"
        reporte += "="*60 + "\n"
        reporte += self.reporte_ventas_diarias(fecha_actual)
        
        reporte += "\n\n2️⃣ " + "="*60 + "\n"
        reporte += "   ESTADO DEL INVENTARIO\n"
        reporte += "="*60 + "\n"
        reporte += self.reporte_inventario()
        
        reporte += "\n\n3️⃣ " + "="*60 + "\n"
        reporte += "   CLIENTES REGISTRADOS\n"
        reporte += "="*60 + "\n"
        reporte += self.reporte_clientes()
        
        return reporte
    
    # ---------------------------------------------------------------------------------
    def obtener_hora_pico(self, ventas):
        """Obtener la hora de mayor actividad (usando campo hora de ventas)"""
        if not ventas:
            return "N/A"
        
        horas = {}
        for venta in ventas:
            if len(venta) > 4 and venta[4]:  # hora está en índice 4
                hora_str = str(venta[4])[:2]  # Primeros 2 caracteres de la hora
                horas[hora_str] = horas.get(hora_str, 0) + 1
        
        if horas:
            hora_pico = max(horas, key=horas.get)
            return f"{hora_pico}:00"
        return "N/A"
    
    # ---------------------------------------------------------------------------------
    def exportar_pdf(self):
        """Exportar reporte a archivo de texto"""
        try:
            contenido = self.texto_reporte.get('1.0', 'end-1c')
            if not contenido.strip():
                messagebox.showwarning("⚠️ Advertencia", "No hay contenido para exportar")
                return
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")],
                title="Guardar Reporte"
            )
            
            if filename:
                with open(filename, 'w', encoding='utf-8') as file:
                    file.write(contenido)
                messagebox.showinfo("✅ Éxito", f"Reporte guardado como:\n{filename}")
                
                if messagebox.askyesno("📄 Abrir Archivo", "¿Desea abrir el archivo guardado?"):
                    self.abrir_archivo(filename)
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al exportar: {e}")
    
    # ---------------------------------------------------------------------------------
    def imprimir_reporte(self):
        """Imprimir el reporte"""
        try:
            contenido = self.texto_reporte.get('1.0', 'end-1c')
            if not contenido.strip():
                messagebox.showwarning("⚠️ Advertencia", "No hay contenido para imprimir")
                return
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as temp_file:
                temp_file.write(contenido)
                temp_filename = temp_file.name
            
            if platform.system() == 'Windows':
                os.startfile(temp_filename, 'print')
            elif platform.system() == 'Darwin':
                subprocess.run(['lpr', temp_filename])
            else:
                subprocess.run(['lp', temp_filename])
            
            messagebox.showinfo("🖨️ Impresión", "Reporte enviado a la impresora")
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al imprimir: {e}")
    
    # ---------------------------------------------------------------------------------
    def abrir_archivo(self, filename):
        """Abrir archivo con la aplicación predeterminada"""
        try:
            if platform.system() == 'Windows':
                os.startfile(filename)
            elif platform.system() == 'Darwin':
                subprocess.run(['open', filename])
            else:
                subprocess.run(['xdg-open', filename])
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al abrir archivo: {e}")