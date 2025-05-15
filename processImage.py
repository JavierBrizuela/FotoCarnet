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

def detect_face(img):
    
    # Convertir a RGB para MediaPipe
    img_rgb = cv.cvtColor(img, cv.COLOR_BGR2RGB)
    # Cargar clasificador de rostros
    mp_face_detection = mp.solutions.face_detection
    face_detection = mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5)
    face = face_detection.process(img_rgb)
    
    if face.detections:
        # Extraer coordenadas de la cara detectada
        detection = face.detections[0]
        bboxC = detection.location_data.relative_bounding_box
        x = int(bboxC.xmin * img.shape[1])
        y = int(bboxC.ymin * img.shape[0])
        w = int(bboxC.width * img.shape[1])
        h = int(bboxC.height * img.shape[0])
        print(f"Rostro detectado: {x}, {y}, {w}, {h}")
        return x, y, w, h
    else:
        print("No se detectó ningún rostro")
        return None

def show_face(img, x, y, w, h):
    # Dibujar un rectángulo alrededor de la cara detectada
    cv.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
    return img

def image_crop(img , width, height, percent, x, y, w, h):
        
    # Correjir la región de la cara
    margin = 0.5
    y = y - int(h * margin)
    h = h + int(h * margin)
    
    # Definir constantes para recortar imagen
    aspect_ratio = width / height
    height_orig = int((h * 100) / percent)
    width_orig = int(height_orig * aspect_ratio)
    side_margin = int((width_orig - w) * 0.5)
    height_diff = height_orig - h
    x = x - side_margin
    y = y - int(height_diff * 0.2)
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

def rem_bg(file):
    session = new_session("birefnet-general")

    # Leer imagen
    img = cv.imdecode(np.frombuffer(file.read(), np.uint8), cv.IMREAD_COLOR)
    # Obtener mascara de segmentación
    mask = remove(
                    img, 
                    only_mask=True, 
                    session=session,
                    alpha_matting=True,
                    alpha_matting_foreground_threshold=240,
                    alpha_matting_background_threshold=10,
                    alpha_matting_erode_size=10,
                  )
    mask = np.array(mask).astype(np.float32) / 255.0  # Normalizar a 0-1
    mask = mask[:, :, np.newaxis]  # Convertir a 3 canales
    return mask, img

def remove_background(file , blur_amount=15):
    """
    Crea una mascara para el posterior recorte o fusion.
    
    Args:
        file: archivo de la imagen
        blur_amount: Cantidad de desenfoque aplicado a la máscara (debe ser impar)
    Returns:
        mask: mascara de segmentación
        image: Imagen original
    """
     # Leer imagen
    img = cv.imdecode(np.frombuffer(file.read(), np.uint8), cv.IMREAD_COLOR)
    
    # Inicializar MediaPipe Selfie Segmentation
    selfie_segmentation = mp.solutions.selfie_segmentation
    selfie_segmentation = selfie_segmentation.SelfieSegmentation(model_selection=0)
    result = selfie_segmentation.process(img)
    # Obtener mascara de segmentación
    mask = result.segmentation_mask
    # Aplicar suavizado adaptativo a la máscara para mejorar los bordes
    blurred = cv.GaussianBlur(mask, (blur_amount, blur_amount), 0)
    mask = blurred[:, :, np.newaxis]  # Convertir a 3 canales
    # Liberar recursos
    selfie_segmentation.close()
    return mask, img

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