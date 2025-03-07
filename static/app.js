const DropZone = document.getElementById('drop-zone');
const FileInput = document.getElementById('file-input');
const Preview = document.getElementById('preview');

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
        handleImage(files[0]);
    }
});

// event click to select file
DropZone.addEventListener('click', (e) => {
    FileInput.click();
});
// file input change event listener
FileInput.addEventListener('change', (e) => {
    previewFile(FileInput.files[0]);
});

async function handleImage(file = File) {
    const formData = new FormData();
    formData.append('image', file);
    const response = await fetch('/upload', {
        method: 'POST',
        body: formData
    });
    const data = await response.json();
    //show image
    const img = document.createElement('img');
    img.src = data.file;
    Preview.appendChild(img);

    return data;
}