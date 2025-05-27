import cv2 as cv
import numpy as np
from PIL import Image
import io
import base64
#from cog import BasePredictor, Input, Path
# Importar tus modules locales
from face_detect import FaceDetect
from image_enhancer import ImageEnhancer
from utils import Utils
from crop_image import CropImage
from remove_bg import RemoveBg

enhancer = ImageEnhancer()
utils = Utils()
face_detect = FaceDetect()
crop_image = CropImage()
remove_bg = RemoveBg()

# Cargar la imagen
img = cv.imread(str("G:/apedido/carnet/entrenamiento/DSCN0002.jpg"))
if img is None:
    raise ValueError("Image not found or cannot be read.")
print(f"Image shape: {img.shape}")

# Detectar y obtener dimensiones de la cara
face_x, face_y, face_w, face_h = face_detect.find_hair_top_boundary(img)
print(f"Face coordinates: x={face_x}, y={face_y}, w={face_w}, h={face_h}")

# Recortar la imagen con las dimensiones de la cara
croped_img = crop_image.crop(
    image=img,
    face_x=face_x,
    face_y=face_y,
    face_w=face_w,
    face_h=face_h,
    width=4.0,  # Ancho en cm
    height=4.0,  # Alto en cm
    dpi=300,  # DPI para salida
    face_percentage=50  # Porcentaje de cara en la imagen
)
# Extraer el fondo y colocarle un color sólido
extracted_img = remove_bg.rem_bg(
    croped_img, 
    bg_color=utils.hex_to_bgr("#FFFFFF")  # Convertir color hexadecimal a BGR
)
# output = self.model(processed_image, scale)

# return postprocess(output)
# Mejorar brillo, contraste y saturación
enhancer_img = enhancer.enhance_image(
    extracted_img, 
)
output_path = utils.encode_image_to_file(enhancer_img)
#return Path(output_path)
