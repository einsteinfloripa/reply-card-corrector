import pandas as pd
import numpy as np
import cv2 as cv
from leitura_e_escrita.leitor import get_foto, get_scans
from leitura_e_escrita.escritor import escrever_csv
from auxilio.template import (get_posicao_respostas_template,
                             get_template)
from auxilio.funcoes_auxiliares import (get_novas_posicoes,
                                        get_img,
                                        get_respostas,
                                        get_posicao_cpf_template,
                                        get_novas_posicoes_cpf,
                                        get_cpf)
from auxilio.path import (ROOT_PATH, join_paths)

from auxilio.variaveis import nome_col_df_respostas

## Temporário
# TODO: Alterar posteriormente esse "import"
paths_pastas = [join_paths(ROOT_PATH, "scans", "1. Matheus (1 a 84)"),
                join_paths(ROOT_PATH, "scans", "2. Harumi (85 a 168)"),
                join_paths(ROOT_PATH,  "scans", "3. Laura (169 a 254)")]

template_path = join_paths(ROOT_PATH, "reply_card_models", "SIMULINHO.jpg")

# Template
template_arquivo = get_foto(template_path)
template = get_template(template_arquivo)
posicao_respostas_template, raio = get_posicao_respostas_template(template)
posicao_cpf, raio_cpf = get_posicao_cpf_template(template)
lista_respostas_final = []

# Scans
for pasta in paths_pastas:
    lista_scans, lista_nomes_arquivos = get_scans(pasta)

    for scan, nome_arquivo in zip(lista_scans, lista_nomes_arquivos):

        lista_respostas_aluno = []
        img = get_img(scan)

        nova_posicoes_cpf = get_novas_posicoes_cpf(template, img, posicao_cpf, raio_cpf)
        novas_posicoes = get_novas_posicoes(template, img, posicao_respostas_template, raio)

        print("------------------------")

        # CPF
        cinza1 = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        borrada1 = cv.GaussianBlur(cinza1, (9, 9), 0)
        thresh1 = cv.threshold(borrada1, 0, 255, cv.THRESH_BINARY_INV + cv.THRESH_OTSU)[1]
        kernel1 = cv.getStructuringElement(cv.MORPH_ELLIPSE, (17,17))
        morph1 = cv.morphologyEx(thresh1, cv.MORPH_OPEN, kernel1)
        img_cpf = morph1

        lista_cpf_aluno = get_cpf(img_cpf, nova_posicoes_cpf, raio_cpf)
        cpf_aluno = ''.join([digito for digito in lista_cpf_aluno])

        # RESPOSTAS
        cinza = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        borrada = cv.GaussianBlur(cinza, (9, 9), 0)
        thresh = cv.threshold(borrada, 0, 255, cv.THRESH_BINARY_INV + cv.THRESH_OTSU)[1]
        kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, (15,15))
        morph = cv.morphologyEx(thresh, cv.MORPH_OPEN, kernel)
        img_respostas = morph

        lista_respostas_aluno.append(cpf_aluno)
        lista_respostas_aluno.extend(get_respostas(img_respostas, novas_posicoes, raio))
        lista_respostas_final.append(lista_respostas_aluno)


        ## DEBUG
        print(nome_arquivo)
        print(lista_respostas_aluno)

        # cv.namedWindow("Final", cv.WINDOW_KEEPRATIO)
        # cv.namedWindow("Borrada", cv.WINDOW_KEEPRATIO)
        # cv.namedWindow("Thresh", cv.WINDOW_KEEPRATIO)
        # cv.namedWindow("", cv.WINDOW_KEEPRATIO)
        # cv.imshow("Final", morph)
        # cv.imshow("Borrada", borrada)
        # cv.imshow("Thresh", thresh)
        # cv.imshow("RESPOSTAS", morph)
        # cv.waitKey(0)
        # cv.destroyAllWindows()

        ## DEBUG

# TODO Melhorar implementação
df_final = pd.DataFrame(lista_respostas_final, columns = nome_col_df_respostas)
escrever_csv(df_final, join_paths(ROOT_PATH, "output", "respostas-alunos-teste.csv"))