import cv2 as cv
import numpy as np

def imageEnhancer(
                    img, 
                    brightness=1.0, 
                    contrast=1.2, 
                    saturation=1.1, 
                    normalize_image=True
                    ):
    """
    Procesa la imagen con OpenCV para ajustar niveles, contraste y saturación.
    Args:
        image: Imagen a procesar
        brightness: Factor de ajuste de brillo (>1 más brillante)
        contrast: Factor de ajuste de contraste (>1 más contraste)
        saturation: Factor de ajuste de saturación (>1 más saturado)
        auto_white_balance: Si aplicar balance de blancos automático
    
    Returns:
        Imagen procesada como array de numpy
    """
    # Separar canales RGB y alpha
    if img.shape[2] == 4:  # RGBA
        rgb = img[:,:,:3]
        alpha = img[:,:,3]
    else:  # RGB
        rgb = img
        alpha = None
        
    # Ajuste del histograma si está activado
    if normalize_image:
        rgb = normalize_channels_individually(rgb)
        
    # Convertir a LAB para ajustes de contraste/brillo más naturales
    lab = cv.cvtColor(rgb, cv.COLOR_BGR2LAB)
    l, a, b = cv.split(lab)
    
    # Aplicar CLAHE (Contrast Limited Adaptive Histogram Equalization) al canal L
    #clahe = cv.createCLAHE(clipLimit=1.0, tileGridSize=(16,16))
    #l = clahe.apply(l)
    
    # Ajustar brillo
    l = cv.convertScaleAbs(l, alpha=brightness, beta=0)
    
    # Ajustar contraste
    l_mean = np.mean(l)
    l = cv.convertScaleAbs(l, alpha=contrast, beta=(1.0-contrast)*l_mean)
    
    # Recombinar canales
    lab = cv.merge((l, a, b))
    enhanced = cv.cvtColor(lab, cv.COLOR_LAB2BGR)
    
    
    # Ajustar saturación
    hsv = cv.cvtColor(enhanced, cv.COLOR_BGR2HSV)
    h, s, v = cv.split(hsv)
    s = cv.convertScaleAbs(s, alpha=saturation, beta=0)
    hsv = cv.merge((h, s, v))
    enhanced = cv.cvtColor(hsv, cv.COLOR_HSV2BGR)
    
    # Reintegrar canal alpha si existía
    if alpha is not None:
        enhanced = cv.cvtColor(enhanced, cv.COLOR_BGR2BGRA)
        enhanced[:,:,3] = alpha
        
    return enhanced
    
def normalize_image_global(image):
    image_float = image.astype(np.float32)
    # Normalización global (todos los canales juntos)
    min_val = np.min(image_float)
    max_val = np.max(image_float)
    
    # Evitar división por cero
    if max_val > min_val:
        normalized = 255 * (image - min_val) / (max_val - min_val)
        return normalized.astype(np.uint8)
    return image

def normalize_channels_individually(image):
    # Separar canales
    if len(image.shape) == 3:  # Imagen a color
        channels = cv.split(image)
        normalized_channels = []
        
        for channel in channels:
            image_float = image.astype(np.float32)
            # Normalización global (todos los canales juntos)
            min_val = np.min(image_float)
            max_val = np.max(image_float)
            
            if max_val > min_val:
                norm_channel = 255 * (channel - min_val) / (max_val - min_val)
                normalized_channels.append(norm_channel.astype(np.uint8))
            else:
                normalized_channels.append(channel)
        
        return cv.merge(normalized_channels)
    else:  # Imagen en escala de grises
        return normalize_image_global(image)