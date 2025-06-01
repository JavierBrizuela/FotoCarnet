import cv2
import mediapipe as mp
import numpy as np
from typing import Tuple, Optional

class FaceDetect:
    def __init__(self):
        # Inicializar MediaPipe Selfie Segmentation
        self.mp_selfie_segmentation = mp.solutions.selfie_segmentation
        self.selfie_segmentation = self.mp_selfie_segmentation.SelfieSegmentation(
            model_selection=0)    
        # También inicializar face detection para mejor precisión
        self.mp_face_detection = mp.solutions.face_detection
        self.face_detection = self.mp_face_detection.FaceDetection(
            model_selection=1, min_detection_confidence=0.5)
    
    def find_hair_top_boundary(self, image) -> int:
        """
        Encuentra el límite superior del cabello para recorte de foto carnet
        
        Args:
            img: imagen
                        
        Returns:
            información del límite superior y coordenadas de recorte
        """
         
        if image is None:
            raise ValueError(f"No se pudo cargar la imagen: {image}")
        
        height, width = image.shape[:2]
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Procesar con selfie segmentation
        selfie_results = self.selfie_segmentation.process(rgb_image)
        
        # También detectar cara para contexto
        face_results = self.face_detection.process(rgb_image)
        
        if face_results.detections is None:
            print("No se detectó a ninguna persona")
            return None
        
        # Convertir máscara a formato utilizable
        selfie_mask = (selfie_results.segmentation_mask * 255).astype(np.uint8)
        
        # Encontrar el límite superior del cabello
        top_hair = self._find_topmost_hair_pixel(selfie_mask)
        
        # Determinar límites laterales y inferior
        face_bbox = self._get_face_bbox(face_results, width, height) if face_results.detections else None
        
        # Usar la cara como referencia para el ancho y alto
        face_x, face_y, face_w, face_h = face_bbox  
        face_h = int(face_y - top_hair + face_h) 
        face_y = top_hair     
        return face_x, face_y, face_w, face_h
    
    def _find_topmost_hair_pixel(self, selfie_mask: np.ndarray) -> int:
        """
        Encuentra el pixel más alto donde hay cabello
        """
        # Buscar de arriba hacia abajo
        for y in range(selfie_mask.shape[0]):
            row = selfie_mask[y, :]
            if np.any(row > 128):  # Threshold para considerar cabello
                return y
        
        # Si no se encuentra cabello, retornar 10% desde arriba
        return int(selfie_mask.shape[0] * 0.1)
    
    def _get_face_bbox(self, face_results, width, heigth) -> Optional[Tuple[int, int, int, int]]:
        """
        Obtiene el bounding box de la cara detectada
        """
        if not face_results.detections:
            return None
        
        detection = face_results.detections[0]  # Tomar la primera cara detectada
        bbox = detection.location_data.relative_bounding_box
        
        x = int(bbox.xmin * width)
        y = int(bbox.ymin * heigth)
        w = int(bbox.width * width)
        h = int(bbox.height * heigth)
        
        return (x, y, w, h)
    