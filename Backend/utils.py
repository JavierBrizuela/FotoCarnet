import base64
import cv2 as cv
import numpy as np

class Utils:
    def __init__(self):
        pass
    
    def read_image(self, file):
    # Leer imagen
        img = cv.imdecode(np.frombuffer(file.read(), np.uint8), cv.IMREAD_COLOR)
        if img is None:
            raise ValueError("La imagen no se pudo leer correctamente.")
        return img
    
    def image_code(self, file):
        # Verificar que file sea una imagen válida
        if file is None or not isinstance(file, np.ndarray) or file.size == 0:
            print("Error: La imagen de entrada para codificar es inválida o está vacía")
            return None
        
        # Si la imagen es BGRA (con transparencia), convertir a BGR primero
        if file.shape[2] == 4:
            file = cv.cvtColor(file, cv.COLOR_BGRA2BGR)
            
        try:
            # Codificar imagen resultante
            _, buffer = cv.imencode('.png', file)
            encoded_image = base64.b64encode(buffer).decode('utf-8')
            return encoded_image
        
        except Exception as e:
            print(f"Error al codificar la imagen: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def resize_image(self, img, width, height, dpi):
        """
        Redimensiona la imagen a las dimensiones especificadas en centímetros y DPI.
        
        """
        # Convertir cm a píxeles
        dpc = int(dpi / 2.54)
        resized_img = cv.resize(img, (int(width * dpc), int(height * dpc)), interpolation=cv.INTER_AREA)
        return resized_img
        
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