import pandas as pd
import numpy as np
import cv2 as cv
from auxilio.variaveis import posicao_caixas_temp1 as pct1, dicionario_simulinho as ds
from auxilio.funcoes_auxiliares import four_point_transform, sort_contornos


def get_template(template_):

    cordenadas_template = []
    template = template_.copy()
    cinza = cv.cvtColor(template, cv.COLOR_BGR2GRAY)
    borrada = cv.GaussianBlur(cinza, (33, 33), 0)
    divide = cv.divide(cinza, borrada, scale=255)
    thresh = cv.threshold(divide, 0, 255, cv.THRESH_BINARY_INV + cv.THRESH_OTSU)[1]

    contornos, _ = cv.findContours(thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    for contorno in contornos:
        # Bounding Rect e medidas (posiX, posiY, Largura, Altura)
        x,y,w,h = cv.boundingRect(contorno)
        area_rect = w*h 
        approx = cv.approxPolyDP(contorno, 0.01*cv.arcLength(c, True),True)

        # Filtra para selecionar apenas os quadrados pretos das pontas
        if (len(approx) == 4) and (0.9 <= (w / h) <= 1.1) and (area_rect > 600):

            # Centroide
            M = cv.moments(contorno)
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])

            cordenadas_template.append((cX, cY))

    folha_cortada = four_point_transform(template, cordenadas_template)
    return folha_cortada



def get_posicao_respostas_template(folha_alinhada):

    lista_posicoes_final = []
    folha2 = folha_alinhada

    for caixa in range(ds["Caixas"]["Quantidade"]):
        lista_posicoes = []

        # box = folha[y1:y2, x1:x2] formato
        box = folha2[pct1[caixa][0]:pct1[caixa][1], pct1[caixa][2]:pct1[caixa][3]]
        cinza = cv.cvtColor(box, cv.COLOR_BGR2GRAY)
        borrada = cv.GaussianBlur(cinza, (9, 9), 0)
        divide = cv.divide(cinza, borrada, scale=255)
        adapt_thresh = cv.adaptiveThreshold(divide, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY_INV, 15, 2)
        kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, (7,7))
        morph = cv.morphologyEx(adapt_thresh, cv.MORPH_CLOSE, kernel)

        contornos, _ = cv.findContours(morph, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        for contorno in contornos:

            peri = cv.arcLength(contorno, True)
            approx = cv.approxPolyDP(contorno, 0.01 * peri, True)
            area = cv.contourArea(contorno)

            if (len(approx) > 5) and (len(approx) < 30) and (300 < area < 500) and raio < 15:

                (x, y), raio = cv.minEnclosingCircle(contorno)
                centro = (int(x+pct1[caixa][2]), int(y+pct1[caixa][0]))
                raio = int(raio)

                lista_posicoes.append(centro)

        lista_posicoes = sort_contornos(lista_posicoes)
        lista_posicoes_final.append(lista_posicoes)

    # TODO: Definir se o valor para o raio será um número pré-determinado ou não 
    # Usando raio = 11
    # return lista_posicoes_final, raio
    return lista_posicoes_final, 11

