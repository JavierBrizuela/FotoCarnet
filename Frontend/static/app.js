const DropZone = document.getElementById("drop-zone");
const FileInput = document.getElementById("file-input");
const previewZone = document.getElementById("preview-zone");
const formZone = document.getElementById("form-zone");
const submitButton = document.getElementById("submit");
const API_URL = window.CONFIG.API_URL || "http://localhost:5000"; // Cambia esto según tu entorno
let selectedFile = null;

// Estado de validación
const validationState = {
  width: false,
  height: false,
  dpi: false,
  percentage: false,
  selectedFile: false,
  bgColor: false,
};

// grag and drop event listener
DropZone.addEventListener("dragover", (e) => {
  e.preventDefault();
  DropZone.classList.add("dragover");
});

DropZone.addEventListener("dragleave", (e) => {
  DropZone.classList.remove("dragover");
});

DropZone.addEventListener("drop", (e) => {
  e.preventDefault();
  DropZone.classList.remove("dragover");
  const files = e.dataTransfer.files;
  if (files.length) {
    selectedFile = files[0];
    showImage(selectedFile);
    validateForm();
  }
});

// event click to select file
DropZone.addEventListener("click", (e) => {
  FileInput.click();
});

// file input change event listener
FileInput.addEventListener("change", (e) => {
  selectedFile = FileInput.files[0];
  showImage(selectedFile);
  validateForm();
});

// Agrega una imagen al dropZone
async function showImage(file) {
  const img = document.createElement("img");
  img.src = URL.createObjectURL(file);
  DropZone.innerHTML = "";
  DropZone.appendChild(img);
  validationState.selectedFile = true;
}

// Hace la petición al servidor para procesar la imagen y la muestra en el previewZone
async function handleImage(file) {
  const formData = new FormData();
  // Obtener datos del formulario
  const unit = document.querySelector('input[name="unit"]:checked').value;
  const width = document.getElementById("width").value;
  const height = document.getElementById("height").value;
  const dpi = document.getElementById("dpi").value;
  const percentage = document.getElementById("percentage").value;
  const bgColor = document.getElementById("bg-color").value;
  // Agregar datos del formulario a formData
  formData.append("unit", unit);
  formData.append("width", width);
  formData.append("height", height);
  formData.append("dpi", dpi);
  formData.append("percentage", percentage);
  formData.append("bg-color", bgColor);
  formData.append("image", file);

  try {
    const response = await fetch(`${API_URL}/process`, {
      method: "POST",
      body: formData,
    });
    const data = await response.json();

    //show image
    const img = document.createElement("img");
    img.src = `data:image/jpeg;base64,${data.processed_image}`;
    previewZone.innerHTML = "";
    previewZone.appendChild(img);
  } catch (error) {
    console.error("Error during fetch:", error);
    alert("Hubo un error al subir la imagen. Por favor, inténtalo de nuevo.");
  }
}

// Función para validar números decimales
function validateDecimal(input, min, max) {
  const value = parseFloat(input.value);
  console.log(input);
  const isValid = !isNaN(value) && value >= min && value <= max;
  
  if (isValid) {
      input.classList.remove('is-invalid');
      input.classList.add('is-valid');
      validationState[input.id] = true;
  } else {
      input.classList.remove('is-valid');
      input.classList.add('is-invalid');
      validationState[input.id] = false;
  }
}

// Función para validar números enteros
function validateInteger(input, min, max) {
  const value = parseInt(input.value);
  const isInteger = String(value) === input.value || Number.isInteger(parseFloat(input.value));
  const isValid = !isNaN(value) && isInteger && value >= min && value <= max;
  
  if (isValid) {
      input.classList.remove('is-invalid');
      input.classList.add('is-valid');
      validationState[input.id] = true;
  } else {
      input.classList.remove('is-valid');
      input.classList.add('is-invalid');
      validationState[input.id] = false;
  }
}

// Función para validar el color de fondo
function validateColor(input) {
  // Regex para validar formato de color hexadecimal (#RRGGBB o #RGB)
  const hexColorRegex = /^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$/;
  const isValid = hexColorRegex.test(input.value);
  
  if (isValid) {
      input.classList.remove('is-invalid');
      input.classList.add('is-valid');
      validationState.bgColor = true;
  } else {
      input.classList.remove('is-valid');
      input.classList.add('is-invalid');
      validationState.bgColor = false;
  }
  validateForm();
}

// Función para validar el formulario
function validateForm() {
  const isFormValid = Object.values(validationState).every(
    (state) => state === true
  );
  submitButton.disabled = !isFormValid;
  return isFormValid;
}
const widthInput = document.getElementById("width");
const heightInput = document.getElementById("height");
const dpiInput = document.getElementById("dpi");
const percentageInput = document.getElementById("percentage");
const bgColorInput = document.getElementById("bg-color");
// Event listeners para validar mientras se escribe
widthInput.addEventListener("input",() => validateDecimal(widthInput, 1, 10));
heightInput.addEventListener("input",() => validateDecimal(heightInput, 1, 10));
dpiInput.addEventListener("input",() => validateInteger(dpiInput, 72, 600));
percentageInput.addEventListener("input",() => validateInteger(percentageInput, 1, 100));
bgColorInput.addEventListener("input",validateColor(bgColorInput));
// Seleccionar color de fondo predefinido
function selectBgColor(bgColor) {
  bgColorInput.value = bgColor;
  validateColor(bgColorInput);
}

// Agregar eventos de cambio a los campos del formulario para validar
document
  .querySelectorAll("#form-zone input, #form-zone select")
  .forEach((element) => {
    element.addEventListener("input", validateForm);
  });

// Inicializar el estado del botón de submit
validateForm();

submitButton.addEventListener("click", (e) => {
  e.preventDefault();
  // Deshabilitar el botón
  submitButton.disabled = true;
  // Mostrar el mensaje de carga
  showLoadingAnimation();
  // Llamar a la función para manejar la imagen
  handleImage(selectedFile);
});

// Función para mostrar la animación de carga
function showLoadingAnimation() {
  previewZone.innerHTML = `
    <div class="loading">
      <div class="loading-spinner"></div>
      <p class="loading-text">Procesando imagen...</p>
      <div class="loading-dots">
        <span></span>
        <span></span>
        <span></span>
      </div>
    </div>
  `;
}

//Actualiza los valores de los campos cuando cambia el dropdown
document.getElementById("templates").addEventListener("change", (e) => {
  const select = e.target;
  const selectedOption = select.options[select.selectedIndex];
  // Actualizar los valores de los campos del formulario con los datos del template seleccionado
  document.getElementById("width").value = selectedOption.dataset.width;
  document.getElementById("height").value = selectedOption.dataset.height;
  document.getElementById("percentage").value = selectedOption.dataset.percentage;
  document.getElementById("dpi").value = selectedOption.dataset.dpi;
  document.getElementById("bg-color").value = selectedOption.dataset.bgColor;
  // Validar todos los campos para actualizar el estado
  validateDecimal(widthInput, 1, 10);
  validateDecimal(heightInput, 1, 10);
  validateInteger(dpiInput, 72, 600);
  validateInteger(percentageInput, 1, 100);
  validateForm();
  // Actualizar radios de unidad
  document.querySelectorAll('input[name="unit"]').forEach((radio) => {
    radio.checked = radio.value === selectedOption.dataset.unit;
  });
});

// Validación inicial de dpi
validateInteger(dpiInput, 72, 600); // El único campo con valor inicial