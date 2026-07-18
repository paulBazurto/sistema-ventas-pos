import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import datetime
import threading
from PIL import Image, ImageTk
import sys
import os

from modulos.ventas.crear_factura import generar_factura
from modulos.ventas.obtener_numero_factura import obtener_numero_factura_actual
from data.models import get_connection
from modulos.configuracion.gestor_configuracion import obtener_configuracion


class VentasModerna(tk.Frame):
    """Versión moderna de la interfaz de ventas con mejor diseño"""
    
    COLORS = {
        'primary': '#2c3e50',
        'secondary': '#3498db',
        'success': '#27ae60',
        'warning': '#f39c12',
        'danger': '#e74c3c',
        'light': '#ecf0f1',
        'white': '#ffffff',
        'dark': '#34495e',
        'accent': '#9b59b6'
    }

    def __init__(self, padre):
        super().__init__(padre)
        self.configure(bg=self.COLORS['light'])
        self.numero_factura = obtener_numero_factura_actual()
        self.productos_seleccionados = []
        self.setup_styles()
        self.widgets_modernos()
        self.timer_producto = None
        self.timer_cliente = None
        
        self.cargar_productos()
        self.cargar_clientes()
        self.actualizar_hora()
    
    # ==================== ESTILOS Y DISEÑO ====================
    def setup_styles(self):
        style = ttk.Style()
        style.configure('Modern.TLabel', 
                       background=self.COLORS['light'],
                       foreground=self.COLORS['primary'],
                       font=('Segoe UI', 11, 'bold'))
        style.configure('Modern.TButton',
                       font=('Segoe UI', 10, 'bold'),
                       padding=(20, 10))
        style.configure('Modern.TEntry',
                       font=('Segoe UI', 11),
                       fieldbackground=self.COLORS['white'])
        style.configure('Modern.TCombobox',
                       font=('Segoe UI', 11),
                       fieldbackground=self.COLORS['white'])

    def crear_frame_moderno(self, parent, title, x, y, width, height):
        shadow_frame = tk.Frame(parent, bg='#bdc3c7', height=height+2, width=width+2)
        shadow_frame.place(x=x+2, y=y+2)
        
        main_frame = tk.Frame(parent, bg=self.COLORS['white'], 
                             relief='flat', bd=1, highlightbackground=self.COLORS['primary'],
                             highlightthickness=1)
        main_frame.place(x=x, y=y, width=width, height=height)
        
        title_frame = tk.Frame(main_frame, bg=self.COLORS['primary'], height=40)
        title_frame.pack(fill='x', side='top')
        tk.Label(title_frame, text=title, 
                bg=self.COLORS['primary'], fg=self.COLORS['white'],
                font=('Segoe UI', 12, 'bold')).pack(pady=8)
        
        content_frame = tk.Frame(main_frame, bg=self.COLORS['white'])
        content_frame.pack(fill='both', expand=True, padx=15, pady=15)
        return content_frame

    def crear_boton_moderno(self, parent, text, command, color='secondary', x=0, y=0, width=150, height=40):
        btn_frame = tk.Frame(parent, bg=self.COLORS['white'])
        btn_frame.place(x=x, y=y, width=width, height=height)
        btn = tk.Button(btn_frame, text=text, command=command,
                       bg=self.COLORS[color], fg=self.COLORS['white'],
                       font=('Segoe UI', 10, 'bold'), relief='flat',
                       cursor='hand2', bd=0)
        btn.pack(fill='both', expand=True)
        
        def on_enter(e):
            btn.configure(bg=self.ajustar_color(self.COLORS[color], -20))
        def on_leave(e):
            btn.configure(bg=self.COLORS[color])
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        return btn

    def ajustar_color(self, color, amount):
        color = color.lstrip('#')
        rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        rgb = tuple(max(0, min(255, c + amount)) for c in rgb)
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"

    # ==================== INTERFAZ PRINCIPAL ====================
    def widgets_modernos(self):
        title_frame = tk.Frame(self, bg=self.COLORS['primary'], height=60)
        title_frame.pack(fill='x', side='top')
        tk.Label(title_frame, text="💰 Sistema de Ventas", 
                bg=self.COLORS['primary'], fg=self.COLORS['white'],
                font=('Segoe UI', 16, 'bold')).pack(pady=15)
        
        content_frame = tk.Frame(self, bg=self.COLORS['light'])
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        info_frame = self.crear_frame_moderno(content_frame, "📋 Información de Venta", 
                                            0, 0, 1350, 220)
        
        tk.Label(info_frame, text="👤 Cliente:", 
                font=('Segoe UI', 11, 'bold'), bg=self.COLORS['white'],
                fg=self.COLORS['primary']).place(x=10, y=20)
        self.entry_cliente = ttk.Combobox(info_frame, font=('Segoe UI', 11), style='Modern.TCombobox')
        self.entry_cliente.place(x=120, y=18, width=280, height=35)
        self.entry_cliente.bind('<KeyRelease>', self.filtrar_clientes)
        
        tk.Label(info_frame, text="📊 Código de Barras:", 
                font=('Segoe UI', 11, 'bold'), bg=self.COLORS['white'],
                fg=self.COLORS['primary']).place(x=10, y=70)
        self.entry_codigo = ttk.Entry(info_frame, font=('Segoe UI', 11), style='Modern.TEntry')
        self.entry_codigo.place(x=170, y=68, width=220, height=35)
        self.entry_codigo.bind('<KeyRelease>', self.buscar_por_codigo)
        self.entry_codigo.bind('<Return>', self.buscar_por_codigo)
        
        tk.Label(info_frame, text="📦 Producto:", 
                font=('Segoe UI', 11, 'bold'), bg=self.COLORS['white'],
                fg=self.COLORS['primary']).place(x=410, y=70)
        self.entry_producto = ttk.Combobox(info_frame, font=('Segoe UI', 11), style='Modern.TCombobox', state='normal')
        self.entry_producto.place(x=510, y=68, width=230, height=35)
        self.entry_producto.bind("<<ComboboxSelected>>", self.actualizar_stock)
        self.entry_producto.bind('<Button-1>', self.mostrar_productos)
        self.entry_producto.bind('<Return>', self.actualizar_stock)
        
        tk.Label(info_frame, text="🔢 Cantidad:", 
                font=('Segoe UI', 11, 'bold'), bg=self.COLORS['white'],
                fg=self.COLORS['primary']).place(x=450, y=20)
        self.entry_cantidad = ttk.Entry(info_frame, font=('Segoe UI', 11), style='Modern.TEntry')
        self.entry_cantidad.place(x=550, y=18, width=120, height=35)
        
        self.label_stock = tk.Label(info_frame, text="📊 Stock: --", 
                                   font=('Segoe UI', 11, 'bold'), bg=self.COLORS['white'],
                                   fg=self.COLORS['success'])
        self.label_stock.place(x=760, y=70)
        
        tk.Label(info_frame, text="🧾 Factura N°:", 
                font=('Segoe UI', 11, 'bold'), bg=self.COLORS['white'],
                fg=self.COLORS['primary']).place(x=900, y=20)
        self.label_numero_factura = tk.Label(info_frame, text=f"{self.numero_factura}", 
                                           font=('Segoe UI', 14, 'bold'), bg=self.COLORS['white'],
                                           fg=self.COLORS['accent'])
        self.label_numero_factura.place(x=1030, y=18)
        
        fecha_actual = datetime.datetime.now().strftime("%d/%m/%Y")
        tk.Label(info_frame, text="📅 Fecha:", 
                font=('Segoe UI', 11, 'bold'), bg=self.COLORS['white'],
                fg=self.COLORS['primary']).place(x=1150, y=20)
        self.label_fecha = tk.Label(info_frame, text=fecha_actual, 
                                   font=('Segoe UI', 12, 'bold'), bg=self.COLORS['white'],
                                   fg=self.COLORS['dark'], width=12, anchor='w')
        self.label_fecha.place(x=1210, y=20, width=100)
        
        hora_actual = datetime.datetime.now().strftime("%H:%M:%S")
        tk.Label(info_frame, text="🕐 Hora:", 
                font=('Segoe UI', 11, 'bold'), bg=self.COLORS['white'],
                fg=self.COLORS['primary']).place(x=1150, y=70)
        self.label_hora = tk.Label(info_frame, text=hora_actual, 
                                  font=('Segoe UI', 12, 'bold'), bg=self.COLORS['white'],
                                  fg=self.COLORS['dark'], width=12, anchor='w')
        self.label_hora.place(x=1210, y=70, width=100)
        
        self.crear_boton_moderno(info_frame, "➕ Agregar Producto", 
                                self.agregar_producto, 'success', 950, 60, 180, 40)
        
        productos_frame = self.crear_frame_moderno(content_frame, "🛒 Productos Seleccionados", 
                                                 0, 240, 850, 480)
        self.tree_productos = ttk.Treeview(productos_frame, 
                                         columns=("Producto", "Precio", "Cantidad", "Total"), 
                                         show="headings", height=20)
        self.tree_productos.heading("Producto", text="Producto")
        self.tree_productos.heading("Precio", text="Precio")
        self.tree_productos.heading("Cantidad", text="Cantidad")
        self.tree_productos.heading("Total", text="Total")
        self.tree_productos.column("Producto", width=300, anchor="w")
        self.tree_productos.column("Precio", width=100, anchor="center")
        self.tree_productos.column("Cantidad", width=100, anchor="center")
        self.tree_productos.column("Total", width=120, anchor="center")
        
        scrollbar_productos = ttk.Scrollbar(productos_frame, orient="vertical", 
                                          command=self.tree_productos.yview)
        self.tree_productos.configure(yscrollcommand=scrollbar_productos.set)
        self.tree_productos.pack(side="left", fill="both", expand=True)
        scrollbar_productos.pack(side="right", fill="y")
        
        totales_frame = self.crear_frame_moderno(content_frame, "💰 Resumen de Venta", 
                                               860, 240, 500, 480)
        self.label_sub_total = tk.Label(totales_frame, text='Subtotal: $0.00', 
                                       font=('Segoe UI', 14, 'bold'), bg=self.COLORS['white'],
                                       fg=self.COLORS['primary'])
        self.label_sub_total.pack(pady=10)
        self.label_iva = tk.Label(totales_frame, text='IVA (15%): $0.00', 
                                 font=('Segoe UI', 12), bg=self.COLORS['white'],
                                 fg=self.COLORS['dark'])
        self.label_iva.pack(pady=5)
        self.label_precio_total = tk.Label(totales_frame, text='TOTAL: $0.00', 
                                          font=('Segoe UI', 16, 'bold'), bg=self.COLORS['white'],
                                          fg=self.COLORS['success'])
        self.label_precio_total.pack(pady=15)
        
        botones_frame = tk.Frame(totales_frame, bg=self.COLORS['white'])
        botones_frame.pack(fill='x', pady=20, padx=10)
        
        btn_procesar = tk.Button(botones_frame, text="💰 PROCESAR PAGO", 
                               command=self.abrir_modal_pago,
                               bg=self.COLORS['success'], fg=self.COLORS['white'],
                               font=('Segoe UI', 14, 'bold'),
                               relief='flat', cursor='hand2', bd=0, pady=15)
        btn_procesar.pack(fill='x', pady=(0, 10))
        btn_procesar.bind("<Enter>", lambda e: btn_procesar.configure(bg='#16a34a'))
        btn_procesar.bind("<Leave>", lambda e: btn_procesar.configure(bg=self.COLORS['success']))
        
        botones_secundarios = tk.Frame(botones_frame, bg=self.COLORS['white'])
        botones_secundarios.pack(fill='x')
        
        btn_ver_ventas = tk.Button(botones_secundarios, text="📊 Ver Ventas", 
                                 command=self.ver_ventas_realizadas,
                                 bg=self.COLORS['secondary'], fg=self.COLORS['white'],
                                 font=('Segoe UI', 10, 'bold'), relief='flat', cursor='hand2', bd=0)
        btn_ver_ventas.pack(side='left', fill='x', expand=True, padx=(0, 5))
        btn_ver_ventas.bind("<Enter>", lambda e: btn_ver_ventas.configure(bg='#0ea5e9'))
        btn_ver_ventas.bind("<Leave>", lambda e: btn_ver_ventas.configure(bg=self.COLORS['secondary']))
        
        btn_limpiar = tk.Button(botones_secundarios, text="🗑️ Limpiar", 
                              command=self.limpiar_venta,
                              bg=self.COLORS['warning'], fg=self.COLORS['white'],
                              font=('Segoe UI', 10, 'bold'), relief='flat', cursor='hand2', bd=0)
        btn_limpiar.pack(side='right', fill='x', expand=True, padx=(5, 0))
        btn_limpiar.bind("<Enter>", lambda e: btn_limpiar.configure(bg='#d97706'))
        btn_limpiar.bind("<Leave>", lambda e: btn_limpiar.configure(bg=self.COLORS['warning']))

    # ==================== CARGA DE DATOS (MYSQL) ====================
    def cargar_productos(self):
        print("🔄 INICIANDO CARGA DE PRODUCTOS...")
        conn = get_connection()
        if not conn:
            messagebox.showerror("Error", "No se pudo conectar a la base de datos")
            return
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM articulos")
            count = cursor.fetchone()[0]
            if count == 0:
                productos_ejemplo = [
                    ("7501234567890", "Producto Ejemplo 1", 10.50, 8.00, 25, "activo", None),
                    ("7501234567891", "Producto Ejemplo 2", 15.75, 12.00, 30, "activo", None),
                    ("7501234567892", "Producto Ejemplo 3", 8.25, 6.50, 15, "activo", None),
                    ("7501234567893", "Producto Ejemplo 4", 22.00, 18.00, 10, "activo", None),
                    ("7501234567894", "Producto Ejemplo 5", 12.99, 10.00, 20, "activo", None)
                ]
                cursor.executemany(
                    "INSERT INTO articulos (codigo, articulo, precio, costo, stock, estado, image_path) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    productos_ejemplo
                )
                conn.commit()
                print("Artículos de ejemplo creados")
            
            cursor.execute("SELECT codigo, articulo, precio, stock FROM articulos WHERE stock > 0 AND estado = 'activo'")
            productos_data = cursor.fetchall()
            print(f"🔍 Productos encontrados: {len(productos_data)}")
            
            self.productos_dict = {}
            self.productos_nombres = []
            self.productos_codigos = []
            
            for codigo, nombre, precio, stock in productos_data:
                if codigo:
                    self.productos_dict[codigo] = {'nombre': nombre, 'precio': precio, 'stock': stock}
                    self.productos_nombres.append(f"{nombre} ({codigo})")
                    self.productos_codigos.append(codigo)
            
            if self.productos_nombres:
                self.entry_producto['values'] = self.productos_nombres
                print(f"✅ Cargados {len(self.productos_nombres)} productos")
            else:
                self.productos_nombres = ["No hay productos disponibles"]
                self.entry_producto['values'] = self.productos_nombres
                print("❌ No se encontraron productos con stock")
        except Exception as e:
            print(f"❌ ERROR CARGANDO PRODUCTOS: {e}")
            import traceback
            traceback.print_exc()
            self.productos_nombres = ["Error cargando productos"]
            self.productos_dict = {}
            self.productos_codigos = []
            self.entry_producto['values'] = self.productos_nombres
        finally:
            cursor.close()
            conn.close()
        print("🏁 CARGA DE PRODUCTOS FINALIZADA")

    def cargar_clientes(self):
        conn = get_connection()
        if not conn:
            return
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM clientes")
            count = cursor.fetchone()[0]
            if count == 0:
                clientes_ejemplo = [
                    ("Cliente Ejemplo 1", "cliente1@email.com", "123-456-7890"),
                    ("Cliente Ejemplo 2", "cliente2@email.com", "123-456-7891"),
                    ("Cliente Ejemplo 3", "cliente3@email.com", "123-456-7892"),
                    ("Cliente General", "general@tienda.com", "123-456-0000")
                ]
                cursor.executemany(
                    "INSERT INTO clientes (nombre, correo, celular) VALUES (%s, %s, %s)",
                    clientes_ejemplo
                )
                conn.commit()
                print("Clientes de ejemplo creados")
            
            cursor.execute("SELECT nombre FROM clientes")
            self.clientes = [row[0] for row in cursor.fetchall()]
            self.entry_cliente['values'] = self.clientes if self.clientes else ["Cliente General"]
        except Exception as e:
            print(f"Error cargando clientes: {e}")
            self.clientes = ["Cliente General"]
            self.entry_cliente['values'] = self.clientes
        finally:
            cursor.close()
            conn.close()

    # ==================== FILTROS Y BÚSQUEDAS ====================
    def filtrar_clientes(self, event):
        if self.timer_cliente:
            self.timer_cliente.cancel()
        self.timer_cliente = threading.Timer(0.5, self._filter_clientes)
        self.timer_cliente.start()

    def _filter_clientes(self):
        texto = self.entry_cliente.get().lower()
        if texto:
            filtrados = [c for c in self.clientes if texto in c.lower()]
            self.entry_cliente['values'] = filtrados
        else:
            self.entry_cliente['values'] = self.clientes

    def filtrar_productos(self, event):
        if self.timer_producto:
            self.timer_producto.cancel()
        self.timer_producto = threading.Timer(0.3, self._filter_productos)
        self.timer_producto.start()

    def _filter_productos(self):
        texto = self.entry_producto.get().lower()
        if texto and hasattr(self, 'productos_nombres'):
            filtrados = [p for p in self.productos_nombres if texto in p.lower()]
            self.entry_producto['values'] = filtrados
        else:
            if hasattr(self, 'productos_nombres'):
                self.entry_producto['values'] = self.productos_nombres

    def mostrar_productos(self, event=None):
        if hasattr(self, 'productos_nombres'):
            self.entry_producto['values'] = self.productos_nombres
            self.entry_producto.event_generate('<Down>')

    def buscar_por_codigo(self, event=None):
        try:
            codigo = self.entry_codigo.get().upper()
            if not codigo:
                self.entry_producto.set("")
                self.label_stock.config(text="📊 Stock: --")
                return
            if not hasattr(self, 'productos_codigos') or not hasattr(self, 'productos_dict'):
                return
            
            codigo_encontrado = None
            for cod in self.productos_codigos:
                if cod.startswith(codigo):
                    codigo_encontrado = cod
                    break
            
            if codigo_encontrado and codigo_encontrado in self.productos_dict:
                info = self.productos_dict[codigo_encontrado]
                nombre_completo = f"{info['nombre']} ({codigo_encontrado})"
                self.entry_producto.delete(0, tk.END)
                self.entry_producto.insert(0, nombre_completo)
                self.label_stock.config(
                    text=f"📊 Stock: {info['stock']} unidades",
                    fg=self.COLORS['success'] if info['stock'] > 10 else self.COLORS['warning']
                )
                if event and event.keysym == 'Return':
                    self.entry_cantidad.focus_set()
            else:
                if len(codigo) > 2:
                    self.entry_producto.delete(0, tk.END)
                    self.label_stock.config(text="📊 Stock: -- (Código no encontrado)", fg=self.COLORS['danger'])
        except Exception as e:
            print(f"Error buscando por código: {e}")

    # ==================== OPERACIONES DE VENTA ====================
    def actualizar_stock(self, event=None):
        try:
            producto_seleccionado = self.entry_producto.get()
            if not producto_seleccionado:
                return
            if hasattr(self, 'productos_dict'):
                if '(' in producto_seleccionado and ')' in producto_seleccionado:
                    codigo = producto_seleccionado.split('(')[-1].replace(')', '')
                    if codigo in self.productos_dict:
                        info = self.productos_dict[codigo]
                        self.entry_codigo.delete(0, tk.END)
                        self.entry_codigo.insert(0, codigo)
                        self.label_stock.config(
                            text=f"📊 Stock: {info['stock']} unidades",
                            fg=self.COLORS['success'] if info['stock'] > 10 else self.COLORS['warning']
                        )
                        return
            self.label_stock.config(text="📊 Stock: --", fg=self.COLORS['dark'])
        except Exception as e:
            print(f"Error actualizando stock: {e}")
            self.label_stock.config(text="📊 Stock: --", fg=self.COLORS['dark'])

    def agregar_producto(self):
        producto = self.entry_producto.get()
        cantidad_str = self.entry_cantidad.get()
        if not producto or not cantidad_str:
            messagebox.showwarning("⚠️ Advertencia", "Por favor complete todos los campos")
            return
        
        try:
            cantidad = int(cantidad_str)
            if cantidad <= 0:
                messagebox.showwarning("⚠️ Advertencia", "La cantidad debe ser mayor a 0")
                return
            
            if '(' in producto and ')' in producto:
                inicio = producto.rfind('(')
                fin = producto.rfind(')')
                codigo = producto[inicio+1:fin].strip()
                nombre_producto = producto[:inicio].strip()
            else:
                nombre_producto = producto.strip()
                codigo = None
            
            conn = get_connection()
            if not conn:
                return
            cursor = conn.cursor()
            try:
                if codigo:
                    cursor.execute("SELECT articulo, precio, stock FROM articulos WHERE codigo = %s AND estado = 'activo'", (codigo,))
                else:
                    cursor.execute("SELECT articulo, precio, stock FROM articulos WHERE articulo = %s AND estado = 'activo'", (nombre_producto,))
                resultado = cursor.fetchone()
                
                if not resultado:
                    messagebox.showerror("❌ Error", f"Producto no encontrado en el inventario\n\nBuscado: '{producto}'")
                    return
                
                nombre_real, precio, stock = resultado
                if cantidad > stock:
                    messagebox.showerror("📦 Stock Insuficiente", f"Solo hay {stock} unidades disponibles")
                    return
                
                total = float(precio) * cantidad
                self.tree_productos.insert("", "end", values=(nombre_real, f"${precio:,.2f}", cantidad, f"${total:,.2f}"))
                self.productos_seleccionados.append({
                    'nombre': nombre_real,
                    'precio': precio,
                    'cantidad': cantidad,
                    'total': total
                })
                
                self.entry_producto.delete(0, tk.END)
                self.entry_codigo.delete(0, tk.END)
                self.entry_cantidad.delete(0, tk.END)
                self.label_stock.config(text="📊 Stock: --")
                self.actualizar_totales()
                
            except Exception as e:
                messagebox.showerror("💾 Error", f"Error al buscar producto: {e}")
            finally:
                cursor.close()
                conn.close()
                
        except ValueError:
            messagebox.showerror("🔢 Error de Cantidad", "La cantidad debe ser un número válido")

    def actualizar_totales(self):
        subtotal = sum(p['total'] for p in self.productos_seleccionados)
        iva = subtotal * 0.15
        total = subtotal + iva
        self.label_sub_total.config(text=f'Subtotal: ${subtotal:,.2f}')
        self.label_iva.config(text=f'IVA (15%): ${iva:,.2f}')
        self.label_precio_total.config(text=f'TOTAL: ${total:,.2f}')

    def limpiar_venta(self):
        self.productos_seleccionados.clear()
        for item in self.tree_productos.get_children():
            self.tree_productos.delete(item)
        self.entry_cliente.set("")
        self.entry_producto.set("")
        self.entry_cantidad.delete(0, tk.END)
        self.label_stock.config(text="📊 Stock: --")
        self.actualizar_totales()

    # ==================== PROCESAMIENTO DE PAGO ====================
    def abrir_modal_pago(self):
        if not self.productos_seleccionados:
            messagebox.showwarning("Advertencia", "No hay productos en la venta")
            return
        cliente = self.entry_cliente.get()
        if not cliente:
            messagebox.showwarning("Advertencia", "Por favor seleccione un cliente")
            return
        
        subtotal = sum(p['total'] for p in self.productos_seleccionados)
        iva = subtotal * 0.15
        total = subtotal + iva
        
        self.modal_pago = tk.Toplevel(self)
        self.modal_pago.title("💰 Caja Registradora - Procesar Pago")
        self.modal_pago.geometry("560x620")
        self.modal_pago.configure(bg=self.COLORS['light'])
        self.modal_pago.resizable(True, True)
        self.modal_pago.minsize(520, 560)
        self.modal_pago.grab_set()
        self.modal_pago.transient(self)
        self.modal_pago.geometry("+{}+{}".format(
            self.winfo_rootx() + 450,
            self.winfo_rooty() + 200
        ))
        
        title_frame = tk.Frame(self.modal_pago, bg=self.COLORS['primary'], height=60)
        title_frame.pack(fill='x')
        tk.Label(title_frame, text="💰 CAJA REGISTRADORA", 
                bg=self.COLORS['primary'], fg=self.COLORS['white'],
                font=('Segoe UI', 16, 'bold')).pack(pady=15)
        
        content_frame = tk.Frame(self.modal_pago, bg=self.COLORS['light'])
        content_frame.pack(fill='both', expand=True, padx=30, pady=20)
        
        info_frame = tk.Frame(content_frame, bg=self.COLORS['white'], relief='solid', bd=1)
        info_frame.pack(fill='x', pady=(0, 20))
        tk.Label(info_frame, text=f"Cliente: {cliente}", 
                font=('Segoe UI', 12, 'bold'), bg=self.COLORS['white'],
                fg=self.COLORS['primary']).pack(pady=5)
        tk.Label(info_frame, text=f"Subtotal: ${subtotal:,.2f}", 
                font=('Segoe UI', 11), bg=self.COLORS['white'],
                fg=self.COLORS['dark']).pack(pady=2)
        tk.Label(info_frame, text=f"IVA (15%): ${iva:,.2f}", 
                font=('Segoe UI', 11), bg=self.COLORS['white'],
                fg=self.COLORS['dark']).pack(pady=2)
        tk.Label(info_frame, text=f"TOTAL A PAGAR: ${total:,.2f}", 
                font=('Segoe UI', 14, 'bold'), bg=self.COLORS['white'],
                fg=self.COLORS['success']).pack(pady=10)
        
        pago_frame = tk.Frame(content_frame, bg=self.COLORS['light'])
        pago_frame.pack(fill='x', pady=(0, 20))
        tk.Label(pago_frame, text="💰 Monto recibido:", 
                font=('Segoe UI', 12, 'bold'), bg=self.COLORS['light'],
                fg=self.COLORS['primary']).pack(anchor='w')
        self.entry_monto_recibido = tk.Entry(pago_frame, font=('Segoe UI', 14), 
                                           relief='solid', bd=1, width=20)
        self.entry_monto_recibido.pack(pady=5, anchor='w')
        self.entry_monto_recibido.bind('<KeyRelease>', lambda e: self.calcular_cambio(total))
        
        self.label_cambio = tk.Label(pago_frame, text="Cambio: $0.00", 
                                   font=('Segoe UI', 14, 'bold'), bg=self.COLORS['light'],
                                   fg=self.COLORS['accent'])
        self.label_cambio.pack(pady=10, anchor='w')
        
        botones_frame = tk.Frame(content_frame, bg=self.COLORS['light'])
        botones_frame.pack(fill='x', pady=20)
        self.crear_boton_modal(botones_frame, "✅ ACEPTAR", 
                              lambda: self.aceptar_venta(total), 
                              'success', 50, 0, 200, 50, layout='pack')
        self.crear_boton_modal(botones_frame, "❌ Cancelar", 
                              self.cerrar_modal_pago, 
                              'danger', 270, 0, 150, 50, layout='pack')

    def crear_boton_modal(self, parent, text, command, estilo, x, y, width, height, layout='place'):
        base_colors = self.COLORS
        bg_base = (base_colors['primary'] if estilo == 'primary' else
                  base_colors['secondary'] if estilo == 'secondary' else
                  base_colors['danger'] if estilo == 'danger' else
                  base_colors['success'])
        hover_bg = self.ajustar_color(bg_base, -20)
        btn = tk.Button(parent, text=text, command=command,
                       bg=bg_base, fg=self.COLORS['white'],
                       font=('Segoe UI', 10, 'bold'),
                       relief='flat', cursor='hand2', bd=0)
        if layout == 'pack':
            btn.pack(side='left', fill='x', expand=True, padx=10)
        else:
            btn.place(x=x, y=y, width=width, height=height)
        btn.bind("<Enter>", lambda e: btn.configure(bg=hover_bg))
        btn.bind("<Leave>", lambda e: btn.configure(bg=bg_base))
        return btn

    def calcular_cambio(self, total):
        try:
            monto_recibido = float(self.entry_monto_recibido.get() or 0)
            cambio = monto_recibido - total
            if cambio >= 0:
                self.label_cambio.config(text=f"Cambio: ${cambio:,.2f}", fg=self.COLORS['success'])
            else:
                self.label_cambio.config(text=f"Falta: ${abs(cambio):,.2f}", fg=self.COLORS['danger'])
        except ValueError:
            self.label_cambio.config(text="Cambio: $0.00", fg=self.COLORS['accent'])

    def aceptar_venta(self, total):
        try:
            monto_recibido = float(self.entry_monto_recibido.get() or 0)
            if monto_recibido < total:
                messagebox.showerror("❌ Error", "El monto recibido es insuficiente")
                return
            cambio = monto_recibido - total
            print("🔄 INICIANDO PROCESO DE VENTA...")
            venta_id = self.guardar_venta_en_bd(total, monto_recibido, cambio)
            if venta_id:
                print(f"✅ Venta guardada exitosamente con ID: {venta_id}")
                self.cerrar_modal_pago()
                self.enviar_a_impresora_fiscal(venta_id, total, monto_recibido, cambio)
                self.limpiar_venta()
                messagebox.showinfo("✅ Venta Completada", 
                                  f"¡Transacción procesada exitosamente!\n\n"
                                  f"📄 Factura N°: {self.numero_factura}\n"
                                  f"💰 Total: ${total:,.2f}\n"
                                  f"💵 Recibido: ${monto_recibido:,.2f}\n"
                                  f"💸 Cambio: ${cambio:,.2f}\n\n"
                                  f"🖨️ Factura enviada a impresora fiscal\n"
                                  f"💾 Transacción guardada en base de datos")
                print("🎉 VENTA COMPLETADA EXITOSAMENTE")
            else:
                messagebox.showerror("❌ Error", "Error al guardar la venta en la base de datos")
        except ValueError:
            messagebox.showerror("❌ Error", "Por favor ingrese un monto válido")
        except Exception as e:
            print(f"❌ Error en aceptar_venta: {e}")
            messagebox.showerror("❌ Error", f"Error procesando la venta: {e}")

    # ==================== GUARDAR VENTA EN MYSQL ====================
    def guardar_venta_en_bd(self, total, monto_recibido, cambio):
        conn = get_connection()
        if not conn:
            return None
        cursor = conn.cursor()
        try:
            cliente = self.entry_cliente.get() or "Cliente General"
            fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d")
            hora_actual = datetime.datetime.now().strftime("%H:%M:%S")
            numero_factura = self.numero_factura

            subtotal = round(sum(p['total'] for p in self.productos_seleccionados), 2)
            iva = round(subtotal * 0.15, 2)
            total_round = round(total, 2)
            monto_round = round(monto_recibido, 2)
            cambio_round = round(cambio, 2)

            cursor.execute('''
                INSERT INTO ventas (numero_factura, cliente, fecha, hora, subtotal, iva, total, monto_recibido, cambio, estado)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'completada')
            ''', (numero_factura, cliente, fecha_actual, hora_actual, subtotal, iva, total_round, monto_round, cambio_round))
            venta_id = cursor.lastrowid
            print(f"✅ Venta insertada con ID: {venta_id}")

            for producto in self.productos_seleccionados:
                precio = round(producto['precio'], 2)
                subtotal_detalle = round(producto['total'], 2)
                cantidad = int(producto['cantidad'])

                cursor.execute('''
                    INSERT INTO detalle_ventas (venta_id, producto, precio_unitario, cantidad, subtotal)
                    VALUES (%s, %s, %s, %s, %s)
                ''', (venta_id, producto['nombre'], precio, cantidad, subtotal_detalle))

                cursor.execute('''
                    UPDATE articulos SET stock = stock - %s WHERE articulo = %s
                ''', (cantidad, producto['nombre']))

            conn.commit()
            print(f"✅ Venta guardada con ID: {venta_id}")
            return venta_id
        except Exception as e:
            print(f"❌ Error guardando venta: {e}")
            import traceback
            traceback.print_exc()
            conn.rollback()
            messagebox.showerror("Error", f"Error al guardar la venta:\n{e}")
            return None
        finally:
            cursor.close()
            conn.close()

    # ==================== IMPRESIÓN FISCAL Y TICKET ====================
    def enviar_a_impresora_fiscal(self, venta_id, total, monto_recibido, cambio):
        try:
            print("🖨️ ENVIANDO A IMPRESORA FISCAL...")
            factura_fiscal = self.generar_factura_fiscal(venta_id, total, monto_recibido, cambio)
            import tempfile, os
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False,
                                           encoding='utf-8', prefix=f"fiscal_{self.numero_factura}_") as f:
                f.write(factura_fiscal)
                fiscal_path = f.name
            print(f"📄 Factura fiscal generada: {fiscal_path}")
            if os.name == 'nt':
                os.startfile(fiscal_path)
            return True
        except Exception as e:
            print(f"❌ Error enviando a impresora fiscal: {e}")
            messagebox.showwarning("⚠️ Advertencia", 
                                 f"Error al enviar a impresora fiscal:\n{e}\n\n"
                                 f"La venta se guardó correctamente en la base de datos.")
            return False

    def generar_factura_fiscal(self, venta_id, total, monto_recibido, cambio):
        cliente = self.entry_cliente.get() or "Cliente General"
        fecha_actual = datetime.datetime.now().strftime("%d/%m/%Y")
        hora_actual = datetime.datetime.now().strftime("%H:%M:%S")
        nombre_empresa = obtener_configuracion('nombre_empresa', 'Mi Tienda')
        direccion_empresa = obtener_configuracion('direccion_empresa', 'Caracas, Venezuela')
        rif_empresa = obtener_configuracion('rif_empresa', 'J-00000000-0')
        
        factura = f"""
{'='*50}
              FACTURA FISCAL
{'='*50}

{nombre_empresa}
RIF: {rif_empresa}
{direccion_empresa}

FACTURA N°: {self.numero_factura:08d}
FECHA: {fecha_actual}
HORA: {hora_actual}
CAJERO: Sistema POS

CLIENTE: {cliente}
{'='*50}

DESCRIPCIÓN                QTY    P.UNIT    TOTAL
{'='*50}
"""
        for producto in self.productos_seleccionados:
            nombre = producto['nombre'][:20].ljust(20)
            cantidad = str(producto['cantidad']).rjust(3)
            precio = f"${producto['precio']:>7.2f}"
            subtotal = f"${producto['total']:>9.2f}"
            factura += f"{nombre} {cantidad} {precio} {subtotal}\n"
        
        subtotal_venta = sum(p['total'] for p in self.productos_seleccionados)
        iva = subtotal_venta * 0.15
        factura += f"""
{'='*50}
SUBTOTAL:                           ${subtotal_venta:>9.2f}
IVA (15%):                          ${iva:>9.2f}
{'='*50}
TOTAL A PAGAR:                      ${total:>9.2f}

EFECTIVO RECIBIDO:                  ${monto_recibido:>9.2f}
CAMBIO:                             ${cambio:>9.2f}

{'='*50}
           GRACIAS POR SU COMPRA
        CONSERVE ESTA FACTURA FISCAL
{'='*50}

CONTROL FISCAL: {venta_id:08d}
SERIAL IMPRESORA: FIS-001-2024
FECHA SISTEMA: {datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")}

Esta es una factura fiscal válida
según normativas SENIAT
"""
        return factura

    def cerrar_modal_pago(self):
        if hasattr(self, 'modal_pago'):
            self.modal_pago.destroy()

    # ==================== HISTORIAL DE VENTAS ====================
    def ver_ventas_realizadas(self):
        # Verificar si la ventana ya existe y está visible
        if hasattr(self, 'ventana_ventas'):
            try:
                if self.ventana_ventas.winfo_exists():
                    self.ventana_ventas.lift()
                    self.ventana_ventas.focus_force()
                    return
                else:
                    delattr(self, 'ventana_ventas')
            except (tk.TclError, AttributeError):
                # La ventana ya fue destruida, eliminar referencia
                if hasattr(self, 'ventana_ventas'):
                    delattr(self, 'ventana_ventas')

        # Crear nueva ventana
        self.ventana_ventas = tk.Toplevel(self)
        self.ventana_ventas.title("📊 Historial de Ventas")
        self.ventana_ventas.geometry("1200x700")
        self.ventana_ventas.configure(bg=self.COLORS['light'])
        self.ventana_ventas.resizable(True, True)
        self.ventana_ventas.minsize(1000, 600)
        self.ventana_ventas.geometry("+{}+{}".format(
            self.winfo_rootx() + 100,
            self.winfo_rooty() + 50
        ))

        def on_close():
            if hasattr(self, 'ventana_ventas'):
                try:
                    self.ventana_ventas.destroy()
                except:
                    pass
                finally:
                    delattr(self, 'ventana_ventas')

        self.ventana_ventas.protocol("WM_DELETE_WINDOW", on_close)

        title_frame = tk.Frame(self.ventana_ventas, bg=self.COLORS['primary'], height=70)
        title_frame.pack(fill='x')
        tk.Label(title_frame, text="📊 Historial de Ventas", 
                bg=self.COLORS['primary'], fg=self.COLORS['white'],
                font=('Segoe UI', 18, 'bold')).pack(pady=20)

        filtros_frame = tk.Frame(self.ventana_ventas, bg=self.COLORS['white'], height=80)
        filtros_frame.pack(fill='x', padx=20, pady=(20, 10))

        tk.Label(filtros_frame, text="📅 Rango de fechas:", 
                font=('Segoe UI', 12, 'bold'), bg=self.COLORS['white'],
                fg=self.COLORS['primary']).place(x=20, y=15)
        tk.Label(filtros_frame, text="Desde:", 
                font=('Segoe UI', 10), bg=self.COLORS['white'],
                fg=self.COLORS['dark']).place(x=160, y=15)
        self.entry_fecha_desde = tk.Entry(filtros_frame, font=('Segoe UI', 10), 
                                        relief='solid', bd=1, width=10)
        self.entry_fecha_desde.place(x=200, y=15)
        self.entry_fecha_desde.insert(0, datetime.datetime.now().strftime("%Y-%m-%d"))

        tk.Label(filtros_frame, text="Hasta:", 
                font=('Segoe UI', 10), bg=self.COLORS['white'],
                fg=self.COLORS['dark']).place(x=300, y=15)
        self.entry_fecha_hasta = tk.Entry(filtros_frame, font=('Segoe UI', 10), 
                                        relief='solid', bd=1, width=10)
        self.entry_fecha_hasta.place(x=340, y=15)
        self.entry_fecha_hasta.insert(0, datetime.datetime.now().strftime("%Y-%m-%d"))

        btn_filtrar = tk.Button(filtros_frame, text="🔍 Filtrar Rango", 
                              command=self.filtrar_ventas_por_rango,
                              bg=self.COLORS['primary'], fg=self.COLORS['white'],
                              font=('Segoe UI', 10, 'bold'), relief='flat', 
                              cursor='hand2', bd=0, width=12, height=1)
        btn_filtrar.place(x=450, y=12)
        btn_hoy = tk.Button(filtros_frame, text="📆 Hoy", 
                          command=self.filtrar_ventas_hoy,
                          bg=self.COLORS['success'], fg=self.COLORS['white'],
                          font=('Segoe UI', 10, 'bold'), relief='flat', 
                          cursor='hand2', bd=0, width=12, height=1)
        btn_hoy.place(x=580, y=12)
        btn_semana = tk.Button(filtros_frame, text="📅 Esta Semana", 
                             command=self.filtrar_ventas_semana,
                             bg=self.COLORS['warning'], fg=self.COLORS['white'],
                             font=('Segoe UI', 10, 'bold'), relief='flat', 
                             cursor='hand2', bd=0, width=12, height=1)
        btn_semana.place(x=450, y=45)
        btn_mes = tk.Button(filtros_frame, text="📊 Este Mes", 
                          command=self.filtrar_ventas_mes,
                          bg=self.COLORS['secondary'], fg=self.COLORS['white'],
                          font=('Segoe UI', 10, 'bold'), relief='flat', 
                          cursor='hand2', bd=0, width=12, height=1)
        btn_mes.place(x=580, y=45)
        btn_todas = tk.Button(filtros_frame, text="📋 Todas", 
                            command=self.mostrar_todas_ventas,
                            bg=self.COLORS['danger'], fg=self.COLORS['white'],
                            font=('Segoe UI', 10, 'bold'), relief='flat', 
                            cursor='hand2', bd=0, width=12, height=1)
        btn_todas.place(x=710, y=12)

        self.label_total_dia = tk.Label(filtros_frame, text="💰 Total del rango: $0.00", 
                                      font=('Segoe UI', 14, 'bold'), bg=self.COLORS['white'],
                                      fg=self.COLORS['success'])
        self.label_total_dia.place(x=820, y=15)
        self.label_total_hoy = tk.Label(filtros_frame, text="📈 Ventas HOY: $0.00", 
                                      font=('Segoe UI', 14, 'bold'), bg=self.COLORS['white'],
                                      fg=self.COLORS['primary'])
        self.label_total_hoy.place(x=820, y=45)

        content_frame = tk.Frame(self.ventana_ventas, bg=self.COLORS['light'])
        content_frame.pack(fill='both', expand=True, padx=20, pady=10)
        tree_frame = tk.Frame(content_frame, bg=self.COLORS['white'], relief='solid', bd=1)
        tree_frame.pack(fill='both', expand=True)

        columns = ("Factura", "Cliente", "Producto", "Precio", "Cantidad", "Total", "Fecha", "Hora")
        self.tree_ventas = ttk.Treeview(tree_frame, columns=columns, show="headings", height=20)
        anchos = {"Factura": 80, "Cliente": 150, "Producto": 200, "Precio": 100, 
                 "Cantidad": 80, "Total": 100, "Fecha": 100, "Hora": 80}
        for col in columns:
            self.tree_ventas.heading(col, text=col)
            self.tree_ventas.column(col, width=anchos[col], anchor="center")

        scrollbar_y = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree_ventas.yview)
        scrollbar_x = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree_ventas.xview)
        self.tree_ventas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        self.tree_ventas.pack(side="left", fill="both", expand=True)
        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x.pack(side="bottom", fill="x")

        self.actualizar_total_hoy()
        self.filtrar_ventas_hoy()

    def filtrar_ventas_por_rango(self):
        if not hasattr(self, 'ventana_ventas') or not self.ventana_ventas.winfo_exists():
            return
        fecha_desde = self.entry_fecha_desde.get()
        fecha_hasta = self.entry_fecha_hasta.get()
        if not fecha_desde or not fecha_hasta:
            messagebox.showwarning("⚠️ Advertencia", "Por favor ingrese ambas fechas")
            return
        conn = get_connection()
        if not conn:
            return
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT v.numero_factura, v.cliente, d.producto, d.precio_unitario, d.cantidad, d.subtotal AS total, v.fecha, v.hora
                FROM detalle_ventas d
                JOIN ventas v ON d.venta_id = v.id
                WHERE v.fecha BETWEEN %s AND %s
                ORDER BY v.fecha DESC, v.hora DESC
            """, (fecha_desde, fecha_hasta))
            ventas = cursor.fetchall()
            descripcion = f"{fecha_desde} - {fecha_hasta}" if fecha_desde != fecha_hasta else fecha_desde
            self.actualizar_tabla_ventas(ventas, descripcion)
            self.actualizar_total_hoy()
        except Exception as e:
            messagebox.showerror("💾 Error", f"Error al filtrar ventas: {e}")
        finally:
            cursor.close()
            conn.close()

    def filtrar_ventas_hoy(self):
        if not hasattr(self, 'ventana_ventas') or not self.ventana_ventas.winfo_exists():
            return
        fecha_hoy = datetime.datetime.now().strftime("%Y-%m-%d")
        self.entry_fecha_desde.delete(0, tk.END)
        self.entry_fecha_desde.insert(0, fecha_hoy)
        self.entry_fecha_hasta.delete(0, tk.END)
        self.entry_fecha_hasta.insert(0, fecha_hoy)
        self.filtrar_ventas_por_rango()

    def filtrar_ventas_semana(self):
        if not hasattr(self, 'ventana_ventas') or not self.ventana_ventas.winfo_exists():
            return
        hoy = datetime.datetime.now()
        inicio_semana = hoy - datetime.timedelta(days=hoy.weekday())
        fin_semana = inicio_semana + datetime.timedelta(days=6)
        self.entry_fecha_desde.delete(0, tk.END)
        self.entry_fecha_desde.insert(0, inicio_semana.strftime("%Y-%m-%d"))
        self.entry_fecha_hasta.delete(0, tk.END)
        self.entry_fecha_hasta.insert(0, fin_semana.strftime("%Y-%m-%d"))
        self.filtrar_ventas_por_rango()

    def filtrar_ventas_mes(self):
        if not hasattr(self, 'ventana_ventas') or not self.ventana_ventas.winfo_exists():
            return
        hoy = datetime.datetime.now()
        inicio_mes = hoy.replace(day=1)
        if hoy.month == 12:
            fin_mes = hoy.replace(year=hoy.year + 1, month=1, day=1) - datetime.timedelta(days=1)
        else:
            fin_mes = hoy.replace(month=hoy.month + 1, day=1) - datetime.timedelta(days=1)
        self.entry_fecha_desde.delete(0, tk.END)
        self.entry_fecha_desde.insert(0, inicio_mes.strftime("%Y-%m-%d"))
        self.entry_fecha_hasta.delete(0, tk.END)
        self.entry_fecha_hasta.insert(0, fin_mes.strftime("%Y-%m-%d"))
        self.filtrar_ventas_por_rango()

    def mostrar_todas_ventas(self):
        if not hasattr(self, 'ventana_ventas') or not self.ventana_ventas.winfo_exists():
            return
        conn = get_connection()
        if not conn:
            return
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT v.numero_factura, v.cliente, d.producto, d.precio_unitario, d.cantidad, d.subtotal AS total, v.fecha, v.hora
                FROM detalle_ventas d
                JOIN ventas v ON d.venta_id = v.id
                ORDER BY v.fecha DESC, v.hora DESC
                LIMIT 500
            """)
            ventas = cursor.fetchall()
            self.actualizar_tabla_ventas(ventas, "Todas las fechas")
            self.actualizar_total_hoy()
        except Exception as e:
            messagebox.showerror("💾 Error", f"Error al cargar ventas: {e}")
        finally:
            cursor.close()
            conn.close()

    def actualizar_tabla_ventas(self, ventas, fecha_filtro):
        if not hasattr(self, 'ventana_ventas') or not self.ventana_ventas.winfo_exists():
            return
        for item in self.tree_ventas.get_children():
            self.tree_ventas.delete(item)
        total_dia = 0
        for venta in ventas:
            factura, cliente, producto, precio, cantidad, total, fecha, hora = venta
            total_dia += total
            self.tree_ventas.insert("", "end", values=(
                factura, cliente, producto, f"${precio:,.2f}", cantidad, f"${total:,.2f}", fecha, hora
            ))
        if fecha_filtro == "Todas las fechas":
            self.label_total_dia.config(text=f"💰 Total general: ${total_dia:,.2f}")
        elif " - " in fecha_filtro:
            self.label_total_dia.config(text=f"💰 Total rango: ${total_dia:,.2f}")
        else:
            self.label_total_dia.config(text=f"💰 Total {fecha_filtro}: ${total_dia:,.2f}")
        if len(ventas) == 0:
            self.label_total_dia.config(text=f"📊 Sin ventas para {fecha_filtro}")

    def actualizar_total_hoy(self):
        if not hasattr(self, 'ventana_ventas') or not self.ventana_ventas.winfo_exists():
            return
        fecha_hoy = datetime.datetime.now().strftime("%Y-%m-%d")
        conn = get_connection()
        if not conn:
            return
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT SUM(total), COUNT(*) FROM ventas WHERE fecha = %s", (fecha_hoy,))
            resultado = cursor.fetchone()
            total_hoy = resultado[0] if resultado[0] else 0
            num_ventas_hoy = resultado[1] if resultado[1] else 0
            if hasattr(self, 'label_total_hoy') and self.label_total_hoy.winfo_exists():
                if num_ventas_hoy > 0:
                    self.label_total_hoy.config(
                        text=f"📈 Ventas HOY: ${total_hoy:,.2f} ({num_ventas_hoy} ventas)",
                        fg=self.COLORS['success']
                    )
                else:
                    self.label_total_hoy.config(
                        text="📈 Ventas HOY: $0.00 (0 ventas)",
                        fg=self.COLORS['secondary']
                    )
        except Exception as e:
            print(f"Error calculando total de hoy: {e}")
            if hasattr(self, 'label_total_hoy') and self.label_total_hoy.winfo_exists():
                self.label_total_hoy.config(text="📈 Ventas HOY: Error", fg=self.COLORS['danger'])
        finally:
            cursor.close()
            conn.close()

    # ==================== RELOJ EN TIEMPO REAL ====================
    def actualizar_hora(self):
        try:
            if not self.winfo_exists():
                return
            hora_actual = datetime.datetime.now().strftime("%H:%M:%S")
            if hasattr(self, 'label_hora') and self.label_hora.winfo_exists():
                self.label_hora.config(text=hora_actual)
            if self.winfo_exists():
                self.after(1000, self.actualizar_hora)
        except:
            pass