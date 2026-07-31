import tkinter as tk
from tkinter import messagebox, simpledialog
import customtkinter as ctk
import hashlib
from modulos.utils.estilos_modernos import estilos
from modulos.utils.utils import resource_path
from PIL import Image, ImageTk
from data.models import get_connection
import cv2
import math
import numpy as np
import face_recognition as fr
import pickle
import os
from tkinter import Toplevel, Label
import mediapipe as mp

# ================= CONFIGURACIÓN DE MEDIAPIPE =================
mp_drawing = mp.solutions.drawing_utils
FacemeshObject = mp.solutions.face_mesh
FaceObject = mp.solutions.face_detection
FaceMesh = FacemeshObject.FaceMesh(max_num_faces=1)
detector = FaceObject.FaceDetection(min_detection_confidence=0.5, model_selection=1)
ConfigDraw = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)

# Variables globales (ya no usamos conteo_parpadeos ni step en login)
parpadeo = False
conteo = 0
step = 0          # Se mantiene pero ya no se usa en login
conteo_parpadeos = 0
current_username = None
cap = None
lblVideo = None
ventana_camara = None
autenticado = False
intentos_fallidos = 0
MAX_INTENTOS = 30

# ================= CARGAR IMÁGENES DE LA CARPETA SetUp =================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SETUP_DIR = os.path.join(BASE_DIR, 'SetUp')

def load_image(name):
    path = os.path.join(SETUP_DIR, name)
    img = cv2.imread(path)
    if img is None:
        print(f"⚠️ No se encontró {path}")
    return img

img_check = load_image('check.png')
img_step0 = load_image('Step0.png')
img_step1 = load_image('Step1.png')
img_step2 = load_image('Step2.png')

# ================= FUNCIONES DE BASE DE DATOS =================
def verificar_login(usuario, password):
    conn = get_connection()
    if not conn:
        return False
    cursor = conn.cursor()
    try:
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        cursor.execute("SELECT username, password FROM usuarios WHERE username = %s", (usuario,))
        user_data = cursor.fetchone()
        if user_data and (user_data[1] == password_hash or user_data[1] == password):
            return True
        return False
    except Exception as e:
        print(f"Error en verificación de login: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def obtener_encodings_faciales():
    conn = get_connection()
    if not conn:
        return [], []
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT u.username, r.encoding
            FROM rostros r
            JOIN usuarios u ON u.id = r.usuario_id
        """)
        encodings = []
        usernames = []
        for username, encoding_bytes in cursor.fetchall():
            encodings.append(pickle.loads(encoding_bytes))
            usernames.append(username)
        return encodings, usernames
    except Exception as e:
        print(f"Error cargando encodings: {e}")
        return [], []
    finally:
        cursor.close()
        conn.close()

def crear_usuario_y_rostro(username, password, frame_bgr, bbox=None):
    from modulos.biometrico.face_auth import FaceAuthenticator

    if frame_bgr is not None and isinstance(frame_bgr, np.ndarray):
        if frame_bgr.dtype != np.uint8:
            try:
                if frame_bgr.dtype in [np.float32, np.float64]:
                    if frame_bgr.max() <= 1.0:
                        frame_bgr = (frame_bgr * 255).astype(np.uint8)
                    else:
                        frame_bgr = frame_bgr.astype(np.uint8)
                else:
                    frame_bgr = frame_bgr.astype(np.uint8)
            except:
                pass
        if len(frame_bgr.shape) == 2:
            frame_bgr = cv2.cvtColor(frame_bgr, cv2.COLOR_GRAY2BGR)
        elif len(frame_bgr.shape) == 3 and frame_bgr.shape[2] == 4:
            frame_bgr = cv2.cvtColor(frame_bgr, cv2.COLOR_BGRA2BGR)
        if not frame_bgr.flags['C_CONTIGUOUS']:
            frame_bgr = np.ascontiguousarray(frame_bgr)

    conn = get_connection()
    if not conn:
        return False, "Error de conexión a la base de datos"
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM usuarios WHERE username = %s", (username,))
        if cursor.fetchone():
            return False, "El nombre de usuario ya existe"

        password_hash = hashlib.sha256(password.encode()).hexdigest()
        cursor.execute("INSERT INTO usuarios (username, password) VALUES (%s, %s)",
                       (username, password_hash))
        usuario_id = cursor.lastrowid
        conn.commit()

        auth = FaceAuthenticator()
        if bbox is not None:
            exito, mensaje = auth.registrar_rostro_con_bbox(usuario_id, frame_bgr, bbox)
        else:
            exito, mensaje = auth.registrar_rostro(usuario_id, frame_bgr)
        if not exito:
            cursor.execute("DELETE FROM usuarios WHERE id = %s", (usuario_id,))
            conn.commit()
            return False, f"Error al registrar rostro: {mensaje}"

        return True, f"Usuario '{username}' creado y rostro registrado correctamente"
    except Exception as e:
        conn.rollback()
        return False, f"Error: {e}"
    finally:
        cursor.close()
        conn.close()

# ================= LOGIN CON ROSTRO (SIN PARPADEOS) =================
def login_con_rostro(root, ventana_principal, callback_exito):
    global cap, lblVideo, ventana_camara, autenticado, current_username, intentos_fallidos

    autenticado = False
    current_username = None
    intentos_fallidos = 0

    FaceCode, clases = obtener_encodings_faciales()
    if not FaceCode:
        messagebox.showwarning("⚠️ Sin registros", "No hay usuarios registrados con rostro.\nRegistre un rostro usando el botón 'Registrar'.")
        return

    ventana_camara = Toplevel(root)
    ventana_camara.title("🔐 Login Facial - Mire a la cámara")
    ventana_camara.geometry("1280x720")
    ventana_camara.configure(bg='black')
    ventana_camara.grab_set()
    ventana_camara.focus_set()

    lblVideo = Label(ventana_camara, bg='black')
    lblVideo.pack(expand=True, fill='both')

    lbl_estado = ctk.CTkLabel(ventana_camara, text="🔍 Buscando rostro...", 
                              font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
                              text_color="white", bg_color="black")
    lbl_estado.place(x=500, y=680)

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(3, 1280)
    cap.set(4, 720)
    if not cap.isOpened():
        messagebox.showerror("Error", "No se pudo abrir la cámara")
        ventana_camara.destroy()
        return

    def cerrar_camara():
        if cap is not None:
            cap.release()
        ventana_camara.destroy()

    def bucle_login():
        global cap, lblVideo, autenticado, current_username, intentos_fallidos

        if autenticado:
            return

        ret, frame = cap.read()
        if not ret:
            lblVideo.after(30, bucle_login)
            return

        frame_copy = frame.copy()
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Dibujar malla facial (solo visual, no afecta liveness)
        res = FaceMesh.process(frame_rgb)
        if res.multi_face_landmarks:
            for rostros in res.multi_face_landmarks:
                mp_drawing.draw_landmarks(frame, rostros, FacemeshObject.FACEMESH_TESSELATION, ConfigDraw, ConfigDraw)

        # ---- RECONOCIMIENTO FACIAL DIRECTO (sin parpadeos) ----
        frame_fr = cv2.resize(frame_copy, (0,0), None, 0.25, 0.25)
        rgb_fr = cv2.cvtColor(frame_fr, cv2.COLOR_BGR2RGB)
        faces_locs = fr.face_locations(rgb_fr)
        faces_encs = fr.face_encodings(rgb_fr, faces_locs)

        if not faces_encs:
            lbl_estado.configure(text="😐 No se detecta rostro, acércate")
        else:
            for face_enc in faces_encs:
                if not FaceCode:
                    break
                distances = fr.face_distance(FaceCode, face_enc)
                if len(distances) > 0:
                    min_dist = np.min(distances)
                    print(f"🔍 Distancia mínima: {min_dist:.4f}")
                    if min_dist < 0.45:
                        best_idx = np.argmin(distances)
                        current_username = clases[best_idx]
                        autenticado = True
                        cap.release()
                        ventana_camara.destroy()
                        messagebox.showinfo("✅ Bienvenido", f"¡Bienvenido {current_username}!")
                        callback_exito()
                        return
                    else:
                        lbl_estado.configure(text="❌ Rostro no reconocido")
                        intentos_fallidos += 1
                        if intentos_fallidos >= MAX_INTENTOS:
                            cap.release()
                            ventana_camara.destroy()
                            messagebox.showerror("❌ Autenticación fallida", 
                                                "No se pudo reconocer el rostro.\n"
                                                "Asegúrese de estar registrado y de que la cámara enfoca correctamente.")
                            return

        # Mostrar el frame procesado
        frame = cv2.resize(frame, (1280, 720))
        im = Image.fromarray(frame)
        img_tk = ImageTk.PhotoImage(im)
        lblVideo.configure(image=img_tk)
        lblVideo.image = img_tk
        lblVideo.after(10, bucle_login)

    btn_cancelar = ctk.CTkButton(ventana_camara, text="❌ Cancelar", command=cerrar_camara,
                                 font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                                 width=100, height=30, fg_color="red")
    btn_cancelar.place(x=10, y=10)

    ventana_camara.protocol("WM_DELETE_WINDOW", cerrar_camara)
    bucle_login()

# ================= REGISTRO DE NUEVO USUARIO CON ROSTRO =================
def registrar_usuario_con_rostro(root):
    root.withdraw()

    reg_window = Toplevel(root)
    reg_window.title("📝 Registrar Nuevo Usuario")
    reg_window.geometry("400x350")
    reg_window.configure(bg=estilos.COLORS['white'])
    reg_window.grab_set()
    reg_window.focus_set()

    def on_reg_window_close():
        root.deiconify()
        reg_window.destroy()
    reg_window.protocol("WM_DELETE_WINDOW", on_reg_window_close)

    tk.Label(reg_window, text="Nuevo Usuario", font=('Segoe UI', 16, 'bold'),
             bg=estilos.COLORS['white'], fg=estilos.COLORS['primary']).pack(pady=15)

    frame = tk.Frame(reg_window, bg=estilos.COLORS['white'])
    frame.pack(pady=10, padx=20, fill='x')

    tk.Label(frame, text="Usuario:", font=('Segoe UI', 12, 'bold'),
             bg=estilos.COLORS['white']).grid(row=0, column=0, sticky='w', pady=5)
    entry_user = ctk.CTkEntry(frame, font=('Segoe UI', 12), width=200)
    entry_user.grid(row=0, column=1, pady=5)

    tk.Label(frame, text="Contraseña:", font=('Segoe UI', 12, 'bold'),
             bg=estilos.COLORS['white']).grid(row=1, column=0, sticky='w', pady=5)
    entry_pass = ctk.CTkEntry(frame, font=('Segoe UI', 12), width=200, show="*")
    entry_pass.grid(row=1, column=1, pady=5)

    def iniciar_captura():
        username = entry_user.get().strip()
        password = entry_pass.get().strip()
        if not username or not password:
            messagebox.showerror("❌ Error", "Usuario y contraseña son requeridos")
            return
        if len(password) < 6:
            messagebox.showerror("❌ Error", "La contraseña debe tener al menos 6 caracteres")
            return
        reg_window.destroy()
        capturar_rostro_para_registro(root, username, password)

    btn_capturar = ctk.CTkButton(reg_window, text="📸 Capturar Rostro y Registrar",
                                 command=iniciar_captura,
                                 width=250, height=45,
                                 font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                                 fg_color=estilos.COLORS['success'])
    btn_capturar.pack(pady=15)

    btn_cancelar = ctk.CTkButton(reg_window, text="❌ Cancelar",
                                 command=on_reg_window_close,
                                 width=250, height=40,
                                 font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                                 fg_color=estilos.COLORS['danger'])
    btn_cancelar.pack(pady=5)

def capturar_rostro_para_registro(root, username, password):
    global cap, lblVideo, ventana_camara, step, conteo, parpadeo

    step = 0
    conteo = 0
    parpadeo = False

    ventana_camara = Toplevel(root)
    ventana_camara.title(f"📸 Registro Facial - {username}")
    ventana_camara.geometry("1280x720")
    ventana_camara.configure(bg='black')
    ventana_camara.grab_set()
    ventana_camara.focus_set()

    lblVideo = Label(ventana_camara, bg='black')
    lblVideo.pack(expand=True, fill='both')

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(3, 1280)
    cap.set(4, 720)
    if not cap.isOpened():
        messagebox.showerror("Error", "No se pudo abrir la cámara")
        root.deiconify()
        ventana_camara.destroy()
        return

    def cerrar_camara():
        if cap is not None:
            cap.release()
        ventana_camara.destroy()
        root.deiconify()

    def bucle_registro():
        global cap, lblVideo, step, conteo, parpadeo
        ret, frame = cap.read()
        if not ret:
            lblVideo.after(30, bucle_registro)
            return

        frame_save = frame.copy()
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        res = FaceMesh.process(frame_rgb)
        if res.multi_face_landmarks:
            for rostros in res.multi_face_landmarks:
                mp_drawing.draw_landmarks(frame, rostros, FacemeshObject.FACEMESH_TESSELATION, ConfigDraw, ConfigDraw)

                lista = []
                for id, puntos in enumerate(rostros.landmark):
                    al, an, _ = frame.shape
                    x, y = int(puntos.x * an), int(puntos.y * al)
                    lista.append([id, x, y])

                if len(lista) == 468:
                    x1, y1 = lista[145][1], lista[145][2]
                    x2, y2 = lista[159][1], lista[159][2]
                    longitud1 = math.hypot(x2 - x1, y2 - y1)

                    x3, y3 = lista[374][1], lista[374][2]
                    x4, y4 = lista[386][1], lista[386][2]
                    longitud2 = math.hypot(x4 - x3, y4 - y3)

                    x5, y5 = lista[139][1], lista[139][2]
                    x6, y6 = lista[368][1], lista[368][2]
                    x7, y7 = lista[70][1], lista[70][2]
                    x8, y8 = lista[300][1], lista[300][2]

                    faces = detector.process(frame_rgb)
                    if faces.detections is not None:
                        for face in faces.detections:
                            score = face.score[0]
                            bbox = face.location_data.relative_bounding_box
                            if score > 0.5:
                                alimg, animg, _ = frame.shape
                                xi = int(bbox.xmin * animg)
                                yi = int(bbox.ymin * alimg)
                                an = int(bbox.width * animg)
                                al = int(bbox.height * alimg)

                                offsetan = (20 / 100) * an
                                xi = int(xi - offsetan/2)
                                an = int(an + offsetan)
                                offsetal = (30 / 100) * al
                                yi = int(yi - offsetal)
                                al = int(al + offsetal)

                                if xi < 0: xi = 0
                                if yi < 0: yi = 0

                                if step == 0:
                                    cv2.rectangle(frame, (xi, yi, an, al), (255, 0, 255), 2)
                                    if img_step0 is not None:
                                        h, w, _ = img_step0.shape
                                        frame[50:50+h, 50:50+w] = img_step0
                                    if img_step1 is not None:
                                        h, w, _ = img_step1.shape
                                        frame[50:50+h, 1030:1030+w] = img_step1
                                    if img_step2 is not None:
                                        h, w, _ = img_step2.shape
                                        frame[270:270+h, 1030:1030+w] = img_step2

                                    if x7 > x5 and x8 < x6:
                                        if longitud1 <= 10 and longitud2 <= 10 and not parpadeo:
                                            conteo += 1
                                            parpadeo = True
                                        elif longitud1 > 10 and longitud2 > 10 and parpadeo:
                                            parpadeo = False

                                        if img_check is not None:
                                            h, w, _ = img_check.shape
                                            frame[165:165+h, 1105:1105+w] = img_check
                                        cv2.putText(frame, f'Parpadeos: {int(conteo)}', (1070, 375),
                                                    cv2.FONT_HERSHEY_COMPLEX, 0.5, (255,255,255), 1)

                                        if conteo >= 3:
                                            if img_check is not None:
                                                h, w, _ = img_check.shape
                                                frame[385:385+h, 1105:1105+w] = img_check
                                            if longitud1 > 14 and longitud2 > 14:
                                                bbox = (yi, yi + al, xi, xi + an)
                                                exito, mensaje = crear_usuario_y_rostro(username, password, frame_save, bbox)
                                                cap.release()
                                                ventana_camara.destroy()
                                                root.deiconify()
                                                if exito:
                                                    messagebox.showinfo("✅ Éxito", mensaje)
                                                else:
                                                    messagebox.showerror("❌ Error", mensaje)
                                                return
                                    else:
                                        conteo = 0

        frame = cv2.resize(frame, (1280, 720))
        im = Image.fromarray(frame)
        img_tk = ImageTk.PhotoImage(im)
        lblVideo.configure(image=img_tk)
        lblVideo.image = img_tk
        lblVideo.after(10, bucle_registro)

    btn_cancelar = ctk.CTkButton(ventana_camara, text="❌ Cancelar", command=cerrar_camara,
                                 font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                                 width=100, height=30, fg_color="red")
    btn_cancelar.place(x=10, y=10)

    ventana_camara.protocol("WM_DELETE_WINDOW", cerrar_camara)
    bucle_registro()

# ================= VENTANA PRINCIPAL DE LOGIN =================
def mostrar_login_simple():
    print("🔄 [mostrar_login_simple] Iniciando...")
    global root
    root = ctk.CTk()
    print("✅ Ventana creada")
    root.title("🔐 Sistema de Punto de Venta - Login")
    root.geometry("500x800+400+50")
    root.configure(fg_color=estilos.COLORS['bg_primary'])
    root.resizable(False, False)

    try:
        icon_path = resource_path("media/icons/tienda.png")
        icon_image = tk.PhotoImage(file=icon_path)
        root.iconphoto(True, icon_image)
        root._icon_image_ref = icon_image
        print("✅ Icono cargado")
    except Exception as e:
        print(f"⚠️ Error cargando icono: {e}")

    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (500 // 2)
    y = (root.winfo_screenheight() // 2) - (700 // 2)
    root.geometry(f"500x700+{x}+{y}")

    usuario_autenticado = None
    print("✅ Variables inicializadas")

    def autenticar_facial_exitoso():
        nonlocal usuario_autenticado
        print("🔐 [autenticar_facial_exitoso] Llamado")
        usuario_autenticado = current_username
        print(f"👤 Usuario autenticado facialmente: {usuario_autenticado}")
        root.destroy()

    def intentar_login():
        nonlocal usuario_autenticado
        usuario = usuario_entry.get().strip()
        password = password_entry.get().strip()
        if not usuario or not password:
            messagebox.showerror("❌ Error", "Por favor ingrese usuario y contraseña")
            return
        if verificar_login(usuario, password):
            usuario_autenticado = usuario
            messagebox.showinfo("✅ Bienvenido", f"¡Bienvenido {usuario}!")
            root.destroy()
        else:
            messagebox.showerror("❌ Error", "Usuario o contraseña incorrectos.")
            password_entry.delete(0, 'end')
            usuario_entry.focus()

    main_frame = ctk.CTkFrame(root, fg_color=estilos.COLORS['white'], corner_radius=20)
    main_frame.pack(fill='both', expand=True, padx=30, pady=30)

    try:
        _logo_img = ctk.CTkImage(light_image=Image.open(resource_path("media/icons/tienda.png")), size=(96, 96))
        logo_label = ctk.CTkLabel(main_frame, text="", image=_logo_img)
        logo_label.pack(pady=(40, 20))
        root._logo_img_ref = _logo_img
        print("✅ Logo cargado")
    except Exception as e:
        print(f"⚠️ Error cargando logo: {e}")
        logo_label = ctk.CTkLabel(main_frame, text="🏪", font=ctk.CTkFont(size=80))
        logo_label.pack(pady=(40, 20))

    title_label = ctk.CTkLabel(main_frame, text="Sistema de Punto de Venta", font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"), text_color=estilos.COLORS['primary'])
    title_label.pack(pady=(0, 10))

    form_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    form_frame.pack(fill='x', padx=40, pady=20)

    user_label = ctk.CTkLabel(form_frame, text="👤 Usuario:", font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"), text_color=estilos.COLORS['dark'])
    user_label.pack(anchor='w', pady=(0, 5))
    usuario_entry = ctk.CTkEntry(form_frame, placeholder_text="Ingrese su usuario", font=ctk.CTkFont(family="Segoe UI", size=12), height=45, corner_radius=10)
    usuario_entry.pack(fill='x', pady=(0, 20))

    password_label = ctk.CTkLabel(form_frame, text="🔒 Contraseña:", font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"), text_color=estilos.COLORS['dark'])
    password_label.pack(anchor='w', pady=(0, 5))
    password_entry = ctk.CTkEntry(form_frame, placeholder_text="Ingrese su contraseña", font=ctk.CTkFont(family="Segoe UI", size=12), height=45, corner_radius=10, show="*")
    password_entry.pack(fill='x', pady=(0, 30))

    login_button = ctk.CTkButton(form_frame, text="🔐 Iniciar Sesión", command=intentar_login, font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"), height=50, corner_radius=15, fg_color=estilos.COLORS['primary'], hover_color=estilos.COLORS['primary_dark'])
    login_button.pack(fill='x', pady=(0, 10))

    btn_facial = ctk.CTkButton(form_frame, text="😀 Login Facial", command=lambda: login_con_rostro(root, root, autenticar_facial_exitoso),
                               font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
                               height=50, corner_radius=15,
                               fg_color=estilos.COLORS['success'],
                               hover_color="#16a34a")
    btn_facial.pack(fill='x', pady=(0, 10))

    btn_registrar = ctk.CTkButton(form_frame, text="📝 Registrar", command=lambda: registrar_usuario_con_rostro(root),
                                  font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
                                  height=50, corner_radius=15,
                                  fg_color=estilos.COLORS['warning'],
                                  hover_color="#d97706")
    btn_registrar.pack(fill='x', pady=(0, 20))

    info_frame = ctk.CTkFrame(main_frame, fg_color=estilos.COLORS['light'], corner_radius=10)
    info_frame.pack(fill='x', padx=40, pady=10)

    footer_label = ctk.CTkLabel(main_frame, text="© 2024 Sistema POS Moderno", font=ctk.CTkFont(family="Segoe UI", size=10), text_color=estilos.COLORS['gray'])
    footer_label.pack(side='bottom', pady=20)

    root.bind('<Return>', lambda event: intentar_login())
    usuario_entry.focus()
    print("🔄 [mostrar_login_simple] Entrando a mainloop...")
    root.mainloop()
    print(f"🔄 [mostrar_login_simple] Salió de mainloop. usuario_autenticado={usuario_autenticado}")
    return usuario_autenticado

if __name__ == "__main__":
    usuario = mostrar_login_simple()
    if usuario:
        print(f"Login exitoso como: {usuario}")
    else:
        print("Login cancelado")