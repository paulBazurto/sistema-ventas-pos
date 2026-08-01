import cv2
import numpy as np
import face_recognition as fr
import pickle
from data.models import get_connection
import mysql.connector

# Umbral de tolerancia muy estricto (login)
TOLERANCIA_FACIAL = 0.4

# Umbral para detectar que un rostro YA existe en la BD al registrar
# (algo más permisivo que el de login para evitar falsos negativos de duplicado)
TOLERANCIA_DUPLICADO = 0.45


class FaceAuthenticator:
    def __init__(self):
        self.encodings = []
        self.usernames = []
        self.user_ids = []
        self.cargar_encodings()

    def cargar_encodings(self):
        # Reiniciar listas para evitar acumular duplicados si se llama más de una vez
        self.encodings = []
        self.usernames = []
        self.user_ids = []

        conn = get_connection()
        if not conn:
            return
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT r.encoding, u.username, u.id
                FROM rostros r
                JOIN usuarios u ON u.id = r.usuario_id
            """)
            for encoding_bytes, username, user_id in cursor.fetchall():
                self.encodings.append(pickle.loads(encoding_bytes))
                self.usernames.append(username)
                self.user_ids.append(user_id)
            print(f"🔐 Cargados {len(self.encodings)} encodings faciales")
        except mysql.connector.Error as e:
            print(f"Error cargando encodings: {e}")
        finally:
            cursor.close()
            conn.close()

    def autenticar(self, frame_bgr, tolerance=None):
        """
        Autentica un rostro comparando con los encodings guardados.
        Retorna (user_id, username) si la distancia mínima es menor que tolerance.
        De lo contrario, retorna (None, None).
        """
        if frame_bgr is None:
            print("⚠️ frame_bgr es None")
            return None, None

        if tolerance is None:
            tolerance = TOLERANCIA_FACIAL

        small_frame = cv2.resize(frame_bgr, (0, 0), fx=0.25, fy=0.25)
        rgb_small = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        face_locations = fr.face_locations(rgb_small)
        face_encodings = fr.face_encodings(rgb_small, face_locations)

        if not face_encodings:
            print("⚠️ No se detectaron rostros en el frame")
            return None, None

        if not self.encodings:
            print("⚠️ No hay encodings en la base de datos")
            return None, None

        for i, face_encoding in enumerate(face_encodings):
            distances = fr.face_distance(self.encodings, face_encoding)
            min_dist = np.min(distances)
            best_idx = np.argmin(distances)
            best_username = self.usernames[best_idx]
            print(f"🔍 Rostro {i+1}: distancia mínima = {min_dist:.4f} (usuario: {best_username})")

            if min_dist < tolerance:
                print(f"✅ AUTENTICADO: {best_username} (distancia {min_dist:.4f} < {tolerance})")
                return self.user_ids[best_idx], self.usernames[best_idx]
            else:
                print(f"❌ Rechazado: distancia {min_dist:.4f} >= {tolerance}")

        print("❌ Ningún rostro superó el umbral de tolerancia")
        return None, None

    def rostro_ya_existe(self, encoding, usuario_id_excluir=None):
        """
        Verifica si un encoding ya corresponde a un rostro guardado en la BD,
        sin importar a qué usuario/username esté asociado.
        Retorna (True, username_existente) si es un duplicado, (False, None) si no.
        """
        if not self.encodings:
            return False, None

        distances = fr.face_distance(self.encodings, encoding)
        min_dist = np.min(distances)
        best_idx = np.argmin(distances)

        print(f"🔎 Verificando duplicado -> distancia mínima: {min_dist:.4f} (usuario existente: {self.usernames[best_idx]})")

        if min_dist < TOLERANCIA_DUPLICADO:
            if usuario_id_excluir is not None and self.user_ids[best_idx] == usuario_id_excluir:
                return False, None
            return True, self.usernames[best_idx]

        return False, None

    def registrar_rostro_con_bbox(self, usuario_id, frame_bgr, bbox):
        """
        Registra un rostro usando una posición (bbox) ya detectada por MediaPipe.
        Ahora valida que el rostro no esté ya registrado con otro usuario
        antes de guardarlo, y usa cursor preparado para evitar el error
        "Invalid utf8mb4 character string".
        """
        print("🔧 [registrar_rostro_con_bbox v5 - con validación de duplicados] ejecutando...")

        if frame_bgr is None:
            return False, "Imagen vacía (frame es None)"

        if not isinstance(frame_bgr, np.ndarray):
            return False, f"Tipo de imagen inválido: {type(frame_bgr)}"

        print(f"    frame_bgr -> shape={frame_bgr.shape}, dtype={frame_bgr.dtype}, "
              f"contiguous={frame_bgr.flags['C_CONTIGUOUS']}")

        # ---- Validar bbox ----
        alto, ancho, _ = frame_bgr.shape
        yi, yf, xi, xf = bbox  # (top, bottom, left, right)

        top = max(0, yi)
        bottom = min(alto, yf)
        left = max(0, xi)
        right = min(ancho, xf)

        print(f"    bbox recibido={bbox} -> recortado top={top} bottom={bottom} left={left} right={right}")

        if bottom <= top or right <= left:
            return False, "El área del rostro (bbox) es inválida"

        # ---- Calcular encoding ----
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)

        encoding = None
        ubicacion = [(top, right, bottom, left)]
        try:
            encodings = fr.face_encodings(frame_rgb, known_face_locations=ubicacion)
            if encodings:
                encoding = encodings[0]
                print("    ✅ Intento 1 (known_face_locations directo) funcionó")
        except Exception as e:
            print(f"    ⚠️ Intento 1 falló: {e}")

        if encoding is None:
            margen_y = int((bottom - top) * 0.3)
            margen_x = int((right - left) * 0.3)
            rec_top = max(0, top - margen_y)
            rec_bottom = min(alto, bottom + margen_y)
            rec_left = max(0, left - margen_x)
            rec_right = min(ancho, right + margen_x)

            if rec_bottom <= rec_top or rec_right <= rec_left:
                return False, "El área del rostro (bbox) es inválida para el recorte de respaldo"

            recorte_rgb = frame_rgb[rec_top:rec_bottom, rec_left:rec_right].copy()
            try:
                ubic_recorte = fr.face_locations(recorte_rgb)
            except Exception as e:
                return False, f"Error al detectar rostro en el recorte: {e}"

            if not ubic_recorte:
                return False, "No se detectó ningún rostro claro (ni con bbox directo ni con recorte)"

            try:
                encodings = fr.face_encodings(recorte_rgb, known_face_locations=ubic_recorte)
            except Exception as e:
                return False, f"Error al codificar rostro en el recorte: {e}"

            if not encodings:
                return False, "No se pudo codificar el rostro (ni con bbox directo ni con recorte)"

            encoding = encodings[0]
            print("    ✅ Intento 2 (recorte + detección) funcionó")

        # ---- VALIDACIÓN DE DUPLICADOS ----
        # Recargar encodings desde la BD para asegurar datos frescos antes de comparar
        self.cargar_encodings()

        ya_existe, username_existente = self.rostro_ya_existe(encoding, usuario_id_excluir=usuario_id)
        if ya_existe:
            print(f"🚫 Rostro duplicado detectado: ya pertenece a '{username_existente}'")
            return False, (f"Este rostro ya está registrado con el usuario '{username_existente}'. "
                            f"No se puede registrar la misma persona con un nombre distinto.")

        # ---- Preparar datos para guardar ----
        encoding_bytes = pickle.dumps(encoding)
        face_img = frame_bgr[top:bottom, left:right]
        ok, img_encoded = cv2.imencode('.png', face_img)
        if not ok:
            return False, "No se pudo codificar la imagen del rostro para guardar"
        img_bytes = img_encoded.tobytes()

        # ---- Guardar en BD con cursor PREPARED ----
        conn = get_connection()
        if not conn:
            return False, "Error de conexión a la base de datos"

        cursor = conn.cursor(prepared=True)
        try:
            cursor.execute("SELECT id FROM rostros WHERE usuario_id = %s", (usuario_id,))
            if cursor.fetchone():
                cursor.execute("DELETE FROM rostros WHERE usuario_id = %s", (usuario_id,))
                conn.commit()

            cursor.execute("""
                INSERT INTO rostros (usuario_id, encoding, imagen)
                VALUES (%s, %s, %s)
            """, (usuario_id, encoding_bytes, img_bytes))
            conn.commit()
            print("✅ Insertado en rostros (cursor preparado)")

            # Actualizar caché local
            self.encodings.append(encoding)
            cursor.execute("SELECT username FROM usuarios WHERE id = %s", (usuario_id,))
            username = cursor.fetchone()[0]
            self.usernames.append(username)
            self.user_ids.append(usuario_id)

            return True, "Rostro registrado correctamente"
        except mysql.connector.Error as e:
            conn.rollback()
            print(f"❌ Error MySQL (prepared): {e}")
            return False, f"Error de base de datos: {e}"
        except Exception as e:
            conn.rollback()
            print(f"❌ Error inesperado: {e}")
            return False, f"Error inesperado: {e}"
        finally:
            cursor.close()
            conn.close()