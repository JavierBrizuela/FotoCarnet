import json
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import processImage as pi
from imageEnhancer import imageEnhancer
# Importar modulos locales
from utils import Utils
from face_detect import FaceDetect
from crop_image import CropImage
from remove_bg import RemoveBg
from image_enhancer import ImageEnhancer

app = Flask(__name__)
CORS(
        app,
        resources={r"/*": {"origins": "https://fotocarnet.javierbrizuela.dev"}}
     )
  
# Instanciar modulos locales
enhancer = ImageEnhancer()
utils = Utils()
face_detect = FaceDetect()
crop_image = CropImage()
remove_bg = RemoveBg()

# Configurar la ruta principal
@app.route('/process', methods=['POST'])
def process_image():
    
    # Verificar si se ha enviado un archivo de imagen
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    # Leer archivo de imagen y parámetros
    file = request.files['image']
    width = float(request.form.get('width'))
    height = float(request.form.get('height'))
    dpi = int(request.form.get('dpi'))
    face_percentage = int(request.form.get('percentage'))
    hex_color = request.form.get('bg-color')
    unit = request.form.get('unit')
    
    # Lleva las unidades a centimetros
    if unit == 'inch':
        width = width * 2.54
        height = height * 2.54
    
    # Cargar imagen desde archivo
    image = pi.read_image(file)
    print(f"Image shape: {image.shape}")
        
    # Detectar y obtener dimensiones de la cara
    face_x, face_y, face_w, face_h = face_detect.find_hair_top_boundary(image)
    print(f"Face coordinates: x={face_x}, y={face_y}, w={face_w}, h={face_h}")
        
    # Recortar la imagen con las dimensiones especificadas
    croped_img = crop_image.crop(image, face_x, face_y, face_w, face_h, width, height, face_percentage)
    print(f"Croped image shape: {croped_img.shape}")
    
    # Redimencionar imagen a DPI especificado
    resized_img = utils.resize_image(croped_img, width, height, dpi)
    
    # Mejorar brillo, contraste y saturación
    enhancer_img = enhancer.enhance_image(
                                            resized_img, 
                                            brightness=1.05, 
                                            contrast=1.05, 
                                            saturation=1.05, 
                                            normalize_histogram_individually=True
                                            )
    
    # Codifica la imagen a base64
    output = utils.image_code(enhancer_img)
    return jsonify({
        'processed_image': output,
        'message': 'Procesamiento exitoso'
    })

if __name__ == '__main__':
    app.run(debug=True)