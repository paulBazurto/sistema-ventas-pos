import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
from modulos.utils.estilos_modernos import estilos
from data.models import get_connection
from PIL import Image, ImageTk
from datetime import datetime
import webbrowser

# Configurar CustomTkinter
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class InformacionModerna(tk.Frame):
    
    def __init__(self, padre):
        super().__init__(padre, bg=estilos.COLORS['bg_primary'])
        self.widgets()
    
    def actualizar_moneda(self, nueva_moneda):
        """Actualizar estadísticas cuando cambia la moneda"""
        try:
            # Recargar estadísticas con nueva moneda si existen
            if hasattr(self, 'cargar_estadisticas'):
                self.cargar_estadisticas()
            print(f"Módulo Información actualizado a moneda: {nueva_moneda}")
        except Exception as e:
            print(f"Error al actualizar moneda en Información: {e}")
        
    def widgets(self):
        # Título principal
        title_frame = tk.Frame(self, bg=estilos.COLORS['bg_primary'])
        title_frame.place(x=0, y=20, width=1400, height=100)
        
        title_label = tk.Label(title_frame, text="📊 Centro de Información", 
                              font=('Segoe UI', 24, 'bold'), 
                              bg=estilos.COLORS['bg_primary'],
                              fg=estilos.COLORS['primary'])
        title_label.place(x=50, y=20)
        
        subtitle_label = tk.Label(title_frame, text="Reportes, estadísticas y información del sistema", 
                                 font=('Segoe UI', 12), 
                                 bg=estilos.COLORS['bg_primary'],
                                 fg=estilos.COLORS['gray'])
        subtitle_label.place(x=50, y=60)

        # Frame principal para las cards
        main_frame = tk.Frame(self, bg=estilos.COLORS['bg_primary'])
        main_frame.place(x=50, y=150, width=1300, height=600)

        # Card 1: Reportes de Ventas
        self.crear_card_reporte(main_frame, x=50, y=50)
        
        # Card 2: Estadísticas del Sistema
        self.crear_card_estadisticas(main_frame, x=450, y=50)
        
        # Card 3: Información del Sistema
        self.crear_card_info_sistema(main_frame, x=850, y=50)
        
        # Card 4: Resumen de Inventario
        self.crear_card_inventario(main_frame, x=50, y=350)
        
        # Card 5: Actividad Reciente
        self.crear_card_actividad(main_frame, x=450, y=350)
        
        # Card 6: Configuración
        self.crear_card_configuracion(main_frame, x=850, y=350)

    # ---------- Cards (sin cambios) ----------
    def crear_card_reporte(self, parent, x, y):
        card = tk.LabelFrame(parent, text="📈 Reportes de Ventas", 
                            font=('Segoe UI', 14, 'bold'), 
                            bg=estilos.COLORS['white'],
                            fg=estilos.COLORS['primary'],
                            relief='solid', bd=1)
        card.place(x=x, y=y, width=350, height=250)
        
        icon_label = tk.Label(card, text="📊", font=('Segoe UI', 56), 
                             bg=estilos.COLORS['white'],
                             fg=estilos.COLORS['success'])
        icon_label.place(x=145, y=15)
        
        desc_label = tk.Label(card, text="Generar reportes detallados\nde ventas y transacciones", 
                             font=('Segoe UI', 11), 
                             bg=estilos.COLORS['white'],
                             fg=estilos.COLORS['dark'],
                             justify='center')
        desc_label.place(x=75, y=120)
        
        btn_reporte = ctk.CTkButton(
            card, 
            text="📊 Generar Reporte", 
            command=self.generar_reporte,
            width=300,
            height=40,
            corner_radius=10,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color=estilos.COLORS['success'],
            hover_color="#28a745"
        )
        btn_reporte.place(x=25, y=180)

    def crear_card_estadisticas(self, parent, x, y):
        card = tk.LabelFrame(parent, text="📊 Estadísticas del Sistema", 
                            font=('Segoe UI', 14, 'bold'), 
                            bg=estilos.COLORS['white'],
                            fg=estilos.COLORS['primary'],
                            relief='solid', bd=1)
        card.place(x=x, y=y, width=350, height=250)
        
        icon_label = tk.Label(card, text="📈", font=('Segoe UI', 56), 
                             bg=estilos.COLORS['white'],
                             fg=estilos.COLORS['info'])
        icon_label.place(x=145, y=15)
        
        self.stats_frame = tk.Frame(card, bg=estilos.COLORS['white'])
        self.stats_frame.place(x=25, y=120, width=300, height=70)
        
        self.cargar_estadisticas()
        
        btn_stats = ctk.CTkButton(
            card, 
            text="🔄 Actualizar Stats", 
            command=self.actualizar_estadisticas,
            width=300,
            height=40,
            corner_radius=10,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color=estilos.COLORS['info'],
            hover_color="#0ea5e9"
        )
        btn_stats.place(x=25, y=180)

    def crear_card_info_sistema(self, parent, x, y):
        card = tk.LabelFrame(parent, text="ℹ️ Información del Sistema", 
                            font=('Segoe UI', 14, 'bold'), 
                            bg=estilos.COLORS['white'],
                            fg=estilos.COLORS['primary'],
                            relief='solid', bd=1)
        card.place(x=x, y=y, width=350, height=250)
        
        icon_label = tk.Label(card, text="💻", font=('Segoe UI', 56), 
                             bg=estilos.COLORS['white'],
                             fg=estilos.COLORS['accent'])
        icon_label.place(x=145, y=15)
        
        info_text = f"""Sistema de Punto de Venta
Versión: 2.0 Moderna
Fecha: {datetime.now().strftime('%Y-%m-%d')}"""
        
        info_label = tk.Label(card, text=info_text, 
                             font=('Segoe UI', 10), 
                             bg=estilos.COLORS['white'],
                             fg=estilos.COLORS['dark'],
                             justify='center')
        info_label.place(x=75, y=120)
        
        btn_info = ctk.CTkButton(
            card, 
            text="ℹ️ Más Información", 
            command=self.mostrar_info_detallada,
            width=300,
            height=40,
            corner_radius=10,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color=estilos.COLORS['accent'],
            hover_color="#7c3aed"
        )
        btn_info.place(x=25, y=180)

    def crear_card_inventario(self, parent, x, y):
        card = tk.LabelFrame(parent, text="📦 Resumen de Inventario", 
                            font=('Segoe UI', 14, 'bold'), 
                            bg=estilos.COLORS['white'],
                            fg=estilos.COLORS['primary'],
                            relief='solid', bd=1)
        card.place(x=x, y=y, width=350, height=250)
        
        icon_label = tk.Label(card, text="📦", font=('Segoe UI', 56), 
                             bg=estilos.COLORS['white'],
                             fg=estilos.COLORS['warning'])
        icon_label.place(x=145, y=15)
        
        self.inventario_frame = tk.Frame(card, bg=estilos.COLORS['white'])
        self.inventario_frame.place(x=25, y=120, width=300, height=70)
        
        self.cargar_resumen_inventario()
        
        btn_inventario = ctk.CTkButton(
            card, 
            text="📦 Ver Inventario", 
            command=self.ver_inventario_detallado,
            width=300,
            height=40,
            corner_radius=10,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color=estilos.COLORS['warning'],
            hover_color="#ffc107"
        )
        btn_inventario.place(x=25, y=180)

    def crear_card_actividad(self, parent, x, y):
        card = tk.LabelFrame(parent, text="🕒 Actividad Reciente", 
                            font=('Segoe UI', 14, 'bold'), 
                            bg=estilos.COLORS['white'],
                            fg=estilos.COLORS['primary'],
                            relief='solid', bd=1)
        card.place(x=x, y=y, width=350, height=250)
        
        icon_label = tk.Label(card, text="📋", font=('Segoe UI', 56), 
                             bg=estilos.COLORS['white'],
                             fg=estilos.COLORS['secondary'])
        icon_label.place(x=145, y=15)
        
        self.actividad_frame = tk.Frame(card, bg=estilos.COLORS['white'])
        self.actividad_frame.place(x=25, y=120, width=300, height=70)
        
        self.cargar_actividad_reciente()
        
        btn_actividad = ctk.CTkButton(
            card, 
            text="📋 Ver Historial", 
            command=self.ver_historial_completo,
            width=300,
            height=40,
            corner_radius=10,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color=estilos.COLORS['secondary'],
            hover_color="#059669"
        )
        btn_actividad.place(x=25, y=180)

    def crear_card_configuracion(self, parent, x, y):
        card = tk.LabelFrame(parent, text="⚙️ Configuración", 
                            font=('Segoe UI', 14, 'bold'), 
                            bg=estilos.COLORS['white'],
                            fg=estilos.COLORS['primary'],
                            relief='solid', bd=1)
        card.place(x=x, y=y, width=350, height=250)
        
        icon_label = tk.Label(card, text="⚙️", font=('Segoe UI', 56), 
                             bg=estilos.COLORS['white'],
                             fg=estilos.COLORS['gray'])
        icon_label.place(x=145, y=15)
        
        desc_label = tk.Label(card, text="Configurar parámetros\ndel sistema y preferencias", 
                             font=('Segoe UI', 11), 
                             bg=estilos.COLORS['white'],
                             fg=estilos.COLORS['dark'],
                             justify='center')
        desc_label.place(x=75, y=120)
        
        btn_config = ctk.CTkButton(
            card, 
            text="⚙️ Configuración", 
            command=self.abrir_configuracion,
            width=300,
            height=40,
            corner_radius=10,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color=estilos.COLORS['gray'],
            hover_color="#475569"
        )
        btn_config.place(x=25, y=180)

    # ---------- Métodos con acceso a base de datos (MODIFICADOS) ----------
    def cargar_estadisticas(self):
        """Cargar estadísticas del sistema (versión MySQL)"""
        conn = get_connection()
        if not conn:
            # Mostrar mensaje de error en el frame
            error_label = tk.Label(self.stats_frame, text="❌ Error de conexión", 
                                  font=('Segoe UI', 10), 
                                  bg=estilos.COLORS['white'],
                                  fg=estilos.COLORS['danger'])
            error_label.place(x=0, y=0)
            return

        cursor = conn.cursor()
        try:
            # Contar artículos (tabla 'articulos')
            cursor.execute("SELECT COUNT(*) FROM articulos")
            total_productos = cursor.fetchone()[0]

            # Contar clientes
            cursor.execute("SELECT COUNT(*) FROM clientes")
            total_clientes = cursor.fetchone()[0]

            # Contar pedidos a proveedores
            cursor.execute("SELECT COUNT(*) FROM pedidos_proveedor")
            total_pedidos = cursor.fetchone()[0]

            # Mostrar estadísticas
            stats_text = f"📦 Artículos: {total_productos}\n👥 Clientes: {total_clientes}\n📋 Pedidos: {total_pedidos}"
            stats_label = tk.Label(self.stats_frame, text=stats_text, 
                                  font=('Segoe UI', 10, 'bold'), 
                                  bg=estilos.COLORS['white'],
                                  fg=estilos.COLORS['dark'],
                                  justify='left')
            stats_label.place(x=0, y=0)

        except Exception as e:
            error_label = tk.Label(self.stats_frame, text=f"Error: {e}", 
                                  font=('Segoe UI', 10), 
                                  bg=estilos.COLORS['white'],
                                  fg=estilos.COLORS['danger'])
            error_label.place(x=0, y=0)
        finally:
            cursor.close()
            conn.close()

    def cargar_resumen_inventario(self):
        """Cargar resumen del inventario (versión MySQL)"""
        conn = get_connection()
        if not conn:
            error_label = tk.Label(self.inventario_frame, text="❌ Error de conexión", 
                                  font=('Segoe UI', 10), 
                                  bg=estilos.COLORS['white'],
                                  fg=estilos.COLORS['danger'])
            error_label.place(x=0, y=0)
            return

        cursor = conn.cursor()
        try:
            # Stock total
            cursor.execute("SELECT SUM(stock) FROM articulos")
            stock_total = cursor.fetchone()[0] or 0

            # Artículos con stock bajo (menos de 10)
            cursor.execute("SELECT COUNT(*) FROM articulos WHERE stock < 10")
            stock_bajo = cursor.fetchone()[0]

            # Mostrar resumen
            resumen_text = f"📊 Stock Total: {stock_total}\n⚠️ Stock Bajo: {stock_bajo} artículos"
            resumen_label = tk.Label(self.inventario_frame, text=resumen_text, 
                                    font=('Segoe UI', 10, 'bold'), 
                                    bg=estilos.COLORS['white'],
                                    fg=estilos.COLORS['dark'],
                                    justify='left')
            resumen_label.place(x=0, y=0)

        except Exception as e:
            error_label = tk.Label(self.inventario_frame, text=f"Error: {e}", 
                                  font=('Segoe UI', 10), 
                                  bg=estilos.COLORS['white'],
                                  fg=estilos.COLORS['danger'])
            error_label.place(x=0, y=0)
        finally:
            cursor.close()
            conn.close()

    def cargar_actividad_reciente(self):
        """Cargar actividad reciente (sin BD)"""
        actividad_text = f"🕒 Última actualización:\n{datetime.now().strftime('%Y-%m-%d %H:%M')}\n✅ Sistema operativo"
        actividad_label = tk.Label(self.actividad_frame, text=actividad_text, 
                                  font=('Segoe UI', 10), 
                                  bg=estilos.COLORS['white'],
                                  fg=estilos.COLORS['dark'],
                                  justify='left')
        actividad_label.place(x=0, y=0)

    # ---------- Funciones de los botones (sin cambios) ----------
    def generar_reporte(self):
        try:
            from modulos.reportes.generador_reportes import GeneradorReportes
            generador = GeneradorReportes(self)
            generador.abrir_ventana_reportes()
        except ImportError as e:
            messagebox.showerror("❌ Error", f"Error al cargar módulo de reportes: {e}")
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al abrir reportes: {e}")

    def actualizar_estadisticas(self):
        for widget in self.stats_frame.winfo_children():
            widget.destroy()
        self.cargar_estadisticas()
        messagebox.showinfo("🔄 Actualizado", "Estadísticas actualizadas correctamente")

    def mostrar_info_detallada(self):
        info_detallada = f"""
🖥️ Sistema de Punto de Venta Moderno

📋 Información Técnica:
• Versión: 2.0 Moderna
• Tecnología: Python + Tkinter + CustomTkinter
• Base de datos: MySQL
• Interfaz: Material Design

✨ Características:
• Gestión de inventario
• Registro de clientes
• Pedidos a proveedores
• Interfaz moderna y responsive
• Actualización automática de stock

👨‍💻 Desarrollado con estilos modernos
📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}
        """
        messagebox.showinfo("ℹ️ Información del Sistema", info_detallada)

    def ver_inventario_detallado(self):
        messagebox.showinfo("📦 Inventario", "Para ver el inventario detallado,\nnavega a la sección 'Inventario' en el menú principal.")

    def ver_historial_completo(self):
        try:
            from modulos.historial.gestor_historial import GestorHistorial
            gestor = GestorHistorial(self)
            gestor.abrir_ventana_historial()
        except ImportError as e:
            messagebox.showerror("❌ Error", f"Error al cargar módulo de historial: {e}")
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al abrir historial: {e}")

    def abrir_configuracion(self):
        try:
            from modulos.configuracion.gestor_configuracion import GestorConfiguracion
            gestor = GestorConfiguracion(self)
            gestor.abrir_ventana_configuracion()
        except ImportError as e:
            messagebox.showerror("❌ Error", f"Error al cargar módulo de configuración: {e}")
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al abrir configuración: {e}")