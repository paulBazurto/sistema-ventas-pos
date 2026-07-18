import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import customtkinter as ctk
from modulos.utils.estilos_modernos import estilos
from data.models import get_connection   # <--- Conexión desde data.models
import hashlib
from datetime import datetime

# Configurar CustomTkinter
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class GestorConfiguracion:
    def __init__(self, parent):
        self.parent = parent
        self.window = None
        self.modo_edicion = False
        self.usuario_editando_id = None
        # La tabla ya se crea en models.py, solo verificamos configuraciones por defecto
        self.crear_configuraciones_default()
        
    def crear_configuraciones_default(self):
        """Insertar configuraciones por defecto si no existen (MySQL)"""
        conn = get_connection()
        if not conn:
            return
        cursor = conn.cursor()
        try:
            configuraciones_default = [
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
            
            for clave, valor, descripcion in configuraciones_default:
                # Verificar si ya existe
                cursor.execute("SELECT id FROM configuracion_sistema WHERE clave = %s", (clave,))
                if not cursor.fetchone():
                    cursor.execute("""
                        INSERT INTO configuracion_sistema (clave, valor, descripcion, fecha_modificacion)
                        VALUES (%s, %s, %s, NOW())
                    """, (clave, valor, descripcion))
            conn.commit()
        except Exception as e:
            print(f"Error al insertar configuraciones por defecto: {e}")
        finally:
            cursor.close()
            conn.close()
    
    def abrir_ventana_configuracion(self):
        """Abrir ventana principal de configuración"""
        self.window = tk.Toplevel(self.parent)
        self.window.title("⚙️ Configuración del Sistema")
        self.window.geometry("1000x700+250+50")
        self.window.configure(bg=estilos.COLORS['bg_primary'])
        self.window.resizable(True, True)
        self.window.grab_set()
        self.window.focus_set()
        
        # Notebook para pestañas
        notebook = ttk.Notebook(self.window)
        notebook.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Pestaña 1: Usuarios
        self.crear_pestaña_usuarios(notebook)
        
        # Pestaña 2: Monedas
        self.crear_pestaña_monedas(notebook)
        
        # Pestaña 3: Empresa
        self.crear_pestaña_empresa(notebook)
    
    def crear_pestaña_usuarios(self, notebook):
        """Crear pestaña de gestión de usuarios"""
        frame_usuarios = tk.Frame(notebook, bg=estilos.COLORS['bg_primary'])
        notebook.add(frame_usuarios, text="👥 Usuarios")
        
        # Título
        title_label = tk.Label(frame_usuarios, text="👥 Gestión de Usuarios", 
                              font=('Segoe UI', 18, 'bold'), 
                              bg=estilos.COLORS['bg_primary'],
                              fg=estilos.COLORS['primary'])
        title_label.pack(pady=(20, 30))
        
        # Frame principal dividido
        main_frame = tk.Frame(frame_usuarios, bg=estilos.COLORS['bg_primary'])
        main_frame.pack(fill='both', expand=True, padx=20)
        
        # Frame izquierdo - Formulario
        self.form_frame_label = tk.LabelFrame(main_frame, text="➕ Nuevo Usuario", 
                                  font=('Segoe UI', 14, 'bold'), 
                                  bg=estilos.COLORS['white'],
                                  fg=estilos.COLORS['primary'])
        self.form_frame_label.pack(side='left', fill='y', padx=(0, 10), pady=10)
        
        # Campos del formulario
        tk.Label(self.form_frame_label, text="👤 Usuario:", font=('Segoe UI', 12, 'bold'), 
                bg=estilos.COLORS['white']).grid(row=0, column=0, sticky='w', padx=10, pady=5)
        self.nuevo_usuario = tk.Entry(self.form_frame_label, font=('Segoe UI', 11), width=20)
        self.nuevo_usuario.grid(row=0, column=1, padx=10, pady=5)
        
        tk.Label(self.form_frame_label, text="🔒 Contraseña:", font=('Segoe UI', 12, 'bold'), 
                bg=estilos.COLORS['white']).grid(row=1, column=0, sticky='w', padx=10, pady=5)
        self.nueva_password = tk.Entry(self.form_frame_label, font=('Segoe UI', 11), width=20, show="*")
        self.nueva_password.grid(row=1, column=1, padx=10, pady=5)
        
        tk.Label(self.form_frame_label, text="📝 Nombre:", font=('Segoe UI', 12, 'bold'), 
                bg=estilos.COLORS['white']).grid(row=2, column=0, sticky='w', padx=10, pady=5)
        self.nuevo_nombre = tk.Entry(self.form_frame_label, font=('Segoe UI', 11), width=20)
        self.nuevo_nombre.grid(row=2, column=1, padx=10, pady=5)
        
        # Frame para botones
        buttons_form_frame = tk.Frame(self.form_frame_label, bg=estilos.COLORS['white'])
        buttons_form_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        self.btn_crear_guardar = ctk.CTkButton(buttons_form_frame, text="➕ Crear Usuario", 
                                 command=self.crear_o_actualizar_usuario,
                                 width=180, height=40,
                                 font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                                 fg_color=estilos.COLORS['success'])
        self.btn_crear_guardar.pack(side='left', padx=5)
        
        self.btn_cancelar = ctk.CTkButton(buttons_form_frame, text="❌ Cancelar", 
                                 command=self.cancelar_edicion,
                                 width=100, height=40,
                                 font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                                 fg_color=estilos.COLORS['danger'])
        self.btn_cancelar.pack(side='left', padx=5)
        self.btn_cancelar.pack_forget()
        
        # Frame derecho - Lista de usuarios
        list_frame = tk.LabelFrame(main_frame, text="📋 Usuarios Registrados", 
                                  font=('Segoe UI', 14, 'bold'), 
                                  bg=estilos.COLORS['white'],
                                  fg=estilos.COLORS['primary'])
        list_frame.pack(side='right', fill='both', expand=True, padx=(10, 0), pady=10)
        
        # Treeview para usuarios
        self.tree_usuarios = ttk.Treeview(list_frame, 
                                         columns=("ID", "Usuario", "Nombre"), 
                                         show="headings", height=15)
        self.tree_usuarios.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.tree_usuarios.heading("ID", text="ID")
        self.tree_usuarios.heading("Usuario", text="Usuario")
        self.tree_usuarios.heading("Nombre", text="Nombre")
        
        self.tree_usuarios.column("ID", width=50, anchor="center")
        self.tree_usuarios.column("Usuario", width=150, anchor="w")
        self.tree_usuarios.column("Nombre", width=200, anchor="w")
        
        # Frame para botones de acción
        buttons_list_frame = tk.Frame(list_frame, bg=estilos.COLORS['white'])
        buttons_list_frame.pack(pady=10)
        
        btn_editar = ctk.CTkButton(buttons_list_frame, text="✏️ Editar Usuario", 
                                    command=self.editar_usuario,
                                    width=180, height=40,
                                    font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                                    fg_color=estilos.COLORS['info'])
        btn_editar.pack(side='left', padx=5)
        
        btn_eliminar = ctk.CTkButton(buttons_list_frame, text="🗑️ Eliminar Usuario", 
                                    command=self.eliminar_usuario,
                                    width=180, height=40,
                                    font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                                    fg_color=estilos.COLORS['danger'])
        btn_eliminar.pack(side='left', padx=5)
        
        self.tree_usuarios.bind('<Double-1>', lambda e: self.editar_usuario())
        self.cargar_usuarios()
    
    def crear_pestaña_monedas(self, notebook):
        """Crear pestaña de configuración de monedas"""
        frame_monedas = tk.Frame(notebook, bg=estilos.COLORS['bg_primary'])
        notebook.add(frame_monedas, text="💰 Monedas")
        
        title_label = tk.Label(frame_monedas, text="💰 Configuración de Monedas", 
                              font=('Segoe UI', 18, 'bold'), 
                              bg=estilos.COLORS['bg_primary'],
                              fg=estilos.COLORS['primary'])
        title_label.pack(pady=(20, 30))
        
        main_frame = tk.Frame(frame_monedas, bg=estilos.COLORS['bg_primary'])
        main_frame.pack(fill='both', expand=True, padx=40)
        
        # Configuración de moneda principal
        moneda_frame = tk.LabelFrame(main_frame, text="🏦 Moneda Principal", 
                                    font=('Segoe UI', 14, 'bold'), 
                                    bg=estilos.COLORS['white'],
                                    fg=estilos.COLORS['primary'])
        moneda_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(moneda_frame, text="💵 Moneda Principal:", font=('Segoe UI', 12, 'bold'), 
                bg=estilos.COLORS['white']).grid(row=0, column=0, sticky='w', padx=20, pady=15)
        
        self.moneda_principal = ttk.Combobox(moneda_frame, font=('Segoe UI', 11), 
                                           values=["USD", "VES"], state="readonly", width=10)
        self.moneda_principal.grid(row=0, column=1, padx=20, pady=15)
        
        # Tasa de cambio
        tasa_frame = tk.LabelFrame(main_frame, text="📈 Tasa de Cambio", 
                                  font=('Segoe UI', 14, 'bold'), 
                                  bg=estilos.COLORS['white'],
                                  fg=estilos.COLORS['primary'])
        tasa_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(tasa_frame, text="💱 1 USD = ", font=('Segoe UI', 12, 'bold'), 
                bg=estilos.COLORS['white']).grid(row=0, column=0, sticky='w', padx=20, pady=15)
        
        self.tasa_cambio = tk.Entry(tasa_frame, font=('Segoe UI', 11), width=15)
        self.tasa_cambio.grid(row=0, column=1, padx=5, pady=15)
        
        self.tasa_cambio.bind('<KeyRelease>', lambda e: self.actualizar_preview())
        self.moneda_principal.bind('<<ComboboxSelected>>', lambda e: self.actualizar_preview())
        
        tk.Label(tasa_frame, text="Bs.", font=('Segoe UI', 12, 'bold'), 
                bg=estilos.COLORS['white']).grid(row=0, column=2, sticky='w', padx=5, pady=15)
        
        # Opciones de visualización
        switch_frame = tk.LabelFrame(main_frame, text="🔄 Opciones de Visualización", 
                                    font=('Segoe UI', 14, 'bold'), 
                                    bg=estilos.COLORS['white'],
                                    fg=estilos.COLORS['primary'])
        switch_frame.pack(fill='x', pady=(0, 20))
        
        self.mostrar_ambas = tk.BooleanVar()
        switch_check = tk.Checkbutton(switch_frame, text="Mostrar precios en ambas monedas", 
                                     variable=self.mostrar_ambas,
                                     font=('Segoe UI', 12), 
                                     bg=estilos.COLORS['white'],
                                     command=self.actualizar_preview)
        switch_check.pack(padx=20, pady=15, anchor='w')
        
        # Botones
        buttons_frame = tk.Frame(main_frame, bg=estilos.COLORS['bg_primary'])
        buttons_frame.pack(fill='x', pady=20)
        
        btn_guardar = ctk.CTkButton(buttons_frame, text="💾 Guardar Configuración", 
                                   command=self.guardar_configuracion_monedas,
                                   width=200, height=45,
                                   font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                                   fg_color=estilos.COLORS['success'])
        btn_guardar.pack(side='left', padx=10)
        
        btn_actualizar_tasa = ctk.CTkButton(buttons_frame, text="💱 Ingresar Tasa del Día", 
                                           command=self.ingresar_tasa_dia,
                                           width=200, height=45,
                                           font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                                           fg_color=estilos.COLORS['info'])
        btn_actualizar_tasa.pack(side='left', padx=10)
        
        # Vista previa
        preview_frame = tk.LabelFrame(main_frame, text="👁️ Vista Previa", 
                                     font=('Segoe UI', 14, 'bold'), 
                                     bg=estilos.COLORS['white'],
                                     fg=estilos.COLORS['primary'])
        preview_frame.pack(fill='x')
        
        self.preview_label = tk.Label(preview_frame, text="Ejemplo: $10.00 = Bs. 365.00", 
                                     font=('Segoe UI', 12), 
                                     bg=estilos.COLORS['white'],
                                     fg=estilos.COLORS['dark'])
        self.preview_label.pack(pady=15)
        
        self.cargar_configuracion_monedas()
    
    def crear_pestaña_empresa(self, notebook):
        """Crear pestaña de información de la empresa"""
        frame_empresa = tk.Frame(notebook, bg=estilos.COLORS['bg_primary'])
        notebook.add(frame_empresa, text="🏢 Empresa")
        
        title_label = tk.Label(frame_empresa, text="🏢 Información de la Empresa", 
                              font=('Segoe UI', 18, 'bold'), 
                              bg=estilos.COLORS['bg_primary'],
                              fg=estilos.COLORS['primary'])
        title_label.pack(pady=(20, 30))
        
        main_frame = tk.LabelFrame(frame_empresa, text="📋 Datos de la Empresa", 
                                  font=('Segoe UI', 14, 'bold'), 
                                  bg=estilos.COLORS['white'],
                                  fg=estilos.COLORS['primary'])
        main_frame.pack(fill='both', expand=True, padx=40, pady=20)
        
        tk.Label(main_frame, text="🏢 Nombre:", font=('Segoe UI', 12, 'bold'), 
                bg=estilos.COLORS['white']).grid(row=0, column=0, sticky='w', padx=20, pady=15)
        self.nombre_empresa = tk.Entry(main_frame, font=('Segoe UI', 11), width=40)
        self.nombre_empresa.grid(row=0, column=1, padx=20, pady=15)
        
        tk.Label(main_frame, text="📍 Dirección:", font=('Segoe UI', 12, 'bold'), 
                bg=estilos.COLORS['white']).grid(row=1, column=0, sticky='w', padx=20, pady=15)
        self.direccion_empresa = tk.Entry(main_frame, font=('Segoe UI', 11), width=40)
        self.direccion_empresa.grid(row=1, column=1, padx=20, pady=15)
        
        tk.Label(main_frame, text="📞 Teléfono:", font=('Segoe UI', 12, 'bold'), 
                bg=estilos.COLORS['white']).grid(row=2, column=0, sticky='w', padx=20, pady=15)
        self.telefono_empresa = tk.Entry(main_frame, font=('Segoe UI', 11), width=40)
        self.telefono_empresa.grid(row=2, column=1, padx=20, pady=15)
        
        tk.Label(main_frame, text="🏢 RIF:", font=('Segoe UI', 12, 'bold'), 
                bg=estilos.COLORS['white']).grid(row=3, column=0, sticky='w', padx=20, pady=15)
        self.rif_empresa = tk.Entry(main_frame, font=('Segoe UI', 11), width=40)
        self.rif_empresa.grid(row=3, column=1, padx=20, pady=15)
        
        btn_guardar_empresa = ctk.CTkButton(main_frame, text="💾 Guardar Información", 
                                           command=self.guardar_info_empresa,
                                           width=250, height=45,
                                           font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                                           fg_color=estilos.COLORS['success'])
        btn_guardar_empresa.grid(row=4, column=0, columnspan=2, pady=30)
        
        self.cargar_info_empresa()
    
    # ==================== FUNCIONES DE USUARIOS ====================
    def crear_o_actualizar_usuario(self):
        usuario = self.nuevo_usuario.get().strip()
        password = self.nueva_password.get().strip()
        nombre = self.nuevo_nombre.get().strip()
        
        if not usuario:
            messagebox.showerror("❌ Error", "El campo Usuario es requerido")
            return
        
        if not self.modo_edicion and not password:
            messagebox.showerror("❌ Error", "El campo Contraseña es requerido para nuevos usuarios")
            return
        
        conn = get_connection()
        if not conn:
            return
        cursor = conn.cursor()
        try:
            if self.modo_edicion:
                if self.usuario_editando_id is None:
                    messagebox.showerror("❌ Error", "Error: No se ha seleccionado un usuario para editar")
                    return
                
                # Verificar si el nuevo nombre de usuario ya existe
                cursor.execute("SELECT id, username FROM usuarios WHERE username = %s", (usuario,))
                usuario_existente = cursor.fetchone()
                if usuario_existente and usuario_existente[0] != self.usuario_editando_id:
                    messagebox.showerror("❌ Error", "El nombre de usuario ya existe")
                    return
                
                # Obtener usuario actual
                cursor.execute("SELECT username FROM usuarios WHERE id = %s", (self.usuario_editando_id,))
                usuario_actual = cursor.fetchone()
                es_admin = usuario_actual and usuario_actual[0] == 'admin'
                
                if password:
                    password_hash = hashlib.sha256(password.encode()).hexdigest()
                    cursor.execute("UPDATE usuarios SET username = %s, password = %s WHERE id = %s",
                                  (usuario, password_hash, self.usuario_editando_id))
                else:
                    cursor.execute("UPDATE usuarios SET username = %s WHERE id = %s",
                                  (usuario, self.usuario_editando_id))
                
                conn.commit()
                mensaje_exito = f"Usuario '{usuario}' actualizado correctamente"
                if es_admin:
                    mensaje_exito += "\n\n⚠️ IMPORTANTE: Se han modificado las credenciales del usuario administrador."
                    if password:
                        mensaje_exito += "\n🔒 La nueva contraseña ha sido actualizada."
                messagebox.showinfo("✅ Éxito", mensaje_exito)
            else:
                if not password:
                    messagebox.showerror("❌ Error", "El campo Contraseña es requerido")
                    return
                
                cursor.execute("SELECT username FROM usuarios WHERE username = %s", (usuario,))
                if cursor.fetchone():
                    messagebox.showerror("❌ Error", "El usuario ya existe")
                    return
                
                password_hash = hashlib.sha256(password.encode()).hexdigest()
                cursor.execute("INSERT INTO usuarios (username, password) VALUES (%s, %s)",
                              (usuario, password_hash))
                conn.commit()
                messagebox.showinfo("✅ Éxito", f"Usuario '{usuario}' creado correctamente")
            
            self.cancelar_edicion()
            self.cargar_usuarios()
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al {'actualizar' if self.modo_edicion else 'crear'} usuario: {e}")
        finally:
            cursor.close()
            conn.close()
    
    def editar_usuario(self):
        selection = self.tree_usuarios.selection()
        if not selection:
            messagebox.showwarning("⚠️ Advertencia", "Seleccione un usuario para editar")
            return
        
        item = selection[0]
        valores = self.tree_usuarios.item(item, "values")
        usuario_id = int(valores[0])
        username = valores[1]
        
        if username == 'admin':
            respuesta = messagebox.askyesno(
                "⚠️ Advertencia de Seguridad",
                "Está intentando editar el usuario administrador.\n\n"
                "⚠️ IMPORTANTE:\n"
                "• Asegúrese de recordar la nueva contraseña.\n"
                "• Si olvida la contraseña, no podrá acceder al sistema.\n"
                "• Se recomienda crear un usuario alternativo antes de cambiar el admin.\n\n"
                "¿Desea continuar con la edición del usuario administrador?",
                icon='warning'
            )
            if not respuesta:
                return
        
        conn = get_connection()
        if not conn:
            return
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id, username FROM usuarios WHERE id = %s", (usuario_id,))
            usuario_data = cursor.fetchone()
            if not usuario_data:
                messagebox.showerror("❌ Error", "Usuario no encontrado")
                return
            
            self.modo_edicion = True
            self.usuario_editando_id = usuario_id
            
            self.nuevo_usuario.delete(0, 'end')
            self.nuevo_usuario.insert(0, usuario_data[1])
            self.nueva_password.delete(0, 'end')
            self.nuevo_nombre.delete(0, 'end')
            self.nuevo_nombre.insert(0, usuario_data[1])
            
            if username == 'admin':
                self.form_frame_label.config(text="⚠️ Editar Usuario Administrador")
                self.btn_crear_guardar.config(text="💾 Guardar Cambios", fg_color=estilos.COLORS['warning'])
            else:
                self.form_frame_label.config(text="✏️ Editar Usuario")
                self.btn_crear_guardar.config(text="💾 Guardar Cambios", fg_color=estilos.COLORS['info'])
            self.btn_cancelar.pack(side='left', padx=5)
            self.nuevo_usuario.focus()
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al cargar usuario: {e}")
        finally:
            cursor.close()
            conn.close()
    
    def cancelar_edicion(self):
        self.modo_edicion = False
        self.usuario_editando_id = None
        self.nuevo_usuario.delete(0, 'end')
        self.nueva_password.delete(0, 'end')
        self.nuevo_nombre.delete(0, 'end')
        self.form_frame_label.config(text="➕ Nuevo Usuario")
        self.btn_crear_guardar.config(text="➕ Crear Usuario", fg_color=estilos.COLORS['success'])
        self.btn_cancelar.pack_forget()
        for item in self.tree_usuarios.selection():
            self.tree_usuarios.selection_remove(item)
    
    def eliminar_usuario(self):
        selection = self.tree_usuarios.selection()
        if not selection:
            messagebox.showwarning("⚠️ Advertencia", "Seleccione un usuario para eliminar")
            return
        
        item = selection[0]
        valores = self.tree_usuarios.item(item, "values")
        usuario_id = valores[0]
        username = valores[1]
        
        if username == 'admin':
            messagebox.showerror("❌ Error", "No se puede eliminar el usuario administrador")
            return
        
        respuesta = messagebox.askyesno("⚠️ Confirmar", 
                                      f"¿Eliminar el usuario '{username}'?\n\nEsta acción no se puede deshacer.")
        if respuesta:
            conn = get_connection()
            if not conn:
                return
            cursor = conn.cursor()
            try:
                cursor.execute("DELETE FROM usuarios WHERE id = %s", (usuario_id,))
                conn.commit()
                messagebox.showinfo("✅ Éxito", f"Usuario '{username}' eliminado")
                self.cargar_usuarios()
            except Exception as e:
                messagebox.showerror("❌ Error", f"Error al eliminar usuario: {e}")
            finally:
                cursor.close()
                conn.close()
    
    def cargar_usuarios(self):
        for item in self.tree_usuarios.get_children():
            self.tree_usuarios.delete(item)
        
        conn = get_connection()
        if not conn:
            return
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id, username FROM usuarios ORDER BY username")
            usuarios = cursor.fetchall()
            for usuario in usuarios:
                self.tree_usuarios.insert("", "end", values=(usuario[0], usuario[1], usuario[1]))
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al cargar usuarios: {e}")
        finally:
            cursor.close()
            conn.close()
    
    # ==================== FUNCIONES DE MONEDAS ====================
    def cargar_configuracion_monedas(self):
        conn = get_connection()
        if not conn:
            return
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT clave, valor FROM configuracion_sistema WHERE clave IN ('moneda_principal', 'tasa_cambio', 'mostrar_ambas_monedas')")
            configs = dict(cursor.fetchall())
            self.moneda_principal.set(configs.get('moneda_principal', 'USD'))
            self.tasa_cambio.delete(0, 'end')
            self.tasa_cambio.insert(0, configs.get('tasa_cambio', '36.50'))
            self.mostrar_ambas.set(configs.get('mostrar_ambas_monedas', '1') == '1')
            self.actualizar_preview()
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al cargar configuración: {e}")
        finally:
            cursor.close()
            conn.close()
    
    def guardar_configuracion_monedas(self):
        try:
            tasa = float(self.tasa_cambio.get())
            if tasa <= 0:
                raise ValueError("La tasa debe ser mayor a 0")
        except ValueError:
            messagebox.showerror("❌ Error", "Ingrese una tasa de cambio válida")
            return
        
        conn = get_connection()
        if not conn:
            return
        cursor = conn.cursor()
        try:
            configs = [
                ('moneda_principal', self.moneda_principal.get()),
                ('tasa_cambio', self.tasa_cambio.get()),
                ('mostrar_ambas_monedas', '1' if self.mostrar_ambas.get() else '0')
            ]
            
            for clave, valor in configs:
                cursor.execute("""
                    INSERT INTO configuracion_sistema (clave, valor, descripcion, fecha_modificacion)
                    VALUES (%s, %s, %s, NOW())
                    ON DUPLICATE KEY UPDATE valor = VALUES(valor), fecha_modificacion = VALUES(fecha_modificacion)
                """, (clave, valor, f'Configuración de {clave}'))
            
            conn.commit()
            cursor.execute("SELECT valor FROM configuracion_sistema WHERE clave = 'tasa_cambio'")
            tasa_guardada = cursor.fetchone()
            messagebox.showinfo("✅ Éxito", f"Configuración guardada correctamente\n\nTasa de cambio: {tasa_guardada[0] if tasa_guardada else 'Error'}")
            self.actualizar_preview()
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al guardar configuración: {e}")
        finally:
            cursor.close()
            conn.close()
    
    def ingresar_tasa_dia(self):
        tasa_actual = self.tasa_cambio.get()
        try:
            valor_inicial = float(tasa_actual) if tasa_actual else 36.50
        except:
            valor_inicial = 36.50
        
        nueva_tasa = simpledialog.askfloat(
            "💱 Tasa del Día",
            f"Ingrese la tasa de cambio actual:\n\n" +
            f"Tasa actual: {tasa_actual} Bs. por USD\n\n" +
            f"Nueva tasa (solo números):",
            initialvalue=valor_inicial,
            minvalue=1.0,
            maxvalue=1000.0
        )
        
        if nueva_tasa:
            try:
                self.tasa_cambio.delete(0, 'end')
                self.tasa_cambio.insert(0, str(nueva_tasa))
                self.actualizar_preview()
                messagebox.showinfo("✅ Tasa Actualizada", 
                                   f"Nueva tasa ingresada:\n\n" +
                                   f"💱 1 USD = {nueva_tasa} Bs.\n\n" +
                                   f"📅 Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n" +
                                   "⚠️ Recuerde guardar la configuración para aplicar los cambios.")
            except Exception as e:
                messagebox.showerror("❌ Error", f"Error al actualizar tasa: {e}")
    
    def actualizar_preview(self):
        try:
            tasa = float(self.tasa_cambio.get())
            ejemplo_usd = 1.00
            ejemplo_ves = ejemplo_usd * tasa
            
            if self.mostrar_ambas.get():
                preview_text = f"Ejemplo: ${ejemplo_usd:.2f} = Bs. {ejemplo_ves:,.2f} (Ambas monedas)"
            else:
                moneda = self.moneda_principal.get()
                if moneda == 'USD':
                    preview_text = f"Ejemplo: ${ejemplo_usd:.2f} (Solo USD)"
                else:
                    preview_text = f"Ejemplo: Bs. {ejemplo_ves:,.2f} (Solo VES)"
            
            self.preview_label.config(text=preview_text)
        except:
            self.preview_label.config(text="Vista previa no disponible")
    
    # ==================== FUNCIONES DE EMPRESA ====================
    def cargar_info_empresa(self):
        conn = get_connection()
        if not conn:
            return
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT clave, valor FROM configuracion_sistema WHERE clave IN ('nombre_empresa', 'direccion_empresa', 'telefono_empresa', 'rif_empresa')")
            configs = dict(cursor.fetchall())
            
            self.nombre_empresa.delete(0, 'end')
            self.nombre_empresa.insert(0, configs.get('nombre_empresa', 'Mi Tienda'))
            self.direccion_empresa.delete(0, 'end')
            self.direccion_empresa.insert(0, configs.get('direccion_empresa', 'Caracas, Venezuela'))
            self.telefono_empresa.delete(0, 'end')
            self.telefono_empresa.insert(0, configs.get('telefono_empresa', '+58-212-1234567'))
            self.rif_empresa.delete(0, 'end')
            self.rif_empresa.insert(0, configs.get('rif_empresa', 'J-00000000-0'))
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al cargar información: {e}")
        finally:
            cursor.close()
            conn.close()
    
    def guardar_info_empresa(self):
        conn = get_connection()
        if not conn:
            return
        cursor = conn.cursor()
        try:
            configs = [
                ('nombre_empresa', self.nombre_empresa.get()),
                ('direccion_empresa', self.direccion_empresa.get()),
                ('telefono_empresa', self.telefono_empresa.get()),
                ('rif_empresa', self.rif_empresa.get())
            ]
            
            for clave, valor in configs:
                cursor.execute("""
                    INSERT INTO configuracion_sistema (clave, valor, descripcion, fecha_modificacion)
                    VALUES (%s, %s, %s, NOW())
                    ON DUPLICATE KEY UPDATE valor = VALUES(valor), fecha_modificacion = VALUES(fecha_modificacion)
                """, (clave, valor, f'Configuración de {clave}'))
            
            conn.commit()
            messagebox.showinfo("✅ Éxito", "Información de la empresa guardada correctamente")
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al guardar información: {e}")
        finally:
            cursor.close()
            conn.close()


# ==================== FUNCIONES GLOBALES ====================
def obtener_configuracion(clave, default=None):
    """Obtener valor de configuración desde MySQL"""
    conn = get_connection()
    if not conn:
        return default
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT valor FROM configuracion_sistema WHERE clave = %s", (clave,))
        resultado = cursor.fetchone()
        return resultado[0] if resultado else default
    except Exception:
        return default
    finally:
        cursor.close()
        conn.close()

def formatear_precio(precio, mostrar_ambas=None):
    """
    Formatear precio según configuración de monedas.
    Si mostrar_ambas no se proporciona, se obtiene de la BD.
    """
    try:
        if mostrar_ambas is None:
            mostrar_ambas = obtener_configuracion('mostrar_ambas_monedas', '1') == '1'
        
        moneda_principal = obtener_configuracion('moneda_principal', 'USD')
        tasa_cambio = float(obtener_configuracion('tasa_cambio', '36.50'))
        
        precio_float = float(precio)
        
        if mostrar_ambas:
            if moneda_principal == 'USD':
                precio_ves = precio_float * tasa_cambio
                return f"${precio_float:.2f} (Bs. {precio_ves:,.2f})"
            else:
                precio_usd = precio_float / tasa_cambio
                return f"Bs. {precio_float:,.2f} (${precio_usd:.2f})"
        else:
            if moneda_principal == 'USD':
                return f"${precio_float:.2f}"
            else:
                return f"Bs. {precio_float:,.2f}"
    except:
        return f"${precio:.2f}"