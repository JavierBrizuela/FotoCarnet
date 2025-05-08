const DropZone = document.getElementById("drop-zone");
const FileInput = document.getElementById("file-input");
const previewZone = document.getElementById("preview-zone");
const formZone = document.getElementById("form-zone");
const submitButton = document.getElementById("submit");
let selectedFile = null;

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
async function showImage(file) {
  const img = document.createElement("img");
  img.src = URL.createObjectURL(file);
  DropZone.innerHTML = "";
  DropZone.appendChild(img);
}
async function handleImage(file) {
  const formData = new FormData();
  formData.append("image", file);

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

  try {
    const response = await fetch("/process", {
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

// Estado de validación
const validationState = {
  width: false,
  height: false,
  dpi: false,
  percentage: false,
};

// Función para validar el formulario
function validateForm() {
  const isFormValid = Object.values(validationState).every(
    (state) => state === true
  );
  submitButton.disabled = !(isFormValid && selectedFile);
  return isFormValid;
}

// Validación específica para el ancho (entre 1 y 10)
function validateWidth() {
  const value = width.value.trim();
  const numValue = parseFloat(value);

  // Verificar si es un número y está en el rango válido
  if (numValue >= 1 && numValue <= 10) {
    width.classList.add("is-valid");
    width.classList.remove("is-invalid");
    validationState.width = true;
  } else {
    width.classList.add("is-invalid");
    width.classList.remove("is-valid");
    validationState.width = false;
  }

  validateForm();
}

// Validación específica para el alto (entre 1 y 10)
function validateHeight() {
  const value = height.value.trim();
  const numValue = parseFloat(value);

  // Verificar si es un número y está en el rango válido
  if (numValue >= 1 && numValue <= 10) {
    height.classList.add("is-valid");
    height.classList.remove("is-invalid");
    validationState.height = true;
  } else {
    height.classList.add("is-invalid");
    height.classList.remove("is-valid");
    validationState.height = false;
  }

  validateForm();
}

// Validación específica para el dpi (entre 72 y 600)
function validateDPI() {
  const value = dpi.value.trim();
  const numValue = parseFloat(value);

  // Verificar si es un número y está en el rango válido
  if (numValue >= 72 && numValue <= 600) {
    dpi.classList.add("is-valid");
    dpi.classList.remove("is-invalid");
    validationState.dpi = true;
  } else {
    dpi.classList.add("is-invalid");
    dpi.classList.remove("is-valid");
    validationState.dpi = false;
  }

  validateForm();
}

// Validación específica para el porcentage (entre 1 y 100)
function validatePercentage() {
  const value = percentage.value.trim();
  const numValue = parseFloat(value);

  // Verificar si es un número y está en el rango válido
  if (numValue >= 1 && numValue <= 100) {
    percentage.classList.add("is-valid");
    percentage.classList.remove("is-invalid");
    validationState.percentage = true;
  } else {
    percentage.classList.add("is-invalid");
    percentage.classList.remove("is-valid");
    validationState.percentage = false;
  }

  validateForm();
}

// Event listeners para validar mientras se escribe
width.addEventListener("input", validateWidth);
height.addEventListener("input", validateHeight);
dpi.addEventListener("input", validateDPI);
percentage.addEventListener("input", validatePercentage);

// Seleccionar color de fondo predefinido
function selectBgColor(bgColor) {
  document.getElementById("bg-color").value = bgColor;
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
  if (selectedFile) {
    handleImage(selectedFile);
  }
});

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
  validateWidth();
  validateHeight();
  validateDPI();
  validatePercentage();
  validateForm();
  // Actualizar radios de unidad
  document.querySelectorAll('input[name="unit"]').forEach((radio) => {
    radio.checked = radio.value === selectedOption.dataset.unit;
  });
});

// Validación inicial
validateDPI(); // El único campo con valor inicial