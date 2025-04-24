import cv2 as cv
import numpy as np
import base64
import mediapipe as mp

def image_crop(img , width, height, percent):
    # Convertir imagen rgb a gris
    img_grey = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    # Cargar clasificador de rostros
    face_cascade = cv.CascadeClassifier('Data/haarcascade_frontalface_default.xml')
    face = face_cascade.detectMultiScale(img_grey, 1.1, 4)
    
    if len(face) != 1:
        
        return None
    x, y, w, h = face[0]
    # Correjir la región de la cara
    margin = 0.2
    y = y - int(h * margin)
    h = h + int(h * margin * 2)
    # Definir constantes para recortar imagen
    aspect_ratio = width / height
    height_orig = int((h * 100) / percent)
    width_orig = int(height_orig * aspect_ratio)
    side_margin = int((width_orig - w) * 0.5)
    height_diff = height_orig - h
    x = x - side_margin
    y = y - int(height_diff * 0.3)
    w =  (side_margin * 2) + w 
    h =  height_diff + h
    # Si la región a recortar está fuera de los límites de la imagen, agregar padding
    if x < 0 or y < 0 or w > img.shape[1] or h > img.shape[0]:
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

def remove_background(file , bg_color=[255, 255, 255], blur_amount=15):
    """
    Remueve el fondo de una imagen con una persona y lo reemplaza con el color especificado.
    
    Args:
        img: Imagen en formato OpenCV (BGR)
        bg_color: Color de fondo deseado en formato BGR [B, G, R]
        blur_amount: Cantidad de desenfoque aplicado a la máscara (debe ser impar)
    Returns:
        Imagen con el fondo reemplazado
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
    blurred = blurred[:, :, np.newaxis]  # Convertir a 3 canales
    # Crear fondo con el color de fondo
    bg_image = np.ones(img.shape, dtype=np.uint8)
    bg_image[:] = bg_color  # Color en BGR
    # crear fusion entre la imagen original y el fondo
    output_image = img * blurred + bg_image * (1 - blurred)
    output_image = output_image.astype(np.uint8)
    
    # Liberar recursos
    selfie_segmentation.close()
    
    return output_image

def image_resizer(file, width, height, dpi):
    
    dpc = int(dpi / 2.54)
    width_px = int(width * dpc)
    height_px = int(height * dpc)
    
    # Redimensionar imagen
    image_resized = cv.resize(file, (width_px, height_px))
    return image_resized

def image_code(file):
    
    # Codificar imagen resultante
    _, buffer = cv.imencode('.jpg', file)
    encoded_image = base64.b64encode(buffer).decode('utf-8')
    return encoded_image