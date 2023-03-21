from pathlib import Path
import pandas as pd
import cv2 as cv
import re

def cpf_regex(frase):
    s = str(frase).split("/")
    s = re.search("[0-9]{1,3}", str(s[-1]))
    return int(s.group(0))



def get_foto(path):
    foto = cv.imread(str(path))
    return foto


def get_scans(path_pasta):
    lista_scans = []
    lista_nomes_arquivos = []
    paths = Path(path_pasta).glob('*')
    s = [str(path) for path in paths ]
    s = sorted(s, key = cpf_regex)
    for arquivo in sorted(s, key = cpf_regex):
        print(arquivo)
        foto = get_foto(arquivo)
        lista_scans.append(foto) 
        lista_nomes_arquivos.append(arquivo)
    return lista_scans, lista_nomes_arquivos

