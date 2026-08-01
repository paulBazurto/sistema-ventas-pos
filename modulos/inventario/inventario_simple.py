import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk
from PIL import Image, ImageTk
from modulos.utils.utils import generar_qr_producto
from modulos.utils.estilos_modernos import estilos
from data.models import get_connection
import threading
import os
import random
import time

# Import para reportlab (generación de PDF)
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import mm, A6, landscape
    from reportlab.lib import colors
    from reportlab.lib.units import mm
    REPORTLAB_DISPONIBLE = True
except ImportError:
    REPORTLAB_DISPONIBLE = False
    print("⚠️ ReportLab no instalado. Para generar PDF ejecuta: pip install reportlab")

# Import único a nivel de módulo, con fallback si el gestor de configuración no existe
try:
    from modulos.configuracion.gestor_configuracion import formatear_precio
except ImportError:
    formatear_precio = None

# Configurar CustomTkinter
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class InventarioSimple(tk.Frame):

    # ==================== NUEVO: CATEGORÍAS DISPONIBLES ====================
    CATEGORIAS = [
        "Alimentos y Bebidas",
        "Cuidado Personal e Higiene",
        "Limpieza y Aseo del Hogar",
        "Textil y Vestimenta",
        "Electrónica y Tecnología",
        "Ferretería y Herramientas",
        "Papelería y Oficina",
        "Mascotas",
        "Farmacia y Salud",
        "Juguetería y Entretenimiento",
        "Hogar y Decoración",
        "Otros"
    ]
    
    def __init__(self, padre):
        super().__init__(padre)
        self.configure(bg=estilos.COLORS['bg_primary'])
        self.asegurar_columna_categoria()  # NUEVO: garantiza que la columna exista en la BD
        self.widgets()
        self.articulos_combobox()
        self.cargar_articulos()
        self.timer_articulos = None
        
        self.image_folder = 'media/img/img_productos'
        if not os.path.exists(self.image_folder):
            os.makedirs(self.image_folder)
    
    def actualizar_moneda(self, nueva_moneda):
        """Actualizar precios cuando cambia la moneda"""
        try:
            # Recargar artículos con nueva moneda
            self.cargar_articulos()
            print(f"Módulo Inventario actualizado a moneda: {nueva_moneda}")
        except Exception as e:
            print(f"Error al actualizar moneda en Inventario: {e}")

    # ==================== NUEVO: MIGRACIÓN DE COLUMNA CATEGORÍA ====================
    def asegurar_columna_categoria(self):
        """Agrega la columna 'categoria' a la tabla articulos si todavía no existe."""
        conn = get_connection()
        if not conn:
            return
        cursor = conn.cursor()
        try:
            cursor.execute(
                "ALTER TABLE articulos ADD COLUMN categoria VARCHAR(100) NOT NULL DEFAULT 'Otros'"
            )
            conn.commit()
            print("✅ Columna 'categoria' creada en articulos")
        except Exception:
            # La columna ya existe (o el motor no soporta IF NOT EXISTS) -> se ignora
            pass
        finally:
            cursor.close()
            conn.close()
        
    def widgets(self):
        # Frame principal de artículos (ancho optimizado para 4 columnas)
        canvas_articulos = tk.LabelFrame(self, text="📦 Inventario de Productos", 
                                        font=('Segoe UI', 15, 'bold'), 
                                        bg=estilos.COLORS['white'])
        canvas_articulos.place(x=300, y=10, width=1100, height=740)
        
        # Canvas scrollable con configuración mejorada
        self.canvas = tk.Canvas(canvas_articulos, bg=estilos.COLORS['white'], highlightthickness=0)
        self.scrollbar = tk.Scrollbar(canvas_articulos, orient='vertical', command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=estilos.COLORS['white'])
        
        # Configurar el scroll correctamente
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        # Crear ventana en el canvas
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Configurar eventos de scroll con mouse
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_to_mousewheel(event):
            self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_from_mousewheel(event):
            self.canvas.unbind_all("<MouseWheel>")
        
        # Bind eventos de mouse
        self.canvas.bind('<Enter>', _bind_to_mousewheel)
        self.canvas.bind('<Leave>', _unbind_from_mousewheel)
        
        # Configurar el ancho del frame interno
        def configure_scroll_region(event):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            # Ajustar el ancho del frame interno al ancho del canvas
            canvas_width = event.width
            self.canvas.itemconfig(self.canvas_window, width=canvas_width)
        
        self.canvas.bind('<Configure>', configure_scroll_region)
        
        # Empaquetar elementos
        self.scrollbar.pack(side='right', fill='y')
        self.canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        # Frame de búsqueda
        search_frame = tk.LabelFrame(self, text="🔍 Buscar", 
                                   font=('Segoe UI', 14, 'bold'), 
                                   bg=estilos.COLORS['white'])
        search_frame.place(x=5, y=10, width=280, height=80)
        
        self.comboboxbuscar = ttk.Combobox(search_frame, font=('Segoe UI', 12))
        self.comboboxbuscar.place(x=5, y=5, width=260, height=40)
        self.comboboxbuscar.bind('<<ComboboxSelected>>', self.on_combobox_select)
        self.comboboxbuscar.bind('<KeyRelease>', self.filtrar_articulos)

        # ==================== NUEVO: FRAME DE FILTRO POR CATEGORÍA ====================
        category_filter_frame = tk.LabelFrame(self, text="🗂️ Filtrar por Categoría", 
                                   font=('Segoe UI', 14, 'bold'), 
                                   bg=estilos.COLORS['white'])
        category_filter_frame.place(x=5, y=95, width=280, height=80)

        self.combo_categoria_filtro = ttk.Combobox(
            category_filter_frame, 
            font=('Segoe UI', 11), 
            state="readonly",
            values=["Todas las categorías"] + self.CATEGORIAS
        )
        self.combo_categoria_filtro.place(x=5, y=5, width=260, height=40)
        self.combo_categoria_filtro.set("Todas las categorías")
        self.combo_categoria_filtro.bind('<<ComboboxSelected>>', self.filtrar_por_categoria)
        
        # Frame de información (movido hacia abajo para dejar espacio al filtro de categoría)
        info_frame = tk.LabelFrame(self, text='📋 Información del Producto', 
                                 font=('Segoe UI', 12, 'bold'), 
                                 bg=estilos.COLORS['white'])
        info_frame.place(x=10, y=180, width=280, height=250)
        
        self.label1 = tk.Label(info_frame, text='Artículo: --', 
                              font=('Segoe UI', 12, 'bold'), 
                              bg=estilos.COLORS['white'], 
                              wraplength=250, anchor='w')
        self.label1.place(x=5, y=5)
        
        self.label2 = tk.Label(info_frame, text='Precio: --', 
                              font=('Segoe UI', 12, 'bold'), 
                              bg=estilos.COLORS['white'])
        self.label2.place(x=5, y=40)
        
        self.label3 = tk.Label(info_frame, text='Código: --', 
                              font=('Segoe UI', 12, 'bold'), 
                              bg=estilos.COLORS['white'])
        self.label3.place(x=5, y=75)
        
        self.label4 = tk.Label(info_frame, text='Stock: --', 
                              font=('Segoe UI', 12, 'bold'), 
                              bg=estilos.COLORS['white'])
        self.label4.place(x=5, y=110)
        
        self.label5 = tk.Label(info_frame, text='Estado: --', 
                              font=('Segoe UI', 12, 'bold'), 
                              bg=estilos.COLORS['white'])
        self.label5.place(x=5, y=145)

        # NUEVO: label de categoría en el panel de información
        self.label6 = tk.Label(info_frame, text='Categoría: --', 
                              font=('Segoe UI', 12, 'bold'), 
                              bg=estilos.COLORS['white'],
                              wraplength=250, anchor='w')
        self.label6.place(x=5, y=180)
        
        # Frame de botones con CustomTkinter (movido hacia abajo)
        buttons_frame = tk.LabelFrame(self, text="⚙️ Opciones", 
                                    font=('Segoe UI', 14, 'bold'), 
                                    bg=estilos.COLORS['white'])
        buttons_frame.place(x=10, y=450, width=280, height=270)
        
        # Botones modernos
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
        btn1.place(x=20, y=20)
        
        btn2 = ctk.CTkButton(
            buttons_frame, 
            text="✏️ Editar Producto", 
            command=self.editar_articulo,
            width=100,
            height=40,
            corner_radius=10,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color=estilos.COLORS['warning'],
            hover_color="#ffc107"
        )
        btn2.place(x=20, y=80)

        btn3 = ctk.CTkButton(
            buttons_frame, 
            text="🏷️ Imprimir Etiqueta", 
            command=self.imprimir_etiqueta,
            width=100,
            height=40,
            corner_radius=10,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color=estilos.COLORS['secondary'],
            hover_color="#6c757d"
        )
        btn3.place(x=20, y=140)
    
    def articulos_combobox(self):
        """Cargar lista de artículos activos (versión MySQL)"""
        conn = get_connection()
        if not conn:
            self.articulos = []
            self.comboboxbuscar['values'] = []
            return
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT articulo FROM articulos WHERE estado = 'activo' ORDER BY articulo")
            self.articulos = [row[0] for row in cursor.fetchall()]
            self.comboboxbuscar['values'] = self.articulos
        except Exception as e:
            print(f"Error cargando artículos para combobox: {e}")
            self.articulos = []
        finally:
            cursor.close()
            conn.close()

    # ==================== NUEVO: FILTRO POR CATEGORÍA ====================
    def filtrar_por_categoria(self, event=None):
        """Se ejecuta al elegir una categoría en el combobox de filtro."""
        texto_actual = self.comboboxbuscar.get()
        self.cargar_articulos(filtro=texto_actual)

    def obtener_categoria_filtro_actual(self):
        """Devuelve la categoría seleccionada en el filtro, o None si es 'Todas'."""
        if not hasattr(self, 'combo_categoria_filtro'):
            return None
        seleccion = self.combo_categoria_filtro.get()
        if not seleccion or seleccion == "Todas las categorías":
            return None
        return seleccion
    
    def agregar_articulo(self):
        """Ventana para agregar un nuevo producto (versión MySQL)"""
        top = tk.Toplevel(self)
        top.title("➕ Agregar Nuevo Producto")
        top.geometry("950x750+200+50")      # Más alto para dar espacio
        top.minsize(800, 650)
        top.configure(bg=estilos.COLORS['white'])
        top.resizable(True, True)
        
        top.transient(self.master)
        top.grab_set()
        top.focus_set()
        top.lift()
        
        # Título
        title_label = tk.Label(top, text="➕ Agregar Nuevo Producto", 
                              font=('Segoe UI', 16, 'bold'), 
                              bg=estilos.COLORS['white'],
                              fg=estilos.COLORS['primary'])
        title_label.pack(pady=15)
        
        # Frame principal
        main_frame = tk.Frame(top, bg=estilos.COLORS['white'])
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Campos de entrada
        tk.Label(main_frame, text="Código de Barras:", 
                font=('Segoe UI', 12, 'bold'), 
                bg=estilos.COLORS['white']).place(x=20, y=20)
        entry_codigo = tk.Entry(main_frame, font=('Segoe UI', 12), width=30)
        entry_codigo.place(x=180, y=20)
        
        tk.Label(main_frame, text="Nombre del Artículo:", 
                font=('Segoe UI', 12, 'bold'), 
                bg=estilos.COLORS['white']).place(x=20, y=60)
        entry_articulo = tk.Entry(main_frame, font=('Segoe UI', 12), width=30)
        entry_articulo.place(x=180, y=60)
        
        tk.Label(main_frame, text="Precio de Venta:", 
                font=('Segoe UI', 12, 'bold'), 
                bg=estilos.COLORS['white']).place(x=20, y=100)
        entry_precio = tk.Entry(main_frame, font=('Segoe UI', 12), width=30)
        entry_precio.place(x=180, y=100)
        
        tk.Label(main_frame, text="Costo del Producto:", 
                font=('Segoe UI', 12, 'bold'), 
                bg=estilos.COLORS['white']).place(x=20, y=140)
        entry_costo = tk.Entry(main_frame, font=('Segoe UI', 12), width=30)
        entry_costo.place(x=180, y=140)
        
        tk.Label(main_frame, text="Stock Inicial:", 
                font=('Segoe UI', 12, 'bold'), 
                bg=estilos.COLORS['white']).place(x=20, y=180)
        entry_stock = tk.Entry(main_frame, font=('Segoe UI', 12), width=30)
        entry_stock.place(x=180, y=180)

        # ==================== NUEVO: CAMPO DE CATEGORÍA ====================
        tk.Label(main_frame, text="Categoría:", 
                font=('Segoe UI', 12, 'bold'), 
                bg=estilos.COLORS['white']).place(x=20, y=220)
        combo_categoria = ttk.Combobox(main_frame, values=self.CATEGORIAS, 
                                      font=('Segoe UI', 12), state="readonly", width=28)
        combo_categoria.place(x=180, y=220)
        combo_categoria.set(self.CATEGORIAS[-1])  # "Otros" por defecto
        
        # Frame para imagen
        self.frameimg = tk.Frame(main_frame, bg='lightgray', relief='solid', bd=1)
        self.frameimg.place(x=480, y=30, width=180, height=180)
        
        img_placeholder = tk.Label(self.frameimg, text="📷\nImagen del\nProducto", 
                                  font=('Segoe UI', 12), bg='lightgray')
        img_placeholder.pack(expand=True)
        
        # Botón Cargar Imagen mejorado
        btn_imagen = ctk.CTkButton(
            main_frame, 
            text='📁 Cargar Imagen', 
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            command=self.load_image, 
            width=180, 
            height=45,
            corner_radius=10,
            fg_color=estilos.COLORS['info'],
            hover_color="#0ea5e9",
            text_color=estilos.COLORS['white'],
            border_width=1,
            border_color=estilos.COLORS['primary']
        )
        btn_imagen.place(x=355, y=225)  # Justo debajo de la imagen
       
        
        def guardar():
            codigo = entry_codigo.get().strip()
            articulo = entry_articulo.get().strip()
            precio_str = entry_precio.get().strip()
            costo_str = entry_costo.get().strip()
            stock_str = entry_stock.get().strip()
            categoria = combo_categoria.get()  # NUEVO
            
            if not all([codigo, articulo, precio_str, costo_str, stock_str, categoria]):
                messagebox.showerror("❌ Error", "Todos los campos deben ser completados")
                return
            
            try:
                precio_float = float(precio_str)
                costo_float = float(costo_str)
                stock_int = int(stock_str)
                if precio_float <= 0 or costo_float <= 0 or stock_int < 0:
                    messagebox.showerror("❌ Error", "Los valores deben ser positivos")
                    return
            except ValueError:
                messagebox.showerror("❌ Error", "Precio, costo y stock deben ser números válidos")
                return
            
            conn = get_connection()
            if not conn:
                return
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT codigo FROM articulos WHERE codigo = %s", (codigo,))
                if cursor.fetchone():
                    messagebox.showerror("❌ Error", f"El código '{codigo}' ya existe")
                    cursor.close()
                    conn.close()
                    return
            except Exception:
                pass
            
            imagen_path = getattr(self, 'image_path', 'media/icons/img_default.png')
            
            try:
                cursor.execute("""INSERT INTO articulos 
                               (codigo, articulo, precio, costo, stock, estado, image_path, categoria) 
                               VALUES (%s, %s, %s, %s, %s, 'activo', %s, %s)""", 
                               (codigo, articulo, precio_float, costo_float, stock_int, imagen_path, categoria))
                conn.commit()
                messagebox.showinfo('✅ Éxito', f'Producto "{articulo}" agregado correctamente')
                top.destroy()
                self.cargar_articulos()
                self.articulos_combobox()
            except Exception as e:
                print(f'Error al agregar producto: {e}')
                messagebox.showerror("❌ Error", f"Error al agregar producto: {e}")
            finally:
                cursor.close()
                conn.close()
        
        # Frame para botones (más abajo para dejar espacio)
        btn_frame = tk.Frame(main_frame, bg=estilos.COLORS['white'])
        btn_frame.place(x=50, y=340, width=400, height=60)  # Antes 320
        
        btn_guardar = ctk.CTkButton(btn_frame, text='💾 Guardar Producto', 
                                   font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                                   command=guardar, width=180, height=40,
                                   fg_color=estilos.COLORS['success'],
                                   hover_color="#28a745")
        btn_guardar.pack(side='left', padx=10, pady=10)
        
        btn_cancelar = ctk.CTkButton(btn_frame, text='❌ Cancelar', 
                                    font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                                    command=top.destroy, width=180, height=40,
                                    fg_color=estilos.COLORS['danger'],
                                    hover_color="#dc3545")
        btn_cancelar.pack(side='right', padx=10, pady=10)
    
    def load_image(self):
        file_path = filedialog.askopenfilename(
            title="Seleccionar imagen del producto",
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.gif *.bmp"), ("PNG", "*.png"), ("JPEG", "*.jpg *.jpeg"), ("Todos los archivos", "*.*")]
        )
        if file_path:
            try:
                image = Image.open(file_path)
                image = image.resize((180, 180), Image.Resampling.LANCZOS)
                image_name = os.path.basename(file_path)
                image_save_path = os.path.join(self.image_folder, image_name)
                image.save(image_save_path)
                self.image_tk = ImageTk.PhotoImage(image)
                self.image_path = image_save_path
                for widget in self.frameimg.winfo_children():
                    widget.destroy()
                image_label = tk.Label(self.frameimg, image=self.image_tk, bg='lightgray')
                image_label.pack(expand=True, fill='both')
                messagebox.showinfo("✅ Éxito", "Imagen cargada correctamente")
            except Exception as e:
                messagebox.showerror("❌ Error", f"Error al cargar la imagen: {e}")
    
    def editar_articulo(self):
        producto_seleccionado = self.comboboxbuscar.get().strip()
        if not producto_seleccionado:
            messagebox.showerror("❌ Error", "Selecciona un producto para editar")
            return
        
        conn = get_connection()
        if not conn:
            return
        cursor = conn.cursor()
        try:
            cursor.execute("""SELECT codigo, articulo, precio, costo, stock, estado, image_path, categoria 
                              FROM articulos WHERE articulo = %s""", (producto_seleccionado,))
            resultado = cursor.fetchone()
            if not resultado:
                messagebox.showerror("❌ Error", "Producto no encontrado")
                return
            (codigo_actual, articulo_actual, precio_actual, costo_actual, 
             stock_actual, estado_actual, imagen_actual, categoria_actual) = resultado
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al obtener datos del producto: {e}")
            return
        finally:
            cursor.close()
            conn.close()

        # NUEVO: si el producto no tiene categoría asignada (registros antiguos), usar "Otros"
        if not categoria_actual:
            categoria_actual = "Otros"
        
        # Ventana de edición más grande y con más espacio
        top = tk.Toplevel(self)
        top.title("✏️ Editar Producto")
        top.geometry("950x750+200+50")
        top.minsize(800, 650)
        top.configure(bg=estilos.COLORS['white'])
        top.resizable(True, True)
        top.transient(self.master)
        top.grab_set()
        top.focus_set()
        top.lift()
        
        title_label = tk.Label(top, text=f"✏️ Editar Producto: {articulo_actual}", 
                              font=('Segoe UI', 16, 'bold'), 
                              bg=estilos.COLORS['white'],
                              fg=estilos.COLORS['primary'])
        title_label.pack(pady=15)
        
        main_frame = tk.Frame(top, bg=estilos.COLORS['white'])
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Campos
        tk.Label(main_frame, text="Código de Barras:", font=('Segoe UI', 12, 'bold'), bg=estilos.COLORS['white']).place(x=20, y=20)
        entry_codigo = tk.Entry(main_frame, font=('Segoe UI', 12), width=30)
        entry_codigo.place(x=180, y=20)
        entry_codigo.insert(0, codigo_actual)
        
        tk.Label(main_frame, text="Nombre del Artículo:", font=('Segoe UI', 12, 'bold'), bg=estilos.COLORS['white']).place(x=20, y=60)
        entry_articulo = tk.Entry(main_frame, font=('Segoe UI', 12), width=30)
        entry_articulo.place(x=180, y=60)
        entry_articulo.insert(0, articulo_actual)
        
        tk.Label(main_frame, text="Precio de Venta:", font=('Segoe UI', 12, 'bold'), bg=estilos.COLORS['white']).place(x=20, y=100)
        entry_precio = tk.Entry(main_frame, font=('Segoe UI', 12), width=30)
        entry_precio.place(x=180, y=100)
        entry_precio.insert(0, str(precio_actual))
        
        tk.Label(main_frame, text="Costo del Producto:", font=('Segoe UI', 12, 'bold'), bg=estilos.COLORS['white']).place(x=20, y=140)
        entry_costo = tk.Entry(main_frame, font=('Segoe UI', 12), width=30)
        entry_costo.place(x=180, y=140)
        entry_costo.insert(0, str(costo_actual))
        
        tk.Label(main_frame, text="Stock:", font=('Segoe UI', 12, 'bold'), bg=estilos.COLORS['white']).place(x=20, y=180)
        entry_stock = tk.Entry(main_frame, font=('Segoe UI', 12), width=30)
        entry_stock.place(x=180, y=180)
        entry_stock.insert(0, str(stock_actual))
        
        tk.Label(main_frame, text="Estado:", font=('Segoe UI', 12, 'bold'), bg=estilos.COLORS['white']).place(x=20, y=220)
        combo_estado = ttk.Combobox(main_frame, values=["activo", "inactivo"], font=('Segoe UI', 12), state="readonly", width=28)
        combo_estado.place(x=180, y=220)
        combo_estado.set(estado_actual)

        # ==================== NUEVO: CAMPO DE CATEGORÍA ====================
        tk.Label(main_frame, text="Categoría:", font=('Segoe UI', 12, 'bold'), bg=estilos.COLORS['white']).place(x=20, y=260)
        combo_categoria = ttk.Combobox(main_frame, values=self.CATEGORIAS, font=('Segoe UI', 12), state="readonly", width=28)
        combo_categoria.place(x=180, y=260)
        combo_categoria.set(categoria_actual)
        
        # Frame para imagen
        self.frameimg_edit = tk.Frame(main_frame, bg='lightgray', relief='solid', bd=1)
        self.frameimg_edit.place(x=480, y=30, width=180, height=180)
        
        if imagen_actual and os.path.exists(imagen_actual):
            try:
                image = Image.open(imagen_actual)
                image = image.resize((180, 180), Image.Resampling.LANCZOS)
                self.current_image_tk = ImageTk.PhotoImage(image)
                self.current_image_path = imagen_actual
                image_label = tk.Label(self.frameimg_edit, image=self.current_image_tk, bg='lightgray')
                image_label.pack(expand=True, fill='both')
            except Exception:
                img_placeholder = tk.Label(self.frameimg_edit, text="📷\nImagen\nActual", font=('Segoe UI', 12), bg='lightgray')
                img_placeholder.pack(expand=True)
        else:
            img_placeholder = tk.Label(self.frameimg_edit, text="📷\nSin\nImagen", font=('Segoe UI', 12), bg='lightgray')
            img_placeholder.pack(expand=True)
            self.current_image_path = imagen_actual
        
        # Botón Cambiar Imagen (justo debajo de la imagen)
        def cambiar_imagen():
            file_path = filedialog.askopenfilename(
                title="Seleccionar nueva imagen",
                filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.gif *.bmp"), ("PNG", "*.png"), ("JPEG", "*.jpg *.jpeg"), ("Todos los archivos", "*.*")]
            )
            if file_path:
                try:
                    image = Image.open(file_path)
                    image = image.resize((180, 180), Image.Resampling.LANCZOS)
                    image_name = os.path.basename(file_path)
                    image_save_path = os.path.join(self.image_folder, image_name)
                    image.save(image_save_path)
                    self.current_image_tk = ImageTk.PhotoImage(image)
                    self.current_image_path = image_save_path
                    for widget in self.frameimg_edit.winfo_children():
                        widget.destroy()
                    image_label = tk.Label(self.frameimg_edit, image=self.current_image_tk, bg='lightgray')
                    image_label.pack(expand=True, fill='both')
                    messagebox.showinfo("✅ Éxito", "Imagen actualizada correctamente")
                except Exception as e:
                    messagebox.showerror("❌ Error", f"Error al cargar imagen: {e}")
        
        btn_imagen = ctk.CTkButton(
            main_frame, 
            text='📁 Cambiar Imagen', 
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            command=cambiar_imagen, 
            width=180, 
            height=45,
            corner_radius=10,
            fg_color=estilos.COLORS['info'],
            hover_color="#0ea5e9",
            text_color=estilos.COLORS['white'],
            border_width=1,
            border_color=estilos.COLORS['primary']
        )
        btn_imagen.place(x=365, y=225)  # Justo debajo de la imagen
        
        # Funciones de guardar, eliminar...
        def guardar_cambios():
            codigo = entry_codigo.get().strip()
            articulo = entry_articulo.get().strip()
            precio_str = entry_precio.get().strip()
            costo_str = entry_costo.get().strip()
            stock_str = entry_stock.get().strip()
            estado = combo_estado.get()
            categoria = combo_categoria.get()  # NUEVO
            
            if not all([codigo, articulo, precio_str, costo_str, stock_str, estado, categoria]):
                messagebox.showerror("❌ Error", "Todos los campos deben ser completados")
                return
            try:
                precio_float = float(precio_str)
                costo_float = float(costo_str)
                stock_int = int(stock_str)
                if precio_float <= 0 or costo_float <= 0 or stock_int < 0:
                    messagebox.showerror("❌ Error", "Los valores deben ser positivos")
                    return
            except ValueError:
                messagebox.showerror("❌ Error", "Precio, costo y stock deben ser números válidos")
                return
            
            conn = get_connection()
            if not conn:
                return
            cursor = conn.cursor()
            try:
                if codigo != codigo_actual:
                    cursor.execute("SELECT codigo FROM articulos WHERE codigo = %s AND articulo != %s", 
                                   (codigo, producto_seleccionado))
                    if cursor.fetchone():
                        messagebox.showerror("❌ Error", f"El código '{codigo}' ya existe en otro producto")
                        cursor.close()
                        conn.close()
                        return
                imagen_path = getattr(self, 'current_image_path', imagen_actual)
                cursor.execute("""UPDATE articulos 
                               SET codigo = %s, articulo = %s, precio = %s, costo = %s, stock = %s, 
                                   estado = %s, image_path = %s, categoria = %s
                               WHERE articulo = %s""", 
                               (codigo, articulo, precio_float, costo_float, stock_int, estado, 
                                imagen_path, categoria, producto_seleccionado))
                conn.commit()
                messagebox.showinfo('✅ Éxito', f'Producto "{articulo}" actualizado correctamente')
                top.destroy()
                self.cargar_articulos()
                self.articulos_combobox()
                self.comboboxbuscar.set(articulo)
                self.actualizar_label()
            except Exception as e:
                print(f'Error al actualizar producto: {e}')
                messagebox.showerror("❌ Error", f"Error al actualizar producto: {e}")
            finally:
                cursor.close()
                conn.close()
        
        def eliminar_producto():
            respuesta = messagebox.askyesno("⚠️ Confirmar Eliminación", 
                                          f"¿Estás seguro de que quieres eliminar el producto '{articulo_actual}'?\n\nEsta acción no se puede deshacer.")
            if respuesta:
                conn = get_connection()
                if not conn:
                    return
                cursor = conn.cursor()
                try:
                    cursor.execute("DELETE FROM articulos WHERE articulo = %s", (producto_seleccionado,))
                    conn.commit()
                    messagebox.showinfo('✅ Éxito', f'Producto "{articulo_actual}" eliminado correctamente')
                    top.destroy()
                    self.cargar_articulos()
                    self.articulos_combobox()
                    self.comboboxbuscar.set("")
                    self.label1.config(text="📦 Artículo: --")
                    self.label2.config(text="💰 Precio: --")
                    self.label3.config(text="🏷️ Código: --")
                    self.label4.config(text="📊 Stock: --")
                    self.label5.config(text="❌ Estado: --")
                    self.label6.config(text="🗂️ Categoría: --")  # NUEVO
                except Exception as e:
                    print(f'Error al eliminar producto: {e}')
                    messagebox.showerror("❌ Error", f"Error al eliminar producto: {e}")
                finally:
                    cursor.close()
                    conn.close()
        
        # Frame para botones (más abajo, para dejar espacio al campo de categoría)
        btn_frame = tk.Frame(main_frame, bg=estilos.COLORS['white'])
        btn_frame.place(x=20, y=380, width=640, height=60)  # Antes y=340
        
        btn_guardar = ctk.CTkButton(btn_frame, text='💾 Guardar Cambios', 
                                   font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                                   command=guardar_cambios, width=150, height=40,
                                   fg_color=estilos.COLORS['success'])
        btn_guardar.pack(side='left', padx=10, pady=10)
        
        btn_eliminar = ctk.CTkButton(btn_frame, text='🗑️ Eliminar', 
                                    font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                                    command=eliminar_producto, width=150, height=40,
                                    fg_color="#dc3545")
        btn_eliminar.pack(side='left', padx=10, pady=10)
        
        btn_cancelar = ctk.CTkButton(btn_frame, text='❌ Cancelar', 
                                    font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                                    command=top.destroy, width=150, height=40,
                                    fg_color=estilos.COLORS['secondary'])
        btn_cancelar.pack(side='right', padx=10, pady=10)
    
    def imprimir_etiqueta(self):
        # (Misma función que antes, sin cambios)
        producto_seleccionado = self.comboboxbuscar.get().strip()
        if not producto_seleccionado:
            messagebox.showerror("❌ Error", "Selecciona un producto para imprimir su etiqueta")
            return

        conn = get_connection()
        if not conn:
            return
        cursor = conn.cursor()
        try:
            cursor.execute("""SELECT codigo, articulo, precio, image_path 
                              FROM articulos WHERE articulo = %s""", (producto_seleccionado,))
            resultado = cursor.fetchone()
            if not resultado:
                messagebox.showerror("❌ Error", "Producto no encontrado")
                return
            codigo, articulo, precio, imagen_path = resultado
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al obtener datos del producto: {e}")
            return
        finally:
            cursor.close()
            conn.close()

        top = tk.Toplevel(self)
        top.title("🏷️ Imprimir / Generar Etiqueta")
        top.geometry("840x800+250+50")
        top.minsize(700, 700)
        top.configure(bg=estilos.COLORS['white'])
        top.resizable(True, True)
        top.transient(self.master)
        top.grab_set()
        top.focus_set()
        top.lift()

        main_container = tk.Frame(top, bg=estilos.COLORS['white'])
        main_container.pack(fill='both', expand=True, padx=10, pady=10)

        title_label = tk.Label(main_container, text="🏷️ Vista Previa de Etiqueta", 
                              font=('Segoe UI', 18, 'bold'), 
                              bg=estilos.COLORS['white'],
                              fg=estilos.COLORS['primary'])
        title_label.pack(pady=(0, 10))

        canvas_container = tk.Frame(main_container, bg='white', relief='solid', bd=1)
        canvas_container.pack(fill='both', expand=True, padx=5, pady=5)

        canvas_etiqueta = tk.Canvas(canvas_container, bg='white', highlightthickness=0)
        scrollbar_y = tk.Scrollbar(canvas_container, orient='vertical', command=canvas_etiqueta.yview)
        scrollbar_x = tk.Scrollbar(canvas_container, orient='horizontal', command=canvas_etiqueta.xview)
        canvas_etiqueta.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        etiqueta_inner = tk.Frame(canvas_etiqueta, bg='white')
        canvas_etiqueta.create_window((0, 0), window=etiqueta_inner, anchor='nw')
        scrollbar_y.pack(side='right', fill='y')
        scrollbar_x.pack(side='bottom', fill='x')
        canvas_etiqueta.pack(side='left', fill='both', expand=True)

        def dibujar_etiqueta(canvas_widget, width=500, height=300):
            canvas_widget.delete('all')
            canvas_widget.create_rectangle(0, 0, width, height, fill='white', outline='black', width=2)
            canvas_widget.create_text(width//2, 50, text=articulo, font=('Arial', 16, 'bold'), fill='black', anchor='center', width=width-40)
            def generar_codigo_barras(canvas, codigo, x, y, w=300, h=60):
                canvas.create_rectangle(x, y, x+w, y+h, fill='white', outline='black')
                random.seed(hash(codigo))
                bar_width = 2.5
                current_x = x + 10
                for _ in range(len(codigo) * 4):
                    if random.choice([True, False]):
                        canvas.create_rectangle(current_x, y+5, current_x+bar_width, y+h-5, fill='black', outline='black')
                    current_x += bar_width
                    if current_x > x + w - 20:
                        break
            generar_codigo_barras(canvas_widget, codigo, (width-300)//2, 100, 300, 60)
            canvas_widget.create_text(width//2, 180, text=codigo, font=('Arial', 14), fill='black', anchor='center')
            canvas_widget.create_text(width//2, 230, text=f"${precio:.2f} USD", font=('Arial', 24, 'bold'), fill='black', anchor='center')
            canvas_widget.configure(scrollregion=canvas_widget.bbox('all'))

        etiqueta_canvas = tk.Canvas(etiqueta_inner, width=500, height=300, bg='white', highlightthickness=1, highlightbackground='gray')
        etiqueta_canvas.pack(padx=20, pady=20)
        dibujar_etiqueta(etiqueta_canvas, 500, 300)

        def on_inner_configure(event):
            canvas_etiqueta.configure(scrollregion=canvas_etiqueta.bbox('all'))
        etiqueta_inner.bind('<Configure>', on_inner_configure)

        info_frame = tk.Frame(main_container, bg=estilos.COLORS['white'])
        info_frame.pack(fill='x', pady=5)
        tk.Label(info_frame, text=f"📦 Producto: {articulo}", font=('Segoe UI', 12), bg=estilos.COLORS['white']).pack(anchor='w', padx=10)
        tk.Label(info_frame, text=f"🏷️ Código: {codigo}", font=('Segoe UI', 12), bg=estilos.COLORS['white']).pack(anchor='w', padx=10)
        tk.Label(info_frame, text=f"💰 Precio: ${precio:.2f} USD", font=('Segoe UI', 12), bg=estilos.COLORS['white']).pack(anchor='w', padx=10)

        config_frame = tk.LabelFrame(main_container, text="⚙️ Configuración", font=('Segoe UI', 12, 'bold'), bg=estilos.COLORS['white'])
        config_frame.pack(fill='x', pady=5, padx=5)
        config_grid = tk.Frame(config_frame, bg=estilos.COLORS['white'])
        config_grid.pack(pady=5, padx=10, fill='x')

        tk.Label(config_grid, text="Cantidad:", font=('Segoe UI', 11), bg=estilos.COLORS['white']).grid(row=0, column=0, sticky='w', padx=5, pady=2)
        cantidad_var = tk.StringVar(value="1")
        cantidad_entry = tk.Entry(config_grid, textvariable=cantidad_var, font=('Segoe UI', 11), width=8)
        cantidad_entry.grid(row=0, column=1, padx=5, pady=2)

        tk.Label(config_grid, text="Tamaño:", font=('Segoe UI', 11), bg=estilos.COLORS['white']).grid(row=0, column=2, sticky='w', padx=15, pady=2)
        tamaño_combo = ttk.Combobox(config_grid, values=["58mm x 40mm", "58mm x 60mm", "80mm x 40mm"], font=('Segoe UI', 11), state="readonly", width=15)
        tamaño_combo.grid(row=0, column=3, padx=5, pady=2)
        tamaño_combo.set("58mm x 40mm")

        def enviar_a_impresora():
            try:
                cantidad = int(cantidad_var.get())
                if cantidad <= 0:
                    messagebox.showerror("❌ Error", "La cantidad debe ser mayor a 0")
                    return
                tamaño = tamaño_combo.get()
                progress_window = tk.Toplevel(top)
                progress_window.title("🖨️ Imprimiendo...")
                progress_window.geometry("300x150+400+200")
                progress_window.configure(bg=estilos.COLORS['white'])
                progress_window.resizable(False, False)
                progress_window.transient(top)
                progress_window.grab_set()

                tk.Label(progress_window, text="🖨️ Enviando a impresora térmica...", font=('Segoe UI', 12, 'bold'), bg=estilos.COLORS['white']).pack(pady=20)
                progress_bar = ttk.Progressbar(progress_window, mode='indeterminate')
                progress_bar.pack(pady=10, padx=20, fill='x')
                progress_bar.start()
                status_label = tk.Label(progress_window, text=f"Imprimiendo {cantidad} etiqueta(s)...", font=('Segoe UI', 10), bg=estilos.COLORS['white'])
                status_label.pack(pady=10)
                progress_window.update()

                import time
                for i in range(cantidad):
                    time.sleep(1)
                    status_label.config(text=f"Imprimiendo etiqueta {i+1} de {cantidad}...")
                    progress_window.update()

                progress_bar.stop()
                progress_window.destroy()

                messagebox.showinfo("✅ Éxito", f"Se enviaron {cantidad} etiqueta(s) a la impresora.\nProducto: {articulo}\nCódigo: {codigo}\nPrecio: ${precio:.2f} USD\nTamaño: {tamaño}")
                top.destroy()
            except ValueError:
                messagebox.showerror("❌ Error", "Cantidad inválida")
            except Exception as e:
                messagebox.showerror("❌ Error", f"Error al imprimir: {e}")

        def generar_pdf_etiqueta():
            if not REPORTLAB_DISPONIBLE:
                messagebox.showerror("❌ Error", "ReportLab no está instalado.\nEjecute: pip install reportlab")
                return
            try:
                cantidad = int(cantidad_var.get())
                if cantidad <= 0:
                    messagebox.showerror("❌ Error", "La cantidad debe ser mayor a 0")
                    return
            except ValueError:
                messagebox.showerror("❌ Error", "Cantidad inválida")
                return

            from tkinter import filedialog
            filename = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("Archivos PDF", "*.pdf"), ("Todos los archivos", "*.*")],
                title="Guardar etiqueta como PDF",
                initialfile=f"etiqueta_{codigo}.pdf"
            )
            if not filename:
                return

            try:
                from reportlab.pdfgen import canvas
                from reportlab.lib.pagesizes import mm
                from reportlab.lib import colors
                import random

                tamaño = tamaño_combo.get()
                if "58mm x 40mm" in tamaño:
                    page_width, page_height = 58 * mm, 40 * mm
                elif "58mm x 60mm" in tamaño:
                    page_width, page_height = 58 * mm, 60 * mm
                else:
                    page_width, page_height = 80 * mm, 40 * mm

                c = canvas.Canvas(filename, pagesize=(page_width, page_height))
                for _ in range(cantidad):
                    c.setPageSize((page_width, page_height))
                    margin = 2 * mm
                    w, h = page_width - 2 * margin, page_height - 2 * margin

                    c.setFillColor(colors.white)
                    c.rect(0, 0, page_width, page_height, fill=1)

                    c.setFont("Helvetica-Bold", 10)
                    c.setFillColor(colors.black)
                    c.drawCentredString(page_width/2, h - 5*mm, articulo[:25])

                    random.seed(hash(codigo))
                    bar_y = 10 * mm
                    bar_height = 8 * mm
                    bar_left = 10 * mm
                    bar_width_total = page_width - 20 * mm
                    bar_width = 0.8 * mm
                    current_x = bar_left
                    for _ in range(len(codigo) * 4):
                        if random.choice([True, False]):
                            c.rect(current_x, bar_y, bar_width, bar_height, fill=1, stroke=0)
                        current_x += bar_width
                        if current_x > bar_left + bar_width_total:
                            break

                    c.setFont("Helvetica", 8)
                    c.drawCentredString(page_width/2, bar_y - 3*mm, codigo)

                    c.setFont("Helvetica-Bold", 14)
                    c.drawCentredString(page_width/2, 3*mm, f"${precio:.2f} USD")

                    c.showPage()

                c.save()
                messagebox.showinfo("✅ Éxito", f"PDF generado correctamente en:\n{filename}")
                import os
                if os.name == 'nt':
                    os.startfile(filename)
                else:
                    os.system(f'xdg-open "{filename}"')
                top.destroy()
            except Exception as e:
                messagebox.showerror("❌ Error", f"Error al generar PDF: {e}")

        btn_frame = tk.Frame(main_container, bg=estilos.COLORS['white'])
        btn_frame.pack(fill='x', pady=10)

        btn_imprimir = ctk.CTkButton(btn_frame, text='🖨️ Imprimir Etiqueta', 
                                     font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
                                     command=enviar_a_impresora, width=170, height=45,
                                     fg_color=estilos.COLORS['success'])
        btn_imprimir.pack(side='left', padx=10, expand=True, fill='x')

        btn_pdf = ctk.CTkButton(btn_frame, text='📄 Generar PDF', 
                                font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
                                command=generar_pdf_etiqueta, width=170, height=45,
                                fg_color=estilos.COLORS['info'])
        btn_pdf.pack(side='left', padx=10, expand=True, fill='x')

        btn_cancelar = ctk.CTkButton(btn_frame, text='❌ Cancelar', 
                                     font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
                                     command=top.destroy, width=170, height=45,
                                     fg_color=estilos.COLORS['danger'])
        btn_cancelar.pack(side='right', padx=10, expand=True, fill='x')

    def cargar_articulos(self, filtro=None):
        self.after(0, self._cargar_articulos, filtro)
    
    def _cargar_articulos(self, filtro=None):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        conn = get_connection()
        if not conn:
            error_label = tk.Label(self.scrollable_frame, text="❌ Error de conexión a la base de datos", font=('Segoe UI', 12, 'bold'), fg='red', bg=estilos.COLORS['white'])
            error_label.pack(pady=20)
            return
        cursor = conn.cursor()
        try:
            # NUEVO: se agrega categoria al SELECT y se combina el filtro de texto con el de categoría
            query = "SELECT codigo, articulo, precio, image_path, categoria FROM articulos WHERE estado = 'activo'"
            params = []
            if filtro:
                query += " AND articulo LIKE %s"
                params.append(f'%{filtro}%')
            categoria_filtro = self.obtener_categoria_filtro_actual()
            if categoria_filtro:
                query += " AND categoria = %s"
                params.append(categoria_filtro)
            query += " ORDER BY articulo"
            cursor.execute(query, params)
            articulos = cursor.fetchall()
            self.row = 0
            self.column = 0
            for codigo, articulo, precio, image_path, categoria in articulos:
                self.mostrar_articulo(codigo, articulo, precio, image_path, categoria)
        except Exception as e:
            print(f"Error cargando artículos: {e}")
            error_label = tk.Label(self.scrollable_frame, text=f"❌ Error cargando productos: {e}", font=('Segoe UI', 12, 'bold'), fg='red', bg=estilos.COLORS['white'])
            error_label.pack(pady=20)
        finally:
            cursor.close()
            conn.close()
    
    def mostrar_articulo(self, codigo, articulo, precio, image_path, categoria=None):
        article_frame = tk.Frame(self.scrollable_frame, bg='white', relief='solid', bd=1, width=250, height=300)
        article_frame.grid(row=self.row, column=self.column, padx=15, pady=15, sticky="nsew")
        article_frame.grid_propagate(False)
        
        if image_path and os.path.exists(image_path):
            try:
                image = Image.open(image_path)
                image = image.resize((200, 200), Image.Resampling.LANCZOS)
                imagen = ImageTk.PhotoImage(image)
                image_label = tk.Label(article_frame, image=imagen, bg='white', cursor='hand2')
                image_label.image = imagen
                image_label.pack(pady=8)
                image_label.bind("<Button-1>", lambda e: self.seleccionar_producto(articulo))
            except Exception:
                placeholder = tk.Label(article_frame, text="📷", font=('Segoe UI', 60), bg='white', cursor='hand2')
                placeholder.pack(pady=40)
                placeholder.bind("<Button-1>", lambda e: self.seleccionar_producto(articulo))
        else:
            placeholder = tk.Label(article_frame, text="📷", font=('Segoe UI', 60), bg='white', cursor='hand2')
            placeholder.pack(pady=40)
            placeholder.bind("<Button-1>", lambda e: self.seleccionar_producto(articulo))
        
        name_label = tk.Label(article_frame, text=articulo, bg='white', anchor='w', wraplength=240, font=('Segoe UI', 11, 'bold'))
        name_label.pack(side="top", fill='x', padx=8)
        
        precio_formateado = f"${precio:.2f} USD"
        precio_label = tk.Label(article_frame, text=f'💰 {precio_formateado}', bg='white', anchor='w', font=('Segoe UI', 10, 'bold'), fg=estilos.COLORS['success'])
        precio_label.pack(side="top", fill='x', padx=8)

        # NUEVO: badge de categoría
        if categoria:
            categoria_label = tk.Label(article_frame, text=f'🗂️ {categoria}', bg='white', anchor='w', 
                                      font=('Segoe UI', 9), fg=estilos.COLORS['primary'])
            categoria_label.pack(side="top", fill='x', padx=8)
        
        codigo_label = tk.Label(article_frame, text=f'🏷️ {codigo}', bg='white', anchor='w', font=('Segoe UI', 9), fg=estilos.COLORS['secondary'])
        codigo_label.pack(side="bottom", fill='x', padx=8, pady=3)
        
        self.column += 1
        if self.column > 3:
            self.column = 0
            self.row += 1
    
    def seleccionar_producto(self, articulo):
        self.comboboxbuscar.set(articulo)
        self.actualizar_label()
    
    def on_combobox_select(self, event):
        self.actualizar_label()
        
    def actualizar_label(self, event=None):
        articulo_seleccionado = self.comboboxbuscar.get()
        if not articulo_seleccionado:
            return
        conn = get_connection()
        if not conn:
            return
        cursor = conn.cursor()
        try:
            cursor.execute("""SELECT codigo, articulo, precio, costo, stock, estado, categoria 
                              FROM articulos WHERE articulo = %s""", (articulo_seleccionado,))
            resultado = cursor.fetchone()
            if resultado:
                codigo, articulo, precio, costo, stock, estado, categoria = resultado
                self.label1.config(text=f'📦 Artículo: {articulo}')
                self.label2.config(text=f'💰 Precio: ${precio:.2f} USD')
                self.label3.config(text=f'🏷️ Código: {codigo}')
                self.label4.config(text=f'📊 Stock: {stock} unidades')
                if estado.lower() == "activo":
                    self.label5.config(text=f'✅ Estado: {estado}', fg=estilos.COLORS['success'])
                else:
                    self.label5.config(text=f'❌ Estado: {estado}', fg=estilos.COLORS['danger'])
                # NUEVO: mostrar categoría
                self.label6.config(text=f'🗂️ Categoría: {categoria or "Sin categoría"}')
            else:
                self.label1.config(text="📦 Artículo: No encontrado")
                self.label2.config(text="💰 Precio: --")
                self.label3.config(text="🏷️ Código: --")
                self.label4.config(text="📊 Stock: --")
                self.label5.config(text="❌ Estado: --")
                self.label6.config(text="🗂️ Categoría: --")
        except Exception as e:
            print("Error al obtener datos del artículo:", e)
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