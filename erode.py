import numpy as np

from kernels import get_star_kernel
from image_utils import get_sub_image
from time_passed import TimePassed


def erode(input_img):
    img = input_img.copy()
    width, height = img.shape
    kernel = get_star_kernel(5)

    time = TimePassed('Erode')

    for i in range(2, width - 3):
        for j in range(2, height - 3):
            if img[i, j] == 0:
                continue
            if np.sum(get_sub_image(input_img, (i, j), 5) * kernel) < (0.25 * 255 * np.sum(kernel)):
                img[i, j] = 0

    time.finish()

    return img
