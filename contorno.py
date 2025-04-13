import math
import numpy as np
import cv2
import matplotlib.pyplot as plt

def processar_imagem(nome_imagem, parametros):
    """
    Processa a imagem com base nos parâmetros fornecidos.
    
    :param nome_imagem: Nome do arquivo da imagem.
    :param parametros: Dicionário com os parâmetros específicos para a análise.
    """
    # Importa e converte para RGB
    img = cv2.imread(nome_imagem)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Converte para escala de cinza
    img_gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    a = img_gray.max()

    # Calcula o limiar de binarização (suporta valores fixos ou funções)
    limiar_binarizacao = parametros['limiar_binarizacao'](a) if callable(parametros['limiar_binarizacao']) else parametros['limiar_binarizacao'] * a

    # Binariza a imagem com limiar adaptado
    _, thresh = cv2.threshold(
        img_gray, 
        limiar_binarizacao, 
        a, 
        cv2.THRESH_BINARY_INV
    )

    # Define o kernel
    tamanhoKernel = parametros['tamanho_kernel']
    kernel = np.ones((tamanhoKernel, tamanhoKernel), np.uint8)

    # Operações morfológicas adicionais (se aplicável)
    if parametros.get('usar_morfologia', False):
        img_close = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)
        img_dilate = cv2.dilate(img_close, kernel, iterations=2)
        img_open = cv2.morphologyEx(img_dilate, cv2.MORPH_OPEN, kernel, iterations=1)
        thresh_open = img_open  # Atualiza o thresh_open para usar a imagem processada
    else:
        thresh_open = thresh

    # Aplica desfoque (blurring)
    img_blur = cv2.blur(img_gray, ksize=(tamanhoKernel, tamanhoKernel))

    # Detecção de bordas com Canny
    edges_gray = cv2.Canny(
        image=img_gray, 
        threshold1=parametros['canny_threshold1'] * a, 
        threshold2=parametros['canny_threshold2'] * a
    )
    edges_blur = cv2.Canny(
        image=img_blur, 
        threshold1=parametros['canny_threshold1'] * a, 
        threshold2=parametros['canny_threshold2'] * a
    )

    # Encontra contornos
    contours, _ = cv2.findContours(
        image=thresh_open,
        mode=cv2.RETR_EXTERNAL if parametros.get('usar_morfologia', False) else cv2.RETR_TREE,
        method=cv2.CHAIN_APPROX_SIMPLE
    )

    # Ordena os contornos por área (decrescente)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    # Cria uma cópia da imagem para desenhar os contornos filtrados
    img_copy = img.copy()

    # Filtra e desenha apenas contornos com área dentro da faixa desejada (se aplicável)
    if 'area_min' in parametros and 'area_max' in parametros and parametros['area_min'] is not None and parametros['area_max'] is not None:
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if parametros['area_min'] < area < parametros['area_max']:
                cv2.drawContours(img_copy, [cnt], -1, (255, 0, 0), 2)
    else:
        # Desenha todos os contornos se área mínima e máxima não forem especificadas
        cv2.drawContours(img_copy, contours, -1, (255, 0, 0), 2)

    # Cria a imagem final com os contornos desenhados
    final = img_copy.copy()

    # Lista de imagens para visualização
    imagens = [img, img_blur, img_gray, edges_gray, edges_blur, thresh, thresh_open, final]
    formatoX = math.ceil(len(imagens) ** 0.5)
    formatoY = formatoX if (formatoX ** 2 - len(imagens)) <= formatoX else formatoX - 1

    # Plot das imagens intermediárias
    plt.figure(figsize=(18, 12))
    for i in range(len(imagens)):
        plt.subplot(formatoY, formatoX, i + 1)
        plt.imshow(imagens[i], cmap='gray' if len(imagens[i].shape) == 2 else None)
        plt.xticks([]), plt.yticks([])

    # Salvar todas as imagens intermediárias em um só PNG
    pasta_saida = nome_imagem.split('/')[0]  # Extrai a pasta da imagem
    plt.tight_layout()
    plt.savefig(f'./{pasta_saida}/contornando_{nome_imagem.split("/")[-1].split(".")[0].lower()}.png', dpi=300, bbox_inches='tight')
    plt.show()

    # Salvar imagem final com contornos
    output_path = f'./{pasta_saida}/contorno_{nome_imagem.split("/")[-1].split(".")[0].lower()}.png'
    cv2.imwrite(output_path, cv2.cvtColor(final, cv2.COLOR_RGB2BGR))


# Parâmetros específicos para cada imagem
parametros_girafa = {
    'limiar_binarizacao': 10,
    'tamanho_kernel': 5,
    'canny_threshold1': 0.5,
    'canny_threshold2': 0.5,
    'area_min': None,
    'area_max': None
}

parametros_aviao = {
    'limiar_binarizacao': 0.4,
    'tamanho_kernel': 5,
    'canny_threshold1': 0.5,
    'canny_threshold2': 0.5,
    'area_min': 5000,
    'area_max': 100000,
    'usar_morfologia': True  # Indica que operações morfológicas adicionais devem ser usadas
}

parametros_satelite = {
    'limiar_binarizacao': lambda a: (a * 50) * 0.3,  # Ajuste do limiar de binarização
    'tamanho_kernel': 5,
    'canny_threshold1': 0.5,
    'canny_threshold2': 0.5,
    'area_min': 500,
    'area_max': 20000
}

# Processa cada imagem com seus respectivos parâmetros
processar_imagem('Analise_Girafa/Girafa.jpeg', parametros_girafa)
processar_imagem('Analise_Aviao/Aviao.jpeg', parametros_aviao)
processar_imagem('Analise_Satelite/Satelite.jpeg', parametros_satelite)