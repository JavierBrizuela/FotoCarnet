from flask import jsonify
import cv2 as cv
import numpy as np
import base64
import mediapipe as mp
from rembg import remove, new_session

def hex_to_bgr(hex_color):
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 3:  # Formato corto (#FFF → #FFFFFF)
        hex_color = ''.join([c * 2 for c in hex_color])
    return tuple(int(hex_color[i:i+2], 16) for i in (4, 2, 0))

def read_image(file):
    # Leer imagen
    img = cv.imdecode(np.frombuffer(file.read(), np.uint8), cv.IMREAD_COLOR)
    return img

def detect_head(img, debug=False):
    # Configurar Face Mesh
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(
        static_image_mode=True,
        max_num_faces=1,
        refine_landmarks=False,
        min_detection_confidence=0.5
    )
    
    # Convertir a RGB
    img_rgb = cv.cvtColor(img, cv.COLOR_BGR2RGB)
    results = face_mesh.process(img_rgb)
    
    if not results.multi_face_landmarks:
        print("No se detectó ningún rostro")
        return None
    
    # Obtener todos los landmarks
    landmarks = results.multi_face_landmarks[0].landmark
    
    x_coords = [l.x for l in landmarks]
    y_coords = [l.y for l in landmarks]
    
    # Convertir a píxeles
    h, w = img.shape[:2]
    # Encontrar límites del rostro
    min_x, max_x = int(w * min(x_coords)), int(w * max(x_coords))
    min_y, max_y = int(h * min(y_coords)),int(h * max(y_coords))
    
    width = max_x - min_x
    height = max_y - min_y 
    # Mejorar detección de altura (coordenada Y) mediante análisis de contenido
    # Recorrer la imagen de arriba a abajo para encontrar el primer punto con información
    new_min_y = find_top_content(img, min_x, max_x)
    if new_min_y < min_y and new_min_y is not None:
        diff = min_y - new_min_y
        min_y = new_min_y
        height = diff + height
    print(f"imagen: {img.shape}")
    print(f"Rostro detectado: {min_x}, {min_y}, {width}, {height}")
    if debug:
        img = show_face(img, min_x, min_y, width, height)
    return min_x, min_y, width, height


def show_face(img, x, y, w, h):
    # Dibujar un rectángulo alrededor de la cara detectada
    cv.rectangle(img, (x, y), (x + w, y + h ), (0, 255, 0), 5)
    return img

def image_crop(img , width, height, percent, x, y, w, h):
    
    # Definir constantes para recortar imagen
    aspect_ratio = width / height
    height_orig = int((h * 100) / percent)
    width_orig = int(height_orig * aspect_ratio)
    side_margin = int((width_orig - w) * 0.5)
    height_diff = height_orig - h
    x = x - side_margin
    y = y - int(height_diff * 0.1)
    w =  (side_margin * 2) + w 
    h =  height_diff + h
    
    # Si la región a recortar está fuera de los límites de la imagen, agregar padding
    if x < 0 or y < 0 or w > img.shape[1] or h > img.shape[0]:
        print("Recortando imagen con padding")
        img_croped = image_padding(img, x, y, w, h)
    else:
        img_croped = img[y:y + h, x:x + w]
    return img_croped

def image_padding(img, x, y, w, h):
    # Asegurarse de que no se salga de los límites de la imagen
    x1 = max(0, x)
    y1 = max(0, y)
    x2 = min(img.shape[1], x + w)
    y2 = min(img.shape[0], y + h)    
    
    img_crop = img[y1:y2, x1:x2]
    # Agregar padding a la imagen
    pad_left = max(0, x1 - x)
    pad_right = max(0, (x + w) - x2)
    pad_top = max(0, y1 - y)
    pad_bottom = max(0, (h + y) - y2)
    img_padded = cv.copyMakeBorder(img_crop, 
                                   pad_top, pad_bottom, pad_left, pad_right, 
                                   cv.BORDER_CONSTANT, 
                                   value=[0, 0, 0])
    
    # Crear máscara (áreas negras = originales, áreas blancas = a rellenar)
    mask = np.zeros(img_padded.shape[:2], dtype=np.uint8)

    # Marcar las áreas de padding como blancas (255)
    if pad_top > 0:
        mask[:pad_top, :] = 255
    if pad_bottom > 0:
        mask[-pad_bottom:, :] = 255
    if pad_left > 0:
        mask[:, :pad_left] = 255
    if pad_right > 0:
        mask[:, -pad_right:] = 255
    
    # Aplicar inpainting (método rápido: cv2.INPAINT_TELEA)
    inpainted_face = cv.inpaint(
        img_padded, 
        mask, 
        inpaintRadius=3,  # Radio de influencia para el relleno
        flags=cv.INPAINT_TELEA
    )
    return inpainted_face

def rem_bg(img, bg_color):
    # "u2net_human_seg" 5seg resultado: regular
    # "u2net_cloth_seg" problema en mask.shape
    # "silueta"  2seg resultado: pelo excelente problema en la ropa
    # "isnet-general-use"  3seg resultado: pelo muy bueno problemas en la ropa pero mejor que silueta
    # "sam" 3seg resultado malo
    # "isnet-anime" 3seg resultado: pelo regular bien en ropa pero le baja el contraste a la imagen
    # "birefnet-portrait" 34seg resultado: excelente
    # "birefnet-general" 44seg resultado: muy bueno
    # "birefnet-general-lite" 17seg resultado: muy bueno
    session = new_session("birefnet-general-lite")
    bg_color = bg_color + (255,)  # Convertir a formato BGRA
    # Obtener mascara de segmentación
    img = remove(
                    img, 
                    session=session,
                    bgcolor=bg_color,
                    alpha_matting=True,
                    alpha_matting_foreground_threshold=240,  # Valor alto para preservar detalles finos
                    alpha_matting_background_threshold=10,   # Valor bajo para preservar detalles finos
                    alpha_matting_erode_size=5               # Valor moderado (balance entre calidad y velocidad)
                )
    return img

def fusion_image_background(img, mask, bg_color):
    
    # Crear fondo con el color de fondo
    bg_image = np.ones(img.shape, dtype=np.uint8)
    bg_image[:] = bg_color  # Color en BGR
    
    # crear fusion entre la imagen original y el fondo
    output_image = img * mask + bg_image * (1 - mask)
    output_image = output_image.astype(np.uint8)
    return output_image

def image_resizer(img, width, height, dpi):
    # Verificar que file sea una imagen válida
    if not isinstance(img, np.ndarray):
        print("Error: La imagen de entrada no es válida")
        return None
    # Calcular dimensiones en píxeles
    dpc = int(dpi / 2.54)
    width_px = int(width * dpc)
    height_px = int(height * dpc)
    
    # Redimensionar imagen
    image_resized = cv.resize(img, (width_px, height_px))
    return image_resized

def find_top_content(img, min_x, max_x):
    """
    Recorre la imagen de arriba hacia abajo para encontrar el primer punto donde hay contenido
    diferente al fondo homogéneo.
    """
    h, w = img.shape[:2]
    
    # Convertir a escala de grises para simplificar la detección
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        
    # Determinar el ancho de la zona a analizar
    roi_width = max_x - min_x
    
    # Umbral para determinar si hay diferencia significativa
    threshold = 20
    
    # Muestra de fondo: tomar el punto más alto de la imagen
    background_sample = np.median(gray[0:10, min_x:max_x])
    
    # Recorrer de arriba a abajo
    for y in range(0, h):
        # Obtener una franja horizontal y calcular su diferencia con el fondo
        row_slice = gray[y, min_x:max_x]
        diff = np.abs(row_slice - background_sample)
        
        # Si hay suficientes píxeles diferentes al fondo, considerar como contenido
        if np.mean(diff) > threshold or np.max(diff) > threshold * 2:
            return max(0, y )  # Retornar con un pequeño margen
    
    return None  # No se encontró un punto con contenido diferente

def image_code(file):
    # Verificar que file sea una imagen válida
    if file is None or not isinstance(file, np.ndarray) or file.size == 0:
        print("Error: La imagen de entrada para codificar es inválida o está vacía")
        return None
    
    try:
        # Codificar imagen resultante
        _, buffer = cv.imencode('.jpg', file)
        encoded_image = base64.b64encode(buffer).decode('utf-8')
        return encoded_image
    except Exception as e:
        print(f"Error al codificar la imagen: {str(e)}")
        import traceback
        traceback.print_exc()
        return None
    