import numpy as np


def get_sub_image(image: np.ndarray, center: tuple, size=3):
    assert size % 2 == 1
    x, y = center
    half_size = int(size / 2)
    assert half_size <= x
    assert half_size <= y
    start_x = x - half_size
    start_y = y - half_size
    end_x = x + half_size + 1
    end_y = y + half_size + 1
    return image[start_x:end_x, start_y:end_y]
