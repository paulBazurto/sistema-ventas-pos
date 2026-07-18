import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk
from PIL import Image, ImageTk
from modulos.utils.utils import generar_qr_producto
from modulos.utils.estilos_modernos import estilos
from data.models import get_connection
import threading
import os

# Configurar CustomTkinter para inventario
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class InventarioModerno(tk.Frame):
    
    def __init__(self, padre):
        super().__init__(padre)
        self.configure(bg=estilos.COLORS['bg_primary'])
        self.widgets()
        self.articulos_combobox()
        self.cargar_articulos()
        self.timer_articulos = None
        
        self.image_folder = 'media/img/img_productos'
        if not os.path.exists(self.image_folder):
            os.makedirs(self.image_folder)
        
    def widgets(self):
        # Frame principal de artículos con estilo moderno
        canvas_articulos = ctk.CTkFrame(self, corner_radius=15)
        canvas_articulos.place(x=300, y=10, width=895, height=740)
        
        # Título moderno
        title_label = ctk.CTkLabel(canvas_articulos, text="📦 Inventario de Productos", 
                                  font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"))
        title_label.pack(pady=10)
        
        # Canvas scrollable para productos
        self.canvas = tk.Canvas(canvas_articulos, bg=estilos.COLORS['white'])
        self.scrollbar = tk.Scrollbar(canvas_articulos, orient='vertical', command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=estilos.COLORS['white'])
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0,0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.scrollbar.pack(side='right', fill='y')
        self.canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        # Frame de búsqueda moderno
        search_frame = ctk.CTkFrame(self, corner_radius=15)
        search_frame.place(x=5, y=10, width=280, height=80)
        
        search_label = ctk.CTkLabel(search_frame, text="🔍 Buscar Producto", 
                                   font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"))
        search_label.pack(pady=5)
        
        self.comboboxbuscar = ttk.Combobox(search_frame, font=("Segoe UI", 12))
        self.comboboxbuscar.pack(padx=10, pady=5, fill='x')
        self.comboboxbuscar.bind('<<ComboboxSelected>>', self.on_combobox_select)
        self.comboboxbuscar.bind('<KeyRelease>', self.filtrar_articulos)
        
        # Frame de información del producto seleccionado
        info_frame = ctk.CTkFrame(self, corner_radius=15)
        info_frame.place(x=10, y=95, width=280, height=240)
        
        info_title = ctk.CTkLabel(info_frame, text="📋 Información del Producto", 
                                 font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"))
        info_title.pack(pady=10)
        
        self.label1 = ctk.CTkLabel(info_frame, text='Artículo: --', 
                                  font=ctk.CTkFont(family="Segoe UI", size=12), 
                                  wraplength=250, anchor='w')
        self.label1.pack(pady=5, padx=10, fill='x')
        
        self.label2 = ctk.CTkLabel(info_frame, text='Precio: --', 
                                  font=ctk.CTkFont(family="Segoe UI", size=12), anchor='w')
        self.label2.pack(pady=5, padx=10, fill='x')
        
        self.label3 = ctk.CTkLabel(info_frame, text='Código: --', 
                                  font=ctk.CTkFont(family="Segoe UI", size=12), anchor='w')
        self.label3.pack(pady=5, padx=10, fill='x')
        
        self.label4 = ctk.CTkLabel(info_frame, text='Stock: --', 
                                  font=ctk.CTkFont(family="Segoe UI", size=12), anchor='w')
        self.label4.pack(pady=5, padx=10, fill='x')
        
        self.label5 = ctk.CTkLabel(info_frame, text='Estado: --', 
                                  font=ctk.CTkFont(family="Segoe UI", size=12), anchor='w')
        self.label5.pack(pady=5, padx=10, fill='x')
        
        # Frame de botones modernos
        buttons_frame = ctk.CTkFrame(self, corner_radius=15)
        buttons_frame.place(x=10, y=350, width=290, height=270)
        
        buttons_title = ctk.CTkLabel(buttons_frame, text="⚙️ Opciones", 
                                    font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"))
        buttons_title.pack(pady=10)
        
        # Botones modernos con CustomTkinter
        btn1 = ctk.CTkButton(
            buttons_frame, 
            text="➕ Agregar Producto", 
            command=self.agregar_articulo,
            width=100,
            height=40,
            corner_radius=10,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color=estilos.COLORS['success'],
            hover_color="#28a745"
        )
        btn1.pack(pady=10)
        
        btn2 = ctk.CTkButton(
            buttons_frame, 
            text="✏️ Editar Producto", 
            command=self.editar_articulo,
            width=220,
            height=40,
            corner_radius=10,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color=estilos.COLORS['warning'],
            hover_color="#ffc107"
        )
        btn2.pack(pady=10)

        btn3 = ctk.CTkButton(
            buttons_frame, 
            text="🏷️ Imprimir Etiqueta", 
            command=generar_qr_producto,
            width=220,
            height=40,
            corner_radius=10,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color=estilos.COLORS['secondary'],
            hover_color="#6c757d"
        )
        btn3.pack(pady=10)
    
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
            
            # Limpiar el frame y mostrar la imagen
            for widget in self.frameimg.winfo_children():
                widget.destroy()
            image_label = tk.Label(self.frameimg, image=self.image_tk, bg='white')
            image_label.pack(expand=True, fill="both")
    
    def articulos_combobox(self):
        """Cargar lista de artículos activos para el combobox (versión MySQL)"""
        conn = get_connection()
        if not conn:
            return
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT articulo FROM articulos WHERE estado = 'activo' ORDER BY articulo")
            self.articulos = [row[0] for row in cursor.fetchall()]
            self.comboboxbuscar['values'] = self.articulos
        except Exception as e:
            print(f"Error al cargar artículos: {e}")
        finally:
            cursor.close()
            conn.close()
    
    def agregar_articulo(self):
        """Ventana para agregar nuevo producto (versión MySQL)"""
        top = ctk.CTkToplevel(self)
        top.title("Agregar Producto")
        top.geometry("800x500+200+50")
        top.resizable(False, False)
        
        # Título
        title = ctk.CTkLabel(top, text="➕ Agregar Nuevo Producto", 
                            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"))
        title.pack(pady=20)
        
        # Frame principal
        main_frame = ctk.CTkFrame(top)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Campos de entrada
        ctk.CTkLabel(main_frame, text="Código de Barras:", 
                    font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold")).place(x=20, y=20)
        entry_codigo = ctk.CTkEntry(main_frame, font=ctk.CTkFont(family="Segoe UI", size=12), width=250)
        entry_codigo.place(x=150, y=20)
        
        ctk.CTkLabel(main_frame, text="Nombre del Artículo:", 
                    font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold")).place(x=20, y=60)
        entry_articulo = ctk.CTkEntry(main_frame, font=ctk.CTkFont(family="Segoe UI", size=12), width=250)
        entry_articulo.place(x=150, y=60)
        
        ctk.CTkLabel(main_frame, text="Precio de Venta:", 
                    font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold")).place(x=20, y=100)
        entry_precio = ctk.CTkEntry(main_frame, font=ctk.CTkFont(family="Segoe UI", size=12), width=250)
        entry_precio.place(x=150, y=100)
        
        ctk.CTkLabel(main_frame, text="Costo del Producto:", 
                    font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold")).place(x=20, y=140)
        entry_costo = ctk.CTkEntry(main_frame, font=ctk.CTkFont(family="Segoe UI", size=12), width=250)
        entry_costo.place(x=150, y=140)
        
        ctk.CTkLabel(main_frame, text="Stock Inicial:", 
                    font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold")).place(x=20, y=180)
        entry_stock = ctk.CTkEntry(main_frame, font=ctk.CTkFont(family="Segoe UI", size=12), width=250)
        entry_stock.place(x=150, y=180)
        
        # Frame para imagen
        self.frameimg = ctk.CTkFrame(main_frame, width=200, height=200)
        self.frameimg.place(x=450, y=30)
        
        # Imagen por defecto (placeholder)
        img_label = ctk.CTkLabel(self.frameimg, text="📷\nImagen del Producto", 
                                font=ctk.CTkFont(family="Segoe UI", size=12))
        img_label.pack(expand=True)
        
        btnimage = ctk.CTkButton(main_frame, text='📁 Cargar Imagen', 
                                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                                command=self.load_image, width=150, height=35)
        btnimage.place(x=475, y=250)
        
        def guardar():
            codigo = entry_codigo.get().strip()
            articulo = entry_articulo.get().strip()
            precio_str = entry_precio.get().strip()
            costo_str = entry_costo.get().strip()
            stock_str = entry_stock.get().strip()
            
            if not all([codigo, articulo, precio_str, costo_str, stock_str]):
                messagebox.showerror("❌ Error", "Todos los campos deben ser completados")
                return
            
            try:
                precio = float(precio_str)
                costo = float(costo_str)
                stock = int(stock_str)
            except ValueError:
                messagebox.showerror("❌ Error", "Precio, costo y stock deben ser números válidos")
                return
            
            image_path = getattr(self, 'image_path', 'media/icons/img_default.png')
            
            conn = get_connection()
            if not conn:
                return
            cursor = conn.cursor()
            try:
                cursor.execute(
                    """INSERT INTO articulos 
                       (codigo, articulo, precio, costo, stock, estado, image_path) 
                       VALUES (%s, %s, %s, %s, %s, 'activo', %s)""",
                    (codigo, articulo, precio, costo, stock, image_path)
                )
                conn.commit()
                messagebox.showinfo('✅ Éxito', 'Producto agregado correctamente')
                top.destroy()
                self.cargar_articulos()
                self.articulos_combobox()
            except Exception as e:
                messagebox.showerror("❌ Error", f"Error al agregar producto: {e}")
            finally:
                cursor.close()
                conn.close()
        
        # Botones
        btn_frame = ctk.CTkFrame(main_frame)
        btn_frame.place(x=50, y=350, width=350, height=60)
        
        ctk.CTkButton(btn_frame, text='💾 Guardar', 
                     font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                     command=guardar, width=150, height=40,
                     fg_color=estilos.COLORS['success']).pack(side='left', padx=10, pady=10)
        
        ctk.CTkButton(btn_frame, text='❌ Cancelar', 
                     font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                     command=top.destroy, width=150, height=40,
                     fg_color=estilos.COLORS['danger']).pack(side='right', padx=10, pady=10)
    
    def cargar_articulos(self, filtro=None):
        """Cargar artículos de forma asíncrona"""
        self.after(0, self._cargar_articulos, filtro)
    
    def _cargar_articulos(self, filtro=None):
        """Cargar artículos desde MySQL (solo activos)"""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        conn = get_connection()
        if not conn:
            return
        cursor = conn.cursor()
        try:
            query = "SELECT codigo, articulo, precio, image_path FROM articulos WHERE estado = 'activo'"
            params = []
            if filtro:
                query += " AND articulo LIKE %s"
                params.append(f'%{filtro}%')
            query += " ORDER BY articulo"
            
            cursor.execute(query, params)
            articulos = cursor.fetchall()
            
            self.row = 0
            self.column = 0
            
            for codigo, articulo, precio, image_path in articulos:
                self.mostrar_articulo(codigo, articulo, precio, image_path)
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al cargar artículos: {e}")
        finally:
            cursor.close()
            conn.close()
    
    def mostrar_articulo(self, codigo, articulo, precio, image_path):
        """Mostrar un artículo en una tarjeta moderna"""
        article_frame = ctk.CTkFrame(self.scrollable_frame, corner_radius=10)
        article_frame.grid(row=self.row, column=self.column, padx=10, pady=10, sticky="nsew")
        
        # Imagen del producto
        if image_path and os.path.exists(image_path):
            try:
                image = Image.open(image_path)
                image = image.resize((120, 120), Image.Resampling.LANCZOS)
                imagen = ImageTk.PhotoImage(image)
                image_label = tk.Label(article_frame, image=imagen, bg='white')
                image_label.image = imagen
                image_label.pack(pady=5)
            except Exception:
                placeholder = ctk.CTkLabel(article_frame, text="📷", 
                                         font=ctk.CTkFont(size=40))
                placeholder.pack(pady=20)
        else:
            placeholder = ctk.CTkLabel(article_frame, text="📷", 
                                     font=ctk.CTkFont(size=40))
            placeholder.pack(pady=20)
        
        # Información del producto
        name_label = ctk.CTkLabel(article_frame, text=articulo, 
                                 font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                                 wraplength=140)
        name_label.pack(pady=2)
        
        precio_label = ctk.CTkLabel(article_frame, text=f'💰 ${precio:.2f}', 
                                   font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
                                   text_color=estilos.COLORS['success'])
        precio_label.pack(pady=2)
        
        codigo_label = ctk.CTkLabel(article_frame, text=f'🏷️ {codigo}', 
                                   font=ctk.CTkFont(family="Segoe UI", size=9),
                                   text_color=estilos.COLORS['secondary'])
        codigo_label.pack(pady=2)
        
        self.column += 1
        if self.column > 4:
            self.column = 0 
            self.row += 1
    
    def on_combobox_select(self, event):
        self.actualizar_label()
        
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
                "SELECT codigo, articulo, precio, costo, stock, estado FROM articulos WHERE articulo = %s",
                (articulo_seleccionado,)
            )
            resultado = cursor.fetchone()
            if resultado:
                codigo, articulo, precio, costo, stock, estado = resultado
                self.label1.configure(text=f'📦 Artículo: {articulo}')
                self.label2.configure(text=f'💰 Precio: ${precio:.2f}')
                self.label3.configure(text=f'🏷️ Código: {codigo}')
                self.label4.configure(text=f'📊 Stock: {stock} unidades')
                if estado.lower() == "activo":
                    self.label5.configure(text=f'✅ Estado: {estado}', text_color=estilos.COLORS['success'])
                else:
                    self.label5.configure(text=f'❌ Estado: {estado}', text_color=estilos.COLORS['danger'])
            else:
                self.label1.configure(text="📦 Artículo: No encontrado")
                self.label2.configure(text="💰 Precio: --")
                self.label3.configure(text="🏷️ Código: --")
                self.label4.configure(text="📊 Stock: --")
                self.label5.configure(text="❌ Estado: --")
        except Exception as e:
            print("Error al obtener datos:", e)
            messagebox.showerror("❌ Error", "Error al obtener los datos del artículo")
        finally:
            cursor.close()
            conn.close()
    
    def filtrar_articulos(self, event): 
        if self.timer_articulos:
            self.timer_articulos.cancel()
        self.timer_articulos = threading.Timer(0.5, self._filter_articulos)   
        self.timer_articulos.start()
    
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

    def editar_articulo(self):
        """Ventana para editar un artículo existente (versión MySQL)"""
        selected_item = self.comboboxbuscar.get()
        if not selected_item:
            messagebox.showerror("❌ Error", "Selecciona un artículo para editar")
            return
        
        conn = get_connection()
        if not conn:
            return
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT id, codigo, articulo, precio, costo, stock, estado, image_path FROM articulos WHERE articulo = %s",
                (selected_item,)
            )
            resultado = cursor.fetchone()
            if not resultado:
                messagebox.showerror("❌ Error", "Artículo no encontrado")
                return
            id_articulo, codigo, articulo, precio, costo, stock, estado, imagen_actual = resultado
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al obtener datos: {e}")
            return
        finally:
            cursor.close()
            conn.close()
        
        # Ventana de edición
        top = ctk.CTkToplevel(self)
        top.title("Editar Producto")
        top.geometry("800x500+200+50")
        top.resizable(False, False)
        
        title = ctk.CTkLabel(top, text="✏️ Editar Producto", 
                            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"))
        title.pack(pady=20)
        
        main_frame = ctk.CTkFrame(top)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Campos de entrada (precargados)
        ctk.CTkLabel(main_frame, text="Código de Barras:", 
                    font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold")).place(x=20, y=20)
        entry_codigo = ctk.CTkEntry(main_frame, font=ctk.CTkFont(family="Segoe UI", size=12), width=250)
        entry_codigo.place(x=150, y=20)
        entry_codigo.insert(0, codigo)
        
        ctk.CTkLabel(main_frame, text="Nombre del Artículo:", 
                    font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold")).place(x=20, y=60)
        entry_articulo = ctk.CTkEntry(main_frame, font=ctk.CTkFont(family="Segoe UI", size=12), width=250)
        entry_articulo.place(x=150, y=60)
        entry_articulo.insert(0, articulo)
        
        ctk.CTkLabel(main_frame, text="Precio de Venta:", 
                    font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold")).place(x=20, y=100)
        entry_precio = ctk.CTkEntry(main_frame, font=ctk.CTkFont(family="Segoe UI", size=12), width=250)
        entry_precio.place(x=150, y=100)
        entry_precio.insert(0, str(precio))
        
        ctk.CTkLabel(main_frame, text="Costo del Producto:", 
                    font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold")).place(x=20, y=140)
        entry_costo = ctk.CTkEntry(main_frame, font=ctk.CTkFont(family="Segoe UI", size=12), width=250)
        entry_costo.place(x=150, y=140)
        entry_costo.insert(0, str(costo))
        
        ctk.CTkLabel(main_frame, text="Stock:", 
                    font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold")).place(x=20, y=180)
        entry_stock = ctk.CTkEntry(main_frame, font=ctk.CTkFont(family="Segoe UI", size=12), width=250)
        entry_stock.place(x=150, y=180)
        entry_stock.insert(0, str(stock))
        
        # Estado
        ctk.CTkLabel(main_frame, text="Estado:", 
                    font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold")).place(x=20, y=220)
        combo_estado = ctk.CTkComboBox(main_frame, values=["activo", "inactivo"], 
                                      font=ctk.CTkFont(family="Segoe UI", size=12), width=250)
        combo_estado.place(x=150, y=220)
        combo_estado.set(estado)
        
        # Frame para imagen
        self.frameimg = ctk.CTkFrame(main_frame, width=200, height=200)
        self.frameimg.place(x=450, y=30)
        
        # Mostrar imagen existente si hay (CORREGIDO: usa imagen_actual, no image_path)
        if imagen_actual and os.path.exists(imagen_actual):
            try:
                image = Image.open(imagen_actual)
                image = image.resize((200, 200), Image.Resampling.LANCZOS)
                self.image_tk = ImageTk.PhotoImage(image)
                self.image_path = imagen_actual
                image_label = tk.Label(self.frameimg, image=self.image_tk, bg='white')
                image_label.pack(expand=True, fill="both")
            except Exception:
                img_label = ctk.CTkLabel(self.frameimg, text="📷\nImagen del Producto", 
                                        font=ctk.CTkFont(family="Segoe UI", size=12))
                img_label.pack(expand=True)
        else:
            img_label = ctk.CTkLabel(self.frameimg, text="📷\nImagen del Producto", 
                                    font=ctk.CTkFont(family="Segoe UI", size=12))
            img_label.pack(expand=True)
        
        btnimage = ctk.CTkButton(main_frame, text='📁 Cambiar Imagen', 
                                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                                command=self.load_image, width=150, height=35)
        btnimage.place(x=475, y=250)
        
        def guardar_edicion():
            nuevo_codigo = entry_codigo.get().strip()
            nuevo_articulo = entry_articulo.get().strip()
            precio_str = entry_precio.get().strip()
            costo_str = entry_costo.get().strip()
            stock_str = entry_stock.get().strip()
            nuevo_estado = combo_estado.get().strip()
            
            if not all([nuevo_codigo, nuevo_articulo, precio_str, costo_str, stock_str, nuevo_estado]):
                messagebox.showerror("❌ Error", "Todos los campos deben ser completados")
                return
            
            try:
                precio = float(precio_str)
                costo = float(costo_str)
                stock = int(stock_str)
            except ValueError:
                messagebox.showerror("❌ Error", "Precio, costo y stock deben ser números válidos")
                return
            
            # CORREGIDO: usa imagen_actual (la que vino de MySQL) como valor por defecto
            # en lugar de referenciar la variable image_path dentro de sí misma
            image_path = getattr(self, 'image_path', None) or imagen_actual
            
            conn = get_connection()
            if not conn:
                return
            cursor = conn.cursor()
            try:
                cursor.execute(
                    """UPDATE articulos 
                       SET codigo = %s, articulo = %s, precio = %s, costo = %s, stock = %s, estado = %s, image_path = %s 
                       WHERE id = %s""",
                    (nuevo_codigo, nuevo_articulo, precio, costo, stock, nuevo_estado, image_path, id_articulo)
                )
                conn.commit()
                self.articulos_combobox()
                self.cargar_articulos()
                top.destroy()
                messagebox.showinfo('✅ Éxito', 'Producto actualizado correctamente')
            except Exception as e:
                messagebox.showerror("❌ Error", f"Error al actualizar: {e}")
            finally:
                cursor.close()
                conn.close()
        
        # Botones
        btn_frame = ctk.CTkFrame(main_frame)
        btn_frame.place(x=50, y=350, width=350, height=60)
        
        ctk.CTkButton(btn_frame, text='💾 Guardar Cambios', 
                     font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                     command=guardar_edicion, width=150, height=40,
                     fg_color=estilos.COLORS['success']).pack(side='left', padx=10, pady=10)
        
        ctk.CTkButton(btn_frame, text='❌ Cancelar', 
                     font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                     command=top.destroy, width=150, height=40,
                     fg_color=estilos.COLORS['danger']).pack(side='right', padx=10, pady=10)
        
        # Botón eliminar (con confirmación)
        def eliminar_articulo():
            if messagebox.askyesno("⚠️ Confirmar", f"¿Eliminar el producto '{articulo}'?"):
                conn = get_connection()
                if not conn:
                    return
                cursor = conn.cursor()
                try:
                    cursor.execute("DELETE FROM articulos WHERE id = %s", (id_articulo,))
                    conn.commit()
                    self.articulos_combobox()
                    self.cargar_articulos()
                    top.destroy()
                    messagebox.showinfo("✅ Éxito", "Producto eliminado correctamente")
                except Exception as e:
                    messagebox.showerror("❌ Error", f"Error al eliminar: {e}")
                finally:
                    cursor.close()
                    conn.close()
        
        btn_eliminar = ctk.CTkButton(main_frame, text='🗑️ Eliminar Producto', 
                                    font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                                    command=eliminar_articulo, width=180, height=40,
                                    fg_color=estilos.COLORS['danger'])
        btn_eliminar.place(x=50, y=420)