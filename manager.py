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
        self.usuario_actual = usuario_actual
        self._cerrar_sesion = False  # Cambiamos a _cerrar_sesion para evitar conflicto con método
        
        self.title("🏪 Mi Tienda - Sistema de Ventas Moderno")
        self.geometry("1500x900+200+50")
        self.resizable(True, True)
        self.minsize(1200, 800)
        
        self.configure(bg=estilos.COLORS['bg_primary'])
        
        try:
            icon_path = resource_path("media/icons/mi_tienda.ico")
            self.iconbitmap(icon_path)
        except:
            pass

        container = Frame(self, bg=estilos.COLORS['bg_primary'])
        container.pack(side=TOP, fill=BOTH, expand=True)
        container.configure(width=1400, height=900)
        
        self.container_frame = Container(container, self, usuario_actual=self.usuario_actual)
        self.container_frame.pack(fill=BOTH, expand=True)
        
        from modulos.ventas.ventas_moderna import VentasModerna as Ventas
        self.container_frame.show_frames(Ventas)
        
        self.configurar_estilos_modernos()

    def configurar_estilos_modernos(self):
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

    def cerrar_sesion(self):
        """Cierra la sesión actual y destruye la ventana principal."""
        print("🔴 [Manager] Cerrando sesión...")
        self._cerrar_sesion = True
        self.destroy()      # Cierra la ventana
        self.quit()         # Sale del mainloop para que el bucle while pueda continuar


def main():
    crear_base_de_datos()
    
    while True:
        usuario = mostrar_login_simple()
        if usuario:
            app = Manager(usuario_actual=usuario)
            app.mainloop()
            # Después de que se cierre la ventana, revisamos si fue por cierre de sesión
            if app._cerrar_sesion:
                print("🔄 [Manager] Cerrando sesión, reiniciando login...")
                continue
            else:
                print("🔄 [Manager] Cerrando aplicación (ventana cerrada con X).")
                break
        else:
            print("🔄 [Manager] Login cancelado o fallido.")
            break
    
    print("🔄 [Manager] Aplicación finalizada.")
    sys.exit(0)


if __name__ == "__main__":
    main()