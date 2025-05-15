import json
from flask import Flask, request, jsonify, render_template
import processImage as pi
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False  # Para respuestas JSON con caracteres especiales

def load_template():
    with open('config/templates.json', 'r', encoding='utf-8') as file:
        return json.load(file)

@app.route('/')
def index():
    templates = load_template()
    return render_template('index.html', templates=templates)
    
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
    x, y, w, h = pi.detect_face(image)
    
    # Muestra un rectangulo alrededor de la cara detectada (opcional)
    #face = pi.show_face(selfie_segmentation, x, y, w, h)
    
    # Recortar imagen con los datos de deteccion de rostro
    image_croped = pi.image_crop(image, width, height, percent, x ,y , w, h)
    if image_croped is None:
            return jsonify({'error': 'Error al recortar la imagen'}), 500
    
    # Redimensionar imagen con el dpi especificado
    image_resized = pi.image_resizer(image_croped, width, height, dpi)
    if image_resized is None:
            return jsonify({'error': 'Error al redimensionar la imagen'}), 500
    
    # Convertir color hexadecimal a BGR
    bg_color = pi.hex_to_bgr(hex_color)
    
    # Procesar imagen - Obtener mascara
    image = pi.rem_bg(image_resized, bg_color)
    if image is None:
            return jsonify({'error': 'Error al remover el fondo de la imagen'}), 500
    
    # Aplicar codificación de imagen para la respuesta
    image_process = pi.image_code(image)
    return jsonify({
        'processed_image': image_process,
        'message': 'Procesamiento exitoso'
    })

if __name__ == '__main__':
    app.run(debug=True)