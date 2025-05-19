# FotoCarnet 📸

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](https://opensource.org/licenses/MIT)

Herramienta para generar y procesar fotos carnet profesionales, ideal para documentos de identificación.

![Demo](https://github.com/user-attachments/assets/f91c518c-1b1c-4ba9-be55-a895b2180b84)

## Características ✨
- Generación automática de fotos carnet en tamaños estándar y personalizados
- Ajuste de fondo (color sólido)
- Optimización para impresión (300 DPI)
- Interfaz Web sencilla
- Soporte múltiples formatos: JPG, PNG, PDF

## Requisitos 📦
- Python 3.8+
- Bibliotecas: Flask, OpenCV, numpy, MediaPipe, RemBg

## Instalación 🔧

```bash
# Clonar repositorio
git clone https://github.com/JavierBrizuela/FotoCarnet.git
cd FotoCarnet

# Instalar dependencias con pip
pip install -r requirements.txt
# Instalar dependencias con pipenv
pipenv install
pipenv shell
# Ejecutar el servidor
python .\main.py
