import json
import cv2 as cv
import matplotlib.pyplot as plt
import numpy as np
import math
import pytesseract
import os


def initAnalyse(imagePath):
    imagePath = os.path.abspath(imagePath)
    image = cv.imread(imagePath)

    # convert image into greyscale mode
    gray_image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)

    # find threshold of the image
    _, thrash = cv.threshold(gray_image, 240, 255, cv.THRESH_BINARY)
    contours, _ = cv.findContours(thrash, cv.RETR_TREE, cv.CHAIN_APPROX_NONE)
    i = 0
    banned = []

    con_base = []

    for contour in contours:
        i += 1
        if ((len(contour) > 300) and (len(contour) < 450)):
            shape = cv.approxPolyDP(contour, 0.01 * cv.arcLength(contour, True), True)
            x_cor = shape.ravel()[0]
            y_cor = shape.ravel()[1] - 15
            x, y, w, h = cv.boundingRect(shape)
            con_base.append((x, y))
            banned.append(i - 1)

    i = 0
    j = 0

    im2 = image.copy()
    kernel = np.ones((2, 2), np.uint8)
    im2 = cv.dilate(im2, kernel, iterations=1)
    crp = []
    whole = True
    text_pre = []
    con = []
    for contour in contours:
        i += 1
        if 10 < len(contour) < 300:
            if whole:
                x, y, w, h = cv.boundingRect(contour)
                if (w < 30):
                    whole = False
                    x -= 27
                    w += 27
                con.append((x, y))
                rect = cv.rectangle(im2, (x, y), (x + w, y + h), (0, 255, 0), 1)
                cropped = im2[y:y + h, x:x + w]
                gray = cv.cvtColor(cropped, cv.COLOR_BGR2GRAY)
                blur = cv.GaussianBlur(gray, (3, 3), 0)
                thresh = cv.threshold(blur, 0, 255, cv.THRESH_BINARY_INV + cv.THRESH_OTSU)[1]
                kernel = cv.getStructuringElement(cv.MORPH_RECT, (3, 3))
                opening = cv.morphologyEx(thresh, cv.MORPH_OPEN, kernel, iterations=1)
                invert = 255 - opening
                file = open("recognized.txt", "a")
                text = pytesseract.image_to_string(invert, lang='eng', config='--psm 6')
                crp.append(invert)
                text_pre.append(text);
                j += 1
            else:
                whole = True

    text_pre1 = []
    for a in text_pre:
        text_pre1.append(a[:2])

    text = []
    fs = False
    for a in text_pre1:
        s = ""

        if (a[:1] == '7'):
            s = 'z' + a[1:]
            fs = True

        if (a[:1] == 'i'):
            s = 'z' + a[1:]
            fs = True

        if (a[:1] == '¥'):
            s = 'y' + a[1:]
            fs = True

        if (a[:1] == 'Y'):
            s = 'y' + a[1:]
            fs = True

        if (a[:1] == 'X'):
            s = 'x' + a[1:]
            fs = True

        if (a[:1] == 'Z'):
            s = 'z' + a[1:]
            fs = True

        if (a[:1] == '¥'):
            s = 'y' + a[1:]
            fs = True

        if (a[1:] == '?'):
            if (fs):
                s = s[:1] + '2'
            else:
                s = a[:1] + '2'

        if (a[1:] == 'z'):
            if (fs):
                s = s[:1] + '2'
            else:
                s = a[:1] + '2'

        if (a[1:] == ']'):
            if (fs):
                s = s[:1] + '1'
            else:
                s = a[:1] + '1'

        if (s == ""):
            s = a
        if ((s[:1] != 'x') and (s[:1] != 'y') and (s[:1] != 'z')):
            s = "er"

        fs = False
        text.append(s)

    z = []
    for a, b in con:
        k = 0
        i = 0
        S = 99999
        for c, d in con_base:
            D = math.sqrt(math.pow(a - c, 2) + math.pow(b - d, 2))
            if (S > D):
                S = D
                k = i
            i += 1
        z.append(k)

    # треугольники шейп от 400 до 425
    # квадраты от 300 до 400
    # круг от 425(включая) до 450
    json_pre = {}
    j = 0
    for i in banned:
        if i:
            shape = cv.approxPolyDP(contours[int(i)], 0.01 * cv.arcLength(contours[int(i)], True), True)
            x, y, w, h = cv.boundingRect(shape)
            s = ""
            if 425 <= len(contours[int(i)]) < 450:
                s = "Circle"
            if 300 <= len(contours[int(i)]) < 400:
                s = "Rectangle"
            if 400 <= len(contours[int(i)]) < 425:
                s = "Triangle"
            for l in range(len(z)):
                if z[l] == j:
                    g = l
            json_pre[i] = [s, (int(x + w / 2), int(h / 2 + y)), text[g]]
            j += 1
    path = 'data.json'
    with open(path, 'w') as f:
        json.dump(json_pre, f)

    return path


#initAnalyse('shapes.jpg')
