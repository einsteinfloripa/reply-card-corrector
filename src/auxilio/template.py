import pandas as pd
import numpy as np
import cv2 as cv
from auxilio.variaveis import posicao_caixas_temp1 as pct1, dicionario_simulinho as ds
from auxilio.funcoes_auxiliares import four_point_transform, sort_contornos, get_centro_e_raio_contorno


def get_template(template_):

    cordenadas_template = []

    template = template_
    cinza1 = cv.cvtColor(template, cv.COLOR_BGR2GRAY)
    borrada1 = cv.GaussianBlur(cinza1, (33, 33), 0)
    divide1 = cv.divide(cinza1, borrada1, scale=255)

    thresh = cv.threshold(divide1, 0, 255, cv.THRESH_BINARY_INV + cv.THRESH_OTSU)[1]

    cnts, hierarchy = cv.findContours(thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    for c in cnts:
        # Bounding Rect e medidas (posiX, posiY, Largura, Altura)
        x,y,w,h = cv.boundingRect(c)
        area_rect = w*h 
        approx = cv.approxPolyDP(c, 0.01*cv.arcLength(c, True),True)

        # Filtra para selecionar apenas os quadrados pretos das pontas
        if (len(approx) == 4) and (0.9 <= (w / h) <= 1.1) and (area_rect > 600):

            ####
            #print(area_rect)
            ####

            # Centroide
            M = cv.moments(c)
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])

            # Desenho rect + centro (DEBUG)
            cv.rectangle(template,(x,y),(x+w,y+h),(36,255,12),1)
            cv.circle(template, (cX, cY), 10, (320, 159, 22), 1)

            # Cordenadas para cortar a foto e pegar apenas a folha centralizada
            cordenadas_template.append((cX, cY))


    cv.namedWindow("TEMPLATE", cv.WINDOW_KEEPRATIO)
    cv.imshow("TEMPLATE", template)

    folha_cortada = four_point_transform(template, cordenadas_template)

    cv.namedWindow("TEMPLATE CORTADO", cv.WINDOW_KEEPRATIO)
    cv.imshow("TEMPLATE CORTADO", folha_cortada)

    # cv.waitKey(0)
    # cv.destroyAllWindows()

    return folha_cortada



def get_posicao_respostas_template(folha_alinhada):

    lista_posicoes_final = []
    folha2 = folha_alinhada

    for caixa in range(ds["Caixas"]["Quantidade"]):
        lista_posicoes = []

        #box1 = folha2[y1:y2, x1:x2]
        box = folha2[pct1[caixa][0]:pct1[caixa][1], pct1[caixa][2]:pct1[caixa][3]]
        cinza = cv.cvtColor(box, cv.COLOR_BGR2GRAY)
        borrada = cv.GaussianBlur(cinza, (9, 9), 0)
        divide = cv.divide(cinza, borrada, scale=255)
        adapt_thresh = cv.adaptiveThreshold(divide, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY_INV, 15, 2)
        kernel1 = cv.getStructuringElement(cv.MORPH_ELLIPSE, (7,7))
        kernel2 = cv.getStructuringElement(cv.MORPH_ELLIPSE, (3,3))
        morph = cv.morphologyEx(adapt_thresh, cv.MORPH_CLOSE, kernel1)
        #morph2 = cv.morphologyEx(adapt_thresh, cv.MORPH_OPEN, kernel2)

        #box2 = morph[645:984, 15:230]
        #         x1, y1  x2, y2  ->  y1, y2    x1, x2
        #template 55:686 353:1043 -> [686:1043, 55:353]
        cnts, _ = cv.findContours(morph, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

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


        for c in cnts:

            peri = cv.arcLength(c, True)
            approx = cv.approxPolyDP(c, 0.01 * peri, True)
            area = cv.contourArea(c)
            ### Arrumar aqui
            (x, y), raio = cv.minEnclosingCircle(c)

            #print(area)
            if (len(approx) > 5) and (len(approx) < 30) and (300 < area < 500) and raio < 15: # check if the contour is circle

                #contornos.append(c)

                ### DEBUG
                (x, y), raio = cv.minEnclosingCircle(c)

                centro = (int(x+pct1[caixa][2]), int(y+pct1[caixa][0]))
                raio = int(raio)
                # print(raio)
                # print(centro)
                # print(area)

                #cv.circle(folha2, centro, raio, (0, 255, 100), 1)
                #cv.drawContours(folha2, c, -1, (0,0,255), 1)
                #posicao.append(center)
                #print("CONTORNOS: ", len(contornos))
                lista_posicoes.append(centro)
                ### DEBUG

        lista_posicoes = sort_contornos(lista_posicoes)
        lista_posicoes_final.append(lista_posicoes)


    ### DEBUG
    cv.namedWindow("TEMPLATE-RESPOSTAS", cv.WINDOW_KEEPRATIO)
    cv.imshow("TEMPLATE-RESPOSTAS", folha2)
    cv.waitKey(0)
    cv.destroyAllWindows()

    #### RETORNA RAIO, USANDO RAIO 11 PARA TESTAR
    return lista_posicoes_final, 11



############################ ignorar daqui pra baixo ##################
def get_posicao_alternativas_template(contornos, teste1, alternativas = 5):

    ### DEBUG
    teste = teste1[686:1043, 55:353]
    ### DEBUG

    contornos_ordenados = []
    centros_alternativas = []
    raios_alternativas = []
    contornos = sort_contornos(contornos, "top-to-bottom")

    for (q, i) in enumerate(np.arange(0, len(contornos), alternativas)):

        ### DEBUG
        print(q, i)
        ### DEBUG

        contornos_linha = sort_contornos(contornos[i:i + alternativas], "left-to-right")
        for c in contornos_linha:
            centro, raio = get_centro_e_raio_contorno(c)
            centros_alternativas.append(centro)
            raios_alternativas.append(raio)
        contornos_ordenados.append(contornos_linha)

        ### DEBUG
        cv.drawContours(teste, contornos_linha, -1, (255,0,255), 1)
        cv.drawContours(teste1, contornos_linha, -1, (255,0,255), 1)
        cv.namedWindow("TESTE", cv.WINDOW_KEEPRATIO)
        cv.namedWindow("TESTE1", cv.WINDOW_KEEPRATIO)
        cv.imshow("TESTE", teste)
        cv.imshow("TESTE1", teste1)
        cv.waitKey(0)
        cv.destroyAllWindows()
        ### DEBUG
    lista_final = [item for sublist in contornos_ordenados for item in sublist]
    #print(len(lista_final))
    #return lista_final, centros_alternativas
    return centros_alternativas, raios_alternativas


    #cv.namedWindow("box2", cv.WINDOW_GUI_EXPANDED)
    #cv.imshow("box2", box2)

    cv.namedWindow("box1", cv.WINDOW_GUI_EXPANDED)
    cv.imshow("box1", box1)

    cv.namedWindow("adaptativo", cv.WINDOW_GUI_EXPANDED)
    cv.imshow("adaptativo", adapt_thresh)

    cv.namedWindow("morph", cv.WINDOW_GUI_EXPANDED)
    cv.imshow("morph", morph)

    cv.namedWindow("folha2", cv.WINDOW_KEEPRATIO)
    cv.imshow("folha2", folha2)

    cv.waitKey(0)
    cv.destroyAllWindows()

    # divide = cv.divide(cinza, borrada, scale=255)




    # # threshold
    # thresh = cv.threshold(divide, 100, 255, cv.THRESH_BINARY+cv.THRESH_OTSU)[1]
    # cv.namedWindow("thresh", cv.WINDOW_KEEPRATIO)
    # cv.imshow("borrada2", borrada)
    # cv.imshow("thresh", thresh)
    # #cv.imshow("thresh2", thresh)

    # # cv.waitKey(0)
    # cv.destroyAllWindows()

    return 10
