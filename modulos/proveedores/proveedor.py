import tkinter as tk
from tkinter import ttk, messagebox, Toplevel
from data.models import get_connection   # <--- Conexión desde data.models

class Proveedor(tk.Frame):
    
    def __init__(self, padre):
        super().__init__(padre)
        self.widgets()
        self.cargar_registros()
        
    def widgets(self):
        self.labelframe = tk.LabelFrame(self, text="Proveedor", font="sans 20 bold", bg="#C6D9E3")
        self.labelframe.place(x=20, y=20, width=250, height=560)

        lblnombre = tk.Label(self.labelframe, text="Empresa:", font="sans 14 bold", bg="#C6D9E3")
        lblnombre.place(x=10, y=20)
        self.nombre = ttk.Entry(self.labelframe, font="sans 14 bold")
        self.nombre.place(x=10, y=50, width=220, height=40)

        lblcedula = tk.Label(self.labelframe, text="RIF:", font="sans 14 bold", bg="#C6D9E3")
        lblcedula.place(x=10, y=100)
        self.cedula = ttk.Entry(self.labelframe, font="sans 14 bold")
        self.cedula.place(x=10, y=130, width=220, height=40)

        # Botón Buscar (aún sin funcionalidad, puedes agregarla después)
        bt0 = tk.Button(self.labelframe, fg="Black", text="Buscar", font="sans 16 bold")
        bt0.place(x=10, y=370, width=220, height=40)

        bt1 = tk.Button(self.labelframe, command=self.registrar_ventana_open, fg="Black", text="Ingresar", font="sans 16 bold")
        bt1.place(x=10, y=420, width=220, height=40)

        bt2 = tk.Button(self.labelframe, fg="Black", text="Modificar", font="sans 16 bold", command=self.modificar)
        bt2.place(x=10, y=470, width=220, height=40)

        treFrame = tk.Frame(self, bg="white")
        treFrame.place(x=280, y=20, width=850, height=720)

        Scrollbar_y = ttk.Scrollbar(treFrame)
        Scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

        Scrollbar_x = ttk.Scrollbar(treFrame, orient=tk.HORIZONTAL)
        Scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.tree = ttk.Treeview(treFrame, yscrollcommand=Scrollbar_y.set, xscrollcommand=Scrollbar_x.set,
                                 height=40, columns=("ID", "Empresa", "Rif", "Celular", "Direccion", "Correo"),
                                 show="headings")
        self.tree.pack(expand=True, fill=tk.BOTH)

        Scrollbar_y.config(command=self.tree.yview)
        Scrollbar_x.config(command=self.tree.xview)

        self.tree.heading("ID", text="ID")
        self.tree.heading("Empresa", text="Empresa")
        self.tree.heading("Rif", text="Rif")
        self.tree.heading("Celular", text="Celular")
        self.tree.heading("Direccion", text="Direccion")
        self.tree.heading("Correo", text="Correo")

        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Empresa", width=150, anchor="center")
        self.tree.column("Rif", width=120, anchor="center")
        self.tree.column("Celular", width=120, anchor="center")
        self.tree.column("Direccion", width=200, anchor="center")
        self.tree.column("Correo", width=200, anchor="center")

    # ---------------------------------------------------------------------------------
    def cargar_registros(self):
        """Cargar todos los proveedores desde MySQL"""
        conn = get_connection()
        if not conn:
            messagebox.showerror("Error", "No se pudo conectar a la base de datos")
            return
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM proveedores ORDER BY empresa")
            rows = cursor.fetchall()
            # Limpiar treeview antes de cargar
            for item in self.tree.get_children():
                self.tree.delete(item)
            for row in rows:
                self.tree.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar los registros: {e}")
        finally:
            cursor.close()
            conn.close()

    # ---------------------------------------------------------------------------------
    def limpiar_treeview(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    # ---------------------------------------------------------------------------------
    def modificar(self):
        """Abrir ventana para modificar o eliminar un proveedor seleccionado"""
        if not self.tree.selection():
            messagebox.showerror("Error", "Por favor seleccione un proveedor para modificar")
            return

        item = self.tree.selection()[0]
        values = self.tree.item(item, "values")
        if not values:
            return

        id_proveedor = values[0]
        empresa_actual = values[1]
        rif_actual = values[2]
        celular_actual = values[3]
        direccion_actual = values[4]
        correo_actual = values[5]

        top_modificar = Toplevel(self)
        top_modificar.title("Modificar proveedor")
        top_modificar.geometry("500x400+400+50")
        top_modificar.config(bg="#C6D9E3")
        top_modificar.resizable(False, False)
        top_modificar.grab_set()
        top_modificar.focus_set()
        top_modificar.lift()

        tk.Label(top_modificar, text="Empresa: ", font="sans 14 bold", bg="#C6D9E3").grid(row=0, column=0, padx=10, pady=5)
        empresa_modificar = tk.Entry(top_modificar, font="sans 14 bold")
        empresa_modificar.insert(0, empresa_actual)
        empresa_modificar.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(top_modificar, text="RIF: ", font="sans 14 bold", bg="#C6D9E3").grid(row=1, column=0, padx=10, pady=5)
        rif_modificar = tk.Entry(top_modificar, font="sans 14 bold")
        rif_modificar.insert(0, rif_actual)
        rif_modificar.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(top_modificar, text="Celular: ", font="sans 14 bold", bg="#C6D9E3").grid(row=2, column=0, padx=10, pady=5)
        celular_modificar = tk.Entry(top_modificar, font="sans 14 bold")
        celular_modificar.insert(0, celular_actual)
        celular_modificar.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(top_modificar, text="Direccion: ", font="sans 14 bold", bg="#C6D9E3").grid(row=3, column=0, padx=10, pady=5)
        direccion_modificar = tk.Entry(top_modificar, font="sans 14 bold")
        direccion_modificar.insert(0, direccion_actual)
        direccion_modificar.grid(row=3, column=1, padx=10, pady=5)

        tk.Label(top_modificar, text="Correo: ", font="sans 14 bold", bg="#C6D9E3").grid(row=4, column=0, padx=10, pady=5)
        correo_modificar = tk.Entry(top_modificar, font="sans 14 bold")
        correo_modificar.insert(0, correo_actual)
        correo_modificar.grid(row=4, column=1, padx=10, pady=5)

        def guardar_modificado():
            modificar_empresa = empresa_modificar.get().strip()
            modificar_rif = rif_modificar.get().strip()
            modificar_celular = celular_modificar.get().strip()
            modificar_direccion = direccion_modificar.get().strip()
            modificar_correo = correo_modificar.get().strip()

            if not modificar_empresa or not modificar_rif:
                messagebox.showerror("Error", "Empresa y RIF son obligatorios")
                return

            conn = get_connection()
            if not conn:
                return
            cursor = conn.cursor()
            try:
                cursor.execute("""UPDATE proveedores
                                  SET empresa = %s, rif = %s, celular = %s, direccion = %s, correo = %s
                                  WHERE id = %s""",
                               (modificar_empresa, modificar_rif, modificar_celular,
                                modificar_direccion, modificar_correo, id_proveedor))
                conn.commit()
                messagebox.showinfo("Éxito", "Proveedor modificado correctamente")
                self.cargar_registros()
                top_modificar.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo modificar el proveedor: {e}")
            finally:
                cursor.close()
                conn.close()

        def eliminar_proveedor():
            if messagebox.askyesno("Confirmar", f"¿Eliminar el proveedor '{empresa_actual}'?"):
                conn = get_connection()
                if not conn:
                    return
                cursor = conn.cursor()
                try:
                    cursor.execute("DELETE FROM proveedores WHERE id = %s", (id_proveedor,))
                    conn.commit()
                    messagebox.showinfo("Éxito", "Proveedor eliminado correctamente")
                    self.cargar_registros()
                    top_modificar.destroy()
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo eliminar el proveedor: {e}")
                finally:
                    cursor.close()
                    conn.close()

        btn_guardar = tk.Button(top_modificar, command=guardar_modificado, text="Guardar cambios", font="sans 14 bold")
        btn_guardar.grid(row=5, column=1, columnspan=2, pady=10)

        btn_eliminar = tk.Button(top_modificar, fg="white", bg="red", text="Eliminar proveedor",
                                 font="sans 14 bold", command=eliminar_proveedor)
        btn_eliminar.grid(row=6, column=1, columnspan=2, pady=10)

    # ---------------------------------------------------------------------------------
    def registrar_empresa(self, empresa, rif, celular, direccion, correo, top_crear):
        """Registrar un nuevo proveedor en MySQL"""
        if not empresa or not rif:
            messagebox.showerror("Error", "Empresa y RIF son obligatorios")
            return

        conn = get_connection()
        if not conn:
            return
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO proveedores (empresa, rif, celular, direccion, correo) VALUES (%s, %s, %s, %s, %s)",
                           (empresa, rif, celular, direccion, correo))
            conn.commit()
            messagebox.showinfo("Éxito", "Proveedor registrado correctamente")
            self.cargar_registros()
            top_crear.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo registrar el proveedor: {e}")
        finally:
            cursor.close()
            conn.close()

    # ---------------------------------------------------------------------------------
    def registrar_ventana_open(self):
        """Abrir ventana para crear un nuevo proveedor"""
        top_crear = Toplevel(self)
        top_crear.title("Crear proveedor")
        top_crear.geometry("500x400+400+50")
        top_crear.config(bg="#C6D9E3")
        top_crear.resizable(False, False)
        top_crear.grab_set()
        top_crear.focus_set()
        top_crear.lift()

        tk.Label(top_crear, text="Empresa: ", font="sans 14 bold", bg="#C6D9E3").grid(row=0, column=0, padx=10, pady=5)
        empresa_nuevo = tk.Entry(top_crear, font="sans 14 bold")
        empresa_nuevo.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(top_crear, text="RIF: ", font="sans 14 bold", bg="#C6D9E3").grid(row=1, column=0, padx=10, pady=5)
        rif_nuevo = tk.Entry(top_crear, font="sans 14 bold")
        rif_nuevo.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(top_crear, text="Celular: ", font="sans 14 bold", bg="#C6D9E3").grid(row=2, column=0, padx=10, pady=5)
        celular_nuevo = tk.Entry(top_crear, font="sans 14 bold")
        celular_nuevo.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(top_crear, text="Direccion: ", font="sans 14 bold", bg="#C6D9E3").grid(row=3, column=0, padx=10, pady=5)
        direccion_nuevo = tk.Entry(top_crear, font="sans 14 bold")
        direccion_nuevo.grid(row=3, column=1, padx=10, pady=5)

        tk.Label(top_crear, text="Correo: ", font="sans 14 bold", bg="#C6D9E3").grid(row=4, column=0, padx=10, pady=5)
        correo_nuevo = tk.Entry(top_crear, font="sans 14 bold")
        correo_nuevo.grid(row=4, column=1, padx=10, pady=5)

        btn_guardar = tk.Button(top_crear,
                                command=lambda: self.registrar_empresa(
                                    empresa_nuevo.get().strip(),
                                    rif_nuevo.get().strip(),
                                    celular_nuevo.get().strip(),
                                    direccion_nuevo.get().strip(),
                                    correo_nuevo.get().strip(),
                                    top_crear
                                ),
                                text="Guardar", font="sans 14 bold")
        btn_guardar.grid(row=5, column=1, columnspan=2, pady=20)