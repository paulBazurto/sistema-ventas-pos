import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
from modulos.utils.estilos_modernos import estilos
from data.models import get_connection

# Configurar CustomTkinter
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class ClientesModerno(tk.Frame):
    
    def __init__(self, padre):
        super().__init__(padre, bg=estilos.COLORS['bg_primary'])
        self.widgets()
        self.cargar_registros()
    
    def actualizar_moneda(self, nueva_moneda):
        try:
            print(f"Módulo Clientes actualizado a moneda: {nueva_moneda}")
        except Exception as e:
            print(f"Error al actualizar moneda en Clientes: {e}")
        
    def widgets(self):
        # Frame principal de formulario - ALTURA AUMENTADA A 680
        form_frame = tk.LabelFrame(self, text="👤 Gestión de Clientes", 
                                  font=('Segoe UI', 16, 'bold'), 
                                  bg=estilos.COLORS['white'],
                                  fg=estilos.COLORS['primary'])
        form_frame.place(x=20, y=20, width=300, height=850)

        title_label = tk.Label(form_frame, text="📝 Datos del Cliente", 
                              font=('Segoe UI', 14, 'bold'), 
                              bg=estilos.COLORS['white'],
                              fg=estilos.COLORS['secondary'])
        title_label.place(x=10, y=10)

        tk.Label(form_frame, text="👤 Nombre:", 
                font=('Segoe UI', 12, 'bold'), 
                bg=estilos.COLORS['white'],
                fg=estilos.COLORS['dark']).place(x=10, y=50)
        self.nombre = tk.Entry(form_frame, font=('Segoe UI', 12), relief='solid', bd=1)
        self.nombre.place(x=10, y=80, width=270, height=35)

        tk.Label(form_frame, text="🆔 Cédula:", 
                font=('Segoe UI', 12, 'bold'), 
                bg=estilos.COLORS['white'],
                fg=estilos.COLORS['dark']).place(x=10, y=130)
        self.cedula = tk.Entry(form_frame, font=('Segoe UI', 12), relief='solid', bd=1)
        self.cedula.place(x=10, y=160, width=270, height=35)

        tk.Label(form_frame, text="📱 Celular:", 
                font=('Segoe UI', 12, 'bold'), 
                bg=estilos.COLORS['white'],
                fg=estilos.COLORS['dark']).place(x=10, y=210)
        self.celular = tk.Entry(form_frame, font=('Segoe UI', 12), relief='solid', bd=1)
        self.celular.place(x=10, y=240, width=270, height=35)

        tk.Label(form_frame, text="🏠 Dirección:", 
                font=('Segoe UI', 12, 'bold'), 
                bg=estilos.COLORS['white'],
                fg=estilos.COLORS['dark']).place(x=10, y=290)
        self.direccion = tk.Entry(form_frame, font=('Segoe UI', 12), relief='solid', bd=1)
        self.direccion.place(x=10, y=320, width=270, height=35)

        tk.Label(form_frame, text="📧 Correo:", 
                font=('Segoe UI', 12, 'bold'), 
                bg=estilos.COLORS['white'],
                fg=estilos.COLORS['dark']).place(x=10, y=370)
        self.correo = tk.Entry(form_frame, font=('Segoe UI', 12), relief='solid', bd=1)
        self.correo.place(x=10, y=400, width=270, height=35)

        # Botones modernos con CustomTkinter - POSICIONES AJUSTADAS
        btn_ingresar = ctk.CTkButton(
            form_frame, 
            text="➕ Registrar Cliente", 
            command=self.registrar,
            width=220,
            height=45,
            corner_radius=10,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color=estilos.COLORS['success'],
            hover_color="#28a745"
        )
        btn_ingresar.place(x=10, y=400)  # Ajustado

        btn_modificar = ctk.CTkButton(
            form_frame, 
            text="✏️ Modificar Cliente", 
            command=self.modificar,
            width=220,
            height=45,
            corner_radius=10,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color=estilos.COLORS['warning'],
            hover_color="#ffc107"
        )
        btn_modificar.place(x=10, y=470)  # Ajustado

        # Tabla de clientes
        table_frame = tk.LabelFrame(self, text="📋 Lista de Clientes", 
                                   font=('Segoe UI', 16, 'bold'), 
                                   bg=estilos.COLORS['white'],
                                   fg=estilos.COLORS['primary'])
        table_frame.place(x=340, y=20, width=880, height=720)

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

        scrollbar_y = ttk.Scrollbar(table_frame, orient='vertical')
        scrollbar_y.pack(side='right', fill='y')
        scrollbar_x = ttk.Scrollbar(table_frame, orient='horizontal')
        scrollbar_x.pack(side='bottom', fill='x')

        self.tree = ttk.Treeview(table_frame, 
                                yscrollcommand=scrollbar_y.set, 
                                xscrollcommand=scrollbar_x.set,
                                columns=("ID", "Nombre", "Cedula", "Celular", "Direccion", "Correo"), 
                                show="headings",
                                height=30)
        self.tree.pack(expand=True, fill='both', padx=10, pady=10)

        scrollbar_y.config(command=self.tree.yview)
        scrollbar_x.config(command=self.tree.xview)

        self.tree.heading("ID", text="🆔 ID")
        self.tree.heading("Nombre", text="👤 Nombre")
        self.tree.heading("Cedula", text="🆔 Cédula")
        self.tree.heading("Celular", text="📱 Celular")
        self.tree.heading("Direccion", text="🏠 Dirección")
        self.tree.heading("Correo", text="📧 Correo")

        self.tree.column("ID", width=60, anchor="center")
        self.tree.column("Nombre", width=150, anchor="w")
        self.tree.column("Cedula", width=120, anchor="center")
        self.tree.column("Celular", width=120, anchor="center")
        self.tree.column("Direccion", width=200, anchor="w")
        self.tree.column("Correo", width=200, anchor="w")

        self.tree.bind('<<TreeviewSelect>>', self.on_select)

        # Frame de estadísticas - POSICIÓN AJUSTADA
        stats_frame = tk.Frame(self, bg=estilos.COLORS['white'], relief='solid', bd=1)
        stats_frame.place(x=20, y=720, width=300, height=100)
        
        tk.Label(stats_frame, text="📊 Estadísticas", 
                font=('Segoe UI', 12, 'bold'), 
                bg=estilos.COLORS['white'],
                fg=estilos.COLORS['primary']).place(x=10, y=10)
        
        self.stats_label = tk.Label(stats_frame, text="Total de clientes: 0", 
                                   font=('Segoe UI', 10), 
                                   bg=estilos.COLORS['white'],
                                   fg=estilos.COLORS['dark'])
        self.stats_label.place(x=10, y=40)

    # ==================== MÉTODOS CRUD ====================
    def validar_campos(self):
        if not all([self.nombre.get().strip(), 
                   self.cedula.get().strip(), 
                   self.celular.get().strip(), 
                   self.direccion.get().strip(), 
                   self.correo.get().strip()]):
            messagebox.showerror("❌ Error", "Todos los campos son requeridos")
            return False
        correo = self.correo.get().strip()
        if '@' not in correo or '.' not in correo:
            messagebox.showerror("❌ Error", "El formato del correo no es válido")
            return False
        return True

    def registrar(self):
        if not self.validar_campos():
            return
        nombre = self.nombre.get().strip()
        cedula = self.cedula.get().strip()
        celular = self.celular.get().strip()
        direccion = self.direccion.get().strip()
        correo = self.correo.get().strip()

        conn = get_connection()
        if not conn:
            return
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id FROM clientes WHERE cedula = %s", (cedula,))
            if cursor.fetchone():
                messagebox.showerror("❌ Error", "Ya existe un cliente con esta cédula")
                return
            cursor.execute("""INSERT INTO clientes (nombre, cedula, celular, direccion, correo) 
                            VALUES (%s, %s, %s, %s, %s)""", 
                          (nombre, cedula, celular, direccion, correo))
            conn.commit()
            messagebox.showinfo("✅ Éxito", "Cliente registrado correctamente")
            self.limpiar_treeview()
            self.limpiar_campos()
            self.cargar_registros()
        except Exception as e:
            messagebox.showerror("❌ Error", f"No se pudo registrar el cliente: {e}")
        finally:
            cursor.close()
            conn.close()

    def cargar_registros(self):
        self.limpiar_treeview()
        conn = get_connection()
        if not conn:
            return
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM clientes ORDER BY nombre")
            rows = cursor.fetchall()
            for row in rows:
                self.tree.insert("", "end", values=row)
            self.stats_label.config(text=f"Total de clientes: {len(rows)}")
        except Exception as e:
            messagebox.showerror("❌ Error", f"No se pudieron cargar los registros: {e}")
        finally:
            cursor.close()
            conn.close()

    def limpiar_treeview(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def limpiar_campos(self):
        self.nombre.delete(0, 'end')
        self.cedula.delete(0, 'end')
        self.celular.delete(0, 'end')
        self.direccion.delete(0, 'end')
        self.correo.delete(0, 'end')

    def on_select(self, event):
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            values = self.tree.item(item, "values")
            self.limpiar_campos()
            if len(values) >= 6:
                self.nombre.insert(0, values[1])
                self.cedula.insert(0, values[2])
                self.celular.insert(0, values[3])
                self.direccion.insert(0, values[4])
                self.correo.insert(0, values[5])

    def modificar(self):
        if not self.tree.selection():
            messagebox.showerror("❌ Error", "Por favor seleccione un cliente para modificar")
            return
        
        item = self.tree.selection()[0]
        values = self.tree.item(item, "values")
        if not values:
            return

        id_cliente = values[0]
        nombre_actual = values[1]
        cedula_actual = values[2]
        celular_actual = values[3]
        direccion_actual = values[4]
        correo_actual = values[5]

        top_modificar = tk.Toplevel(self)
        top_modificar.title("✏️ Modificar Cliente")
        top_modificar.geometry("500x600+400+50")
        top_modificar.configure(bg=estilos.COLORS['white'])
        top_modificar.resizable(False, False)
        top_modificar.grab_set()
        top_modificar.focus_set()
        top_modificar.lift()

        title_label = tk.Label(top_modificar, text="✏️ Modificar Datos del Cliente", 
                              font=('Segoe UI', 16, 'bold'), 
                              bg=estilos.COLORS['white'],
                              fg=estilos.COLORS['primary'])
        title_label.pack(pady=20)

        main_frame = tk.Frame(top_modificar, bg=estilos.COLORS['white'])
        main_frame.pack(fill='both', expand=True, padx=30, pady=10)

        tk.Label(main_frame, text="👤 Nombre:", 
                font=('Segoe UI', 12, 'bold'), 
                bg=estilos.COLORS['white']).place(x=20, y=20)
        nombre_nuevo = tk.Entry(main_frame, font=('Segoe UI', 12), relief='solid', bd=1)
        nombre_nuevo.insert(0, nombre_actual)
        nombre_nuevo.place(x=20, y=50, width=400, height=35)

        tk.Label(main_frame, text="🆔 Cédula:", 
                font=('Segoe UI', 12, 'bold'), 
                bg=estilos.COLORS['white']).place(x=20, y=100)
        cedula_nuevo = tk.Entry(main_frame, font=('Segoe UI', 12), relief='solid', bd=1)
        cedula_nuevo.insert(0, cedula_actual)
        cedula_nuevo.place(x=20, y=130, width=400, height=35)

        tk.Label(main_frame, text="📱 Celular:", 
                font=('Segoe UI', 12, 'bold'), 
                bg=estilos.COLORS['white']).place(x=20, y=180)
        celular_nuevo = tk.Entry(main_frame, font=('Segoe UI', 12), relief='solid', bd=1)
        celular_nuevo.insert(0, celular_actual)
        celular_nuevo.place(x=20, y=210, width=400, height=35)

        tk.Label(main_frame, text="🏠 Dirección:", 
                font=('Segoe UI', 12, 'bold'), 
                bg=estilos.COLORS['white']).place(x=20, y=260)
        direccion_nuevo = tk.Entry(main_frame, font=('Segoe UI', 12), relief='solid', bd=1)
        direccion_nuevo.insert(0, direccion_actual)
        direccion_nuevo.place(x=20, y=290, width=400, height=35)

        tk.Label(main_frame, text="📧 Correo:", 
                font=('Segoe UI', 12, 'bold'), 
                bg=estilos.COLORS['white']).place(x=20, y=340)
        correo_nuevo = tk.Entry(main_frame, font=('Segoe UI', 12), relief='solid', bd=1)
        correo_nuevo.insert(0, correo_actual)
        correo_nuevo.place(x=20, y=370, width=400, height=35)

        def guardar_modificado():
            nuevo_nombre = nombre_nuevo.get().strip()
            nuevo_cedula = cedula_nuevo.get().strip()
            nuevo_celular = celular_nuevo.get().strip()
            nuevo_direccion = direccion_nuevo.get().strip()
            nuevo_correo = correo_nuevo.get().strip()

            if not all([nuevo_nombre, nuevo_cedula, nuevo_celular, nuevo_direccion, nuevo_correo]):
                messagebox.showerror("❌ Error", "Todos los campos son requeridos")
                return

            if '@' not in nuevo_correo or '.' not in nuevo_correo:
                messagebox.showerror("❌ Error", "El formato del correo no es válido")
                return

            conn = get_connection()
            if not conn:
                return
            cursor = conn.cursor()
            try:
                if nuevo_cedula != cedula_actual:
                    cursor.execute("SELECT id FROM clientes WHERE cedula = %s AND id != %s", 
                                 (nuevo_cedula, id_cliente))
                    if cursor.fetchone():
                        messagebox.showerror("❌ Error", "Ya existe otro cliente con esta cédula")
                        return
                
                cursor.execute("""UPDATE clientes SET nombre = %s, cedula = %s, celular = %s, 
                                direccion = %s, correo = %s WHERE id = %s""", 
                             (nuevo_nombre, nuevo_cedula, nuevo_celular, 
                              nuevo_direccion, nuevo_correo, id_cliente))
                conn.commit()
                messagebox.showinfo("✅ Éxito", "Cliente modificado correctamente")
                self.cargar_registros()
                top_modificar.destroy()
            except Exception as e:
                messagebox.showerror("❌ Error", f"No se pudo modificar el cliente: {e}")
            finally:
                cursor.close()
                conn.close()

        def eliminar_cliente():
            if messagebox.askyesno("⚠️ Confirmar Eliminación", 
                                  f"¿Estás seguro de que quieres eliminar al cliente '{nombre_actual}'?\n\nEsta acción no se puede deshacer."):
                conn = get_connection()
                if not conn:
                    return
                cursor = conn.cursor()
                try:
                    cursor.execute("DELETE FROM clientes WHERE id = %s", (id_cliente,))
                    conn.commit()
                    messagebox.showinfo("✅ Éxito", "Cliente eliminado correctamente")
                    self.limpiar_treeview()
                    self.limpiar_campos()
                    self.cargar_registros()
                    top_modificar.destroy()
                except Exception as e:
                    messagebox.showerror("❌ Error", f"No se pudo eliminar el cliente: {e}")
                finally:
                    cursor.close()
                    conn.close()

        btn_frame = tk.Frame(main_frame, bg=estilos.COLORS['white'])
        btn_frame.place(x=20, y=440, width=400, height=80)

        btn_guardar = ctk.CTkButton(btn_frame, text='💾 Guardar Cambios', 
                                   font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                                   command=guardar_modificado, width=180, height=40,
                                   fg_color=estilos.COLORS['success'],
                                   hover_color="#28a745")
        btn_guardar.pack(side='left', padx=5, pady=10)

        btn_eliminar = ctk.CTkButton(btn_frame, text='🗑️ Eliminar', 
                                    font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                                    command=eliminar_cliente, width=100, height=40,
                                    fg_color=estilos.COLORS['danger'],
                                    hover_color="#dc3545")
        btn_eliminar.pack(side='left', padx=5, pady=10)

        btn_cancelar = ctk.CTkButton(btn_frame, text='❌ Cancelar', 
                                    font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                                    command=top_modificar.destroy, width=100, height=40,
                                    fg_color=estilos.COLORS['secondary'],
                                    hover_color="#6c757d")
        btn_cancelar.pack(side='right', padx=5, pady=10)