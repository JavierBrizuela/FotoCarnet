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
    const unit = document.querySelector('input[name="unit"]:checked').value;
    const width = document.getElementById('width').value;
    const height = document.getElementById('height').value;
    const dpi = document.getElementById('dpi').value;
    const percentage = document.getElementById('percentage').value;
    const bgColor = document.getElementById('bg-color').value;

    // Agregar datos del formulario a formData
    formData.append('unit', unit);
    formData.append('width', width);
    formData.append('height', height);
    formData.append('dpi', dpi);
    formData.append('percentage', percentage);
    formData.append('bg-color', bgColor);
    
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
    const unit = document.querySelector('input[name="unit"]:checked');
    const width = document.getElementById('width').value;
    const height = document.getElementById('height').value;
    const dpi = document.getElementById('dpi').value;
    const percentage = document.getElementById('percentage').value;
    const bgColor = document.getElementById('bg-color').value;
    const selectedFile = FileInput.files[0];

    if (unit && width && height && dpi && percentage && bgColor && selectedFile) {
        submitButton.disabled = false;
    } else {
        submitButton.disabled = true;
    }
}

// Seleccionar color de fondo predefinido
function selectBgColor(bgColor) {
    document.getElementById("bg-color").value = bgColor;
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

//Actualiza los valores de los campos cuando cambia el dropdown
document.getElementById('templates').addEventListener('change', (e) => {
    const select = e.target;
    const selectedOption = select.options[select.selectedIndex];
    // Actualizar los valores de los campos del formulario con los datos del template seleccionado
    document.getElementById('width').value = selectedOption.dataset.width;
    document.getElementById('height').value = selectedOption.dataset.height;
    document.getElementById('percentage').value = selectedOption.dataset.percentage;
    document.getElementById('dpi').value = selectedOption.dataset.dpi;
    document.getElementById('bg-color').value = selectedOption.dataset.bgColor;
    validateForm();
    // Actualizar radios de unidad
    document.querySelectorAll('input[name="unit"]').forEach(radio => {
        radio.checked = (radio.value === selectedOption.dataset.unit);
    });
});