# test_local.py - Script para probar el modelo localmente
import sys
from pathlib import Path
from PIL import Image
from predict import Predictor

def test_model():
    """Prueba el modelo localmente"""
    
    # Inicializar el predictor
    print("Inicializando modelo...")
    predictor = Predictor()
    predictor.setup()
    print("Modelo cargado correctamente!")
    
    # Ruta de imagen de prueba
    input_image_path = "original.jpeg"  # Cambia por tu imagen
    
    if not Path(input_image_path).exists():
        print(f"Error: No se encuentra la imagen {input_image_path}")
        print("Por favor, coloca una imagen llamada 'test_image.jpg' en este directorio")
        return
    
    try:
        print(f"Procesando imagen: {input_image_path}")
        
        # Ejecutar predicción
        result_path = predictor.predict(
            image=Path(input_image_path),
            width = 4,
            height = 4,
            dpi = 300,
            face_percentage = 70,
            brightness = 1.05,
            contrast = 1.05,
            saturation = 1.05,
            bg_color = "#FFFFFF",
            normalize_histogram_individually = True,
        )
        
        print(f"✅ Imagen procesada exitosamente!")
        print(f"📁 Resultado guardado en: {result_path}")
        
        # Mostrar información de la imagen resultante
        result_image = Image.open(result_path)
        print(f"📏 Dimensiones: {result_image.size}")
        print(f"🎨 Modo: {result_image.mode}")
        
        # Copiar resultado a ubicación fija para fácil acceso
        final_path = "resultado_fondo_removido.png"
        result_image.save(final_path)
        print(f"📋 Copia guardada como: {final_path}")
        
    except Exception as e:
        print(f"❌ Error durante el procesamiento: {str(e)}")

if __name__ == "__main__":
    test_model()