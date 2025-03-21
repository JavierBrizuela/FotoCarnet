from flask import Flask, request, jsonify, render_template
from processImage import image_crop, image_resizer, image_code
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_image():
    
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    file = request.files['image']
    width = float(request.form.get('ancho'))
    height = float(request.form.get('alto'))
    dpi = int(request.form.get('dpi'))
    percent = int(request.form.get('porcentaje'))
    
    image_croped = image_crop(file, width, height, dpi, percent)
    #image_resized = image_resizer(image_croped, width, height, dpi)
    image_process = image_code(image_croped)
    
    return jsonify({
        'processed_image': image_process,
        'message': 'Procesamiento exitoso'
    })

if __name__ == '__main__':
    app.run(debug=True)