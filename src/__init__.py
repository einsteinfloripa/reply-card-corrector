import pandas as pd
import numpy as np
import cv2 as cv
from leitura_e_escrita.leitor import get_foto
from auxilio.template import (get_posicao_respostas_template,
                             get_template)
from auxilio.funcoes_auxiliares import (get_novas_posicoes,
                                        get_img,
                                        get_respostas,
                                        get_posicao_cpf_template)

# ## jogar para outro lugar
# from svglib.svglib import svg2rlg
# from reportlab.graphics import renderPM

# drawing = svg2rlg("/home/matos/Einstein/Vale/reply-card-corrector/reply_card_models/response_card_model_v4_SIMULINHO.svg")
# renderPM.drawToFile(drawing, "reply_card_models/modelo_SIMULINHO.png", fmt='PNG',)


#img_ = get_foto("/home/matos/Einstein/Vale/reply-card-corrector/scans/scan0003.pdf_1.jpg")
#img_ = get_foto("/home/matos/Einstein/Vale/reply-card-corrector/reply_card_models/SIMULINHO.jpg")
template_ = get_foto("/home/matos/Einstein/Vale/reply-card-corrector/reply_card_models/SIMULINHO.jpg")
img_ = get_foto("/home/matos/Einstein/Vale/reply-card-corrector/scans/1. Matheus (1 a 84)/3.jpg")
#template_ = get_foto("/home/matos/Einstein/Vale/reply-card-corrector/scans/1. Matheus (1 a 84)/4.jpg")

#template
template = get_template(template_)
posicao_respostas_template, raio = get_posicao_respostas_template(template)
posicao_cpf, raio = get_posicao_cpf_template(template)

img = get_img(img_, template_)
novas_posicoes = get_novas_posicoes(template, img, posicao_respostas_template, raio)

#lista_verificacao = get_respostas()

### remover

cinza = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
borrada = cv.GaussianBlur(cinza, (9, 9), 0)
# #divide = cv.divide(cinza, borrada, scale=255)

# # threshold
thresh = cv.threshold(borrada, 0, 255, cv.THRESH_BINARY_INV + cv.THRESH_OTSU)[1]
# adapt_thresh = cv.adaptiveThreshold(cinza, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY_INV, 5, 2)
# # apply morphology
kernel = cv.getStructuringElement(cv.MORPH_RECT, (15,15))
morph = cv.morphologyEx(thresh, cv.MORPH_OPEN, kernel)
img3 = morph

# cv.namedWindow("img2", cv.WINDOW_KEEPRATIO)
#cv.namedWindow("threshold", cv.WINDOW_KEEPRATIO)
# cv.namedWindow("morph", cv.WINDOW_KEEPRATIO)
# # cv.namedWindow("divide", cv.WINDOW_KEEPRATIO)
# # cv.namedWindow("borrada", cv.WINDOW_KEEPRATIO)
# cv.imshow("img2", img_)
#cv.imshow("threshold", thresh)
# cv.imshow("morph", morph)
# cv.imshow("borrada", borrada)


###
cv.namedWindow("mask1", cv.WINDOW_KEEPRATIO)
cv.namedWindow("IMG", cv.WINDOW_KEEPRATIO)
# cv.namedWindow("AREA ATIVA", cv.WINDOW_KEEPRATIO)
cv.namedWindow("IMG ANTES", cv.WINDOW_KEEPRATIO)
cv.namedWindow("MASCARA", cv.WINDOW_KEEPRATIO)
get_respostas(img3, novas_posicoes, raio)




# for linha in posicao_respostas_template:
#     nova_posicao_linha = []
#     for coordenada in linha:
#         nova_posicao = new_coordinates_after_resize_img(template.shape[0:2], folha_cortada.shape[0:2], coordenada)
#         nova_posicao_linha.append(nova_posicao)
#         ### DEBUG
#         cv.circle(folha_cortada, nova_posicao, raio-2, (320, 159, 22), 1)
#         ### DEBUG
#     novas_posicoes.append(nova_posicao_linha)


# for c in contornos_alternativas:
#     print(c)
#     print(c[0])
#     # c[0].x += x1
#     # c[0].y += y1
#     cv.drawContours(folha_cortada, c, -1, (0,0,255), 1)

cv.namedWindow("FOLHA CORTADA", cv.WINDOW_KEEPRATIO)
cv.imshow("FOLHA CORTADA",  img)
cv.waitKey(0)
cv.destroyAllWindows()