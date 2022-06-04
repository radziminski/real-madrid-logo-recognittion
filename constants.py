import numpy as np

neighbors = np.array(
    [(-1, -1), (0, -1), (1, -1), (1, 0), (-1, 1), (0, 1), (1, 1)])
extended_neighbors = np.array([(-2, -1), (-2, 0), (-2, 1), (-1, -2), (0, -2), (1, -2), (2, -1), (2, 0),
                               (2, 1), (-1, 2), (0, 2), (1, 2), (-1, -1), (0, -1), (1, -1), (1, 0), (-1, 1), (0, 1), (1, 1)])
merge_threshold = -3
