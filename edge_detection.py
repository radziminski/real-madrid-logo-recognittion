import numpy as np

from kernels import get_star_kernel
from image_utils import get_sub_image
from time_passed import TimePassed


def edge_detection(input_img):
    img = input_img.copy()
    height, width = img.shape
    kernel = get_star_kernel(5)

    time = TimePassed('Edge detection')

    for i in range(2, height - 3):
        for j in range(2, width - 3):
            if np.sum(get_sub_image(input_img, (i, j), 5) * kernel) == (255 * np.sum(kernel)):
                img[i, j] = 0

    time.finish()

    return img
