import cv2
import numpy as np
from time_passed import TimePassed


class ThresholdingParams:
    def __init__(self, sat_limit, val_limit, hue_low_limit, hue_high_limit):
        self.sat_limit = sat_limit
        self.val_limit = val_limit
        self.hue_low_limit = hue_low_limit
        self.hue_high_limit = hue_high_limit


colors_set_1 = ThresholdingParams(50, 40, 11, 27)
colors_set_2 = ThresholdingParams(
    50, 180, 14, 27)  # best for sklep 1 i zawodnicy
colors_set_3 = ThresholdingParams(160, 170, 14, 24)  # bst for sklep 4
colors_set_4 = ThresholdingParams(
    50, 210, 10, 20)  # bst for sklep 3 and sklep2


def BGR_to_HSV(input_img):
    width, height, _ = input_img.shape
    output = np.zeros(input_img.shape, dtype=int)

    for i in range(width):
        for j in range(height):
            pixel = input_img[i, j]

            hsv = np.zeros(3, dtype=int)

            bgr_min = np.min(pixel)
            bgr_max = np.max(pixel)
            diff = (bgr_max - bgr_min)

            hsv[2] = bgr_max
            if bgr_max == 0:
                output[i, j] = hsv
                continue

            hsv[1] = 255 * diff / hsv[2]
            if hsv[1] == 0:
                output[i, j] = hsv
                continue

            multiplier = 43
            if bgr_max == pixel[2]:
                hsv[0] = 0 + multiplier * (int(pixel[1]) -
                                           int(pixel[0])) / diff
            elif bgr_max == pixel[1]:
                hsv[0] = 85 + multiplier * (int(pixel[0]) -
                                            int(pixel[2])) / diff
            else:
                hsv[0] = 171 + multiplier * (int(pixel[2]) -
                                             int(pixel[1])) / diff
            output[i, j] = hsv

    return output


def hsv2bgr(input_img):
    None


def thresholding(input_img, params: ThresholdingParams = colors_set_4):
    sat_limit = params.sat_limit
    val_limit = params.val_limit
    hue_low_limit = params.hue_low_limit
    hue_high_limit = params.hue_high_limit

    img = BGR_to_HSV(input_img)

    time = TimePassed("Thresholding")

    img[np.where(np.logical_not(np.logical_and(img > [hue_low_limit, sat_limit, val_limit], img < [
                 hue_high_limit, 255, 255]).all(axis=2)))] = [0, 0, 0]

    img[np.where(np.logical_and(img > [hue_low_limit, sat_limit, val_limit], img < [
        hue_high_limit, 255, 255]).all(axis=2))] = [255, 255, 255]

    time.finish()

    return img[:, :, 0]
