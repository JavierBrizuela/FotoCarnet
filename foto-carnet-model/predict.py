import cv2 as cv
import numpy as np
from PIL import Image
import io
import base64
from cog import BasePredictor, Input, Path

# Importar tus modulos locales
from image_enhancer import ImageEnhancer
from utils import Utils
from face_detect import FaceDetect
from crop_image import CropImage
from remove_bg import RemoveBg

class Predictor(BasePredictor):
    def setup(self) -> None:
        """Load the model into memory to make running multiple predictions efficient"""
        self.enhancer = ImageEnhancer()
        self.utils = Utils()
        self.face_detect = FaceDetect()
        self.crop_image = CropImage()
        self.remove_bg = RemoveBg()
        
    def predict(
        self,
        image: Path = Input(description="selfie input image"),
        width: float = Input(description="Width in cm", default=4),
        height: float = Input(description="Height in cm", default=4),
        dpi: int = Input(description="DPI for output", default=300),
        face_percentage: int = Input(description="Face percentage in image", default=70),
        brightness: float = Input(description="Brightness adjustment", default=1.05),
        contrast: float = Input(description="Contrast adjustment", default=1.05),
        saturation: float = Input(description="Saturation adjustment", default=1.05),
        bg_color: str = Input(description="Background color (hex)", default="#FFFFFF"),
        normalize_histogram_individually: bool = Input(description="Normalize histogram image", default=True),
    ) -> Path:
        """Run a single prediction on the model"""
        # Cargar la imagen
        img = cv.imread(str(image))
        if img is None:
            raise ValueError("Image not found or cannot be read.")
        print(f"Image shape: {img.shape}")
        
        # Detectar y obtener dimensiones de la cara
        face_x, face_y, face_w, face_h = self.face_detect.find_hair_top_boundary(img)
        print(f"Face coordinates: x={face_x}, y={face_y}, w={face_w}, h={face_h}")
        
        # Recortar la imagen con las dimensiones especificadas
        croped_img = self.crop_image.crop(
            image=img,
            face_x=face_x,
            face_y=face_y,
            face_w=face_w,
            face_h=face_h,
            width=width,  # Ancho en cm
            height=height,  # Alto en cm
            face_percentage=face_percentage  # Porcentaje de cara en la imagen
        )
        print(f"Croped image shape: {croped_img.shape}")
        
        # Extraer el fondo y colocarle un color sólido
        extracted_img = self.remove_bg.rem_bg(
            croped_img, 
            bg_color=self.utils.hex_to_bgr(bg_color)
        )
        # Redimencionar imagen a DPI especificado
        dpc = int(dpi / 2.54) # Conversion de DPI a DPC (dots por cm)
        resized_img = cv.resize(extracted_img, (int(width * dpc), int(height * dpc)), interpolation=cv.INTER_AREA)
        
        # Mejorar brillo, contraste y saturación
        enhancer_img = self.enhancer.enhance_image(
            resized_img, 
            brightness=brightness, 
            contrast=contrast, 
            saturation=saturation, 
            normalize_histogram_individually=normalize_histogram_individually
        )
        output_path = self.utils.encode_image_to_file(enhancer_img)
        return Path(output_path)
