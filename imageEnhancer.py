import cv2 as cv
import numpy as np

def imageEnhancer(
                    img, 
                    brightness=1.0, 
                    contrast=1.2, 
                    saturation=1.1, 
                    sharpness=1.2, 
                    auto_white_balance=True
                    ):
    """
    Procesa la imagen con OpenCV para ajustar niveles
    Args:
        image: Imagen a procesar
        brightness: Factor de ajuste de brillo (>1 más brillante)
        contrast: Factor de ajuste de contraste (>1 más contraste)
        saturation: Factor de ajuste de saturación (>1 más saturado)
        sharpness: Factor de ajuste de nitidez (>1 más nitidez)
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
        
    # Convertir a LAB para ajustes de contraste/brillo más naturales
    lab = cv.cvtColor(rgb, cv.COLOR_BGR2LAB)
    l, a, b = cv.split(lab)
    
    # Aplicar CLAHE (Contrast Limited Adaptive Histogram Equalization) al canal L
    clahe = cv.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    l = clahe.apply(l)
    
    # Ajustar brillo
    l = cv.convertScaleAbs(l, alpha=brightness, beta=0)
    
    # Ajustar contraste
    l_mean = np.mean(l)
    l = cv.convertScaleAbs(l, alpha=contrast, beta=(1.0-contrast)*l_mean)
    
    # Recombinar canales
    lab = cv.merge((l, a, b))
    enhanced = cv.cvtColor(lab, cv.COLOR_LAB2BGR)
    
    # Balance de blancos automático si está activado
    if auto_white_balance:
        enhanced = autoWhiteBalance(enhanced)
    
        # Ajustar saturación
    hsv = cv.cvtColor(enhanced, cv.COLOR_BGR2HSV)
    h, s, v = cv.split(hsv)
    s = cv.convertScaleAbs(s, alpha=saturation, beta=0)
    hsv = cv.merge((h, s, v))
    enhanced = cv.cvtColor(hsv, cv.COLOR_HSV2BGR)
    
    # Aplicar sharpening/nitidez
    kernel = np.array([[-1, -1, -1], 
                        [-1,  9, -1], 
                        [-1, -1, -1]])
    enhanced = cv.filter2D(enhanced, -1, kernel * sharpness)
    
    # Reintegrar canal alpha si existía
    if alpha is not None:
        enhanced = cv.cvtColor(enhanced, cv.COLOR_BGR2BGRA)
        enhanced[:,:,3] = alpha
        
    return enhanced

def autoWhiteBalance(img):
        """Aplica balance de blancos automático a una imagen BGR"""
        # Convertir a LAB
        lab = cv.cvtColor(img, cv.COLOR_BGR2LAB)
        avg_a = np.average(lab[:, :, 1])
        avg_b = np.average(lab[:, :, 2])
        
        # Ajustar componentes a y b para neutralizar color
        lab[:, :, 1] = lab[:, :, 1] - ((avg_a - 128) * 0.8)
        lab[:, :, 2] = lab[:, :, 2] - ((avg_b - 128) * 0.8)
        
        # Convertir de vuelta a BGR
        balanced = cv.cvtColor(lab, cv.COLOR_LAB2BGR)
        return balanced