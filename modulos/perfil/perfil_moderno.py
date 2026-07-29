import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import customtkinter as ctk
from modulos.utils.estilos_modernos import estilos
from data.models import get_connection
import hashlib
from PIL import Image, ImageTk
import io

class PerfilModerno(tk.Frame):
    def __init__(self, padre, usuario_actual=None):
        super().__init__(padre, bg=estilos.COLORS['bg_primary'])
        self.usuario_actual = usuario_actual
        self.user_id = None
        
        # Obtener el ID del usuario a partir del nombre
        if self.usuario_actual:
            self.obtener_id_usuario()
        else:
            # Fallback: si no se pasa usuario, intentar obtener el primero (admin)
            self.cargar_usuario_por_defecto()
        
        # Crear la interfaz
        self.widgets()
        # Cargar la foto del rostro si existe
        self.cargar_foto_rostro()

    def obtener_id_usuario(self):
        """Obtiene el ID del usuario a partir del nombre de usuario."""
        conn = get_connection()
        if not conn:
            return
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id FROM usuarios WHERE username = %s", (self.usuario_actual,))
            row = cursor.fetchone()
            if row:
                self.user_id = row[0]
            else:
                self.user_id = None
                print(f"⚠️ Usuario '{self.usuario_actual}' no encontrado en la base de datos.")
        except Exception as e:
            print(f"Error obteniendo ID: {e}")
        finally:
            cursor.close()
            conn.close()

    def cargar_usuario_por_defecto(self):
        """Carga el primer usuario de la tabla (fallback)."""
        conn = get_connection()
        if not conn:
            self.usuario_actual = "admin"
            self.user_id = 1
            return
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id, username FROM usuarios ORDER BY id LIMIT 1")
            row = cursor.fetchone()
            if row:
                self.user_id, self.usuario_actual = row
            else:
                self.usuario_actual = "admin"
                self.user_id = 1
        except Exception as e:
            print(f"Error cargando usuario por defecto: {e}")
            self.usuario_actual = "admin"
            self.user_id = 1
        finally:
            cursor.close()
            conn.close()

    def widgets(self):
        """Crea la interfaz de perfil."""
        # Card principal
        card = ctk.CTkFrame(self, corner_radius=20, fg_color=estilos.COLORS['white'])
        card.pack(fill='both', expand=True, padx=40, pady=40)

        # Título
        title_label = ctk.CTkLabel(card, text="👤 Mi Perfil", font=ctk.CTkFont(family="Segoe UI", size=28, weight="bold"), text_color=estilos.COLORS['primary'])
        title_label.pack(pady=(30, 10))

        # Subtítulo con nombre de usuario
        self.subtitle_label = ctk.CTkLabel(card, text=f"Usuario: {self.usuario_actual}", font=ctk.CTkFont(family="Segoe UI", size=16), text_color=estilos.COLORS['gray'])
        self.subtitle_label.pack(pady=(0, 30))

        # Frame para foto de perfil
        self.foto_frame = ctk.CTkFrame(card, fg_color="transparent", width=150, height=150)
        self.foto_frame.pack(pady=10)
        self.foto_label = ctk.CTkLabel(self.foto_frame, text="📷", font=ctk.CTkFont(size=60))
        self.foto_label.pack()

        # Frame de campos
        fields_frame = ctk.CTkFrame(card, fg_color="transparent")
        fields_frame.pack(pady=20, padx=40, fill='x')

        # Campo de nombre de usuario
        tk.Label(fields_frame, text="Nombre de usuario:", font=('Segoe UI', 12, 'bold'), bg=estilos.COLORS['white']).grid(row=0, column=0, sticky='w', pady=5)
        self.entry_username = ctk.CTkEntry(fields_frame, font=('Segoe UI', 12), width=300)
        self.entry_username.insert(0, self.usuario_actual)
        self.entry_username.grid(row=0, column=1, pady=5)

        # Botón actualizar usuario
        btn_update_user = ctk.CTkButton(fields_frame, text="Cambiar nombre de usuario", command=self.cambiar_usuario, width=200, height=40, fg_color=estilos.COLORS['info'], hover_color="#0ea5e9")
        btn_update_user.grid(row=0, column=2, padx=10)

        # Botón cambiar contraseña
        btn_change_pass = ctk.CTkButton(fields_frame, text="🔑 Cambiar contraseña", command=self.abrir_ventana_cambiar_password, width=200, height=40, fg_color=estilos.COLORS['warning'], hover_color="#d97706")
        btn_change_pass.grid(row=1, column=2, padx=10, pady=10)

        # Botón eliminar cuenta
        btn_delete = ctk.CTkButton(fields_frame, text="🗑️ Eliminar cuenta", command=self.eliminar_cuenta, width=200, height=40, fg_color=estilos.COLORS['danger'], hover_color="#dc3545")
        btn_delete.grid(row=2, column=2, padx=10, pady=10)

        # --- NUEVO BOTÓN CERRAR SESIÓN ---
        btn_logout = ctk.CTkButton(fields_frame, text="🚪 Cerrar sesión", command=self.cerrar_sesion, width=200, height=40, fg_color=estilos.COLORS['secondary'], hover_color="#6c757d")
        btn_logout.grid(row=3, column=2, padx=10, pady=10)

        # Espaciador
        tk.Label(fields_frame, text="", bg=estilos.COLORS['white']).grid(row=4, column=0, columnspan=2)

    def cerrar_sesion(self):
        """Cierra la sesión actual y vuelve a mostrar la ventana de login."""
        respuesta = messagebox.askyesno("🚪 Cerrar sesión", "¿Está seguro de que desea cerrar sesión?")
        if respuesta:
            # Destruir la ventana principal (Manager)
            root = self.winfo_toplevel()
            root.destroy()

    def cargar_foto_rostro(self):
        """Carga la foto del rostro desde la tabla rostros si existe."""
        if not self.user_id:
            return
        conn = get_connection()
        if not conn:
            return
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT imagen FROM rostros WHERE usuario_id = %s", (self.user_id,))
            row = cursor.fetchone()
            if row and row[0]:
                img_bytes = row[0]
                # Convertir bytes a imagen
                img = Image.open(io.BytesIO(img_bytes))
                img = img.resize((120, 120), Image.Resampling.LANCZOS)
                img_tk = ImageTk.PhotoImage(img)
                self.foto_label.configure(image=img_tk, text="")
                self.foto_label.image = img_tk
        except Exception as e:
            print(f"Error al cargar foto: {e}")
        finally:
            cursor.close()
            conn.close()

    def cambiar_usuario(self):
        """Cambia el nombre de usuario."""
        nuevo = self.entry_username.get().strip()
        if not nuevo:
            messagebox.showerror("❌ Error", "El nombre de usuario no puede estar vacío")
            return
        if nuevo == self.usuario_actual:
            messagebox.showinfo("ℹ️ Información", "El nombre de usuario es el mismo")
            return
        # Verificar si ya existe otro usuario con ese nombre
        conn = get_connection()
        if not conn:
            return
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id FROM usuarios WHERE username = %s AND id != %s", (nuevo, self.user_id))
            if cursor.fetchone():
                messagebox.showerror("❌ Error", "El nombre de usuario ya está en uso")
                return
            cursor.execute("UPDATE usuarios SET username = %s WHERE id = %s", (nuevo, self.user_id))
            conn.commit()
            self.usuario_actual = nuevo
            self.subtitle_label.configure(text=f"Usuario: {self.usuario_actual}")
            messagebox.showinfo("✅ Éxito", "Nombre de usuario actualizado correctamente")
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al actualizar: {e}")
        finally:
            cursor.close()
            conn.close()

    def abrir_ventana_cambiar_password(self):
        """Abre ventana para cambiar contraseña."""
        ventana = ctk.CTkToplevel(self)
        ventana.title("Cambiar contraseña")
        ventana.geometry("450x350")
        ventana.resizable(False, False)
        ventana.grab_set()

        frame = ctk.CTkFrame(ventana, fg_color=estilos.COLORS['white'])
        frame.pack(fill='both', expand=True, padx=30, pady=30)

        ctk.CTkLabel(frame, text="Cambiar contraseña", font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold")).pack(pady=10)

        # Contraseña actual
        ctk.CTkLabel(frame, text="Contraseña actual:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor='w', pady=(10, 0))
        entry_actual = ctk.CTkEntry(frame, show="*", width=300)
        entry_actual.pack(pady=5)

        # Nueva contraseña
        ctk.CTkLabel(frame, text="Nueva contraseña:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor='w', pady=(10, 0))
        entry_nueva = ctk.CTkEntry(frame, show="*", width=300)
        entry_nueva.pack(pady=5)

        # Confirmar
        ctk.CTkLabel(frame, text="Confirmar nueva contraseña:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor='w', pady=(10, 0))
        entry_confirm = ctk.CTkEntry(frame, show="*", width=300)
        entry_confirm.pack(pady=5)

        def guardar_password():
            actual = entry_actual.get()
            nueva = entry_nueva.get()
            confirm = entry_confirm.get()
            if not actual or not nueva or not confirm:
                messagebox.showerror("❌ Error", "Todos los campos son requeridos")
                return
            if nueva != confirm:
                messagebox.showerror("❌ Error", "Las contraseñas no coinciden")
                return
            if len(nueva) < 6:
                messagebox.showerror("❌ Error", "La nueva contraseña debe tener al menos 6 caracteres")
                return
            # Verificar contraseña actual
            conn = get_connection()
            if not conn:
                return
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT password FROM usuarios WHERE id = %s", (self.user_id,))
                row = cursor.fetchone()
                if not row:
                    messagebox.showerror("❌ Error", "Usuario no encontrado")
                    return
                stored_hash = row[0]
                input_hash = hashlib.sha256(actual.encode()).hexdigest()
                if input_hash != stored_hash:
                    messagebox.showerror("❌ Error", "Contraseña actual incorrecta")
                    return
                # Actualizar
                new_hash = hashlib.sha256(nueva.encode()).hexdigest()
                cursor.execute("UPDATE usuarios SET password = %s WHERE id = %s", (new_hash, self.user_id))
                conn.commit()
                messagebox.showinfo("✅ Éxito", "Contraseña actualizada correctamente")
                ventana.destroy()
            except Exception as e:
                messagebox.showerror("❌ Error", f"Error al actualizar contraseña: {e}")
            finally:
                cursor.close()
                conn.close()

        btn_guardar = ctk.CTkButton(frame, text="Guardar", command=guardar_password, width=200, height=40, fg_color=estilos.COLORS['success'])
        btn_guardar.pack(pady=20)

    def eliminar_cuenta(self):
        """Elimina la cuenta del usuario actual."""
        respuesta = messagebox.askyesno("⚠️ Confirmar eliminación", 
                                        f"¿Está seguro de que desea eliminar su cuenta '{self.usuario_actual}'?\n\n"
                                        "Esta acción es irreversible y eliminará todos sus datos asociados (incluyendo rostro).\n"
                                        "Se cerrará la sesión automáticamente.")
        if not respuesta:
            return
        password = simpledialog.askstring("Confirmar", "Ingrese su contraseña para confirmar:", show='*')
        if password is None:
            return
        # Verificar contraseña
        conn = get_connection()
        if not conn:
            return
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT password FROM usuarios WHERE id = %s", (self.user_id,))
            row = cursor.fetchone()
            if not row:
                messagebox.showerror("❌ Error", "Usuario no encontrado")
                return
            stored_hash = row[0]
            input_hash = hashlib.sha256(password.encode()).hexdigest()
            if input_hash != stored_hash:
                messagebox.showerror("❌ Error", "Contraseña incorrecta")
                return
            # Eliminar usuario (ON DELETE CASCADE eliminará rostros)
            cursor.execute("DELETE FROM usuarios WHERE id = %s", (self.user_id,))
            conn.commit()
            messagebox.showinfo("🗑️ Cuenta eliminada", "Su cuenta ha sido eliminada correctamente.\nLa aplicación se cerrará.")
            # Cerrar la aplicación
            self.quit()
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al eliminar cuenta: {e}")
        finally:
            cursor.close()
            conn.close()