import base64
import cv2 as cv
import numpy as np

class Utils:
    def __init__(self):
        pass
    
    def encode_image_to_file(self, img: np.ndarray, output_path: str = None) -> str:
        """codificar imagen base64 string"""
        if img is None or not isinstance(img, np.ndarray) or img.size == 0:
            raise ValueError("Invalid image for encoding")
        
        # Si la imagen es BGRA, convertir a BGR
        #if len(img.shape) == 3 and img.shape[2] == 4:
        #    img = cv.cvtColor(img, cv.COLOR_BGRA2BGR)
            
        try:
            # Si no se proporciona ruta, crear una temporal
            if output_path is None:
                output_path = "/tmp/output_image.png"
            
            # Guardar la imagen directamente
            success = cv.imwrite(output_path, img)
            if not success:
                raise ValueError("Failed to save image")
                
            return output_path
            
        except Exception as e:
            raise ValueError(f"Error saving image: {str(e)}")
        
    def hex_to_bgr(self, hex_color):
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 3:  # Formato corto (#FFF → #FFFFFF)
            hex_color = ''.join([c * 2 for c in hex_color])
        if len(hex_color) != 6:
            raise ValueError("Color hex debe tener formato #RRGGBB")
        try:
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        except ValueError:
            raise ValueError("Color hex inválido")