import tkinter as tk
from tkinter import ttk, messagebox, Toplevel
from modulos.utils.estilos_modernos import estilos
from data.models import get_connection   # <--- Conexión MySQL


class Clientes(tk.Frame):
    """Gestión de clientes (versión clásica)"""
    
    def __init__(self, padre):
        super().__init__(padre)
        self.widgets()
        self.cargar_registros()
        
    def widgets(self):
        # Frame izquierdo - Formulario
        self.labelframe = tk.LabelFrame(self, text="Clientes", font="sans 20 bold", bg=estilos.COLORS['bg_primary'])
        self.labelframe.place(x=20, y=20, width=250, height=560)

        lblnombre = tk.Label(self.labelframe, text="Nombre:", font=('Segoe UI', 11, 'bold'), bg=estilos.COLORS['bg_primary'])
        lblnombre.place(x=10, y=20)
        self.nombre = ttk.Entry(self.labelframe, font=('Segoe UI', 11))
        self.nombre.place(x=10, y=50, width=220, height=40)

        lblcedula = tk.Label(self.labelframe, text="Cédula:", font=('Segoe UI', 11, 'bold'), bg=estilos.COLORS['bg_primary'])
        lblcedula.place(x=10, y=100)
        self.cedula = ttk.Entry(self.labelframe, font=('Segoe UI', 11))
        self.cedula.place(x=10, y=130, width=220, height=40)

        lblcelular = tk.Label(self.labelframe, text="Celular:", font=('Segoe UI', 11, 'bold'), bg=estilos.COLORS['bg_primary'])
        lblcelular.place(x=10, y=180)
        self.celular = ttk.Entry(self.labelframe, font=('Segoe UI', 11))
        self.celular.place(x=10, y=210, width=220, height=40)

        lbldireccion = tk.Label(self.labelframe, text="Dirección:", font=('Segoe UI', 11, 'bold'), bg=estilos.COLORS['bg_primary'])
        lbldireccion.place(x=10, y=260)
        self.direccion = ttk.Entry(self.labelframe, font=('Segoe UI', 11))
        self.direccion.place(x=10, y=290, width=220, height=40)

        lblcorreo = tk.Label(self.labelframe, text="Correo:", font=('Segoe UI', 11, 'bold'), bg=estilos.COLORS['bg_primary'])
        lblcorreo.place(x=10, y=340)
        self.correo = ttk.Entry(self.labelframe, font=('Segoe UI', 11))
        self.correo.place(x=10, y=370, width=220, height=40)

        # Botones
        bt1 = tk.Button(self.labelframe, fg="Black", text="Ingresar", font="sans 16 bold", command=self.registrar)
        bt1.place(x=10, y=420, width=220, height=40)

        bt2 = tk.Button(self.labelframe, fg="Black", text="Modificar", font="sans 16 bold", command=self.modificar)
        bt2.place(x=10, y=470, width=220, height=40)

        # Treeview
        treFrame = tk.Frame(self, bg="white")
        treFrame.place(x=280, y=20, width=850, height=720)

        Scrollbar_y = ttk.Scrollbar(treFrame)
        Scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

        Scrollbar_x = ttk.Scrollbar(treFrame, orient=tk.HORIZONTAL)
        Scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.tree = ttk.Treeview(treFrame, yscrollcommand=Scrollbar_y.set, xscrollcommand=Scrollbar_x.set,
                                 height=40, columns=("ID", "Nombre", "Cedula", "Celular", "Direccion", "Correo"),
                                 show="headings")
        self.tree.pack(expand=True, fill=tk.BOTH)

        Scrollbar_y.config(command=self.tree.yview)
        Scrollbar_x.config(command=self.tree.xview)

        self.tree.heading("ID", text="ID")
        self.tree.heading("Nombre", text="Nombre")
        self.tree.heading("Cedula", text="Cédula")
        self.tree.heading("Celular", text="Celular")
        self.tree.heading("Direccion", text="Dirección")
        self.tree.heading("Correo", text="Correo")

        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Nombre", width=150, anchor="center")
        self.tree.column("Cedula", width=120, anchor="center")
        self.tree.column("Celular", width=120, anchor="center")
        self.tree.column("Direccion", width=200, anchor="center")
        self.tree.column("Correo", width=200, anchor="center")

    # ==================== VALIDACIÓN ====================
    def validar_campos(self):
        """Validar que todos los campos estén llenos"""
        if not self.nombre.get().strip():
            messagebox.showerror("Error", "El campo Nombre es requerido")
            return False
        if not self.cedula.get().strip():
            messagebox.showerror("Error", "El campo Cédula es requerido")
            return False
        if not self.celular.get().strip():
            messagebox.showerror("Error", "El campo Celular es requerido")
            return False
        if not self.direccion.get().strip():
            messagebox.showerror("Error", "El campo Dirección es requerido")
            return False
        if not self.correo.get().strip():
            messagebox.showerror("Error", "El campo Correo es requerido")
            return False
        return True

    # ==================== REGISTRAR CLIENTE ====================
    def registrar(self):
        """Registrar un nuevo cliente en MySQL"""
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
            # Verificar si la cédula ya existe
            cursor.execute("SELECT id FROM clientes WHERE cedula = %s", (cedula,))
            if cursor.fetchone():
                messagebox.showerror("Error", f"Ya existe un cliente con la cédula '{cedula}'")
                return

            cursor.execute(
                "INSERT INTO clientes (nombre, cedula, celular, direccion, correo) VALUES (%s, %s, %s, %s, %s)",
                (nombre, cedula, celular, direccion, correo)
            )
            conn.commit()
            messagebox.showinfo("Éxito", "Cliente registrado correctamente")
            self.limpiar_treeview()
            self.limpiar_campos()
            self.cargar_registros()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo registrar el cliente: {e}")
        finally:
            cursor.close()
            conn.close()

    # ==================== CARGAR REGISTROS ====================
    def cargar_registros(self):
        """Cargar todos los clientes desde MySQL"""
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
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los registros: {e}")
        finally:
            cursor.close()
            conn.close()

    # ==================== LIMPIAR TREEVIEW ====================
    def limpiar_treeview(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    # ==================== LIMPIAR CAMPOS ====================
    def limpiar_campos(self):
        self.nombre.delete(0, tk.END)
        self.cedula.delete(0, tk.END)
        self.celular.delete(0, tk.END)
        self.direccion.delete(0, tk.END)
        self.correo.delete(0, tk.END)

    # ==================== MODIFICAR / ELIMINAR ====================
    def modificar(self):
        """Abrir ventana para modificar o eliminar un cliente seleccionado"""
        if not self.tree.selection():
            messagebox.showerror("Error", "Por favor seleccione un cliente para modificar")
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

        top_modificar = Toplevel(self)
        top_modificar.title("Modificar cliente")
        top_modificar.geometry("400x450+400+50")
        top_modificar.config(bg=estilos.COLORS['bg_primary'])
        top_modificar.resizable(False, False)
        top_modificar.grab_set()
        top_modificar.focus_set()
        top_modificar.lift()

        tk.Label(top_modificar, text="Nombre: ", font=('Segoe UI', 11, 'bold'), bg=estilos.COLORS['bg_primary']).grid(row=0, column=0, padx=10, pady=5)
        nombre_nuevo = tk.Entry(top_modificar, font=('Segoe UI', 11))
        nombre_nuevo.insert(0, nombre_actual)
        nombre_nuevo.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(top_modificar, text="Cédula: ", font=('Segoe UI', 11, 'bold'), bg=estilos.COLORS['bg_primary']).grid(row=1, column=0, padx=10, pady=5)
        cedula_nuevo = tk.Entry(top_modificar, font=('Segoe UI', 11))
        cedula_nuevo.insert(0, cedula_actual)
        cedula_nuevo.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(top_modificar, text="Celular: ", font=('Segoe UI', 11, 'bold'), bg=estilos.COLORS['bg_primary']).grid(row=2, column=0, padx=10, pady=5)
        celular_nuevo = tk.Entry(top_modificar, font=('Segoe UI', 11))
        celular_nuevo.insert(0, celular_actual)
        celular_nuevo.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(top_modificar, text="Dirección: ", font=('Segoe UI', 11, 'bold'), bg=estilos.COLORS['bg_primary']).grid(row=3, column=0, padx=10, pady=5)
        direccion_nuevo = tk.Entry(top_modificar, font=('Segoe UI', 11))
        direccion_nuevo.insert(0, direccion_actual)
        direccion_nuevo.grid(row=3, column=1, padx=10, pady=5)

        tk.Label(top_modificar, text="Correo: ", font=('Segoe UI', 11, 'bold'), bg=estilos.COLORS['bg_primary']).grid(row=4, column=0, padx=10, pady=5)
        correo_nuevo = tk.Entry(top_modificar, font=('Segoe UI', 11))
        correo_nuevo.insert(0, correo_actual)
        correo_nuevo.grid(row=4, column=1, padx=10, pady=5)

        # ==================== GUARDAR MODIFICACIÓN ====================
        def guardar_modificado():
            nuevo_nombre = nombre_nuevo.get().strip()
            nuevo_cedula = cedula_nuevo.get().strip()
            nuevo_celular = celular_nuevo.get().strip()
            nuevo_direccion = direccion_nuevo.get().strip()
            nuevo_correo = correo_nuevo.get().strip()

            if not all([nuevo_nombre, nuevo_cedula, nuevo_celular, nuevo_direccion, nuevo_correo]):
                messagebox.showerror("Error", "Todos los campos son requeridos")
                return

            conn = get_connection()
            if not conn:
                return
            cursor = conn.cursor()
            try:
                # Verificar si la nueva cédula ya existe en otro cliente
                cursor.execute("SELECT id FROM clientes WHERE cedula = %s AND id != %s", (nuevo_cedula, id_cliente))
                if cursor.fetchone():
                    messagebox.showerror("Error", f"La cédula '{nuevo_cedula}' ya está registrada en otro cliente")
                    return

                cursor.execute(
                    "UPDATE clientes SET nombre = %s, cedula = %s, celular = %s, direccion = %s, correo = %s WHERE id = %s",
                    (nuevo_nombre, nuevo_cedula, nuevo_celular, nuevo_direccion, nuevo_correo, id_cliente)
                )
                conn.commit()
                messagebox.showinfo("Éxito", "Cliente modificado correctamente")
                self.cargar_registros()
                top_modificar.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo modificar el cliente: {e}")
            finally:
                cursor.close()
                conn.close()

        # ==================== ELIMINAR CLIENTE ====================
        def eliminar_cliente():
            if messagebox.askyesno("Confirmar", f"¿Está seguro de eliminar al cliente '{nombre_actual}'?"):
                conn = get_connection()
                if not conn:
                    return
                cursor = conn.cursor()
                try:
                    cursor.execute("DELETE FROM clientes WHERE id = %s", (id_cliente,))
                    conn.commit()
                    messagebox.showinfo("Éxito", "Cliente eliminado correctamente")
                    self.cargar_registros()
                    top_modificar.destroy()
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo eliminar el cliente: {e}")
                finally:
                    cursor.close()
                    conn.close()

        # ==================== BOTONES ====================
        btn_guardar = tk.Button(top_modificar, text="Guardar cambios", command=guardar_modificado, font=('Segoe UI', 11, 'bold'))
        btn_guardar.grid(row=5, column=0, columnspan=2, pady=10)

        btn_eliminar = tk.Button(top_modificar, bg="red", fg="white", text="Eliminar cliente", command=eliminar_cliente, font=('Segoe UI', 11, 'bold'))
        btn_eliminar.grid(row=6, column=0, columnspan=2, pady=10)