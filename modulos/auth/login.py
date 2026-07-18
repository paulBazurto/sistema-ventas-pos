import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from modulos.utils.estilos_modernos import estilos
import hashlib
from data.models import get_connection  # Importar la conexión MySQL

# Configurar CustomTkinter
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class LoginWindow:
    def __init__(self):
        self.window = None
        self.usuario_autenticado = False
        # No creamos tablas aquí, ya se crean en models.py
        # Solo aseguramos que el usuario admin exista (opcional)
        self.asegurar_usuario_admin()
        
    def asegurar_usuario_admin(self):
        """Verificar que el usuario admin exista en la base de datos MySQL"""
        try:
            conn = get_connection()
            if not conn:
                return
            cursor = conn.cursor()
            # Verificar si existe admin
            cursor.execute("SELECT id FROM usuarios WHERE username = %s", ('admin',))
            if not cursor.fetchone():
                password_hash = hashlib.sha256('admin123'.encode()).hexdigest()
                cursor.execute("INSERT INTO usuarios (username, password) VALUES (%s, %s)", ('admin', password_hash))
                conn.commit()
                print("✅ Usuario admin creado en MySQL: admin/admin123")
            conn.close()
        except Exception as e:
            print(f"❌ Error al asegurar usuario admin: {e}")
    
    def hash_password(self, password):
        """Hashear password con SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verificar_credenciales(self, usuario, password):
        """Verificar credenciales del usuario en MySQL"""
        try:
            conn = get_connection()
            if not conn:
                return None
            cursor = conn.cursor()
            
            password_hash = self.hash_password(password)
            
            # Buscar usuario por username y comparar password hasheada
            cursor.execute("SELECT id, username, password FROM usuarios WHERE username = %s", (usuario,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                user_id, username_db, password_db = row
                # Comparar con hash
                if password_db == password_hash:
                    # Obtener rol (si existe columna rol, sino devolver 'admin' por defecto)
                    # Para simplificar, asumimos que el usuario admin tiene rol 'admin'
                    rol = 'admin' if username_db == 'admin' else 'usuario'
                    return (user_id, username_db, rol)
                else:
                    # Si la contraseña no coincide con hash, probar en texto plano (por si acaso)
                    if password_db == password:
                        rol = 'admin' if username_db == 'admin' else 'usuario'
                        return (user_id, username_db, rol)
            
            return None
            
        except Exception as e:
            print(f"❌ Error al verificar credenciales: {e}")
            return None
    
    def mostrar_login(self):
        """Mostrar ventana de login (sin cambios en la interfaz)"""
        self.window = ctk.CTk()
        self.window.title("🔐 Sistema de Punto de Venta - Login")
        self.window.geometry("500x700+400+50")
        self.window.configure(fg_color=estilos.COLORS['bg_primary'])
        self.window.resizable(False, False)
        
        # Centrar ventana
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.window.winfo_screenheight() // 2) - (700 // 2)
        self.window.geometry(f"500x700+{x}+{y}")
        
        # Frame principal
        main_frame = ctk.CTkFrame(self.window, 
                                 fg_color=estilos.COLORS['white'],
                                 corner_radius=20)
        main_frame.pack(fill='both', expand=True, padx=30, pady=30)
        
        # Logo/Icono principal
        logo_label = ctk.CTkLabel(main_frame, 
                                 text="🏪", 
                                 font=ctk.CTkFont(size=80))
        logo_label.pack(pady=(40, 20))
        
        # Título principal
        title_label = ctk.CTkLabel(main_frame, 
                                  text="Sistema de Punto de Venta", 
                                  font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
                                  text_color=estilos.COLORS['primary'])
        title_label.pack(pady=(0, 10))
        
        # Subtítulo
        subtitle_label = ctk.CTkLabel(main_frame, 
                                     text="Versión 2.0 Moderna", 
                                     font=ctk.CTkFont(family="Segoe UI", size=14),
                                     text_color=estilos.COLORS['gray'])
        subtitle_label.pack(pady=(0, 40))
        
        # Frame del formulario
        form_frame = ctk.CTkFrame(main_frame, 
                                 fg_color="transparent")
        form_frame.pack(fill='x', padx=40, pady=20)
        
        # Campo Usuario
        user_label = ctk.CTkLabel(form_frame, 
                                 text="👤 Usuario:", 
                                 font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
                                 text_color=estilos.COLORS['dark'])
        user_label.pack(anchor='w', pady=(0, 5))
        
        self.usuario_entry = ctk.CTkEntry(form_frame, 
                                         placeholder_text="Ingrese su usuario",
                                         font=ctk.CTkFont(family="Segoe UI", size=12),
                                         height=45,
                                         corner_radius=10)
        self.usuario_entry.pack(fill='x', pady=(0, 20))
        
        # Campo Password
        password_label = ctk.CTkLabel(form_frame, 
                                     text="🔒 Contraseña:", 
                                     font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
                                     text_color=estilos.COLORS['dark'])
        password_label.pack(anchor='w', pady=(0, 5))
        
        self.password_entry = ctk.CTkEntry(form_frame, 
                                          placeholder_text="Ingrese su contraseña",
                                          font=ctk.CTkFont(family="Segoe UI", size=12),
                                          height=45,
                                          corner_radius=10,
                                          show="*")
        self.password_entry.pack(fill='x', pady=(0, 30))
        
        # Botón de Login
        login_button = ctk.CTkButton(form_frame, 
                                    text="🔐 Iniciar Sesión", 
                                    command=self.iniciar_sesion,
                                    font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
                                    height=50,
                                    corner_radius=15,
                                    fg_color=estilos.COLORS['primary'],
                                    hover_color=estilos.COLORS['primary_dark'])
        login_button.pack(fill='x', pady=(0, 20))
        
        # Información de usuario demo
        info_frame = ctk.CTkFrame(main_frame, 
                                 fg_color=estilos.COLORS['light'],
                                 corner_radius=10)
        info_frame.pack(fill='x', padx=40, pady=20)
        
        info_title = ctk.CTkLabel(info_frame, 
                                 text="ℹ️ Credenciales de Prueba", 
                                 font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                                 text_color=estilos.COLORS['info'])
        info_title.pack(pady=(15, 5))
        
        info_text = ctk.CTkLabel(info_frame, 
                                text="Usuario: admin\nContraseña: admin123", 
                                font=ctk.CTkFont(family="Segoe UI", size=11),
                                text_color=estilos.COLORS['dark'])
        info_text.pack(pady=(0, 15))
        
        # Footer
        footer_label = ctk.CTkLabel(main_frame, 
                                   text="© 2024 Sistema POS Moderno", 
                                   font=ctk.CTkFont(family="Segoe UI", size=10),
                                   text_color=estilos.COLORS['gray'])
        footer_label.pack(side='bottom', pady=20)
        
        # Bind Enter key
        self.window.bind('<Return>', lambda event: self.iniciar_sesion())
        
        # Focus en campo usuario
        self.usuario_entry.focus()
        
        # Ejecutar ventana
        self.window.mainloop()
        
        return self.usuario_autenticado
    
    def iniciar_sesion(self):
        """Procesar inicio de sesión"""
        usuario = self.usuario_entry.get().strip()
        password = self.password_entry.get().strip()
        
        print(f"🔐 Intento de login: usuario='{usuario}', password='{password}'")
        
        # Validaciones básicas
        if not usuario or not password:
            messagebox.showerror("❌ Error", "Por favor ingrese usuario y contraseña")
            return
        
        # Verificar credenciales
        resultado = self.verificar_credenciales(usuario, password)
        print(f"🎯 Resultado verificación: {resultado}")
        
        if resultado:
            user_id, nombre, rol = resultado
            self.usuario_autenticado = True
            print(f"✅ Login exitoso para: {nombre}")
            
            # Mostrar mensaje de bienvenida
            messagebox.showinfo("✅ Bienvenido", 
                              f"¡Bienvenido {nombre}!\n\nRol: {rol.title()}\nAcceso concedido al sistema")
            
            # Cerrar ventana de login
            print("🚪 Cerrando ventana de login...")
            self.window.quit()
            self.window.destroy()
            
        else:
            print("❌ Login fallido")
            messagebox.showerror("❌ Error de Autenticación", 
                               "Usuario o contraseña incorrectos.\n\nVerifique sus credenciales e intente nuevamente.")
            self.password_entry.delete(0, 'end')
            self.usuario_entry.focus()
    
    def cerrar_aplicacion(self):
        """Cerrar aplicación"""
        self.window.destroy()

# Función para mostrar login
def mostrar_login():
    """Función principal para mostrar login"""
    login = LoginWindow()
    return login.mostrar_login()