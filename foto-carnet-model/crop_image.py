import cv2 as cv

class CropImage:
    def __init__(self):
        pass
    
    def crop(self, image, face_x, face_y, face_w, face_h, width=4.0, height=4.0, face_percentage=65):
        
        # Calcular proporciones para recortar imagen
        aspect_ratio = width / height
        height_final = int((face_h * 100) / face_percentage)
        width_final = int(height_final * aspect_ratio)
        side_margin = int((width_final - face_w) * 0.5)
        top_margin = int(height_final * 0.06)
        crop_x = face_x - side_margin
        crop_y = face_y - top_margin
        crop_w = crop_x + width_final
        crop_h = crop_y + height_final
        # Si la región a recortar está fuera de los límites de la imagen, agregar padding
        if crop_x < 0 or crop_y < 0 or crop_w > image.shape[1] or crop_h > image.shape[0]:
            print("Recortando imagen con padding")
            img_croped = self.image_padding(image, crop_x, crop_y, crop_w, crop_h)
        else:
            img_croped = image[crop_y:crop_h, crop_x:crop_w]
        
        return img_croped
        
    def image_padding(self, img, x, y, w, h):
        # Asegurar que la imagen tenga canal alfa
        if img.shape[2] == 3:
            # Convertir imagen a escala de grises si es necesario
            img = cv.cvtColor(img, cv.COLOR_BGR2BGRA)
            
        # Asegurarse de que no se salga de los límites de la imagen
        x1 = max(0, x)
        y1 = max(0, y)
        x2 = min(img.shape[1], w)
        y2 = min(img.shape[0], h)    
        
        img_crop = img[y1:y2, x1:x2]
        # Crear el padding con transparencia
        transparent_color = [128, 128, 128, 0]  # Negro completamente transparente
        pad_left = max(0, x1 - x)
        pad_right = max(0, w - x2)
        pad_top = max(0, y1 - y)
        pad_bottom = max(0, h - y2)
        img_padded = cv.copyMakeBorder(img_crop, 
                                    pad_top, pad_bottom, pad_left, pad_right, 
                                    cv.BORDER_CONSTANT, 
                                    value=transparent_color)
        return img_padded
        