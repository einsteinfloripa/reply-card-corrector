from pathlib import Path
import pandas as pd
import cv2 as cv

def get_foto(path):

    foto_ = cv.imread(path)
    return foto_
