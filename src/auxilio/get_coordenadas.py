import cv2 as cv
import numpy as np

def coordenadas(img_arg = None, caminho = None):
    if caminho != None:
        img = cv.imread(caminho)

    if img_arg is not np.array:
        img = img_arg

    def click_event(event, x, y, flags, params):
        if event == cv.EVENT_LBUTTONDOWN:
            print('Left Click')
            print(f'({x},{y})')

            cv.putText(img, f'({x},{y})', (x, y),   cv.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            cv.circle(img, (x, y), 3, (0, 0, 255), -1)
        if event == cv.EVENT_RBUTTONDOWN:
            print('Right Click')
            print(f'({x},{y})')
 
            cv.putText(img, f'({x},{y})', (x, y),
            cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
            cv.circle(img, (x, y), 3, (0, 0, 255), -1)


    cv.namedWindow('Point Coordinates')
    cv.setMouseCallback('Point Coordinates', click_event)

    while True:
        cv.imshow('Point Coordinates', img)
        k = cv.waitKey(1) & 0xFF
        if k == 27:
            break
    cv.destroyAllWindows()





# ## jogar para outro lugar
# from svglib.svglib import svg2rlg
# from reportlab.graphics import renderPM

# drawing = svg2rlg("/home/matos/Einstein/Vale/reply-card-corrector/reply_card_models/response_card_model_v4_SIMULINHO.svg")
# renderPM.drawToFile(drawing, "reply_card_models/modelo_SIMULINHO.png", fmt='PNG',)