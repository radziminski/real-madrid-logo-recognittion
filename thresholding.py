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


def thresholding(input_img, params: ThresholdingParams = colors_set_1):
    sat_limit = params.sat_limit
    val_limit = params.val_limit
    hue_low_limit = params.hue_low_limit
    hue_high_limit = params.hue_high_limit

    img = cv2.cvtColor(input_img, cv2.COLOR_BGR2HSV)

    time = TimePassed("Thresholding")

    img[np.where(np.logical_not(np.logical_and(img > [hue_low_limit, sat_limit, val_limit], img < [
                 hue_high_limit, 255, 255]).all(axis=2)))] = [0, 0, 0]

    img[np.where(np.logical_and(img > [hue_low_limit, sat_limit, val_limit], img < [
        hue_high_limit, 255, 255]).all(axis=2))] = [255, 255, 255]

    time.finish()

    return img[:, :, 0]
