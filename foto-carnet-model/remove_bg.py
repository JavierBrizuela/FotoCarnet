
from rembg import remove, new_session
class RemoveBg:
    
    def __init__(self):
        self.session = new_session("birefnet-general-lite")
    
    def rem_bg(self, img, bg_color):
        bg_color = bg_color + (255,)  # Convertir a formato BGRA
        # Obtener mascara de segmentación
        img = remove(
                        img, 
                        session=self.session,
                        bgcolor=bg_color,
                        alpha_matting=True,
                        alpha_matting_foreground_threshold=240,  # Valor alto para preservar detalles finos
                        alpha_matting_background_threshold=10,   # Valor bajo para preservar detalles finos
                        alpha_matting_erode_size=5               # Valor moderado (balance entre calidad y velocidad)
                    )
        print("Fondo extraido correctamente")
        return img