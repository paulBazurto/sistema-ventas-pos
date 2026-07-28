from tkinter import *
import tkinter as tk
import customtkinter as ctk
from modulos.ventas.ventas_moderna import VentasModerna as Ventas
from modulos.inventario.inventario_simple import InventarioSimple as Inventario
from modulos.clientes_moderno import ClientesModerno as Clientes
from modulos.pedidos_moderno import PedidosModerno as Pedidos
from modulos.proveedores.proveedor_moderno import ProveedorModerno as Proveedor
from modulos.informacion.informacion_moderna import InformacionModerna as Informacion
from modulos.perfil.perfil_moderno import PerfilModerno as Perfil  # <-- NUEVA IMPORT
from modulos.utils.estilos_modernos import estilos
from PIL import Image, ImageTk
import sys
import os

# Configurar CustomTkinter
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class Container(tk.Frame):
    def __init__(self, padre, controlador, usuario_actual=None):
        super().__init__(padre)
        self.controlador = controlador
        self.usuario_actual = usuario_actual  # Guardamos el usuario logueado
        
        # Configurar el frame principal
        self.configure(bg=estilos.COLORS['bg_primary'])
        self.pack()
        # Antes: self.place(x=0, y=0, width=1400, height=900)
        # Ahora ocupa todo el espacio disponible del contenedor padre, sea cual sea su tamaño
        self.place(x=0, y=0, relwidth=1.0, relheight=1.0)
        
        # Inicializar
        self.frames = {}
        self.buttons = []
        self.active_button = None
        self.button_map = {}
        
        self.widgets_modernos()
        
        # Crear los frames de los módulos (incluyendo Perfil)
        for i in (Ventas, Inventario, Clientes, Pedidos, Proveedor, Informacion, Perfil):
            if i == Perfil:
                # Pasamos el usuario al perfil
                frame = i(self, usuario_actual=self.usuario_actual)
            else:
                frame = i(self)
            self.frames[i] = frame
            frame.pack()
            frame.config(bg=estilos.COLORS['bg_primary'])
            frame.place(x=0, y=70, relwidth=1.0, relheight=1.0, height=-70)
        
        self.show_frames(Ventas)
        
    def show_frames(self, container):
        frame = self.frames[container]
        frame.tkraise()
        self.actualizar_boton_activo(container)
        
    def Ventas(self):
        self.show_frames(Ventas)
        
    def Inventario(self):
        self.show_frames(Inventario)
        
    def Clientes(self):
        self.show_frames(Clientes)
        
    def Pedidos(self):
        self.show_frames(Pedidos)
        
    def Proveedor(self):
        self.show_frames(Proveedor)
    
    def Informacion(self):
        self.show_frames(Informacion)
    
    def Perfil(self):
        self.show_frames(Perfil)
    
    def actualizar_boton_activo(self, container):
        for btn in self.buttons:
            btn.configure(fg_color=estilos.COLORS['primary_light'])
        if container in self.button_map:
            active_btn = self.button_map[container]
            active_btn.configure(fg_color=estilos.COLORS['secondary'])
            self.active_button = active_btn
            
    def widgets_modernos(self):
        navbar_frame = tk.Frame(self, bg=estilos.COLORS['primary'], height=70)
        # Antes: navbar_frame.place(x=0, y=0, width=1400, height=70)
        # Ahora el navbar ocupa el 100% del ancho real de la ventana
        navbar_frame.place(x=0, y=0, relwidth=1.0, height=70)
        
        title_label = tk.Label(navbar_frame, text="🏪 Mi Tienda", 
                              bg=estilos.COLORS['primary'], fg=estilos.COLORS['white'],
                              font=('Segoe UI', 18, 'bold'))
        title_label.place(x=20, y=20)
        
        buttons_frame = tk.Frame(navbar_frame, bg=estilos.COLORS['primary'])
        # Antes: buttons_frame.place(x=460, y=10, width=910, height=50)
        # Ahora se ancla a la derecha del navbar y ocupa un % relativo del ancho, no un valor fijo
        buttons_frame.place(relx=1.0, rely=0.5, relwidth=0.82, height=50, anchor='e')
        
        from modulos.utils.utils import resource_path
        
        # Agregamos el botón de Perfil al final (con un ícono de usuario)
        button_configs = [
            {"text": "💰 Ventas", "command": self.Ventas, "module": Ventas},
            {"text": "📦 Inventario", "command": self.Inventario, "module": Inventario},
            {"text": "👥 Clientes", "command": self.Clientes, "module": Clientes},
            {"text": "📋 Pedidos", "command": self.Pedidos, "module": Pedidos},
            {"text": "🏭 Proveedores", "command": self.Proveedor, "module": Proveedor},
            {"text": "ℹ️ Info", "command": self.Informacion, "module": Informacion},
            {"text": "👤 Perfil", "command": self.Perfil, "module": Perfil}   # <-- NUEVO
        ]
        
        self.buttons = []
        for config in button_configs:
            btn = self.crear_boton_navbar(buttons_frame, config["text"], config["command"])
            self.buttons.append(btn)
            self.button_map[config["module"]] = btn
        
        if Ventas in self.button_map:
            self.actualizar_boton_activo(Ventas)
    
    def crear_boton_navbar(self, parent, text, command):
        btn = ctk.CTkButton(
            parent,
            text=text,
            command=command,
            width=1,  # Antes era 115 (fijo); ahora el ancho real lo reparte el pack(expand=True, fill='x')
            height=40,
            corner_radius=15,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color=estilos.COLORS['primary_light'],
            hover_color=estilos.COLORS['secondary'],
            text_color=estilos.COLORS['white'],
            border_width=0,
            cursor="hand2"
        )
        # Antes: btn.pack(side='left', padx=3, pady=5)
        # Ahora con expand=True y fill='x' los 7 botones se reparten el espacio disponible por igual
        btn.pack(side='left', padx=3, pady=5, expand=True, fill='x')
        return btn