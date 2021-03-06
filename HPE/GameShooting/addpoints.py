#This program could detect human gestures using the input from the computer's camera.

import tensorflow as tf
import numpy as np
np.set_printoptions(suppress=True)
from matplotlib import pyplot as plt
import cv2
from PIL import Image
import random
from scipy.signal import convolve, convolve2d

def add_points(img, y, x, cc, points):
    im = img.copy()
    conc = cc
    cy = y
    cx = x
    while conc >= 0.4:
        print(conc)
        yc, xc, mc, pos, cd = add_one(im, cy, cx, conc)
        if mc >= conc or abs(cy-y) > 10 or abs(cx-x) > 10:
            break
        if mc < conc:
            pl = str([yc, xc])
            if pl not in points.keys():
                points[pl] = [0, 0, 0]
            points[pl][pos] += cd
            px = im[yc][xc][pos]
            im[yc][xc][pos] = px + cd
            conc = mc
        con = getConfidence(im)
        cy = int(con[0])
        cx = int(con[1])
    return im


def add_one(img, y, x, cc):
    minc = cc
    miny = y
    minx = x
    pos = 0
    cd = 0
    imarr = img.copy()
    for yc in range(y-5, y+6):
        for xc in range(x-5, x+6):
            for pid in range(0, 3):
                px = imarr[yc][xc][pid]
                if px < 255:
                    imarr[yc][xc][pid] = px + 1
                    con = getConfidence(imarr)
                    confidence = con[2]
                    if confidence < minc:
                        minc = confidence
                        miny = yc
                        minx = xc
                        pos = pid
                        cd = 1

                if px > 0:
                    imarr[yc][xc][pid] = px - 1
                    con = getConfidence(imarr)
                    confidence = con[2]
                    if confidence < minc:
                        minc = confidence
                        miny = yc
                        minx = xc
                        pos = pid
                        cd = -1

                imarr[yc][xc][pid] = px

    return miny, minx, minc, pos, cd



def getConfidence(img):
    im = img.copy()
    fr = im
    im = tf.image.resize_with_pad(np.expand_dims(im, axis=0), 192, 192)
    input_image = tf.cast(im, dtype=tf.float32)

    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    interpreter.set_tensor(input_details[0]['index'], np.array(input_image))
    interpreter.invoke()
    keypoints_with_scores = interpreter.get_tensor(output_details[0]['index'])
    y = fr.shape[0]
    x = fr.shape[1]
    shaped = np.squeeze(np.multiply(keypoints_with_scores, [y, x, 1]))
    return shaped[6]
img_path = '4.jpg'
interpreter = tf.lite.Interpreter(model_path='lite-model_movenet_singlepose_lightning_3.tflite')
interpreter.allocate_tensors()
frame = cv2.imread(img_path)
arr = getConfidence(frame)
points = {}
frame = add_points(frame, int(arr[0]), int(arr[1]), arr[2], points)
con = getConfidence(frame)
print(con[2])



# def gasuss_noise(image, mean=0, var=0.1):
#     image = np.array(image/255, dtype=float)
#     noise = np.random.normal(mean, var ** 0.5, image.shape)
#     out = image + noise
#     if out.min() < 0:
#         low_clip = -1.
#     else:
#         low_clip = 0.
#     out = np.clip(out, low_clip, 1.0)
#     out = np.uint8(out*255)
#     #cv.imshow("gasuss", out)
#     return out


#frame = gasuss_noise(frame, var=0.01)
with open('temp.txt', 'w') as f:
    for key in points.keys():
        f.write(str(key))
        f.write(': ')
        f.write(str(points[key]))
        f.write('\n')


cv2.imshow('Movenet Lightning', frame)
cv2.imwrite('6.jpg', frame)
cv2.waitKey()
