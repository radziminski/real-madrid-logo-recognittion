import numpy as np

from image_utils import get_sub_image
from time_passed import TimePassed


def dilate(input_img):
    img = input_img.copy()
    height, width = img.shape

    time = TimePassed("Dilate")

    for i in range(1, height - 2):
        for j in range(1, width - 2):
            if np.sum(get_sub_image(input_img, (i, j), 3)) > (3 * 255):
                img[i, j] = 255

    time.finish()

    return img
