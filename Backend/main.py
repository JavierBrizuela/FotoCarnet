import json
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import processImage as pi
from imageEnhancer import imageEnhancer

app = Flask(__name__)
CORS(
        app,
        resources={r"/*": {"origins": "https://fotocarnet.netlify.app"}}
     )
  
@app.route('/process', methods=['POST'])
def process_image():
    
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    # Leer archivo de imagen y parámetros
    file = request.files['image']
    width = float(request.form.get('width'))
    height = float(request.form.get('height'))
    dpi = int(request.form.get('dpi'))
    percent = int(request.form.get('percentage'))
    hex_color = request.form.get('bg-color')
    unit = request.form.get('unit')
    # Lleva las unidades a centimetros
    if unit == 'inch':
        width = width * 2.54
        height = height * 2.54
    
    # Cargar imagen desde archivo
    image = pi.read_image(file)
     
    #detección de rostro
    x, y, w, h = pi.detect_head(image, debug=False)
    
    # Recortar imagen con los datos de deteccion de rostro
    image_croped = pi.image_crop(image, width, height, percent, x ,y , w, h)
    if image_croped is None:
            return jsonify({'error': 'Error al recortar la imagen'}), 500
    
    # Redimensionar imagen con el dpi especificado
    image_resized = pi.image_resizer(image_croped, width, height, dpi)
    if image_resized is None:
            return jsonify({'error': 'Error al redimensionar la imagen'}), 500
    
    # Ajustar brillo, contraste, saturación y normalizar histograma
    image_enhancer = imageEnhancer(
                                    image_resized, 
                                    brightness=1.05, 
                                    contrast=1.05, 
                                    saturation=1.05,
                                    normalize_image=True
                                    )
    # Convertir color hexadecimal a BGR
    bg_color = pi.hex_to_bgr(hex_color)
    
    # Procesar imagen - Obtener mascara
    image = pi.replicate_api(image_enhancer)
    if image is None:
            return jsonify({'error': 'Error al remover el fondo de la imagen'}), 500
    # Agregar fondo a la imagen
    image = pi.add_background(image, bg_color)
    
    # Aplicar codificación de imagen para la respuesta
    image_process = pi.image_code(image)
    return jsonify({
        'processed_image': image_process,
        'message': 'Procesamiento exitoso'
    })

if __name__ == '__main__':
    app.run(debug=True)