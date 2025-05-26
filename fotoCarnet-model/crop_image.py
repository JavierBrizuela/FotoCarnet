import cv2 as cv

class CropImage:
    def __init__(self):
        pass
    
    def crop(self, image, face_x, face_y, face_w, face_h, width=4.0, height=4.0, dpi=300, face_percentage=65):
        
        # Calcular proporciones para recortar imagen
        aspect_ratio = width / height
        height_final = int((face_h * 100) / face_percentage)
        width_final = int(height_final * aspect_ratio)
        side_margin = int((width_final - face_w) * 0.5)
        top_margin = int(height_final * 0.06)
        face_x = face_x - side_margin
        face_y = face_y - top_margin
        img_croped = image[face_y:face_y + height_final, face_x:face_x + width_final]
        return img_croped
        
    