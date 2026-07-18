import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
from modulos.utils.utils import generar_qr_producto
from modulos.utils.estilos_modernos import estilos
from data.models import get_connection
import threading
import os

class Inventario(tk.Frame):
    
    def __init__(self, padre):
        super().__init__(padre)
        self.widgets()
        self.articulos_combobox()
        self.cargar_articulos()
        self.timer_articulos = None
        
        self.image_folder = 'media/img/img_productos'
        if not os.path.exists(self.image_folder):
            os.makedirs(self.image_folder)
        
    def widgets(self):
        # Canvas para artículos (con scroll)
        canvas_articulos = tk.LabelFrame(self, text="Articulos", font='arial 15 bold', bg=estilos.COLORS['bg_primary'])
        canvas_articulos.place(x=300, y=10, width=895, height=740)
        
        self.canvas = tk.Canvas(canvas_articulos, bg=estilos.COLORS['bg_primary'])
        self.scrollbar = tk.Scrollbar(canvas_articulos, orient='vertical', command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=estilos.COLORS['bg_primary'])
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        
        self.canvas.create_window((0,0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.scrollbar.pack(side='right', fill='y')
        self.canvas.pack(side="left", fill="both", expand=True)
        
        # Frame de búsqueda
        lblframe_buscar = tk.LabelFrame(self, text="Buscar", font="arial 14 bold", bg=estilos.COLORS['bg_primary'])
        lblframe_buscar.place(x=5, y=10, width=280, height=80)
        
        self.comboboxbuscar = ttk.Combobox(lblframe_buscar, font="arial 12")
        self.comboboxbuscar.place(x=5, y=5, width=260, height=40)
        self.comboboxbuscar.bind('<<ComboboxSelected>>', self.on_combobox_select)
        self.comboboxbuscar.bind('<KeyRelease>', self.filtrar_articulos)
        
        # Frame de selección (muestra detalles)
        lblframe_seleccion = tk.LabelFrame(self, text='Seleccion', font="arial 12 bold", bg=estilos.COLORS['bg_primary'])
        lblframe_seleccion.place(x=10, y=95, width=280, height=240)
        
        self.label1 = tk.Label(lblframe_seleccion, text='Articulo: ', font="arial 12 bold", bg=estilos.COLORS['bg_primary'], wraplength=300)
        self.label1.place(x=5, y=5)
        
        self.label2 = tk.Label(lblframe_seleccion, text='Precio : ', font="arial 12 bold", bg=estilos.COLORS['bg_primary'])
        self.label2.place(x=5, y=40)
        
        self.label4 = tk.Label(lblframe_seleccion, text='Stock: ', font="arial 12 bold", bg=estilos.COLORS['bg_primary'])
        self.label4.place(x=5, y=70)
        
        self.label5 = tk.Label(lblframe_seleccion, text='Estado: ', font="arial 12 bold", bg=estilos.COLORS['bg_primary'])
        self.label5.place(x=5, y=100)
        
        # Frame de botones
        lblframe_botones = tk.LabelFrame(self, text="Opciones", font="arial 14 bold", bg=estilos.COLORS['bg_primary'])
        lblframe_botones.place(x=10, y=350, width=280, height=250)
        
        btn1 = tk.Button(lblframe_botones, text="Agregar", font="arial 14 bold", command=self.agregar_articulo)
        btn1.place(x=40, y=20, width=180, height=40)
        
        btn2 = tk.Button(lblframe_botones, text="Editar", font="arial 14 bold", command=self.editar_articulo)
        btn2.place(x=40, y=80, width=180, height=40)

        btn3 = tk.Button(lblframe_botones, text="Imprimir etiqueta", font="arial 14 bold", command=generar_qr_producto)
        btn3.place(x=40, y=140, width=180, height=40)
    
    # ---------------------------------------------------------------------------------
    def load_image(self):
        """Cargar imagen desde archivo y guardar en carpeta"""
        file_path = filedialog.askopenfilename()
        if file_path:
            image = Image.open(file_path)
            image = image.resize((200, 200), Image.Resampling.LANCZOS)
            image_name = os.path.basename(file_path)
            image_save_path = os.path.join(self.image_folder, image_name)
            image.save(image_save_path)
            
            self.image_tk = ImageTk.PhotoImage(image)
            self.product_img = self.image_tk
            self.image_path = image_save_path
            
            image_label = tk.Label(self.frameimg, image=self.image_tk)
            image_label.place(x=0, y=0, width=200, height=200)
    
    # ---------------------------------------------------------------------------------
    def articulos_combobox(self):
        """Cargar lista de artículos para el combobox (versión MySQL)"""
        conn = get_connection()
        if not conn:
            return
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT articulo FROM articulos ORDER BY articulo")
            self.articulos = [row[0] for row in cursor.fetchall()]
            self.comboboxbuscar['values'] = self.articulos
        except Exception as e:
            print(f"Error al cargar artículos: {e}")
        finally:
            cursor.close()
            conn.close()
    
    # ---------------------------------------------------------------------------------
    def agregar_articulo(self):
        """Ventana para agregar nuevo artículo"""
        top = tk.Toplevel(self)
        top.title("Agregar Articulo")
        top.geometry("700x400+200+50")
        top.config(bg=estilos.COLORS['bg_primary'])
        top.resizable(False, False)
        top.transient(self.master)
        top.grab_set()
        top.focus_set()
        top.lift()
        
        tk.Label(top, text="Articulo:", font="arial 12 bold", bg=estilos.COLORS['bg_primary']).place(x=20, y=20, width=80, height=25)
        entry_articulo = ttk.Entry(top, font="arial 12 bold")
        entry_articulo.place(x=120, y=20, width=250, height=30)
        
        tk.Label(top, text="Precio:", font="arial 12 bold", bg=estilos.COLORS['bg_primary']).place(x=20, y=60, width=80, height=25)
        entry_precio = ttk.Entry(top, font="arial 12 bold")
        entry_precio.place(x=120, y=60, width=250, height=30)
        
        tk.Label(top, text="Costo:", font="arial 12 bold", bg=estilos.COLORS['bg_primary']).place(x=20, y=100, width=80, height=25)
        entry_costo = ttk.Entry(top, font="arial 12 bold")
        entry_costo.place(x=120, y=100, width=250, height=30)
        
        tk.Label(top, text="Stock:", font="arial 12 bold", bg=estilos.COLORS['bg_primary']).place(x=20, y=140, width=80, height=25)
        entry_stock = ttk.Entry(top, font="arial 12 bold")
        entry_stock.place(x=120, y=140, width=250, height=30)
        
        tk.Label(top, text="Estado:", font="arial 12 bold", bg=estilos.COLORS['bg_primary']).place(x=20, y=180, width=80, height=25)
        entry_estado = ttk.Combobox(top, values=["Activo", "Inactivo"], font="arial 12 bold", state="readonly")
        entry_estado.place(x=120, y=180, width=250, height=30)
        entry_estado.set("Activo")
        
        self.frameimg = tk.Frame(top, bg='#ffffff', highlightbackground="gray", highlightthickness=1)
        self.frameimg.place(x=440, y=30, width=200, height=200)
        
        btnimage = tk.Button(top, text='Cargar imagen', font="arial 12 bold", command=self.load_image)
        btnimage.place(x=470, y=260, width=150, height=40)
        
        # -----------------------------------------------------------------------------
        def guardar():
            articulo = entry_articulo.get().strip()
            precio_str = entry_precio.get().strip()
            costo_str = entry_costo.get().strip()
            stock_str = entry_stock.get().strip()
            estado = entry_estado.get().strip()
            
            if not articulo or not precio_str or not costo_str or not estado:
                messagebox.showerror("Error", "Todos los campos deben ser completados")
                return
            
            try:
                precio = float(precio_str)
                costo = float(costo_str)
                stock = int(stock_str) if stock_str else 0
            except ValueError:
                messagebox.showerror("Error", "Precio, costo y stock deben ser números válidos")
                return
            
            image_path = getattr(self, 'image_path', 'media/icons/img_default.png')
            
            conn = get_connection()
            if not conn:
                return
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO articulos (articulo, precio, costo, stock, estado, image_path) VALUES (%s, %s, %s, %s, %s, %s)",
                    (articulo, precio, costo, stock, estado, image_path)
                )
                conn.commit()
                messagebox.showinfo('Éxito', 'Artículo agregado correctamente')
                top.destroy()
                self.cargar_articulos()
                self.articulos_combobox()
            except Exception as e:
                messagebox.showerror("Error", f"Error al agregar artículo: {e}")
            finally:
                cursor.close()
                conn.close()
        
        tk.Button(top, text='Guardar', font="arial 12 bold", command=guardar).place(x=50, y=260, width=150, height=40)
        tk.Button(top, text='Cancelar', font="arial 12 bold", command=top.destroy).place(x=260, y=260, width=150, height=40)
    
    # ---------------------------------------------------------------------------------
    def cargar_articulos(self, filtro=None, categoria=None):
        """Cargar artículos en el canvas (llamada segura)"""
        self.after(0, self._cargar_articulos, filtro, categoria)
    
    # ---------------------------------------------------------------------------------
    def _cargar_articulos(self, filtro=None, categoria=None):
        """Cargar artículos desde MySQL y mostrarlos en el canvas"""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        conn = get_connection()
        if not conn:
            return
        cursor = conn.cursor()
        try:
            query = "SELECT articulo, precio, image_path FROM articulos"
            params = []
            if filtro:
                query += " WHERE articulo LIKE %s"
                params.append(f'%{filtro}%')
            query += " ORDER BY articulo"
            
            cursor.execute(query, params)
            articulos = cursor.fetchall()
            
            self.row = 0
            self.column = 0
            
            for articulo, precio, image_path in articulos:
                self.mostrar_articulo(articulo, precio, image_path)
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar artículos: {e}")
        finally:
            cursor.close()
            conn.close()
    
    # ---------------------------------------------------------------------------------
    def mostrar_articulo(self, articulo, precio, image_path):
        """Mostrar un artículo en una tarjeta del canvas"""
        article_frame = tk.Frame(self.scrollable_frame, bg='white', relief='solid')
        article_frame.grid(row=self.row, column=self.column, padx=10, pady=10)
        
        if image_path and os.path.exists(image_path):
            try:
                image = Image.open(image_path)
                image = image.resize((150, 150), Image.Resampling.LANCZOS)
                imagen = ImageTk.PhotoImage(image)
                image_label = tk.Label(article_frame, image=imagen)
                image_label.image = imagen
                image_label.pack(expand=True, fill='both')
            except Exception as e:
                print(f"Error cargando imagen {image_path}: {e}")
        
        name_label = tk.Label(article_frame, text=articulo, bg='white', anchor='w', wraplength=150, font='arial 10 bold')
        name_label.pack(side="top", fill='x')
        
        precio_label = tk.Label(article_frame, text=f'precio: ${precio:.2f}', bg='white', anchor='w', wraplength=150, font='arial 8 bold')
        precio_label.pack(side="bottom", fill='x')
        
        self.column += 1
        if self.column > 4:
            self.column = 0
            self.row += 1
    
    # ---------------------------------------------------------------------------------
    def on_combobox_select(self, event):
        self.actualizar_label()
    
    # ---------------------------------------------------------------------------------
    def actualizar_label(self, event=None):
        """Actualizar etiquetas de detalles al seleccionar un artículo"""
        articulo_seleccionado = self.comboboxbuscar.get()
        if not articulo_seleccionado:
            return
        
        conn = get_connection()
        if not conn:
            return
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT articulo, precio, costo, stock, estado FROM articulos WHERE articulo = %s",
                (articulo_seleccionado,)
            )
            resultado = cursor.fetchone()
            if resultado:
                articulo, precio, costo, stock, estado = resultado
                self.label1.config(text=f'Articulo: {articulo}')
                self.label2.config(text=f'Precio: {precio:.2f} $')
                self.label4.config(text=f'Stock: {stock}')
                self.label5.config(text=f'Estado: {estado}')
                if estado.lower() == "activo":
                    self.label5.config(fg="green")
                elif estado.lower() == "inactivo":
                    self.label5.config(fg="red")
                else:
                    self.label5.config(fg="black")
            else:
                self.label1.config(text="Articulo: No encontrado")
                self.label2.config(text="Precio: N/A")
                self.label4.config(text="Stock: N/A")
                self.label5.config(text="Estado: N/A")
        except Exception as e:
            print(f"Error al obtener datos: {e}")
        finally:
            cursor.close()
            conn.close()
    
    # ---------------------------------------------------------------------------------
    def filtrar_articulos(self, event):
        """Filtro en tiempo real del combobox"""
        if self.timer_articulos:
            self.timer_articulos.cancel()
        self.timer_articulos = threading.Timer(0.5, self._filter_articulos)
        self.timer_articulos.start()
    
    # ---------------------------------------------------------------------------------
    def _filter_articulos(self):
        typed = self.comboboxbuscar.get()
        if typed == '':
            data = self.articulos
        else:
            data = [item for item in self.articulos if typed.lower() in item.lower()]
        
        if data:
            self.comboboxbuscar['values'] = data
            self.comboboxbuscar.event_generate('<Down>')
        else:
            self.comboboxbuscar['values'] = ['No se encontraron resultados']
            self.comboboxbuscar.event_generate('<Down>')
        
        self.cargar_articulos(filtro=typed)
    
    # ---------------------------------------------------------------------------------
    def editar_articulo(self):
        """Ventana para editar un artículo existente"""
        selected_item = self.comboboxbuscar.get()
        if not selected_item:
            messagebox.showerror("Error", "Selecciona un artículo para editar")
            return
        
        conn = get_connection()
        if not conn:
            return
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT articulo, precio, costo, stock, estado, image_path FROM articulos WHERE articulo = %s",
                (selected_item,)
            )
            resultado = cursor.fetchone()
            if not resultado:
                messagebox.showerror("Error", "Artículo no encontrado")
                return
            articulo, precio, costo, stock, estado, image_path = resultado
        except Exception as e:
            messagebox.showerror("Error", f"Error al obtener datos: {e}")
            return
        finally:
            cursor.close()
            conn.close()
        
        # Ventana de edición
        top = tk.Toplevel(self)
        top.title("Editar Articulo")
        top.geometry("700x400+200+50")
        top.config(bg=estilos.COLORS['bg_primary'])
        top.resizable(False, False)
        top.transient(self.master)
        top.grab_set()
        top.focus_set()
        top.lift()
        
        tk.Label(top, text="Articulo", font="arial 12 bold", bg=estilos.COLORS['bg_primary']).place(x=20, y=20, width=130, height=25)
        entry_articulo = ttk.Entry(top, font='arial 12 bold')
        entry_articulo.place(x=160, y=20, width=250, height=30)
        entry_articulo.insert(0, articulo)
        entry_articulo.config(justify="center")
        
        tk.Label(top, text="Precio venta", font="arial 12 bold", bg=estilos.COLORS['bg_primary']).place(x=20, y=60, width=130, height=25)
        entry_precio = ttk.Entry(top, font='arial 12 bold')
        entry_precio.place(x=160, y=60, width=250, height=30)
        entry_precio.insert(0, str(precio))
        entry_precio.config(justify="center")
        
        tk.Label(top, text="Costo proveedor", font="arial 12 bold", bg=estilos.COLORS['bg_primary']).place(x=20, y=100, width=130, height=25)
        entry_costo = ttk.Entry(top, font='arial 12 bold')
        entry_costo.place(x=160, y=100, width=250, height=30)
        entry_costo.insert(0, str(costo))
        entry_costo.config(justify="center")
        
        tk.Label(top, text="Stock", font="arial 12 bold", bg=estilos.COLORS['bg_primary']).place(x=20, y=140, width=130, height=25)
        entry_stock = ttk.Entry(top, font='arial 12 bold')
        entry_stock.place(x=160, y=140, width=250, height=30)
        entry_stock.insert(0, str(stock))
        entry_stock.config(justify="center")
        
        tk.Label(top, text="Estado", font="arial 12 bold", bg=estilos.COLORS['bg_primary']).place(x=20, y=180, width=130, height=25)
        combo_estado = ttk.Combobox(top, values=["Activo", "Inactivo"], font='arial 12 bold', state="readonly")
        combo_estado.place(x=160, y=180, width=250, height=30)
        combo_estado.set(estado)
        combo_estado.config(justify="center")
        
        self.frameimg = tk.Frame(top, bg='#ffffff', highlightbackground="gray", highlightthickness=1)
        self.frameimg.place(x=440, y=30, width=200, height=200)
        
        if image_path and os.path.exists(image_path):
            try:
                image = Image.open(image_path)
                image = image.resize((200, 200), Image.Resampling.LANCZOS)
                self.product_img = ImageTk.PhotoImage(image)
                self.image_path = image_path
                image_label = tk.Label(self.frameimg, image=self.product_img)
                image_label.pack(expand=True, fill="both")
            except Exception as e:
                print(f"Error cargando imagen: {e}")
        
        btnimage = tk.Button(top, text='Cargar imagen', font="arial 12 bold", command=self.load_image)
        btnimage.place(x=470, y=260, width=150, height=40)
        
        def guardar_edicion():
            nuevo_articulo = entry_articulo.get().strip()
            precio_str = entry_precio.get().strip()
            costo_str = entry_costo.get().strip()
            stock_str = entry_stock.get().strip()
            estado = combo_estado.get().strip()
            
            if not nuevo_articulo or not precio_str or not costo_str or not estado:
                messagebox.showerror("Error", "Todos los campos deben ser completados")
                return
            
            try:
                precio = float(precio_str)
                costo = float(costo_str)
                stock = int(stock_str) if stock_str else 0
            except ValueError:
                messagebox.showerror("Error", "Precio, costo y stock deben ser números válidos")
                return
            
            image_path = getattr(self, 'image_path', 'media/icons/img_default.png')
            
            conn = get_connection()
            if not conn:
                return
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "UPDATE articulos SET articulo = %s, precio = %s, costo = %s, stock = %s, image_path = %s, estado = %s WHERE articulo = %s",
                    (nuevo_articulo, precio, costo, stock, image_path, estado, selected_item)
                )
                conn.commit()
                self.articulos_combobox()
                self.after(0, lambda: self.cargar_articulos(filtro=nuevo_articulo))
                top.destroy()
                messagebox.showinfo('Éxito', 'Artículo actualizado correctamente')
            except Exception as e:
                messagebox.showerror("Error", f"Error al actualizar: {e}")
            finally:
                cursor.close()
                conn.close()
        
        tk.Button(top, text='Guardar', font="arial 12 bold", command=guardar_edicion).place(x=50, y=260, width=150, height=40)
        tk.Button(top, text='Cancelar', font="arial 12 bold", command=top.destroy).place(x=260, y=260, width=150, height=40)
        
        # Botón eliminar (con confirmación)
        def eliminar_articulo():
            if messagebox.askyesno("Confirmar", f"¿Eliminar el artículo '{selected_item}'?"):
                conn = get_connection()
                if not conn:
                    return
                cursor = conn.cursor()
                try:
                    cursor.execute("DELETE FROM articulos WHERE articulo = %s", (selected_item,))
                    conn.commit()
                    self.articulos_combobox()
                    self.cargar_articulos()
                    top.destroy()
                    messagebox.showinfo("Éxito", "Artículo eliminado correctamente")
                except Exception as e:
                    messagebox.showerror("Error", f"Error al eliminar: {e}")
                finally:
                    cursor.close()
                    conn.close()
        
        tk.Button(top, bg="red", fg="white", text='Eliminar artículo', font="arial 12 bold", command=eliminar_articulo).place(x=260, y=330, width=150, height=40)