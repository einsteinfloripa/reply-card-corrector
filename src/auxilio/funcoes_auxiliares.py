import pandas as pd
import numpy as np
import cv2 as cv
from auxilio.variaveis import (dicionario_simulinho as ds,
                               alternativas,
                               cpf_digitos,
                               posicao_cpf)


def sort_contornos(lista_contornos, alternativas = ds["Caixas"]["Alternativas"], cpf = False):
    lista_final =[]

    # Região CPF
    if cpf == True:
        lista_ordenada_x = sorted(lista_contornos, key = lambda x: x[0])
        for digito, coluna in enumerate(np.arange(0, len(lista_ordenada_x), 10)):
            print(digito, coluna)
            lista_ordenada_y = sorted(lista_ordenada_x[coluna:coluna + 10],
                                      key = lambda y: y[1])
            lista_final.append(lista_ordenada_y)

    # Região Caixas
    elif cpf == False:
        lista_ordenada_y = sorted(lista_contornos, key = lambda y: y[1])
        for questao, centro in enumerate(np.arange(0, len(lista_ordenada_y), alternativas)):
            lista_ordenada_x = sorted(lista_ordenada_y[centro:centro + alternativas],
                                      key = lambda x: x[0])
            lista_final.append(lista_ordenada_x)

    return lista_final


def ordenar_cordenadas(pts):
    pts_array = np.array(pts, dtype = "float32")
    rect = np.zeros((4, 2), dtype = "float32")

    soma = pts_array.sum(axis = 1)
    rect[0] = pts_array[np.argmin(soma)]
    rect[2] = pts_array[np.argmax(soma)]

    diff = np.diff(pts_array, axis = 1)
    rect[1] = pts_array[np.argmin(diff)]
    rect[3] = pts_array[np.argmax(diff)]

    return rect


# Realiza transformação para alinhar a imagem com os quadrados
def four_point_transform(image, pts):

    rect = ordenar_cordenadas(pts)
    (tl, tr, br, bl) = rect

    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))

    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))

    dst = np.array([
        [0, 0],
	    [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
		[0, maxHeight - 1]], dtype = "float32")

    M = cv.getPerspectiveTransform(rect, dst)
    warped = cv.warpPerspective(image, M, (maxWidth, maxHeight))

    return warped


def new_coordinates_after_resize_img(original_size, new_size, original_coordinate):
    original_size = np.array(original_size)
    new_size = np.array(new_size)
    original_coordinate = np.array(original_coordinate)
    xy = original_coordinate/(original_size/new_size)
    x, y = int(xy[0]), int(xy[1])
    return (x, y)

# TODO: Remover ou Atualizar - Atualmente não utilizado
def get_centro_e_raio_contorno(c):
    x1 = 55 # Remover Depois
    x2 = 353
    y1 = 686
    y2 = 1043
    (x, y), raio = cv.minEnclosingCircle(c)
    center = (int(x+x1), int(y+y1))
    raio = int(raio)
    return center, raio

def get_novas_posicoes(template, folha, posicoes, raio):

    novas_posicoes = []
    for caixa in posicoes:
        for linha in caixa:
            nova_posicao_linha = []
            for coordenada in linha:
                    nova_posicao = new_coordinates_after_resize_img(template.shape[0:2], folha.shape[0:2], coordenada)
                    nova_posicao_linha.append(nova_posicao)
                    ### DEBUG
                    # cv.circle(folha, nova_posicao, raio-2, (320, 159, 22), 1)
                    ### DEBUG
            novas_posicoes.append(nova_posicao_linha)

    return novas_posicoes


def verificar_circulo(img, mask, coordenada):
    sample = mask[coordenada[1] - 3: coordenada[1] + 3, coordenada[0] - 3: coordenada[0] + 3]
    h, w = sample.shape
    if np.count_nonzero(sample) > h*w*6/10:
        #print("SIM") # debug
        return True
    else: 
        #print("NÃO") # debug
        return False

# TODO: Remover ou atualizar - Atualmente não utilizado
def verificar_alternativa(img, mask, coordenada, ):
    pass

def get_respostas(img1, lista_posicoes, raio):
    img = img1.copy()
    lista_respostas = []
    
    ### DEBUG
    # mask = np.zeros(img.shape[:2], dtype=np.uint8)
    # img = cv.bitwise_not(img)
    # cv.imshow("IMG ANTES", img)
    ### DEBUG

    for linha in lista_posicoes:
        lista_resposta_alternativa = []
        for coordenada in linha:
            mask = np.zeros(img.shape[:2], dtype=np.uint8)
            mask = cv.circle(mask, coordenada, raio-2, 255, -1)
            masked = cv.bitwise_and(img, img, mask = mask)
            verificacao = verificar_circulo(img, masked, coordenada)
            lista_resposta_alternativa.append(verificacao)

        if sum(lista_resposta_alternativa) != 1:
            lista_respostas.append('')
            print("Vazio/dupla marcação")
        else:
            index = lista_resposta_alternativa.index(True)
            resposta = alternativas[index]
            lista_respostas.append(resposta)

            ### DEBUG
            # cv.namedWindow("IMG", cv.WINDOW_KEEPRATIO)
            # cv.imshow("IMG", img)
            # #cv.imshow("MASCARA", masked)
            # cv.waitKey(0)
            # cv.destroyAllWindows()
            ### DEBUG

    return lista_respostas


# TODO: Realizar testes para definir os melhores parâmetros
def get_img(img_, template):
    cinza = cv.cvtColor(img_, cv.COLOR_BGR2GRAY)
    borrada = cv.GaussianBlur(cinza, (9, 9), 0)
    # divide = cv.divide(cinza, borrada, scale=255)

    # threshold
    thresh = cv.threshold(borrada, 0, 255, cv.THRESH_BINARY_INV + cv.THRESH_OTSU)[1]
    # adapt_thresh = cv.adaptiveThreshold(cinza, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY_INV, 5, 2)
    # apply morphology
    kernel = cv.getStructuringElement(cv.MORPH_RECT, (5,5))
    morph = cv.morphologyEx(thresh, cv.MORPH_OPEN, kernel)


    #### DEBUG
    # cv.namedWindow("GET IMAGE", cv.WINDOW_KEEPRATIO)
    # cv.namedWindow("threshold111", cv.WINDOW_KEEPRATIO)
    # cv.namedWindow("morph111", cv.WINDOW_KEEPRATIO)
    # cv.namedWindow("divide", cv.WINDOW_KEEPRATIO)
    # cv.namedWindow("borrada", cv.WINDOW_KEEPRATIO)
    # cv.imshow("GET IMAGE", img_)
    # cv.imshow("threshold111", thresh)
    # cv.imshow("morph111", morph)
    # cv.imshow("borrada", borrada)
    # cv.imshow("divide", divide)
    # cv.waitKey(0)
    # cv.destroyAllWindows()
    #### DEBUG

    cnts, _ = cv.findContours(morph, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    cordenadas = []

    for c in cnts:
        # Bounding Rect e medidas (posiX, posiY, Largura, Altura)
        x,y,w,h = cv.boundingRect(c)
        area_rect = w*h 
        approx = cv.approxPolyDP(c, 0.01*cv.arcLength(c, True), True)

        # Filtra para selecionar apenas os quadrados pretos das pontas
        if (len(approx) == 4) and (0.9 <= (w / h) <= 1.1) and (area_rect > 100):

            ### DEBUG
            # print(area_rect)
            # print(area_rect, approx)
            # print(c)
            ### DEBUG

            # Centroide
            M = cv.moments(c)
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])

            ### (DEBUG) Desenho rect + centro
            cv.rectangle(img_,(x,y),(x+w,y+h),(36,255,12),1)
            cv.circle(img_, (cX, cY), 10, (320, 159, 22), 1)

            # Cordenadas para cortar a foto e pegar apenas a folha centralizada
            cordenadas.append((cX, cY))

    folha_cortada = four_point_transform(img_, cordenadas)
    return folha_cortada


def get_posicao_cpf_template(template_alinhado):

    lista_posicoes_final = []
    lista_posicoes = []
    folha = template_alinhado.copy()

    # box = folha[y1:y2, x1:x2] - Formato
    box = folha[posicao_cpf[0]:posicao_cpf[1], posicao_cpf[2]:posicao_cpf[3]]
    cinza = cv.cvtColor(box, cv.COLOR_BGR2GRAY)
    borrada = cv.GaussianBlur(cinza, (9, 9), 0)
    divide = cv.divide(cinza, borrada, scale=255)
    adapt_thresh = cv.adaptiveThreshold(divide, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY_INV, 15, 2)
    kernel1 = cv.getStructuringElement(cv.MORPH_ELLIPSE, (3,3))

    # box2 = morph[645:984, 15:230]
    #         x1, y1  x2, y2  ->  y1, y2    x1, x2
    # template 55:686 353:1043 -> [686:1043, 55:353]
    cnts, _ = cv.findContours(adapt_thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    ### DEBUG
    # cv.namedWindow("threshold-CPF", cv.WINDOW_KEEPRATIO)
    # cv.namedWindow("morph1-CPF", cv.WINDOW_KEEPRATIO)
    # cv.namedWindow("morph2-TEMPLATE", cv.WINDOW_KEEPRATIO)
    # cv.namedWindow("divide-CPF", cv.WINDOW_KEEPRATIO)
    # cv.namedWindow("borrada-CPF", cv.WINDOW_KEEPRATIO)
    # cv.imshow("threshold-CPF", adapt_thresh)
    # cv.imshow("morph1-CPF", morph)
    # cv.imshow("morph2-TEMPLATE", morph2)
    # cv.imshow("divide-CPF", divide)
    # cv.imshow("borrada-CPF", borrada)
    ### DEBUG

    for c in cnts:

        peri = cv.arcLength(c, True)
        approx = cv.approxPolyDP(c, 0.01 * peri, True)
        area = cv.contourArea(c)

        ### Arrumar aqui
        (x, y), raio = cv.minEnclosingCircle(c)
        # print(area)
        # print(raio)

        if (300 < area < 500) and raio < 15:

            ### DEBUG
            centro = (int(x+posicao_cpf[2]), int(y+posicao_cpf[0]))
            raio = int(raio)
            # print(raio)
            # print(centro)
            # print(area)
            # cv.circle(folha, centro, raio, (0, 255, 100), 1)
            # cv.drawContours(folha2, c, -1, (0,0,255), 1)
            # posicao.append(center)
            # print("CONTORNOS: ", len(contornos))
            lista_posicoes.append(centro)
            ### DEBUG

    lista_posicoes = sort_contornos(lista_posicoes, cpf = True)
    lista_posicoes_final.append(lista_posicoes)

    ### DEBUG
    # cv.namedWindow("CPF", cv.WINDOW_KEEPRATIO)
    # cv.imshow("CPF", folha2)
    # cv.waitKey(0)
    # cv.destroyAllWindows()

    #### RETORNA RAIO, USANDO RAIO 11 PARA TESTAR
    return lista_posicoes_final, 11


def get_novas_posicoes_cpf(template, img, posicao_cpf, raio_cpf):
    novas_posicoes_cpf = []
    folha = img.copy()
    for caixa in posicao_cpf:
        for coluna in caixa:
            nova_posicao_coluna = []
            for digito in coluna:
                # print(digito)
                nova_posicao = new_coordinates_after_resize_img(template.shape[0:2], img.shape[0:2], digito)
                nova_posicao_coluna.append(nova_posicao)
                ### DEBUG
                # cv.circle(folha, nova_posicao, raio_cpf-2, (320, 159, 22), 1)
                ### DEBUG

            novas_posicoes_cpf.append(nova_posicao_coluna)

    ### REMOVER
    # cv.namedWindow("CPF-GETCPF", cv.WINDOW_KEEPRATIO)
    # cv.imshow("CPF-GETCPF", folha)
    # cv.waitKey(0)
    # cv.destroyAllWindows()
    return novas_posicoes_cpf

def get_cpf(img1, lista_posicoes, raio):
    img = img1.copy()
    cpf_aluno = []

    ## DEBUG
    # mask = np.zeros(img.shape[:2], dtype=np.uint8)
    # img = cv.bitwise_not(img)
    # cv.imshow("IMG ANTES", img)
    ## DEBUG

    for coluna in lista_posicoes:
        lista_digito_cpf = []
        # print(coluna, "COLUNA")
        for coordenada in coluna:
            # cv.namedWindow("CPF-ANTES", cv.WINDOW_KEEPRATIO)
            # cv.imshow("CPF-ANTES", img)
            mask = np.zeros(img.shape[:2], dtype=np.uint8)
            mask = cv.circle(mask, coordenada, raio-2, 255, -1)
            masked = cv.bitwise_and(img, img, mask = mask)
            verificacao = verificar_circulo(img, masked, coordenada)
            lista_digito_cpf.append(verificacao)

            ### DEBUG
            # cv.namedWindow("CPF-LEITURA", cv.WINDOW_KEEPRATIO)
            # cv.imshow("CPF-LEITURA", masked)
            # cv.waitKey(0)
            # cv.destroyAllWindows()
            ### DEBUG

        # print(lista_digito_cpf, "AQUI")
        if True in lista_digito_cpf:
            index = lista_digito_cpf.index(True)
            numero = cpf_digitos[index]
        else:
            numero = ''
        cpf_aluno.append(numero)

    return cpf_aluno







