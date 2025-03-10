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
    margin = 0.2
    # Calcular coordenadas de la región de cara
    x = x - int(w * margin)
    y = y - int(h * margin)
    w = w + int(w * margin * 2)
    h = h + int(h * margin * 2)
    # Recortar imagen
    aspect_ratio = width / height
    height_orig = int((h * 100) / percent)
    width_orig = int(height_orig * aspect_ratio)
    print('altura de la cabeza' + str(h))
    print('altura original' + str(height_orig))
    upper_margin = int((height_orig - h) * 0.3)
    lower_margin = int((height_orig - h) * 0.7)
    left_margin = int((width_orig - w) * 0.5)
    right_margin = int((width_orig - w) * 0.5)
    print('margen superior' + str(upper_margin))
    print('margen inferior' + str(lower_margin))
    processed_img = img[y-upper_margin:y+h+lower_margin, x-left_margin:x+w+right_margin]
    
    return processed_img

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