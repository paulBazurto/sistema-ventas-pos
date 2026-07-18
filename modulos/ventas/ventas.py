import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import datetime
import threading
from PIL import Image, ImageTk
import sys
import os

from modulos.ventas.crear_factura import generar_factura
from modulos.ventas.obtener_numero_factura import obtener_numero_factura_actual
from data.models import get_connection   # <--- Conexión MySQL
from modulos.utils.utils import resource_path


class Ventas(tk.Frame):
    """Versión clásica de la interfaz de ventas (adaptada a MySQL)"""
    
    def __init__(self, padre):
        super().__init__(padre)
        self.numero_factura = obtener_numero_factura_actual()
        self.productos_seleccionados = []
        self.widgets()
        self.cargar_productos()
        self.cargar_clientes()
        self.timer_producto = None
        self.timer_cliente = None

    # ==================== CLIENTES ====================
    def cargar_clientes(self):
        """Cargar clientes desde MySQL"""
        conn = get_connection()
        if not conn:
            return
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT nombre FROM clientes ORDER BY nombre")
            self.clientes = [row[0] for row in cursor.fetchall()]
            self.entry_cliente['values'] = self.clientes
        except Exception as e:
            print("Error cargando clientes:", e)
        finally:
            cursor.close()
            conn.close()

    def filtrar_clientes(self, event):
        if self.timer_cliente:
            self.timer_cliente.cancel()
        self.timer_cliente = threading.Timer(0.5, self._filter_clientes)
        self.timer_cliente.start()
    
    def _filter_clientes(self):
        typed = self.entry_cliente.get()
        if typed == '':
            data = self.clientes
        else:
            data = [item for item in self.clientes if typed.lower() in item.lower()]
        if data:
            self.entry_cliente['values'] = data
            self.entry_cliente.event_generate('<Down>')
        else:
            self.entry_cliente['values'] = ['No se encuentra resultado']
            self.entry_cliente.event_generate('<Down>')
            self.entry_cliente.delete(0, tk.END)

    # ==================== PRODUCTOS ====================
    def cargar_productos(self):
        """Cargar productos activos desde MySQL (tabla articulos)"""
        conn = get_connection()
        if not conn:
            return
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT articulo FROM articulos WHERE estado = 'activo' ORDER BY articulo")
            self.products = [row[0] for row in cursor.fetchall()]
            self.entry_producto['values'] = self.products
        except Exception as e:
            print("Error cargando productos:", e)
        finally:
            cursor.close()
            conn.close()

    def filtrar_productos(self, event):
        if self.timer_producto:
            self.timer_producto.cancel()
        self.timer_producto = threading.Timer(0.5, self._filter_products)
        self.timer_producto.start()
    
    def _filter_products(self):
        typed = self.entry_producto.get()
        if typed == '':
            data = self.products
        else:
            data = [item for item in self.products if typed.lower() in item.lower()]
        if data:
            self.entry_producto['values'] = data
            self.entry_producto.event_generate('<Down>')
        else:
            self.entry_producto['values'] = ['No se encuentra resultado']
            self.entry_producto.event_generate('<Down>')
            self.entry_producto.delete(0, tk.END)

    # ==================== AGREGAR ARTÍCULO A LA VENTA ====================
    def agregar_articulos(self):
        """Agregar producto seleccionado a la lista de venta"""
        cliente = self.entry_cliente.get().strip()
        producto = self.entry_producto.get().strip()
        cantidad_str = self.entry_cantidad.get().strip()

        if not cliente:
            messagebox.showerror("Error", "Por favor seleccione un cliente.")
            return
        if not producto:
            messagebox.showerror("Error", "Por favor seleccione un producto.")
            return
        if not cantidad_str.isdigit() or int(cantidad_str) <= 0:
            messagebox.showerror("Error", "Por favor ingrese una cantidad válida.")
            return

        cantidad = int(cantidad_str)

        conn = get_connection()
        if not conn:
            return
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT precio, costo, stock FROM articulos WHERE articulo = %s AND estado = 'activo'", (producto,))
            resultado = cursor.fetchone()
            if resultado is None:
                messagebox.showerror("Error", "Producto no encontrado")
                return
            precio, costo, stock = resultado

            if cantidad > stock:
                messagebox.showerror("Error", f"Stock insuficiente. Solo hay {stock} unidades disponibles.")
                return

            total = precio * cantidad
            total_cop = "{:,.0f}".format(total)

            # Insertar en Treeview
            self.tre.insert("", "end", values=(
                self.numero_factura,
                cliente,
                producto,
                "{:,.0f}".format(precio),
                cantidad,
                total_cop
            ))

            # Guardar en lista interna (con costo para actualizar stock)
            self.productos_seleccionados.append({
                'factura': self.numero_factura,
                'cliente': cliente,
                'producto': producto,
                'precio': precio,
                'cantidad': cantidad,
                'total': total,
                'costo': costo
            })

            # Limpiar campos de producto y cantidad
            self.entry_producto.set('')
            self.entry_cantidad.delete(0, 'end')

            self.calcular_precio_total()

        except Exception as e:
            print("Error al agregar artículo:", e)
            messagebox.showerror("Error", f"Error al agregar artículo: {e}")
        finally:
            cursor.close()
            conn.close()

    # ==================== CÁLCULO DE TOTALES ====================
    def calcular_precio_total(self):
        """Calcular subtotal, IVA y total general"""
        subtotal = sum(float(item['total']) for item in self.productos_seleccionados)
        iva = subtotal * 0.15
        total = subtotal + iva

        self.label_sub_total.config(text=f'Sub - Total : $ {subtotal:,.2f}')
        self.label_iva.config(text=f'IVA (15%): $ {iva:,.2f}')
        self.label_precio_total.config(text=f'Precio a Pagar: $ {total:,.2f}')

    # ==================== ACTUALIZAR STOCK (visual) ====================
    def actualizar_stock(self, event=None):
        producto_seleccionado = self.entry_producto.get()
        if not producto_seleccionado:
            self.label_stock.config(text="Stock: --")
            return

        conn = get_connection()
        if not conn:
            return
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT stock FROM articulos WHERE articulo = %s", (producto_seleccionado,))
            resultado = cursor.fetchone()
            stock = resultado[0] if resultado else 0
            self.label_stock.config(text=f"Stock: {stock}")
        except Exception as e:
            print("Error al obtener stock:", e)
            self.label_stock.config(text="Stock: Error")
        finally:
            cursor.close()
            conn.close()

    # ==================== PROCESAR PAGO ====================
    def realizar_pago(self):
        if not self.tre.get_children():
            messagebox.showerror("Error", "No hay productos seleccionados para realizar el pago.")
            return

        total_venta = sum(item['total'] for item in self.productos_seleccionados)
        total_formateado = "{:,.2f}".format(total_venta)

        ventana_pago = tk.Toplevel(self)
        ventana_pago.title("Realizar pago")
        ventana_pago.geometry("400x400+450+80")
        ventana_pago.config(bg="#C6D9E3")
        ventana_pago.resizable(False, False)
        ventana_pago.transient(self.master)
        ventana_pago.grab_set()
        ventana_pago.focus_set()
        ventana_pago.lift()

        tk.Label(ventana_pago, text="Realizar pago", font="sans 30 bold", bg="#C6D9E3").place(x=70, y=10)
        tk.Label(ventana_pago, text=f"Total a pagar: {total_formateado}", font="sans 14 bold", bg="#C6D9E3").place(x=80, y=100)
        tk.Label(ventana_pago, text="Ingrese monto pagado", font="sans 14 bold", bg="#C6D9E3").place(x=80, y=160)

        entry_monto = ttk.Entry(ventana_pago, font="sans 14 bold")
        entry_monto.place(x=80, y=210, width=240, height=40)

        btn_aceptar = tk.Button(ventana_pago, text="Aceptar", font="sans 14 bold",
                               command=lambda: self.procesar_pago(entry_monto.get(), ventana_pago, total_venta))
        btn_aceptar.place(x=80, y=270, width=240, height=40)

    # ==================== PROCESAR PAGO (GUARDAR EN BD) ====================
    def procesar_pago(self, cantidad_pagada_str, ventana_pago, total_venta):
        try:
            cantidad_pagada = float(cantidad_pagada_str)
        except ValueError:
            messagebox.showerror("Error", "Ingrese un monto válido.")
            return

        if cantidad_pagada < total_venta:
            messagebox.showerror("Error", "La cantidad pagada es insuficiente.")
            return

        cambio = cantidad_pagada - total_venta
        cliente = self.entry_cliente.get().strip() or "Cliente General"

        mensaje = f"Total: {total_venta:,.2f} $\nCantidad pagada: {cantidad_pagada:,.2f} $\nCambio: {cambio:,.2f} $"
        messagebox.showinfo("Pago realizado", mensaje)

        conn = get_connection()
        if not conn:
            return
        cursor = conn.cursor()
        try:
            fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d")
            hora_actual = datetime.datetime.now().strftime("%H:%M:%S")

            # Calcular subtotal e IVA
            subtotal = sum(item['total'] for item in self.productos_seleccionados)
            iva = subtotal * 0.15

            # Insertar venta principal
            cursor.execute("""
                INSERT INTO ventas (numero_factura, cliente, fecha, hora, subtotal, iva, total, monto_recibido, cambio, estado)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'completada')
            """, (self.numero_factura, cliente, fecha_actual, hora_actual, subtotal, iva, total_venta, cantidad_pagada, cambio))
            venta_id = cursor.lastrowid

            # Insertar detalles y actualizar stock
            for item in self.productos_seleccionados:
                cursor.execute("""
                    INSERT INTO detalle_ventas (venta_id, producto, precio_unitario, cantidad, subtotal)
                    VALUES (%s, %s, %s, %s, %s)
                """, (venta_id, item['producto'], item['precio'], item['cantidad'], item['total']))

                # Actualizar stock en articulos
                cursor.execute("""
                    UPDATE articulos SET stock = stock - %s WHERE articulo = %s
                """, (item['cantidad'], item['producto']))

            conn.commit()

            # Generar factura PDF
            generar_factura(total_venta, cliente, self.productos_seleccionados)

            # Actualizar número de factura
            self.numero_factura += 1
            self.label_numero_factura.config(text=str(self.numero_factura))

            # Limpiar venta
            self.productos_seleccionados = []
            self.limpiar_campos()
            ventana_pago.destroy()

            messagebox.showinfo("Éxito", "Venta registrada correctamente")

        except Exception as e:
            conn.rollback()
            messagebox.showerror("Error", f"Error al registrar la venta: {e}")
        finally:
            cursor.close()
            conn.close()

    # ==================== LIMPIAR CAMPOS ====================
    def limpiar_campos(self):
        for item in self.tre.get_children():
            self.tre.delete(item)
        self.label_precio_total.config(text='Precio a pagar: $ 0.00')
        self.label_sub_total.config(text='Sub - Total : $ 0.00')
        self.label_iva.config(text='IVA (15%): $ 0.00')
        self.entry_producto.set('')
        self.entry_cantidad.delete(0, 'end')
        self.label_stock.config(text="Stock: --")

    def limpiar_lista(self):
        self.tre.delete(*self.tre.get_children())
        self.productos_seleccionados.clear()
        self.calcular_precio_total()

    # ==================== ELIMINAR ARTÍCULO ====================
    def eliminar_articulo(self):
        selected = self.tre.selection()
        if not selected:
            messagebox.showerror("Error", "No hay ningún artículo seleccionado.")
            return

        item_id = selected[0]
        valores = self.tre.item(item_id)["values"]
        producto = valores[2]  # nombre del producto

        self.tre.delete(item_id)

        # Eliminar de la lista interna
        self.productos_seleccionados = [p for p in self.productos_seleccionados if p['producto'] != producto]

        self.calcular_precio_total()

    # ==================== EDITAR ARTÍCULO ====================
    def editar_articulo(self):
        selected = self.tre.selection()
        if not selected:
            messagebox.showerror("Error", "Por favor seleccione un artículo para editar.")
            return

        item_values = self.tre.item(selected[0], "values")
        if not item_values:
            return

        current_producto = item_values[2]
        current_cantidad = int(item_values[4])

        nueva_cantidad = simpledialog.askinteger(
            "Editar artículo",
            "Ingrese la nueva cantidad:",
            initialvalue=current_cantidad,
            minvalue=1
        )

        if nueva_cantidad is None:
            return  # Cancelado

        conn = get_connection()
        if not conn:
            return
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT precio, costo, stock FROM articulos WHERE articulo = %s AND estado = 'activo'", (current_producto,))
            resultado = cursor.fetchone()
            if resultado is None:
                messagebox.showerror("Error", "Producto no encontrado")
                return
            precio, costo, stock = resultado

            if nueva_cantidad > stock:
                messagebox.showerror("Error", f"Stock insuficiente. Solo hay {stock} unidades disponibles.")
                return

            total = precio * nueva_cantidad
            total_cop = "{:,.0f}".format(total)

            # Actualizar Treeview
            self.tre.item(selected[0], values=(
                self.numero_factura,
                self.entry_cliente.get(),
                current_producto,
                "{:,.0f}".format(precio),
                nueva_cantidad,
                total_cop
            ))

            # Actualizar lista interna
            for producto in self.productos_seleccionados:
                if producto['producto'] == current_producto:
                    producto['cantidad'] = nueva_cantidad
                    producto['total'] = total
                    break

            self.calcular_precio_total()

        except Exception as e:
            print("Error al editar artículo:", e)
            messagebox.showerror("Error", f"Error al editar: {e}")
        finally:
            cursor.close()
            conn.close()

    # ==================== VER VENTAS REALIZADAS ====================
    def ver_ventas_realizadas(self):
        """Mostrar historial de ventas (MySQL) con filtros"""
        conn = get_connection()
        if not conn:
            return
        cursor = conn.cursor()
        try:
            # Obtener todas las ventas con sus detalles
            cursor.execute("""
                SELECT v.numero_factura, v.cliente, d.producto, d.precio_unitario, d.cantidad, d.subtotal, v.fecha, v.hora
                FROM detalle_ventas d
                JOIN ventas v ON d.venta_id = v.id
                ORDER BY v.fecha DESC, v.hora DESC
            """)
            ventas = cursor.fetchall()
        except Exception as e:
            messagebox.showerror("Error", f"Error al obtener ventas: {e}")
            cursor.close()
            conn.close()
            return
        finally:
            cursor.close()
            conn.close()

        ventana_ventas = tk.Toplevel(self)
        ventana_ventas.title("Ventas realizadas")
        ventana_ventas.geometry("1100x770+120+20")
        ventana_ventas.configure(bg='#C6D9E3')
        ventana_ventas.resizable(False, False)
        ventana_ventas.transient(self.master)
        ventana_ventas.grab_set()
        ventana_ventas.focus_set()
        ventana_ventas.lift()

        def filtrar_ventas():
            factura_buscar = entry_factura.get().strip()
            cliente_buscar = entry_cliente.get().strip()
            fecha_start = entry_fecha_start.get().strip()
            fecha_end = entry_Fecha_end.get().strip()

            # Limpiar treeview
            for item in tree.get_children():
                tree.delete(item)

            ventas_filtradas = ventas
            if factura_buscar:
                ventas_filtradas = [v for v in ventas_filtradas if str(v[0]) == factura_buscar]
            if cliente_buscar:
                ventas_filtradas = [v for v in ventas_filtradas if cliente_buscar.lower() in v[1].lower()]
            if fecha_start:
                ventas_filtradas = [v for v in ventas_filtradas if v[6] >= fecha_start]
            if fecha_end:
                ventas_filtradas = [v for v in ventas_filtradas if v[6] <= fecha_end]

            for v in ventas_filtradas:
                tree.insert("", "end", values=(
                    v[0],  # Factura
                    v[1],  # Cliente
                    v[2],  # Producto
                    f"${v[3]:,.2f}",  # Precio
                    v[4],  # Cantidad
                    f"${v[5]:,.2f}",  # Total
                    v[6],  # Fecha
                    v[7]   # Hora
                ))

        # Título
        tk.Label(ventana_ventas, text="Ventas realizadas", font='sans 14 bold', bg='#C6D9E3').place(x=450, y=20)

        # Frame de filtros
        filtro_frame = tk.Frame(ventana_ventas, bg='#C6D9E3')
        filtro_frame.place(x=20, y=60, width=1060, height=140)

        tk.Label(filtro_frame, text="Número de factura:", font='sans 14 bold', bg='#C6D9E3').place(x=10, y=15)
        entry_factura = ttk.Entry(filtro_frame, font='sans 14 bold')
        entry_factura.place(x=200, y=10, width=200, height=40)

        tk.Label(filtro_frame, text="Cliente:", font='sans 14 bold', bg='#C6D9E3').place(x=540, y=15)
        entry_cliente = ttk.Entry(filtro_frame, font='sans 14 bold')
        entry_cliente.place(x=620, y=10, width=200, height=40)

        tk.Label(filtro_frame, text="Fecha desde:", font='sans 14 bold', bg='#C6D9E3').place(x=30, y=70)
        entry_fecha_start = ttk.Entry(filtro_frame, font='sans 14 bold')
        entry_fecha_start.place(x=200, y=70, width=200, height=40)

        tk.Label(filtro_frame, text="Fecha hasta:", font='sans 14 bold', bg='#C6D9E3').place(x=510, y=70)
        entry_Fecha_end = ttk.Entry(filtro_frame, font='sans 14 bold')
        entry_Fecha_end.place(x=620, y=70, width=200, height=40)

        btn_filtrar = tk.Button(filtro_frame, text="Filtrar", font='sans 14 bold', command=filtrar_ventas)
        btn_filtrar.place(x=860, y=40, width=150, height=40)

        # Treeview
        tree_frame = tk.Frame(ventana_ventas, bg="white")
        tree_frame.place(x=20, y=240, width=1060, height=500)

        scrol_y = ttk.Scrollbar(tree_frame)
        scrol_y.pack(side=tk.RIGHT, fill=tk.Y)

        scrol_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        scrol_x.pack(side=tk.BOTTOM, fill=tk.X)

        tree = ttk.Treeview(tree_frame, columns=("Factura", "Cliente", "Producto", "Precio", "Cantidad", "Total", "Fecha", "Hora"), show="headings")
        tree.pack(expand=True, fill=tk.BOTH)

        scrol_y.config(command=tree.yview)
        scrol_x.config(command=tree.xview)

        tree.heading("Factura", text="Factura")
        tree.heading("Cliente", text="Cliente")
        tree.heading("Producto", text="Producto")
        tree.heading("Precio", text="Precio")
        tree.heading("Cantidad", text="Cantidad")
        tree.heading("Total", text="Total")
        tree.heading("Fecha", text="Fecha")
        tree.heading("Hora", text="Hora")

        tree.column("Factura", width=60, anchor="center")
        tree.column("Cliente", width=120, anchor="center")
        tree.column("Producto", width=120, anchor="center")
        tree.column("Precio", width=80, anchor="center")
        tree.column("Cantidad", width=80, anchor="center")
        tree.column("Total", width=80, anchor="center")
        tree.column("Fecha", width=80, anchor="center")
        tree.column("Hora", width=80, anchor="center")

        # Cargar datos iniciales
        for v in ventas:
            tree.insert("", "end", values=(
                v[0], v[1], v[2], f"${v[3]:,.2f}", v[4], f"${v[5]:,.2f}", v[6], v[7]
            ))

    # ==================== INTERFAZ GRÁFICA ====================
    def widgets(self):
        labelframe = tk.LabelFrame(self, font='sans 12 bold', bg='#C6D9E3')
        labelframe.place(x=25, y=30, width=1150, height=180)
        
        # Cliente
        tk.Label(labelframe, text="Cliente: ", font='sans 14 bold', bg='#C6D9E3').place(x=10, y=11)
        self.entry_cliente = ttk.Combobox(labelframe, font="sans 14 bold")
        self.entry_cliente.place(x=120, y=8, width=260, height=40)
        self.entry_cliente.bind('<KeyRelease>', self.filtrar_clientes)
        
        # Producto
        tk.Label(labelframe, text="Producto: ", font="sans 14 bold", bg='#C6D9E3').place(x=10, y=70)
        self.entry_producto = ttk.Combobox(labelframe, font="sans 14 bold")
        self.entry_producto.place(x=120, y=66, width=260, height=40)
        self.entry_producto.bind('<KeyRelease>', self.filtrar_productos)
        self.entry_producto.bind("<<ComboboxSelected>>", self.actualizar_stock)
          
        # Cantidad
        tk.Label(labelframe, text="Cantidad: ", font='sans 14 bold', bg='#C6D9E3').place(x=500, y=11)
        self.entry_cantidad = ttk.Entry(labelframe, font="sans 14 bold")
        self.entry_cantidad.place(x=610, y=8, width=100, height=40)
        
        # Stock
        self.label_stock = tk.Label(labelframe, text="Stock: --", font='sans 14 bold', bg='#C6D9E3')
        self.label_stock.place(x=500, y=70)
        
        # Número de factura
        tk.Label(labelframe, text="Número de Factura: ", font='sans 14 bold', bg='#C6D9E3').place(x=750, y=11)
        self.label_numero_factura = tk.Label(labelframe, text=f"{self.numero_factura}", font='sans 14 bold', bg='#C6D9E3', fg="green")
        self.label_numero_factura.place(x=950, y=11)
        
        # Botones
        tk.Button(labelframe, text="Agregar Artículo", font='sans 14 bold', command=self.agregar_articulos).place(x=90, y=120, height=40, width=200)
        tk.Button(labelframe, text="Eliminar Artículo", font='sans 14 bold', command=self.eliminar_articulo).place(x=310, y=120, height=40, width=200)
        tk.Button(labelframe, text="Editar Artículo", font='sans 14 bold', command=self.editar_articulo).place(x=530, y=120, height=40, width=200)
        tk.Button(labelframe, text="Limpiar lista", font='sans 14 bold', command=self.limpiar_lista).place(x=750, y=120, height=40, width=200)
        
        # Treeview de productos seleccionados
        treFrame = tk.Frame(self, background='white')
        treFrame.place(x=110, y=220, width=980, height=350)
        
        scrol_y = ttk.Scrollbar(treFrame)
        scrol_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrol_x = ttk.Scrollbar(treFrame, orient=tk.HORIZONTAL)
        scrol_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.tre = ttk.Treeview(treFrame, yscrollcommand=scrol_y.set, xscrollcommand=scrol_x.set,
                                height=40, columns=('Factura', 'Cliente', 'Producto', 'Precio', 'Cantidad', 'Total'),
                                show='headings')
        self.tre.pack(expand=True, fill=tk.BOTH)

        scrol_x.config(command=self.tre.xview)
        scrol_y.config(command=self.tre.yview)

        self.tre.heading("Factura", text="Factura")
        self.tre.heading("Cliente", text="Cliente")
        self.tre.heading("Producto", text="Producto")
        self.tre.heading("Precio", text="Precio")
        self.tre.heading("Cantidad", text="Cantidad")
        self.tre.heading("Total", text="Total")

        self.tre.column("Factura", width=70, anchor="center")
        self.tre.column("Cliente", width=250, anchor="center")
        self.tre.column("Producto", width=250, anchor="center")
        self.tre.column("Precio", width=120, anchor="center")
        self.tre.column("Cantidad", width=120, anchor="center")
        self.tre.column("Total", width=150, anchor="center")

        # Totales
        self.label_sub_total = tk.Label(self, text='Sub - Total : $ 0.00', font='sans 18 bold', bg='#C6D9E3')
        self.label_sub_total.place(x=740, y=610)

        self.label_iva = tk.Label(self, text='IVA (15%): $ 0.00', font='sans 18 bold', bg='#C6D9E3')
        self.label_iva.place(x=740, y=650)

        self.label_precio_total = tk.Label(self, text='Precio a Pagar: $ 0.00', font='sans 18 bold', bg='#C6D9E3')
        self.label_precio_total.place(x=740, y=690)

        # Botón Pagar con icono
        image_pago = Image.open(resource_path("media/icons/pago_icon.png"))
        image_pago_resize = image_pago.resize((50, 50))
        image_pago_tk = ImageTk.PhotoImage(image_pago_resize)

        boton_pagar = tk.Button(self, text="Pagar", font='sans 14 bold', command=self.realizar_pago,
                                bg="#77BEF0", fg="white", borderwidth=2, relief="raised")
        boton_pagar.config(image=image_pago_tk, compound=tk.LEFT, padx=20)
        boton_pagar.image = image_pago_tk
        boton_pagar.place(x=70, y=650, width=180, height=40)

        boton_ver_ventas = tk.Button(self, text="Ver ventas realizadas", font='sans 14 bold', command=self.ver_ventas_realizadas)
        boton_ver_ventas.place(x=290, y=650, width=280, height=40)