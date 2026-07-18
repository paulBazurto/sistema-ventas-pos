
from tkinter import *
import tkinter as tk
from tkinter import ttk, messagebox
from container import Container
from PIL import Image, ImageTk
from modulos.utils.utils import resource_path
from data.models import get_connection   # <--- Conexión MySQL
import hashlib   # Para hashear contraseñas

#---------------------------------------------------------------------------------
class Login(tk.Frame):
    
    # Ya no usamos db_name, la conexión la obtenemos de get_connection
    
    def __init__(self, padre, controlador):
        super().__init__(padre)
        self.pack()
        self.place(x = 0, y = 0, width = 1100, height = 650)
        self.controlador = controlador
        self.widgets()
        
    #---------------------------------------------------------------------------------       
    def validacion(self, user, clave):
        return len(user) > 0 and len(clave) > 0
    
    #---------------------------------------------------------------------------------   
    def login(self):
        user = self.username.get().strip()
        pas = self.pass_word.get().strip()
        
        if self.validacion(user, pas):
            # Hashear la contraseña ingresada con SHA2 (256 bits) para comparar con la BD
            password_hash = hashlib.sha256(pas.encode()).hexdigest()
            
            conn = get_connection()
            if not conn:
                messagebox.showerror(title='Error', message='No se pudo conectar a la base de datos')
                return
            cursor = conn.cursor()
            try:
                # Buscar usuario por username y password (hash)
                consulta = "SELECT * FROM usuarios WHERE username = %s AND password = %s"
                cursor.execute(consulta, (user, password_hash))
                result = cursor.fetchone()
                
                if result:
                    self.control1()
                else:
                    self.username.delete(0, 'end')
                    self.pass_word.delete(0, 'end')
                    messagebox.showerror(title='Error', message='Usuario y/o contraseña incorrecta')
            except Exception as e:
                messagebox.showerror(title='Error', message='Error al consultar la base de datos: {}'.format(e))
            finally:
                cursor.close()
                conn.close()
        else:
            messagebox.showerror(title='Error', message='Llene todas las casillas')
            
    #---------------------------------------------------------------------------------     
    def control1(self):
        self.controlador.show_frame(Container)
        
    #---------------------------------------------------------------------------------       
    def widgets(self):
        # Fondo
        fondo = tk.Frame(self, bg='#C6D9E3')
        fondo.pack()
        fondo.place(x = 0, y = 0, width = 1100, height = 650)
        
        self.bg_image = Image.open('media/img/fondo.png')
        self.bg_image = self.bg_image.resize((1200, 800))
        self.bg_image = ImageTk.PhotoImage(self.bg_image)
        self.bg_label = ttk.Label(fondo, image = self.bg_image)
        self.bg_label.place(x = 0, y = 0, width = 1200, height = 800 )
        
        # Cuadro de login
        frame1 = tk.Frame(self, bg ='#77BEF0', highlightbackground ='black', highlightthickness = 2 )
        frame1.place(x = 350, y = 50, width = 400, height = 560 )
           
        self.logo_image = Image.open(resource_path('media/icons/tienda.png'))
        self.logo_image = self.logo_image.resize((200, 200))
        self.logo_image = ImageTk.PhotoImage(self.logo_image)
        self.logo_label = ttk.Label(frame1, image = self.logo_image)
        self.logo_label.place(x = 100, y = 20)
        
        # Input usuario
        user = ttk.Label(frame1, text = "Nombre de usuario :", font = "arial 16 bold", background = "#77BEF0")
        user.place(x = 100, y = 250)
        self.username = ttk.Entry(frame1, font = "arial 16 bold", justify='center')
        self.username.place(x = 80, y = 290, width = 240, height = 40 )
    
        # Input password
        password = ttk.Label(frame1, text = "Contraseña :",font = "arial 16 bold", background = "#77BEF0")
        password.place(x = 100, y = 340)
        self.pass_word = ttk.Entry(frame1, show='*', font = "arial 16 bold",  justify='center')
        self.pass_word.place(x = 80, y = 380, width = 240, height = 40 )
        
        # Botones
        btn1 = tk.Button(frame1, text='Iniciar', font = "arial 16 bold", command=self.login)
        btn1.place(x=100, y=440, width=200, height=40)

        # Botón para registro (redirige a la clase Registro)
        btn2 = tk.Button(frame1, text='Registrar', font = "arial 16 bold", command=self.control2)
        btn2.place(x=100, y=500, width=200, height=40)

    def control2(self):
        # Redirige al frame de Registro
        self.controlador.show_frame(Registro)

#---------------------------------------------------------------------------------           
class Registro(tk.Frame):
    
    # Ya no usamos db_name
    
    def __init__(self, padre, controlador):
        super().__init__(padre)
        self.pack()
        self.place(x = 0, y = 0, width = 1100, height = 650)
        self.controlador = controlador
        self.widgets()
    
    #---------------------------------------------------------------------------------       
    def validacion(self, user, clave):
        return len(user) > 0 and len(clave) > 0
    
    #---------------------------------------------------------------------------------      
    def registro(self):
        user = self.username.get().strip()
        pas = self.pass_word.get().strip()
        key = self.key.get().strip()
        
        if self.validacion(user, pas):
            if len(pas) < 6:
                messagebox.showinfo(title='Error', message='Contraseña demasiado corta (mínimo 6 caracteres)')
                self.username.delete(0, 'end')
                self.pass_word.delete(0, 'end')
                return
            else:
                # Verificar clave de registro (fija "1234")
                if key == '1234':
                    # Hashear la contraseña
                    password_hash = hashlib.sha256(pas.encode()).hexdigest()
                    conn = get_connection()
                    if not conn:
                        messagebox.showerror(title='Error', message='No se pudo conectar a la base de datos')
                        return
                    cursor = conn.cursor()
                    try:
                        # Verificar si el usuario ya existe
                        cursor.execute("SELECT username FROM usuarios WHERE username = %s", (user,))
                        if cursor.fetchone():
                            messagebox.showerror(title='Error', message='El nombre de usuario ya existe')
                            return
                        # Insertar nuevo usuario (id autoincrement, username, password)
                        cursor.execute("INSERT INTO usuarios (username, password) VALUES (%s, %s)", (user, password_hash))
                        conn.commit()
                        messagebox.showinfo(title='Registro', message='Usuario registrado correctamente')
                        self.control1()  # Ir al contenedor principal
                    except Exception as e:
                        messagebox.showerror(title='Error', message='Error al registrar usuario: {}'.format(e))
                    finally:
                        cursor.close()
                        conn.close()
                else:
                    messagebox.showerror(title="Registro", message='Código de registro incorrecto')
        else:
            messagebox.showerror(title='Error', message='Llene todos los campos')
     
    #---------------------------------------------------------------------------------        
    def control1(self):
        self.controlador.show_frame(Container)
        
    #--------------------------------------------------------------------------------- 
    def control2(self):
        self.controlador.show_frame(Login)
        
    #--------------------------------------------------------------------------------- 
    def widgets(self):
        # Fondo
        fondo = tk.Frame(self, bg='#C6D9E3')
        fondo.pack()
        fondo.place(x = 0, y = 0, width = 1100, height = 650)
        
        self.bg_image = Image.open('media/img/fondo.png')
        self.bg_image = self.bg_image.resize((1100, 650))
        self.bg_image = ImageTk.PhotoImage(self.bg_image)
        self.bg_label = ttk.Label(fondo, image = self.bg_image)
        self.bg_label.place(x = 0, y = 0, width = 1100, height = 650 )
        
        # Cuadro de registro
        frame1 = tk.Frame(self, bg = '#ffffff', highlightbackground ='black', highlightthickness = 1 )
        frame1.place(x = 350, y = 10, width = 400, height = 630 )
        
        self.logo_image = Image.open('media/icons/tienda.png')
        self.logo_image = self.logo_image.resize((200, 200))
        self.logo_image = ImageTk.PhotoImage(self.logo_image)
        self.logo_label = ttk.Label(frame1, image = self.logo_image)
        self.logo_label.place(x = 100, y = 20)
        
        # Input usuario
        user = ttk.Label(frame1, text = "Nombre de usuario", font = "arial 16 bold", background = "#ffffff")
        user.place(x = 100, y = 250)
        self.username = ttk.Entry(frame1, font = "arial 16 bold")
        self.username.place(x = 80, y = 290, width = 240, height = 40 )
    
        # Input password
        password = ttk.Label(frame1, text = "Contraseña",font = "arial 16 bold", background = "#ffffff")
        password.place(x = 100, y = 340)
        self.pass_word = ttk.Entry(frame1, show='*', font = "arial 16 bold")
        self.pass_word.place(x = 80, y = 380, width = 240, height = 40 )
        
        # Input código de registro
        key = ttk.Label(frame1, text = "Código de registro",font = "arial 16 bold", background = "#ffffff")
        key.place(x = 100, y = 430)
        self.key = ttk.Entry(frame1, show='*', font = "arial 16 bold")
        self.key.place(x = 80, y = 470, width = 240, height = 40 )
        
        # Botones
        style = ttk.Style()
        style.configure('my.TButton', font=("arial", 18, "bold"))
        
        btn3 = ttk.Button(frame1, text='Registrarse', style='my.TButton', command=self.registro)
        btn3.place(x=80, y=520, width=240, height=40)

        btn4 = ttk.Button(frame1, text='Regresar', style='my.TButton', command=self.control2)
        btn4.place(x=80, y=570, width=240, height=40)