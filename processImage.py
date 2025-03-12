import cv2 as cv
import numpy as np
import base64

def image_crop(file, width, height, dpi, percent):
    # Leer imagen
    img = cv.imdecode(np.frombuffer(file.read(), np.uint8), cv.IMREAD_COLOR)
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
    # Recortar imagen    
    processed_img = img[y:y+h, x:x+w]
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
    
    return img_padded

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