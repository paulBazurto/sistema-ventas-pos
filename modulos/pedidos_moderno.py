import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
from modulos.utils.estilos_modernos import estilos
from data.models import get_connection
from datetime import datetime

ctk.set_appearance_mode("light")

class PedidosModerno(tk.Frame):
    
    def __init__(self, padre):
        super().__init__(padre, bg=estilos.COLORS['bg_primary'])
        self.widgets()
        self.cargar_pedidos()
        self.cargar_proveedores()
    
    def actualizar_moneda(self, nueva_moneda):
        try:
            self.cargar_pedidos()
            print(f"Módulo Pedidos actualizado a moneda: {nueva_moneda}")
        except Exception as e:
            print(f"Error al actualizar moneda en Pedidos: {e}")
    
    def widgets(self):
        # Frame principal de formulario
        form_frame = tk.LabelFrame(self, text="📦 Pedidos a Proveedores", 
                                  font=('Segoe UI', 16, 'bold'), 
                                  bg=estilos.COLORS['white'],
                                  fg=estilos.COLORS['primary'])
        form_frame.place(x=20, y=20, width=320, height=800)  # Altura aumentada

        # Título del formulario
        title_label = tk.Label(form_frame, text="📝 Pedido de Reposición", 
                              font=('Segoe UI', 14, 'bold'), 
                              bg=estilos.COLORS['white'],
                              fg=estilos.COLORS['secondary'])
        title_label.place(x=10, y=10)

        # Campo Proveedor
        tk.Label(form_frame, text="🏢 Proveedor:", 
                font=('Segoe UI', 12, 'bold'), 
                bg=estilos.COLORS['white'],
                fg=estilos.COLORS['dark']).place(x=10, y=50)
        
        self.proveedor_entry = tk.Entry(form_frame, font=('Segoe UI', 11), relief='solid', bd=1)
        self.proveedor_entry.place(x=10, y=80, width=290, height=35)

        # Campo Estado
        tk.Label(form_frame, text="📊 Estado:", 
                font=('Segoe UI', 12, 'bold'), 
                bg=estilos.COLORS['white'],
                fg=estilos.COLORS['dark']).place(x=10, y=130)
        
        self.estado_combo = ttk.Combobox(form_frame, font=('Segoe UI', 11), 
                                        values=["Pendiente", "En Proceso", "Completado", "Cancelado"],
                                        state="readonly")
        self.estado_combo.set("Pendiente")
        self.estado_combo.place(x=10, y=160, width=290, height=35)

        # Campo Producto a Pedir
        tk.Label(form_frame, text="📦 Producto:", 
                font=('Segoe UI', 12, 'bold'), 
                bg=estilos.COLORS['white'],
                fg=estilos.COLORS['dark']).place(x=10, y=210)
        
        self.producto_combo = ttk.Combobox(form_frame, font=('Segoe UI', 11), state="readonly")
        self.producto_combo.place(x=10, y=240, width=290, height=35)
        self.cargar_productos()
        
        # Campo Cantidad
        tk.Label(form_frame, text="🔢 Cantidad:", 
                font=('Segoe UI', 12, 'bold'), 
                bg=estilos.COLORS['white'],
                fg=estilos.COLORS['dark']).place(x=10, y=290)
        
        self.cantidad = tk.Entry(form_frame, font=('Segoe UI', 12), relief='solid', bd=1)
        self.cantidad.place(x=10, y=320, width=140, height=35)
        
        # Campo Precio Unitario
        tk.Label(form_frame, text="💰 Precio:", 
                font=('Segoe UI', 12, 'bold'), 
                bg=estilos.COLORS['white'],
                fg=estilos.COLORS['dark']).place(x=160, y=290)
        
        self.precio = tk.Entry(form_frame, font=('Segoe UI', 12), relief='solid', bd=1)
        self.precio.place(x=160, y=320, width=140, height=35)

        # Campo Observaciones
        tk.Label(form_frame, text="📝 Observaciones:", 
                font=('Segoe UI', 12, 'bold'), 
                bg=estilos.COLORS['white'],
                fg=estilos.COLORS['dark']).place(x=10, y=370)
        
        self.observaciones = tk.Text(form_frame, font=('Segoe UI', 10), 
                                   relief='solid', bd=1, wrap='word')
        self.observaciones.place(x=10, y=400, width=290, height=60)

        # --- Botones modernos ---
        btn_crear = ctk.CTkButton(
            form_frame, 
            text="➕ Crear Pedido", 
            command=self.crear_pedido,
            width=240,
            height=40,
            corner_radius=10,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color=estilos.COLORS['success'],
            hover_color="#28a745"
        )
        btn_crear.place(x=10, y=380)

        btn_modificar = ctk.CTkButton(
            form_frame, 
            text="✏️ Modificar Estado", 
            command=self.modificar_pedido,
            width=240,
            height=40,
            corner_radius=10,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color=estilos.COLORS['warning'],
            hover_color="#ffc107"
        )
        btn_modificar.place(x=10, y=430)

        btn_recibir = ctk.CTkButton(
            form_frame, 
            text="📥 Recibir Pedido", 
            command=self.recibir_pedido,
            width=240,
            height=40,
            corner_radius=10,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color=estilos.COLORS['info'],
            hover_color="#0ea5e9"
        )
        btn_recibir.place(x=10, y=480)

        # --- NUEVO BOTÓN ELIMINAR PEDIDO ---
        btn_eliminar = ctk.CTkButton(
            form_frame,
            text="🗑️ Eliminar Pedido",
            command=self.eliminar_pedido,
            width=240,
            height=40,
            corner_radius=10,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color=estilos.COLORS['danger'],
            hover_color="#dc3545"
        )
        btn_eliminar.place(x=10, y=530)

        # Etiqueta de estadísticas
        self.stats_label = tk.Label(form_frame, text="Total pedidos: 0", 
                                   font=('Segoe UI', 10, 'bold'), 
                                   bg=estilos.COLORS['white'],
                                   fg=estilos.COLORS['primary'])
        self.stats_label.place(x=10, y=725)

        # Frame para la tabla
        table_frame = tk.LabelFrame(self, text="📋 Lista de Pedidos", 
                                   font=('Segoe UI', 16, 'bold'), 
                                   bg=estilos.COLORS['white'],
                                   fg=estilos.COLORS['primary'])
        table_frame.place(x=360, y=20, width=860, height=720)

        # Configurar Treeview
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure("Treeview",
                       background=estilos.COLORS['white'],
                       foreground=estilos.COLORS['dark'],
                       fieldbackground=estilos.COLORS['white'],
                       font=('Segoe UI', 10))
        
        style.configure("Treeview.Heading",
                       background=estilos.COLORS['primary'],
                       foreground='white',
                       font=('Segoe UI', 11, 'bold'))
        
        style.map('Treeview',
                 background=[('selected', estilos.COLORS['primary'])],
                 foreground=[('selected', 'white')])

        # Scrollbars
        scrollbar_y = ttk.Scrollbar(table_frame, orient='vertical')
        scrollbar_y.pack(side='right', fill='y')

        scrollbar_x = ttk.Scrollbar(table_frame, orient='horizontal')
        scrollbar_x.pack(side='bottom', fill='x')

        # Treeview
        self.tree = ttk.Treeview(table_frame, 
                                yscrollcommand=scrollbar_y.set, 
                                xscrollcommand=scrollbar_x.set,
                                columns=("ID", "Cliente", "Fecha", "Estado", "Total", "Observaciones"), 
                                show="headings",
                                height=30)

        self.tree.pack(expand=True, fill='both', padx=10, pady=10)

        scrollbar_y.config(command=self.tree.yview)
        scrollbar_x.config(command=self.tree.xview)

        # Encabezados
        self.tree.heading("ID", text="🆔 ID")
        self.tree.heading("Cliente", text="🏢 Proveedor")
        self.tree.heading("Fecha", text="📅 Fecha")
        self.tree.heading("Estado", text="📊 Estado")
        self.tree.heading("Total", text="💰 Total")
        self.tree.heading("Observaciones", text="📝 Observaciones")

        # Columnas
        self.tree.column("ID", width=60, anchor="center")
        self.tree.column("Cliente", width=150, anchor="w")
        self.tree.column("Fecha", width=120, anchor="center")
        self.tree.column("Estado", width=100, anchor="center")
        self.tree.column("Total", width=100, anchor="e")
        self.tree.column("Observaciones", width=200, anchor="w")

        self.tree.bind('<<TreeviewSelect>>', self.on_select)

    # ==================== CARGAR PRODUCTOS ====================
    def cargar_productos(self):
        conn = get_connection()
        if not conn:
            return
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT codigo, articulo FROM articulos WHERE estado = 'activo' ORDER BY articulo")
            productos = cursor.fetchall()
            producto_list = [f"{codigo} - {nombre}" for codigo, nombre in productos]
            self.producto_combo['values'] = producto_list
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al cargar productos: {e}")
        finally:
            cursor.close()
            conn.close()

    # ==================== CARGAR PROVEEDORES (placeholder) ====================
    def cargar_proveedores(self):
        pass  # Para futura implementación de autocompletado

    # ==================== CREAR PEDIDO ====================
    def crear_pedido(self):
        if not self.proveedor_entry.get().strip():
            messagebox.showerror("❌ Error", "Debe ingresar el nombre del proveedor")
            return
        if not self.producto_combo.get():
            messagebox.showerror("❌ Error", "Debe seleccionar un producto")
            return
        if not self.cantidad.get().strip() or not self.precio.get().strip():
            messagebox.showerror("❌ Error", "Debe ingresar cantidad y precio")
            return

        try:
            producto_info = self.producto_combo.get()
            producto_codigo = producto_info.split(' - ')[0]
            producto_nombre = producto_info.split(' - ')[1]
            
            proveedor_nombre = self.proveedor_entry.get().strip()
            fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            estado = self.estado_combo.get()
            cantidad = int(self.cantidad.get())
            precio_unitario = float(self.precio.get())
            subtotal = cantidad * precio_unitario
            observaciones = self.observaciones.get("1.0", "end-1c")

            conn = get_connection()
            if not conn:
                return
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO pedidos_proveedor (proveedor_nombre, fecha, estado, total, observaciones)
                VALUES (%s, %s, %s, %s, %s)
            """, (proveedor_nombre, fecha, estado, subtotal, observaciones))
            pedido_id = cursor.lastrowid
            cursor.execute("""
                INSERT INTO pedidos_detalle (pedido_id, producto_codigo, producto_nombre, 
                        cantidad, precio_unitario, subtotal)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (pedido_id, producto_codigo, producto_nombre, cantidad, precio_unitario, subtotal))
            conn.commit()
            messagebox.showinfo("✅ Éxito", f"Pedido creado correctamente\nTotal: ${subtotal:.2f}")
            self.limpiar_campos()
            self.limpiar_treeview()
            self.cargar_pedidos()
        except ValueError:
            messagebox.showerror("❌ Error", "Cantidad y precio deben ser números válidos")
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al crear pedido: {e}")
        finally:
            cursor.close()
            conn.close()

    # ==================== CARGAR PEDIDOS ====================
    def cargar_pedidos(self):
        self.limpiar_treeview()
        conn = get_connection()
        if not conn:
            return
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM pedidos_proveedor ORDER BY fecha DESC")
            rows = cursor.fetchall()
            for row in rows:
                total_formateado = f"${row[4]:.2f}"
                row_formateada = list(row)
                row_formateada[4] = total_formateado
                self.tree.insert("", "end", values=row_formateada)
            self.stats_label.config(text=f"Total pedidos: {len(rows)}")
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al cargar pedidos: {e}")
        finally:
            cursor.close()
            conn.close()

    # ==================== LIMPIAR TREEVIEW ====================
    def limpiar_treeview(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    # ==================== LIMPIAR CAMPOS ====================
    def limpiar_campos(self):
        self.proveedor_entry.delete(0, 'end')
        self.producto_combo.set("")
        self.estado_combo.set("Pendiente")
        self.cantidad.delete(0, 'end')
        self.precio.delete(0, 'end')
        self.observaciones.delete("1.0", 'end')

    # ==================== SELECCIÓN ====================
    def on_select(self, event):
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            values = self.tree.item(item, "values")
            if len(values) >= 6:
                self.proveedor_entry.delete(0, 'end')
                self.proveedor_entry.insert(0, values[1])
                self.estado_combo.set(values[3])
                self.observaciones.delete("1.0", 'end')
                self.observaciones.insert("1.0", values[5])
                self.cargar_detalle_pedido(values[0])

    # ==================== CARGAR DETALLE ====================
    def cargar_detalle_pedido(self, pedido_id):
        conn = get_connection()
        if not conn:
            return
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT producto_codigo, producto_nombre, cantidad, precio_unitario
                FROM pedidos_detalle WHERE pedido_id = %s LIMIT 1
            """, (pedido_id,))
            detalle = cursor.fetchone()
            if detalle:
                producto_codigo, producto_nombre, cantidad, precio_unitario = detalle
                for producto in self.producto_combo['values']:
                    if producto_codigo in producto:
                        self.producto_combo.set(producto)
                        break
                self.cantidad.delete(0, 'end')
                self.cantidad.insert(0, str(cantidad))
                self.precio.delete(0, 'end')
                self.precio.insert(0, str(precio_unitario))
        except Exception as e:
            print(f"Error al cargar detalle: {e}")
        finally:
            cursor.close()
            conn.close()

    # ==================== MODIFICAR ESTADO ====================
    def modificar_pedido(self):
        if not self.tree.selection():
            messagebox.showerror("❌ Error", "Seleccione un pedido para modificar")
            return
        try:
            item = self.tree.selection()[0]
            pedido_id = self.tree.item(item, "values")[0]
            nuevo_estado = self.estado_combo.get()
            observaciones = self.observaciones.get("1.0", "end-1c")
            conn = get_connection()
            if not conn:
                return
            cursor = conn.cursor()
            cursor.execute("UPDATE pedidos_proveedor SET estado = %s, observaciones = %s WHERE id = %s",
                          (nuevo_estado, observaciones, pedido_id))
            conn.commit()
            messagebox.showinfo("✅ Éxito", f"Estado actualizado a: {nuevo_estado}")
            self.limpiar_campos()
            self.limpiar_treeview()
            self.cargar_pedidos()
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al modificar pedido: {e}")
        finally:
            cursor.close()
            conn.close()

    # ==================== RECIBIR PEDIDO ====================
    def recibir_pedido(self):
        if not self.tree.selection():
            messagebox.showerror("❌ Error", "Seleccione un pedido para recibir")
            return
        item = self.tree.selection()[0]
        pedido_id = self.tree.item(item, "values")[0]
        proveedor_nombre = self.tree.item(item, "values")[1]
        estado_actual = self.tree.item(item, "values")[3]
        if estado_actual == "Completado":
            messagebox.showwarning("⚠️ Advertencia", "Este pedido ya fue recibido")
            return
        if not messagebox.askyesno("📥 Confirmar Recepción", 
                                  f"¿Marcar como recibido el pedido de '{proveedor_nombre}'?"):
            return
        conn = get_connection()
        if not conn:
            return
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT producto_codigo, cantidad FROM pedidos_detalle WHERE pedido_id = %s", (pedido_id,))
            detalles = cursor.fetchall()
            for producto_codigo, cantidad in detalles:
                cursor.execute("UPDATE articulos SET stock = stock + %s WHERE codigo = %s",
                              (cantidad, producto_codigo))
            cursor.execute("UPDATE pedidos_proveedor SET estado = 'Completado' WHERE id = %s", (pedido_id,))
            conn.commit()
            messagebox.showinfo("✅ Éxito", f"Pedido recibido. Stock actualizado para {len(detalles)} producto(s)")
            self.limpiar_campos()
            self.limpiar_treeview()
            self.cargar_pedidos()
        except Exception as e:
            conn.rollback()
            messagebox.showerror("❌ Error", f"Error al recibir pedido: {e}")
        finally:
            cursor.close()
            conn.close()

    # ==================== ELIMINAR PEDIDO (NUEVO) ====================
    def eliminar_pedido(self):
        """Elimina el pedido seleccionado (junto con sus detalles por ON DELETE CASCADE)"""
        if not self.tree.selection():
            messagebox.showerror("❌ Error", "Seleccione un pedido para eliminar")
            return
        
        item = self.tree.selection()[0]
        values = self.tree.item(item, "values")
        if not values:
            return
        pedido_id = values[0]
        proveedor = values[1]
        estado = values[3]
        
        # No permitir eliminar pedidos ya completados (opcional)
        if estado == "Completado":
            if not messagebox.askyesno("⚠️ Advertencia", 
                                      "Este pedido ya está completado. ¿Eliminarlo igualmente? Se perderá el historial."):
                return
        
        if not messagebox.askyesno("⚠️ Confirmar Eliminación", 
                                  f"¿Está seguro de que desea eliminar el pedido a '{proveedor}'?\n\nEsta acción no se puede deshacer."):
            return
        
        conn = get_connection()
        if not conn:
            return
        cursor = conn.cursor()
        try:
            # Al tener ON DELETE CASCADE en pedidos_detalle, solo necesitamos eliminar el padre
            cursor.execute("DELETE FROM pedidos_proveedor WHERE id = %s", (pedido_id,))
            conn.commit()
            messagebox.showinfo("✅ Éxito", "Pedido eliminado correctamente")
            self.limpiar_campos()
            self.limpiar_treeview()
            self.cargar_pedidos()
        except Exception as e:
            conn.rollback()
            messagebox.showerror("❌ Error", f"Error al eliminar pedido: {e}")
        finally:
            cursor.close()
            conn.close()