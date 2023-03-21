import pandas as pd
import numpy as np
import cv2 as cv
from auxilio.variaveis import posicao_caixas_temp1 as pct1, dicionario_simulinho as ds
from auxilio.funcoes_auxiliares import four_point_transform, sort_contornos


def get_template(template_):

    cordenadas_template = []

    template = template_
    cinza = cv.cvtColor(template, cv.COLOR_BGR2GRAY)
    borrada = cv.GaussianBlur(cinza, (33, 33), 0)
    divide = cv.divide(cinza, borrada, scale=255)
    thresh = cv.threshold(divide, 0, 255, cv.THRESH_BINARY_INV + cv.THRESH_OTSU)[1]

    cnts, _ = cv.findContours(thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    for c in cnts:
        # Bounding Rect e medidas (posiX, posiY, Largura, Altura)
        x,y,w,h = cv.boundingRect(c)
        area_rect = w*h 
        approx = cv.approxPolyDP(c, 0.01*cv.arcLength(c, True),True)

        # Filtra para selecionar apenas os quadrados pretos das pontas
        if (len(approx) == 4) and (0.9 <= (w / h) <= 1.1) and (area_rect > 600):

            ####
            # print(area_rect)
            ####

            # Centroide
            M = cv.moments(c)
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])

            # Desenho rect + centro (DEBUG)
            # cv.rectangle(template,(x,y),(x+w,y+h),(36,255,12),1)
            # cv.circle(template, (cX, cY), 10, (320, 159, 22), 1)

            # Cordenadas para cortar a foto e pegar apenas a folha centralizada
            cordenadas_template.append((cX, cY))


    folha_cortada = four_point_transform(template, cordenadas_template)

    ### DEBUG
    # cv.namedWindow("TEMPLATE CORTADO", cv.WINDOW_KEEPRATIO)
    # cv.imshow("TEMPLATE CORTADO", folha_cortada)
    # cv.waitKey(0)
    # cv.destroyAllWindows()
    ### DEBUG

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

        # box = morph[645:984, 15:230]
        #         x1, y1  x2, y2  ->  y1, y2    x1, x2
        # template 55:686 353:1043 -> [686:1043, 55:353]
        cnts, _ = cv.findContours(morph, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)


        ### DEBUG
        # cv.namedWindow("threshold-TEMPLATE", cv.WINDOW_KEEPRATIO)
        # cv.namedWindow("morph1-TEMPLATE", cv.WINDOW_KEEPRATIO)
        # cv.namedWindow("morph2-TEMPLATE", cv.WINDOW_KEEPRATIO)
        # cv.namedWindow("divide-TEMPLATE", cv.WINDOW_KEEPRATIO)
        # cv.namedWindow("borrada-TEMPLATE", cv.WINDOW_KEEPRATIO)
        # cv.imshow("threshold-TEMPLATE", adapt_thresh)
        # cv.imshow("morph1-TEMPLATE", morph)
        # cv.imshow("morph2-TEMPLATE", morph2)
        # cv.imshow("divide-TEMPLATE", divide)
        # cv.imshow("borrada-TEMPLATE", borrada)
        ### DEBUG

        for c in cnts:

            peri = cv.arcLength(c, True)
            approx = cv.approxPolyDP(c, 0.01 * peri, True)
            area = cv.contourArea(c)

            # print(area)
            if (len(approx) > 5) and (len(approx) < 30) and (300 < area < 500) and raio < 15:

                (x, y), raio = cv.minEnclosingCircle(c)
                centro = (int(x+pct1[caixa][2]), int(y+pct1[caixa][0]))

                ### DEBUG
                raio = int(raio)
                # print(raio)
                # print(centro)
                # print(area)
                # cv.circle(folha2, centro, raio, (0, 255, 100), 1)
                # cv.drawContours(folha2, c, -1, (0,0,255), 1)
                # print("CONTORNOS: ", len(contornos))
                ### DEBUG
                lista_posicoes.append(centro)

        lista_posicoes = sort_contornos(lista_posicoes)
        lista_posicoes_final.append(lista_posicoes)


    ### DEBUG
    # cv.namedWindow("TEMPLATE-RESPOSTAS", cv.WINDOW_KEEPRATIO)
    # cv.imshow("TEMPLATE-RESPOSTAS", folha2)
    # cv.waitKey(0)
    # cv.destroyAllWindows()
    ### DEBUG

    #### RETORNA RAIO, USANDO RAIO 11 PARA TESTAR
    return lista_posicoes_final, 11

