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
    50, 175, 14, 27)  # best for sklep 1 i zawodnicy
colors_set_3 = ThresholdingParams(165, 170, 14, 24)  # best for sklep 4
colors_set_4 = ThresholdingParams(
    50, 210, 10, 20)  # best for sklep3 and sklep2


def BGR_to_HSV(input_img: np.array):
    height, width, _ = input_img.shape
    output = np.zeros(input_img.shape)

    max_val = 255
    for i in range(height):
        for j in range(width):
            blue = input_img[i, j][0] / max_val
            green = input_img[i, j][1] / max_val
            red = input_img[i, j][2] / max_val

            max_color = max(red, green, blue)
            min_color = min(red, green, blue)
            diff = max_color - min_color

            v = max_color
            multiplier = 60

            if diff == 0:
                h = 0
            elif max_color == red:
                h = (((green - blue) / diff) % 6) * multiplier
            elif max_color == green:
                h = (((blue - red) / diff) + 2) * multiplier
            elif max_color == blue:
                h = (((red - green) / diff) + 4) * multiplier

            if max_color == 0:
                s = 0
            else:
                s = diff / max_color

            colors = [int(h / 2), int(s * max_val), int(v * max_val)]

            output[i, j] = np.array(colors)

    return output


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
