// Iniciar la carga de plantillas cuando se carga la página
document.addEventListener('DOMContentLoaded', () => {
    loadTemplates();
});
// Variable global para almacenar las plantillas cargadas desde JSON
let templates = {};

// Cargar las plantillas desde el archivo JSON local o desde la API
async function loadTemplates() {
        // Primero intentamos cargar desde el archivo JSON local
        let response = await fetch('static/templates.json');
        
        // Si no podemos cargar el archivo local
        if (!response.ok) {
            console.log('No se pudo cargar templates.json');
        }
        // Si la carga fue exitosa, parsear el JSON
        templates = await response.json();
        
        // Una vez cargadas las plantillas, actualizar el selector
        populateTemplateSelector();
    } 

function populateTemplateSelector() {
    const templateSelect = document.getElementById('templates');
    
    // Limpiar opciones existentes excepto la primera (placeholder)
    while (templateSelect.options.length > 1) {
        templateSelect.remove(1);
    }
    
    // Agregar las opciones de plantillas desde el objeto templates
    for (const [key, value] of Object.entries(templates)) {
        const option = document.createElement('option');
        option.value = key;
        option.text = key.charAt(0).toUpperCase() + key.slice(1); // Capitalizar primera letra
        
        // Agregar atributos de datos para cada valor de la plantilla
        option.dataset.width = value.width;
        option.dataset.height = value.height;
        option.dataset.percentage = value.percentage;
        option.dataset.bgColor = value["bg-color"];
        option.dataset.dpi = value.dpi;
        option.dataset.unit = value.unit;
        
        templateSelect.appendChild(option);
    }
}
