import numpy as np


def get_filled_kernel(size=3):
    return np.ones([size, size], dtype=int)


def get_empty_kernel(size=3):
    return np.zeros([size, size], dtype=int)


def get_cross_kernel(size=3):
    assert size % 2 == 1

    if size == 3:
        return np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]])

    if size == 5:
        return np.array([[0, 0, 1, 0, 0], [0, 0, 1, 0, 0], [1, 1, 1, 1, 1], [0, 0, 1, 0, 0], [0, 0, 1, 0, 0]])


def get_star_kernel(size=3):
    assert size % 2 == 1

    if size == 3:
        return np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]])

    if size == 5:
        return np.array([[0, 0, 1, 0, 0], [0, 1, 1, 1, 0], [1, 1, 1, 1, 1], [0, 1, 1, 1, 0], [0, 0, 1, 0, 0]])
