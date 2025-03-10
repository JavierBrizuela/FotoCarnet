const DropZone = document.getElementById('drop-zone');
const FileInput = document.getElementById('file-input');
const preview = document.getElementById('preview');
const formZone = document.getElementById('form-zone');
const submitButton = document.getElementById('submit');
let selectedFile = null;

// grag and drop event listener
DropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    DropZone.classList.add('dragover');
});

DropZone.addEventListener('dragleave', (e) => {
    DropZone.classList.remove('dragover');
});

DropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    DropZone.classList.remove('dragover');
    const files = e.dataTransfer.files;
    if (files.length) {
        selectedFile = files[0];
        showImage(selectedFile);
        validateForm();
    }
});

// event click to select file
DropZone.addEventListener('click', (e) => {
    FileInput.click();
});
// file input change event listener
FileInput.addEventListener('change', (e) => {
    selectedFile = FileInput.files[0];
    showImage(selectedFile);
    validateForm();
});
async function showImage(file) {
    const img = document.createElement('img');
    img.src = URL.createObjectURL(file);
    DropZone.innerHTML = '';
    DropZone.appendChild(img);
    
}
async function handleImage(file) {
    const formData = new FormData();
    formData.append('image', file);

    // Obtener datos del formulario
    const unidad = document.querySelector('input[name="unidad"]:checked').value;
    const ancho = document.getElementById('ancho').value;
    const alto = document.getElementById('alto').value;
    const dpi = document.getElementById('dpi').value;
    const porcentaje = document.getElementById('porcentaje').value;

    // Agregar datos del formulario a formData
    formData.append('unidad', unidad);
    formData.append('ancho', ancho);
    formData.append('alto', alto);
    formData.append('dpi', dpi);
    formData.append('porcentaje', porcentaje);
    
    try {
        const response = await fetch('/process', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        //show image
        const img = document.createElement('img');
        img.src = `data:image/jpeg;base64,${data.processed_image}`;
        preview.innerHTML = 'imagen procesada:';
        preview.appendChild(img);
        
    } catch (error) {
        console.error('Error during fetch:', error);
        alert('Hubo un error al subir la imagen. Por favor, inténtalo de nuevo.');
    }
}

// Función para validar el formulario
function validateForm() {
    const unidad = document.querySelector('input[name="unidad"]:checked');
    const ancho = document.getElementById('ancho').value;
    const alto = document.getElementById('alto').value;
    const dpi = document.getElementById('dpi').value;
    const porcentaje = document.getElementById('porcentaje').value;

    if (unidad && ancho && alto && dpi && porcentaje && selectedFile) {
        submitButton.disabled = false;
    } else {
        submitButton.disabled = true;
    }
}

// Agregar eventos de cambio a los campos del formulario para validar
document.querySelectorAll('#form-zone input, #form-zone select').forEach(element => {
    element.addEventListener('input', validateForm);
});

// Inicializar el estado del botón de submit
validateForm();

submitButton.addEventListener('click', (e) => {
    e.preventDefault();
    if (selectedFile) {
        handleImage(selectedFile);
    }
});