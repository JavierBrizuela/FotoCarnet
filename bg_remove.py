#from bgremove import bg
import cv2 as cv
import matplotlib.pyplot as plt
import numpy as np
import mediapipe as mp

bg_color = [100, 181, 246]
blur_amount = 15
erode_amount = 5
#Leer imagen
img = cv.imread('img.jpg')
img_rgb = cv.cvtColor(img, cv.COLOR_BGR2RGB)

# Inicializar MediaPipe Selfie Segmentation
selfie_segmentation = mp.solutions.selfie_segmentation
selfie_segmentation = selfie_segmentation.SelfieSegmentation(model_selection=0)
result = selfie_segmentation.process(img_rgb)
mask = result.segmentation_mask
blurred = cv.GaussianBlur(mask, (blur_amount, blur_amount), 0)
kernel = np.ones((erode_amount, erode_amount), np.uint8)
eroded = cv.erode(blurred, kernel, iterations=1)
bg_image = np.ones(img.shape, dtype=np.uint8)
bg_image[:] = bg_color  # Color en BGR
condition = eroded[:,:,np.newaxis] # Convertir máscara a 3 canales
#output_image = np.where(condition > 0.5, img_rgb, bg_image)
output_image = img_rgb * condition + bg_image * (1 - condition)
output_image = output_image.astype(np.uint8)
# Liberar recursos
selfie_segmentation.close()
# Mostrar imagenes
plt.figure(figsize=(12, 10))
plt.subplot(131); plt.imshow(img_rgb);plt.title("Original")
plt.subplot(132); plt.imshow(mask, cmap='gray');plt.title("mask")
plt.subplot(133); plt.imshow(output_image);plt.title("result")
plt.tight_layout()  # Ajusta automáticamente el espaciado
plt.show()
output_image = cv.cvtColor(output_image, cv.COLOR_RGB2BGR)
cv.imwrite('output.jpg', output_image)
