import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
from modulos.utils.estilos_modernos import estilos
from data.models import get_connection   # <--- Conexión desde data.models

# Configurar CustomTkinter
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class ProveedorModerno(tk.Frame):
    
    def __init__(self, padre):
        super().__init__(padre, bg=estilos.COLORS['bg_primary'])
        # La tabla ya existe en models.py, no es necesario crearla aquí
        # self.crear_tabla_proveedores()  # <--- Eliminado
        self.widgets()
        self.cargar_registros()
    
    def actualizar_moneda(self, nueva_moneda):
        """Actualizar cuando cambia la moneda (proveedores no tiene precios)"""
        try:
            print(f"Módulo Proveedores actualizado a moneda: {nueva_moneda}")
        except Exception as e:
            print(f"Error al actualizar moneda en Proveedores: {e}")
    
    # ---------------------------------------------------------------------------------
    # (Opcional) Si quieres mantener el método por compatibilidad, lo dejas vacío
    def crear_tabla_proveedores(self):
        pass  # La tabla ya existe en la base de datos MySQL
    
    # ---------------------------------------------------------------------------------
    def widgets(self):
        # Frame principal de formulario con estilo moderno
        form_frame = tk.LabelFrame(self, text="🏢 Gestión de Proveedores", 
                                  font=('Segoe UI', 16, 'bold'), 
                                  bg=estilos.COLORS['white'],
                                  fg=estilos.COLORS['primary'])
        form_frame.place(x=20, y=20, width=300, height=700)

        # Título del formulario
        title_label = tk.Label(form_frame, text="📝 Datos del Proveedor", 
                              font=('Segoe UI', 14, 'bold'), 
                              bg=estilos.COLORS['white'],
                              fg=estilos.COLORS['secondary'])
        title_label.place(x=10, y=10)

        # Campo Empresa
        tk.Label(form_frame, text="🏢 Empresa:", 
                font=('Segoe UI', 12, 'bold'), 
                bg=estilos.COLORS['white'],
                fg=estilos.COLORS['dark']).place(x=10, y=50)
        
        self.empresa = tk.Entry(form_frame, font=('Segoe UI', 12), 
                               relief='solid', bd=1)
        self.empresa.place(x=10, y=80, width=270, height=35)

        # Campo RIF
        tk.Label(form_frame, text="🆔 RIF:", 
                font=('Segoe UI', 12, 'bold'), 
                bg=estilos.COLORS['white'],
                fg=estilos.COLORS['dark']).place(x=10, y=130)
        
        self.rif = tk.Entry(form_frame, font=('Segoe UI', 12), 
                           relief='solid', bd=1)
        self.rif.place(x=10, y=160, width=270, height=35)

        # Campo Celular
        tk.Label(form_frame, text="📱 Celular:", 
                font=('Segoe UI', 12, 'bold'), 
                bg=estilos.COLORS['white'],
                fg=estilos.COLORS['dark']).place(x=10, y=210)
        
        self.celular = tk.Entry(form_frame, font=('Segoe UI', 12), 
                               relief='solid', bd=1)
        self.celular.place(x=10, y=240, width=270, height=35)

        # Campo Dirección
        tk.Label(form_frame, text="🏠 Dirección:", 
                font=('Segoe UI', 12, 'bold'), 
                bg=estilos.COLORS['white'],
                fg=estilos.COLORS['dark']).place(x=10, y=290)
        
        self.direccion = tk.Entry(form_frame, font=('Segoe UI', 12), 
                                 relief='solid', bd=1)
        self.direccion.place(x=10, y=320, width=270, height=35)

        # Campo Correo
        tk.Label(form_frame, text="📧 Correo:", 
                font=('Segoe UI', 12, 'bold'), 
                bg=estilos.COLORS['white'],
                fg=estilos.COLORS['dark']).place(x=10, y=370)
        
        self.correo = tk.Entry(form_frame, font=('Segoe UI', 12), 
                              relief='solid', bd=1)
        self.correo.place(x=10, y=400, width=270, height=35)

        # Botones modernos con CustomTkinter
        btn_buscar = ctk.CTkButton(
            form_frame, 
            text="🔍 Buscar Proveedor", 
            command=self.buscar_proveedor,
            width=220,
            height=45,
            corner_radius=10,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color=estilos.COLORS['info'],
            hover_color="#0ea5e9"
        )
        btn_buscar.place(x=10, y=370)

        btn_registrar = ctk.CTkButton(
            form_frame, 
            text="➕ Registrar Proveedor", 
            command=self.registrar_proveedor,
            width=220,
            height=45,
            corner_radius=10,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color=estilos.COLORS['success'],
            hover_color="#28a745"
        )
        btn_registrar.place(x=10, y=420)

        # Frame para la tabla con estilo moderno
        table_frame = tk.LabelFrame(self, text="📋 Lista de Proveedores", 
                                   font=('Segoe UI', 16, 'bold'), 
                                   bg=estilos.COLORS['white'],
                                   fg=estilos.COLORS['primary'])
        table_frame.place(x=340, y=20, width=880, height=720)

        # Configurar Treeview con estilo moderno
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
                                columns=("ID", "Empresa", "RIF", "Celular", "Direccion", "Correo"), 
                                show="headings",
                                height=30)

        self.tree.pack(expand=True, fill='both', padx=10, pady=10)

        scrollbar_y.config(command=self.tree.yview)
        scrollbar_x.config(command=self.tree.xview)

        self.tree.heading("ID", text="🆔 ID")
        self.tree.heading("Empresa", text="🏢 Empresa")
        self.tree.heading("RIF", text="🆔 RIF")
        self.tree.heading("Celular", text="📱 Celular")
        self.tree.heading("Direccion", text="🏠 Dirección")
        self.tree.heading("Correo", text="📧 Correo")

        self.tree.column("ID", width=60, anchor="center")
        self.tree.column("Empresa", width=150, anchor="w")
        self.tree.column("RIF", width=120, anchor="center")
        self.tree.column("Celular", width=120, anchor="center")
        self.tree.column("Direccion", width=200, anchor="w")
        self.tree.column("Correo", width=200, anchor="w")

        # Bind para selección
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        self.tree.bind('<Double-1>', self.modificar_proveedor)

        # Frame de estadísticas
        stats_frame = tk.Frame(self, bg=estilos.COLORS['white'], relief='solid', bd=1)
        stats_frame.place(x=20, y=640, width=300, height=100)
        
        tk.Label(stats_frame, text="📊 Estadísticas", 
                font=('Segoe UI', 12, 'bold'), 
                bg=estilos.COLORS['white'],
                fg=estilos.COLORS['primary']).place(x=10, y=10)
        
        self.stats_label = tk.Label(stats_frame, text="Total de proveedores: 0", 
                                   font=('Segoe UI', 10), 
                                   bg=estilos.COLORS['white'],
                                   fg=estilos.COLORS['dark'])
        self.stats_label.place(x=10, y=40)

    # ---------------------------------------------------------------------------------
    def validar_campos(self):
        """Validar que todos los campos estén llenos"""
        if not all([self.empresa.get().strip(), 
                   self.rif.get().strip(), 
                   self.celular.get().strip(), 
                   self.direccion.get().strip(), 
                   self.correo.get().strip()]):
            messagebox.showerror("❌ Error", "Todos los campos son requeridos")
            return False
        
        # Validar formato de correo básico
        correo = self.correo.get().strip()
        if '@' not in correo or '.' not in correo:
            messagebox.showerror("❌ Error", "El formato del correo no es válido")
            return False
            
        return True

    # ---------------------------------------------------------------------------------
    def registrar_proveedor(self):
        """Registrar un nuevo proveedor (versión MySQL)"""
        if not self.validar_campos():
            return
        
        empresa = self.empresa.get().strip()
        rif = self.rif.get().strip()
        celular = self.celular.get().strip()
        direccion = self.direccion.get().strip()
        correo = self.correo.get().strip()

        conn = get_connection()
        if not conn:
            return
        cursor = conn.cursor()
        try:
            # Verificar si el RIF ya existe
            cursor.execute("SELECT id FROM proveedores WHERE rif = %s", (rif,))
            if cursor.fetchone():
                messagebox.showerror("❌ Error", "Ya existe un proveedor con este RIF")
                return
            
            cursor.execute("""INSERT INTO proveedores (empresa, rif, celular, direccion, correo) 
                            VALUES (%s, %s, %s, %s, %s)""", 
                          (empresa, rif, celular, direccion, correo))
            conn.commit()
            messagebox.showinfo("✅ Éxito", "Proveedor registrado correctamente")
            self.limpiar_treeview()
            self.limpiar_campos()
            self.cargar_registros()
        except Exception as e:
            messagebox.showerror("❌ Error", f"No se pudo registrar el proveedor: {e}")
        finally:
            cursor.close()
            conn.close()

    # ---------------------------------------------------------------------------------
    def buscar_proveedor(self):
        """Buscar proveedor por empresa o RIF (versión MySQL)"""
        termino_busqueda = self.empresa.get().strip() or self.rif.get().strip()
        
        if not termino_busqueda:
            messagebox.showwarning("⚠️ Advertencia", "Ingrese el nombre de la empresa o RIF para buscar")
            return
        
        conn = get_connection()
        if not conn:
            return
        cursor = conn.cursor()
        try:
            cursor.execute("""SELECT * FROM proveedores 
                            WHERE empresa LIKE %s OR rif LIKE %s""", 
                          (f"%{termino_busqueda}%", f"%{termino_busqueda}%"))
            resultados = cursor.fetchall()
            
            self.limpiar_treeview()
            if resultados:
                for row in resultados:
                    self.tree.insert("", "end", values=row)
                self.stats_label.config(text=f"Resultados encontrados: {len(resultados)}")
                messagebox.showinfo("🔍 Búsqueda", f"Se encontraron {len(resultados)} proveedor(es)")
            else:
                messagebox.showinfo("🔍 Búsqueda", "No se encontraron proveedores con ese criterio")
                self.cargar_registros()  # Recargar todos si no hay resultados
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error en la búsqueda: {e}")
        finally:
            cursor.close()
            conn.close()

    # ---------------------------------------------------------------------------------
    def cargar_registros(self):
        """Cargar todos los registros en el Treeview (versión MySQL)"""
        self.limpiar_treeview()  # Limpiar antes de cargar
        conn = get_connection()
        if not conn:
            return
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM proveedores ORDER BY empresa")
            rows = cursor.fetchall()
            for row in rows:
                self.tree.insert("", "end", values=row)
            self.stats_label.config(text=f"Total de proveedores: {len(rows)}")
        except Exception as e:
            messagebox.showerror("❌ Error", f"No se pudieron cargar los registros: {e}")
        finally:
            cursor.close()
            conn.close()

    # ---------------------------------------------------------------------------------
    def limpiar_treeview(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    # ---------------------------------------------------------------------------------
    def limpiar_campos(self):
        self.empresa.delete(0, 'end')
        self.rif.delete(0, 'end')
        self.celular.delete(0, 'end')
        self.direccion.delete(0, 'end')
        self.correo.delete(0, 'end')

    # ---------------------------------------------------------------------------------
    def on_select(self, event):
        """Manejar selección en el Treeview"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            values = self.tree.item(item, "values")
            self.limpiar_campos()
            if len(values) >= 6:
                self.empresa.insert(0, values[1])
                self.rif.insert(0, values[2])
                self.celular.insert(0, values[3])
                self.direccion.insert(0, values[4])
                self.correo.insert(0, values[5])

    # ---------------------------------------------------------------------------------
    def modificar_proveedor(self, event=None):
        """Modificar un proveedor existente (versión MySQL)"""
        if not self.tree.selection():
            messagebox.showerror("❌ Error", "Por favor seleccione un proveedor para modificar")
            return
        
        item = self.tree.selection()[0]
        values = self.tree.item(item, "values")
        if not values:
            return
            
        id_proveedor = values[0]

        # Crear ventana modal moderna para modificar
        top_modificar = tk.Toplevel(self)
        top_modificar.title("✏️ Modificar Proveedor")
        top_modificar.geometry("500x600+400+50")
        top_modificar.configure(bg=estilos.COLORS['white'])
        top_modificar.resizable(False, False)
        top_modificar.grab_set()
        top_modificar.focus_set()
        top_modificar.lift()

        title_label = tk.Label(top_modificar, text="✏️ Modificar Datos del Proveedor", 
                              font=('Segoe UI', 16, 'bold'), 
                              bg=estilos.COLORS['white'],
                              fg=estilos.COLORS['primary'])
        title_label.pack(pady=20)

        main_frame = tk.Frame(top_modificar, bg=estilos.COLORS['white'])
        main_frame.pack(fill='both', expand=True, padx=30, pady=10)

        # Campos de entrada con valores actuales
        tk.Label(main_frame, text="🏢 Empresa:", 
                font=('Segoe UI', 12, 'bold'), 
                bg=estilos.COLORS['white']).place(x=20, y=20)
        empresa_nuevo = tk.Entry(main_frame, font=('Segoe UI', 12), relief='solid', bd=1)
        empresa_nuevo.insert(0, values[1])
        empresa_nuevo.place(x=20, y=50, width=400, height=35)

        tk.Label(main_frame, text="🆔 RIF:", 
                font=('Segoe UI', 12, 'bold'), 
                bg=estilos.COLORS['white']).place(x=20, y=100)
        rif_nuevo = tk.Entry(main_frame, font=('Segoe UI', 12), relief='solid', bd=1)
        rif_nuevo.insert(0, values[2])
        rif_nuevo.place(x=20, y=130, width=400, height=35)

        tk.Label(main_frame, text="📱 Celular:", 
                font=('Segoe UI', 12, 'bold'), 
                bg=estilos.COLORS['white']).place(x=20, y=180)
        celular_nuevo = tk.Entry(main_frame, font=('Segoe UI', 12), relief='solid', bd=1)
        celular_nuevo.insert(0, values[3])
        celular_nuevo.place(x=20, y=210, width=400, height=35)

        tk.Label(main_frame, text="🏠 Dirección:", 
                font=('Segoe UI', 12, 'bold'), 
                bg=estilos.COLORS['white']).place(x=20, y=260)
        direccion_nuevo = tk.Entry(main_frame, font=('Segoe UI', 12), relief='solid', bd=1)
        direccion_nuevo.insert(0, values[4])
        direccion_nuevo.place(x=20, y=290, width=400, height=35)

        tk.Label(main_frame, text="📧 Correo:", 
                font=('Segoe UI', 12, 'bold'), 
                bg=estilos.COLORS['white']).place(x=20, y=340)
        correo_nuevo = tk.Entry(main_frame, font=('Segoe UI', 12), relief='solid', bd=1)
        correo_nuevo.insert(0, values[5])
        correo_nuevo.place(x=20, y=370, width=400, height=35)

        def guardar_modificado():
            """Guardar los cambios del proveedor"""
            nueva_empresa = empresa_nuevo.get().strip()
            nuevo_rif = rif_nuevo.get().strip()
            nuevo_celular = celular_nuevo.get().strip()
            nueva_direccion = direccion_nuevo.get().strip()
            nuevo_correo = correo_nuevo.get().strip()

            if not all([nueva_empresa, nuevo_rif, nuevo_celular, nueva_direccion, nuevo_correo]):
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
                # Verificar si el nuevo RIF ya existe en otro proveedor
                if nuevo_rif != values[2]:
                    cursor.execute("SELECT id FROM proveedores WHERE rif = %s AND id != %s", 
                                 (nuevo_rif, id_proveedor))
                    if cursor.fetchone():
                        messagebox.showerror("❌ Error", "Ya existe otro proveedor con este RIF")
                        return
                
                cursor.execute("""UPDATE proveedores SET empresa = %s, rif = %s, celular = %s, 
                                direccion = %s, correo = %s WHERE id = %s""", 
                             (nueva_empresa, nuevo_rif, nuevo_celular, 
                              nueva_direccion, nuevo_correo, id_proveedor))
                conn.commit()
                messagebox.showinfo("✅ Éxito", "Proveedor modificado correctamente")
                self.cargar_registros()
                top_modificar.destroy()
            except Exception as e:
                messagebox.showerror("❌ Error", f"No se pudo modificar el proveedor: {e}")
            finally:
                cursor.close()
                conn.close()

        def eliminar_proveedor():
            """Eliminar el proveedor seleccionado"""
            respuesta = messagebox.askyesno("⚠️ Confirmar Eliminación", 
                                          f"¿Estás seguro de que quieres eliminar al proveedor '{values[1]}'?\n\nEsta acción no se puede deshacer.")
            if respuesta:
                conn = get_connection()
                if not conn:
                    return
                cursor = conn.cursor()
                try:
                    cursor.execute("DELETE FROM proveedores WHERE id = %s", (id_proveedor,))
                    conn.commit()
                    messagebox.showinfo("✅ Éxito", "Proveedor eliminado correctamente")
                    self.limpiar_treeview()
                    self.limpiar_campos()
                    self.cargar_registros()
                    top_modificar.destroy()
                except Exception as e:
                    messagebox.showerror("❌ Error", f"No se pudo eliminar el proveedor: {e}")
                finally:
                    cursor.close()
                    conn.close()

        # Frame para botones
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
                                    command=eliminar_proveedor, width=100, height=40,
                                    fg_color=estilos.COLORS['danger'],
                                    hover_color="#dc3545")
        btn_eliminar.pack(side='left', padx=5, pady=10)

        btn_cancelar = ctk.CTkButton(btn_frame, text='❌ Cancelar', 
                                    font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                                    command=top_modificar.destroy, width=100, height=40,
                                    fg_color=estilos.COLORS['secondary'],
                                    hover_color="#6c757d")
        btn_cancelar.pack(side='right', padx=5, pady=10)