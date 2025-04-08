#pip install opencv-python

import math

import numpy as np
import cv2
import matplotlib.pyplot as plt
import os
import glob

img_list = []
for ext in ['*.jpg', '*.jpeg']:
    img_list.extend(glob.glob(os.path.join(os.getcwd(), ext)))

    for img_path in img_list:
        # Importa e converte para RGB
        img = cv2.imread(img_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Convertendo para preto e branco (RGB -> Gray Scale -> BW)
        img_gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        a = img_gray.max()
        _, thresh = cv2.threshold(img_gray, a / 2 * 1.7, a, cv2.THRESH_BINARY_INV)

        # Processamento adicional e salvamento de resultados
        tamanhoKernel = 3  # Smaller kernel size
        kernel = np.ones((tamanhoKernel, tamanhoKernel), np.uint8)

        # Apply morphological closing to fill gaps (reduced intensity)
        thresh_close = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

        # Skip morphological opening to retain more edge details

        # Detecção borda com Canny (increased sensitivity)
        edges_morph = cv2.Canny(image=thresh_close, threshold1=a / 3, threshold2=a / 1.5)

        # Contorno
        contours, hierarchy = cv2.findContours(
            image=edges_morph,
            mode=cv2.RETR_TREE,
            method=cv2.CHAIN_APPROX_SIMPLE
        )
        contours = sorted(contours, key=cv2.contourArea, reverse=True)
        img_copy = img.copy()
        final = cv2.drawContours(img_copy, contours, contourIdx=-1,
                                 color=(255, 0, 0), thickness=2)

        # Plot imagens
        imagens = [img, img_gray, thresh, thresh_close, edges_morph, final]

        # Save image
        output_path = os.path.join(os.getcwd(), f'contorno_{os.path.basename(img_path)[:-4]}.png')
        cv2.imwrite(output_path, final)