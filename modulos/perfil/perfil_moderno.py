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
        
        if self.usuario_actual:
            self.obtener_id_usuario()
        else:
            self.cargar_usuario_por_defecto()
        
        self.widgets()
        self.cargar_foto_rostro()

    def obtener_id_usuario(self):
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
        except Exception as e:
            print(f"Error obteniendo ID: {e}")
        finally:
            cursor.close()
            conn.close()

    def cargar_usuario_por_defecto(self):
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
        card = ctk.CTkFrame(self, corner_radius=20, fg_color=estilos.COLORS['white'])
        card.pack(fill='both', expand=True, padx=40, pady=40)

        title_label = ctk.CTkLabel(card, text="👤 Mi Perfil", font=ctk.CTkFont(family="Segoe UI", size=28, weight="bold"), text_color=estilos.COLORS['primary'])
        title_label.pack(pady=(30, 10))

        self.subtitle_label = ctk.CTkLabel(card, text=f"Usuario: {self.usuario_actual}", font=ctk.CTkFont(family="Segoe UI", size=16), text_color=estilos.COLORS['gray'])
        self.subtitle_label.pack(pady=(0, 30))

        self.foto_frame = ctk.CTkFrame(card, fg_color="transparent", width=150, height=150)
        self.foto_frame.pack(pady=10)
        self.foto_label = ctk.CTkLabel(self.foto_frame, text="📷", font=ctk.CTkFont(size=60))
        self.foto_label.pack()

        fields_frame = ctk.CTkFrame(card, fg_color="transparent")
        fields_frame.pack(pady=20, padx=40, fill='x')

        tk.Label(fields_frame, text="Nombre de usuario:", font=('Segoe UI', 12, 'bold'), bg=estilos.COLORS['white']).grid(row=0, column=0, sticky='w', pady=5)
        self.entry_username = ctk.CTkEntry(fields_frame, font=('Segoe UI', 12), width=300)
        self.entry_username.insert(0, self.usuario_actual)
        self.entry_username.grid(row=0, column=1, pady=5)

        btn_update_user = ctk.CTkButton(fields_frame, text="Cambiar nombre de usuario", command=self.cambiar_usuario, width=200, height=40, fg_color=estilos.COLORS['info'], hover_color="#0ea5e9")
        btn_update_user.grid(row=0, column=2, padx=10)

        btn_change_pass = ctk.CTkButton(fields_frame, text="🔑 Cambiar contraseña", command=self.abrir_ventana_cambiar_password, width=200, height=40, fg_color=estilos.COLORS['warning'], hover_color="#d97706")
        btn_change_pass.grid(row=1, column=2, padx=10, pady=10)

        btn_delete = ctk.CTkButton(fields_frame, text="🗑️ Eliminar cuenta", command=self.eliminar_cuenta, width=200, height=40, fg_color=estilos.COLORS['danger'], hover_color="#dc3545")
        btn_delete.grid(row=2, column=2, padx=10, pady=10)

        # Botón Cerrar Sesión
        btn_logout = ctk.CTkButton(
            fields_frame,
            text="🔌 Cerrar Sesión",
            command=self.cerrar_sesion,  # llama al método con pregunta por defecto
            width=200,
            height=40,
            fg_color=estilos.COLORS['secondary'],
            hover_color="#4a5568",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold")
        )
        btn_logout.grid(row=3, column=2, padx=10, pady=10)

        tk.Label(fields_frame, text="", bg=estilos.COLORS['white']).grid(row=1, column=0, columnspan=2)

    def cargar_foto_rostro(self):
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
        nuevo = self.entry_username.get().strip()
        if not nuevo:
            messagebox.showerror("❌ Error", "El nombre de usuario no puede estar vacío")
            return
        if nuevo == self.usuario_actual:
            messagebox.showinfo("ℹ️ Información", "El nombre de usuario es el mismo")
            return
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
        ventana = ctk.CTkToplevel(self)
        ventana.title("Cambiar contraseña")
        ventana.geometry("450x400")
        ventana.resizable(False, False)
        ventana.grab_set()

        frame = ctk.CTkFrame(ventana, fg_color=estilos.COLORS['white'])
        frame.pack(fill='both', expand=True, padx=30, pady=30)

        ctk.CTkLabel(frame, text="Cambiar contraseña", font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold")).pack(pady=10)

        ctk.CTkLabel(frame, text="Contraseña actual:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor='w', pady=(10, 0))
        entry_actual = ctk.CTkEntry(frame, show="*", width=300)
        entry_actual.pack(pady=5)

        ctk.CTkLabel(frame, text="Nueva contraseña:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor='w', pady=(10, 0))
        entry_nueva = ctk.CTkEntry(frame, show="*", width=300)
        entry_nueva.pack(pady=5)

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
        """Elimina la cuenta del usuario actual (sin preguntar cerrar sesión)"""
        respuesta = messagebox.askyesno("⚠️ Confirmar eliminación", 
                                        f"¿Está seguro de que desea eliminar su cuenta '{self.usuario_actual}'?\n\n"
                                        "Esta acción es irreversible y eliminará todos sus datos asociados (incluyendo rostro).\n"
                                        "Se cerrará la sesión automáticamente.")
        if not respuesta:
            return
        password = simpledialog.askstring("Confirmar", "Ingrese su contraseña para confirmar:", show='*')
        if password is None:
            return
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
            cursor.execute("DELETE FROM usuarios WHERE id = %s", (self.user_id,))
            conn.commit()
            messagebox.showinfo("🗑️ Cuenta eliminada", "Su cuenta ha sido eliminada correctamente.\nSe cerrará la sesión.")
            # Cierra sesión SIN preguntar de nuevo
            self.cerrar_sesion(preguntar=False)
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al eliminar cuenta: {e}")
        finally:
            cursor.close()
            conn.close()

    # ========== MÉTODO CERRAR SESIÓN CON PARÁMETRO OPCIONAL ==========
    def cerrar_sesion(self, preguntar=True):
        """Cierra la sesión. Si preguntar=True, pide confirmación."""
        if preguntar:
            if not messagebox.askyesno("🔌 Cerrar Sesión", "¿Está seguro de que desea cerrar sesión?"):
                return
        print("🔵 [Perfil] Cerrando sesión...")
        if hasattr(self.master, 'cerrar_sesion'):
            self.master.cerrar_sesion()
        else:
            print("⚠️ [Perfil] El contenedor no tiene método cerrar_sesion")