from tkinter import *
from tkinter import ttk
from data.models import crear_base_de_datos
from PIL import Image, ImageTk

from login_simple import mostrar_login_simple
from container import Container
from modulos.utils.utils import resource_path
from modulos.utils.estilos_modernos import estilos

import sys
import os


class Manager(Tk):
    def __init__(self, usuario_actual=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.usuario_actual = usuario_actual  # Guardar usuario autenticado
        
        self.title("🏪 Mi Tienda - Sistema de Ventas Moderno")
        self.geometry("1400x900+200+50")
        self.resizable(True, True)
        self.minsize(1200, 800)
        
        self.configure(bg=estilos.COLORS['bg_primary'])
        
        # Icono de la aplicación
        try:
            icon_path = resource_path("media/icons/mi_tienda.ico")
            self.iconbitmap(icon_path)
        except:
            pass

        # Container principal
        container = Frame(self, bg=estilos.COLORS['bg_primary'])
        container.pack(side=TOP, fill=BOTH, expand=True)
        container.configure(width=1400, height=900)
        
        # Pasar el usuario al container
        self.container_frame = Container(container, self, usuario_actual=self.usuario_actual)
        self.container_frame.pack(fill=BOTH, expand=True)
        
        # Iniciar en la sección de ventas
        from modulos.ventas.ventas_moderna import VentasModerna as Ventas
        self.container_frame.show_frames(Ventas)
        
        # Configurar estilos modernos
        self.configurar_estilos_modernos()

    def configurar_estilos_modernos(self):
        """Configurar todos los estilos modernos de la aplicación"""
        try:
            from ttkthemes import ThemedStyle
            self.style = ThemedStyle(self)
            self.style.set_theme("arc")
        except ImportError:
            self.style = ttk.Style()
            self.style.theme_use("clam")
        
        self.style.configure('Modern.TLabel',
                           background=estilos.COLORS['bg_primary'],
                           foreground=estilos.COLORS['primary'],
                           font=estilos.FONTS['primary'] + ' ' + str(estilos.FONTS['sizes']['base']))
        
        self.style.configure('Title.TLabel',
                           background=estilos.COLORS['bg_primary'],
                           foreground=estilos.COLORS['primary'],
                           font=estilos.FONTS['primary'] + ' ' + str(estilos.FONTS['sizes']['2xl']) + ' bold')
        
        self.style.configure('Modern.TButton',
                           font=estilos.FONTS['primary'] + ' ' + str(estilos.FONTS['sizes']['base']) + ' bold',
                           padding=(15, 8))
        
        self.style.configure('Modern.TEntry',
                           font=estilos.FONTS['primary'] + ' ' + str(estilos.FONTS['sizes']['base']),
                           fieldbackground=estilos.COLORS['white'],
                           borderwidth=1,
                           relief='solid')
        
        self.style.configure('Modern.TCombobox',
                           font=estilos.FONTS['primary'] + ' ' + str(estilos.FONTS['sizes']['base']),
                           fieldbackground=estilos.COLORS['white'],
                           borderwidth=1,
                           relief='solid')
        
        self.style.configure('Modern.Treeview',
                           font=estilos.FONTS['primary'] + ' ' + str(estilos.FONTS['sizes']['base']),
                           background=estilos.COLORS['white'],
                           foreground=estilos.COLORS['dark'],
                           fieldbackground=estilos.COLORS['white'])
        
        self.style.configure('Modern.Treeview.Heading',
                           font=estilos.FONTS['primary'] + ' ' + str(estilos.FONTS['sizes']['base']) + ' bold',
                           background=estilos.COLORS['primary'],
                           foreground=estilos.COLORS['white'])


def main():
    # Crear la base de datos antes del login
    crear_base_de_datos()
    
    # Mostrar login y obtener usuario autenticado
    usuario = mostrar_login_simple()
    
    if usuario:
        # Si el login fue exitoso, abrir la aplicación principal
        app = Manager(usuario_actual=usuario)
        app.mainloop()
    else:
        # Si se canceló o falló el login, salir
        print("Login cancelado. Cerrando aplicación...")
        sys.exit()


if __name__ == "__main__":
    main()