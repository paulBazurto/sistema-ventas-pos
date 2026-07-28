import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import customtkinter as ctk
from modulos.utils.estilos_modernos import estilos
from data.models import get_connection
import hashlib
from datetime import datetime
from modulos.biometrico.face_auth import FaceAuthenticator
import cv2
from PIL import Image, ImageTk
from tkinter import Toplevel, Label
import math
import mediapipe as mp
import numpy as np
import face_recognition as fr
import os

# ================= CONFIGURACIÓN DE MEDIAPIPE =================
# Importación única y correcta para la versión instalada (0.10.13)
mp_drawing = mp.solutions.drawing_utils
FacemeshObject = mp.solutions.face_mesh
FaceObject = mp.solutions.face_detection
FaceMesh = FacemeshObject.FaceMesh(max_num_faces=1)
detector = FaceObject.FaceDetection(min_detection_confidence=0.5, model_selection=1)
ConfigDraw = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)

# ================= CARGAR IMÁGENES DE LA CARPETA SetUp =================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))          # modulos/configuracion/
SETUP_DIR = os.path.join(os.path.dirname(os.path.dirname(BASE_DIR)), 'SetUp')

def load_image(name):
    path = os.path.join(SETUP_DIR, name)
    img = cv2.imread(path)
    if img is None:
        print(f"⚠️ No se encontró {path}")
    return img

img_check = load_image('check.png')
img_step0 = load_image('Step0.png')
img_step1 = load_image('Step1.png')
img_step2 = load_image('Step2.png')
img_liche = load_image('LivenessCheck.png')

# Variables globales para el bucle de registro
cap = None
lblVideo = None
ventana_camara = None
step = 0
conteo = 0
parpadeo = False
current_user_id = None

# ================= CLASE GESTORCONFIGURACION =================
class GestorConfiguracion:
    def __init__(self, parent):
        self.parent = parent
        self.window = None
        self.modo_edicion = False
        self.usuario_editando_id = None
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
        self.window = tk.Toplevel(self.parent)
        self.window.title("⚙️ Configuración del Sistema")
        self.window.geometry("1000x700+250+50")
        self.window.configure(bg=estilos.COLORS['bg_primary'])
        self.window.resizable(True, True)
        self.window.grab_set()
        self.window.focus_set()
        
        notebook = ttk.Notebook(self.window)
        notebook.pack(fill='both', expand=True, padx=20, pady=20)
        
        self.crear_pestaña_usuarios(notebook)
        self.crear_pestaña_monedas(notebook)
        self.crear_pestaña_empresa(notebook)
    
    def crear_pestaña_usuarios(self, notebook):
        frame_usuarios = tk.Frame(notebook, bg=estilos.COLORS['bg_primary'])
        notebook.add(frame_usuarios, text="👥 Usuarios")
        
        title_label = tk.Label(frame_usuarios, text="👥 Gestión de Usuarios", 
                              font=('Segoe UI', 18, 'bold'), 
                              bg=estilos.COLORS['bg_primary'],
                              fg=estilos.COLORS['primary'])
        title_label.pack(pady=(20, 30))
        
        main_frame = tk.Frame(frame_usuarios, bg=estilos.COLORS['bg_primary'])
        main_frame.pack(fill='both', expand=True, padx=20)
        
        # Formulario izquierdo
        self.form_frame_label = tk.LabelFrame(main_frame, text="➕ Nuevo Usuario", 
                                  font=('Segoe UI', 14, 'bold'), 
                                  bg=estilos.COLORS['white'],
                                  fg=estilos.COLORS['primary'])
        self.form_frame_label.pack(side='left', fill='y', padx=(0, 10), pady=10)
        
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
        
        # Lista de usuarios
        list_frame = tk.LabelFrame(main_frame, text="📋 Usuarios Registrados", 
                                  font=('Segoe UI', 14, 'bold'), 
                                  bg=estilos.COLORS['white'],
                                  fg=estilos.COLORS['primary'])
        list_frame.pack(side='right', fill='both', expand=True, padx=(10, 0), pady=10)
        
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
        
        btn_rostro = ctk.CTkButton(buttons_list_frame, text="😀 Registrar Rostro", 
                                   command=self.registrar_rostro_usuario,
                                   width=180, height=40,
                                   font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                                   fg_color=estilos.COLORS['secondary'])
        btn_rostro.pack(side='left', padx=5)
        
        self.tree_usuarios.bind('<Double-1>', lambda e: self.editar_usuario())
        self.cargar_usuarios()
    
    def crear_pestaña_monedas(self, notebook):
        frame_monedas = tk.Frame(notebook, bg=estilos.COLORS['bg_primary'])
        notebook.add(frame_monedas, text="💰 Monedas")
        
        title_label = tk.Label(frame_monedas, text="💰 Configuración de Monedas", 
                              font=('Segoe UI', 18, 'bold'), 
                              bg=estilos.COLORS['bg_primary'],
                              fg=estilos.COLORS['primary'])
        title_label.pack(pady=(20, 30))
        
        main_frame = tk.Frame(frame_monedas, bg=estilos.COLORS['bg_primary'])
        main_frame.pack(fill='both', expand=True, padx=40)
        
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
            messagebox.showerror("❌ Error", "La contraseña es requerida para nuevos usuarios")
            return
        conn = get_connection()
        if not conn:
            return
        cursor = conn.cursor()
        try:
            if self.modo_edicion:
                if self.usuario_editando_id is None:
                    messagebox.showerror("❌ Error", "No se ha seleccionado un usuario para editar")
                    return
                cursor.execute("SELECT id, username FROM usuarios WHERE username = %s", (usuario,))
                usuario_existente = cursor.fetchone()
                if usuario_existente and usuario_existente[0] != self.usuario_editando_id:
                    messagebox.showerror("❌ Error", "El nombre de usuario ya existe")
                    return
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
                mensaje = f"Usuario '{usuario}' actualizado correctamente"
                if es_admin:
                    mensaje += "\n⚠️ Se modificaron credenciales del administrador."
                messagebox.showinfo("✅ Éxito", mensaje)
            else:
                if not password:
                    messagebox.showerror("❌ Error", "La contraseña es requerida")
                    return
                cursor.execute("SELECT username FROM usuarios WHERE username = %s", (usuario,))
                if cursor.fetchone():
                    messagebox.showerror("❌ Error", "El usuario ya existe")
                    return
                password_hash = hashlib.sha256(password.encode()).hexdigest()
                cursor.execute("INSERT INTO usuarios (username, password) VALUES (%s, %s)",
                              (usuario, password_hash))
                conn.commit()
                messagebox.showinfo("✅ Éxito", f"Usuario '{usuario}' creado")
            self.cancelar_edicion()
            self.cargar_usuarios()
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error: {e}")
        finally:
            cursor.close()
            conn.close()
    
    def editar_usuario(self):
        selection = self.tree_usuarios.selection()
        if not selection:
            messagebox.showwarning("⚠️ Advertencia", "Seleccione un usuario")
            return
        item = selection[0]
        valores = self.tree_usuarios.item(item, "values")
        usuario_id = int(valores[0])
        username = valores[1]
        if username == 'admin':
            if not messagebox.askyesno("⚠️ Seguridad", "¿Editar al administrador? Continuar?"):
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
                self.form_frame_label.config(text="⚠️ Editar Administrador")
                self.btn_crear_guardar.config(text="💾 Guardar", fg_color=estilos.COLORS['warning'])
            else:
                self.form_frame_label.config(text="✏️ Editar Usuario")
                self.btn_crear_guardar.config(text="💾 Guardar", fg_color=estilos.COLORS['info'])
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
            messagebox.showwarning("⚠️ Advertencia", "Seleccione un usuario")
            return
        item = selection[0]
        valores = self.tree_usuarios.item(item, "values")
        usuario_id = valores[0]
        username = valores[1]
        if username == 'admin':
            messagebox.showerror("❌ Error", "No se puede eliminar al administrador")
            return
        if messagebox.askyesno("⚠️ Confirmar", f"¿Eliminar usuario '{username}'?"):
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
                messagebox.showerror("❌ Error", f"Error: {e}")
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
    
    # =============== REGISTRO FACIAL CON LIVENESS ===============
  
    def registrar_rostro_usuario(self):
        global cap, lblVideo, ventana_camara, step, conteo, parpadeo, current_user_id
        
        selection = self.tree_usuarios.selection()
        if not selection:
            messagebox.showwarning("⚠️ Advertencia", "Seleccione un usuario de la lista")
            return
        
        item = selection[0]
        valores = self.tree_usuarios.item(item, "values")
        usuario_id = int(valores[0])
        username = valores[1]
        
        conn = get_connection()
        if not conn:
            messagebox.showerror("❌ Error", "No se pudo conectar a la base de datos")
            return
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id FROM rostros WHERE usuario_id = %s", (usuario_id,))
            if cursor.fetchone():
                if not messagebox.askyesno("⚠️ Rostro existente",
                                          f"El usuario '{username}' ya tiene un rostro.\n¿Reemplazarlo?"):
                    return
                cursor.execute("DELETE FROM rostros WHERE usuario_id = %s", (usuario_id,))
                conn.commit()
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al verificar rostro: {e}")
            return
        finally:
            cursor.close()
            conn.close()
        
        step = 0
        conteo = 0
        parpadeo = False
        current_user_id = usuario_id
        
        ventana_camara = Toplevel(self.window)
        ventana_camara.title(f"📸 Registro Facial - {username}")
        ventana_camara.geometry("800x600")
        ventana_camara.configure(bg='black')
        ventana_camara.grab_set()
        ventana_camara.focus_set()
        
        lblVideo = Label(ventana_camara, bg='black')
        lblVideo.pack(expand=True, fill='both')
        
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        cap.set(3, 1280)
        cap.set(4, 720)
        if not cap.isOpened():
            messagebox.showerror("Error", "No se pudo abrir la cámara")
            ventana_camara.destroy()
            return
        
        auth = FaceAuthenticator()
        
        def cerrar_camara():
            if cap is not None:
                cap.release()
            ventana_camara.destroy()
        
        def bucle_registro():
            global cap, lblVideo, step, conteo, parpadeo, current_user_id
            
            ret, frame = cap.read()
            if not ret:
                lblVideo.after(30, bucle_registro)
                return
            
            frame_save = frame.copy()
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            res = FaceMesh.process(frame_rgb)
            if res.multi_face_landmarks:
                for rostros in res.multi_face_landmarks:
                    mp_drawing.draw_landmarks(frame, rostros, FacemeshObject.FACEMESH_TESSELATION, ConfigDraw, ConfigDraw)
                    
                    lista = []
                    for id, puntos in enumerate(rostros.landmark):
                        al, an, _ = frame.shape
                        x, y = int(puntos.x * an), int(puntos.y * al)
                        lista.append([id, x, y])
                    
                    if len(lista) == 468:
                        x1, y1 = lista[145][1], lista[145][2]
                        x2, y2 = lista[159][1], lista[159][2]
                        longitud1 = math.hypot(x2 - x1, y2 - y1)
                        x3, y3 = lista[374][1], lista[374][2]
                        x4, y4 = lista[386][1], lista[386][2]
                        longitud2 = math.hypot(x4 - x3, y4 - y3)
                        x5, y5 = lista[139][1], lista[139][2]
                        x6, y6 = lista[368][1], lista[368][2]
                        x7, y7 = lista[70][1], lista[70][2]
                        x8, y8 = lista[300][1], lista[300][2]
                        
                        faces = detector.process(frame_rgb)
                        if faces.detections is not None:
                            for face in faces.detections:
                                score = face.score[0]
                                bbox = face.location_data.relative_bounding_box
                                if score > 0.5:
                                    alimg, animg, _ = frame.shape
                                    xi = int(bbox.xmin * animg)
                                    yi = int(bbox.ymin * alimg)
                                    an = int(bbox.width * animg)
                                    al = int(bbox.height * alimg)
                                    offsetan = (20 / 100) * an
                                    xi = int(xi - offsetan/2)
                                    an = int(an + offsetan)
                                    offsetal = (30 / 100) * al
                                    yi = int(yi - offsetal)
                                    al = int(al + offsetal)
                                    if xi < 0: xi = 0
                                    if yi < 0: yi = 0
                                    
                                    if step == 0:
                                        cv2.rectangle(frame, (xi, yi, an, al), (255, 0, 255), 2)
                                        if img_step0 is not None:
                                            h, w, _ = img_step0.shape
                                            frame[50:50+h, 50:50+w] = img_step0
                                        if img_step1 is not None:
                                            h, w, _ = img_step1.shape
                                            frame[50:50+h, 1030:1030+w] = img_step1
                                        if img_step2 is not None:
                                            h, w, _ = img_step2.shape
                                            frame[270:270+h, 1030:1030+w] = img_step2
                                        
                                        if x7 > x5 and x8 < x6:
                                            if longitud1 <= 10 and longitud2 <= 10 and not parpadeo:
                                                conteo += 1
                                                parpadeo = True
                                            elif longitud1 > 10 and longitud2 > 10 and parpadeo:
                                                parpadeo = False
                                            
                                            if img_check is not None:
                                                h, w, _ = img_check.shape
                                                frame[165:165+h, 1105:1105+w] = img_check
                                            cv2.putText(frame, f'Parpadeos: {int(conteo)}', (1070, 375),
                                                       cv2.FONT_HERSHEY_COMPLEX, 0.5, (255,255,255), 1)
                                            
                                            if conteo >= 3:
                                                if img_check is not None:
                                                    h, w, _ = img_check.shape
                                                    frame[385:385+h, 1105:1105+w] = img_check
                                                if longitud1 > 14 and longitud2 > 14:
                                                    # Construir bbox en formato (top, bottom, left, right)
                                                    bbox = (yi, yi + al, xi, xi + an)
                                                    exito, mensaje = auth.registrar_rostro_con_bbox(current_user_id, frame_save, bbox)
                                                    if exito:
                                                        messagebox.showinfo("✅ Éxito", mensaje)
                                                        cap.release()
                                                        ventana_camara.destroy()
                                                        self.cargar_usuarios()
                                                        return
                                                    else:
                                                        messagebox.showerror("❌ Error", mensaje)
                                                        step = 0
                                                        conteo = 0
                                    else:
                                        conteo = 0
            
            frame = cv2.resize(frame, (800, 600))
            im = Image.fromarray(frame)
            img_tk = ImageTk.PhotoImage(im)
            lblVideo.configure(image=img_tk)
            lblVideo.image = img_tk
            lblVideo.after(10, bucle_registro)
        
        btn_cancelar = ctk.CTkButton(ventana_camara, text="❌ Cancelar", command=cerrar_camara,
                                     font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                                     width=100, height=30, fg_color="red")
        btn_cancelar.place(x=10, y=10)
        
        ventana_camara.protocol("WM_DELETE_WINDOW", cerrar_camara)
        bucle_registro()
        
        
        
    
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
                raise ValueError
        except:
            messagebox.showerror("❌ Error", "Ingrese una tasa válida")
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
            messagebox.showinfo("✅ Éxito", "Configuración guardada")
            self.actualizar_preview()
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al guardar: {e}")
        finally:
            cursor.close()
            conn.close()
    
    def ingresar_tasa_dia(self):
        tasa_actual = self.tasa_cambio.get()
        try:
            valor_inicial = float(tasa_actual) if tasa_actual else 36.50
        except:
            valor_inicial = 36.50
        nueva_tasa = simpledialog.askfloat("💱 Tasa del Día", 
            f"Ingrese la tasa actual:\nTasa actual: {tasa_actual} Bs.\nNueva tasa:", 
            initialvalue=valor_inicial, minvalue=1.0, maxvalue=1000.0)
        if nueva_tasa:
            self.tasa_cambio.delete(0, 'end')
            self.tasa_cambio.insert(0, str(nueva_tasa))
            self.actualizar_preview()
            messagebox.showinfo("✅ Tasa Actualizada", f"1 USD = {nueva_tasa} Bs.\nRecuerde guardar.")
    
    def actualizar_preview(self):
        try:
            tasa = float(self.tasa_cambio.get())
            ejemplo_usd = 1.00
            ejemplo_ves = ejemplo_usd * tasa
            if self.mostrar_ambas.get():
                preview_text = f"Ejemplo: ${ejemplo_usd:.2f} = Bs. {ejemplo_ves:,.2f} (Ambas)"
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
            messagebox.showinfo("✅ Éxito", "Información guardada")
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al guardar: {e}")
        finally:
            cursor.close()
            conn.close()


# ==================== FUNCIONES GLOBALES ====================
def obtener_configuracion(clave, default=None):
    conn = get_connection()
    if not conn:
        return default
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT valor FROM configuracion_sistema WHERE clave = %s", (clave,))
        resultado = cursor.fetchone()
        return resultado[0] if resultado else default
    except:
        return default
    finally:
        cursor.close()
        conn.close()

def formatear_precio(precio, mostrar_ambas=None):
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