import numpy as np

WHITE_PIXEL = 255
ALREADY_SEEN = 1
UNSEEN = -1


class BoundingBoxesExtractor:
    def __init__(self, image: np.ndarray, rows, cols):
        self.height = rows
        self.width = cols
        self.seen_pixels_cache = np.full((rows, cols), UNSEEN)
        self.image = image
        self.boxes = []

    def get_bounding_boxes(self):
        for i in range(1, self.height - 1):
            for j in range(1, self.width - 1):
                if self.seen_pixels_cache[i, j] != ALREADY_SEEN and self.image[i, j] == WHITE_PIXEL:
                    self.entry_point(i, j)

        return self.boxes

    def entry_point(self, y: int, x: int):
        pixels_to_see = [(y, x)]
        bounding_box = BoundingBox()
        while pixels_to_see:
            y, x = pixels_to_see.pop()
            if y == 0 or x == 0 or y == self.height - 1 or x == self.width - 1:
                pass
            if self.see_pixel(y, x, bounding_box):
                pixels_to_see.extend(
                    self.get_connected_neighbours_indexes(y, x))
        self.boxes.append(bounding_box)

    def see_pixel(self, y: int, x: int, box: BoundingBox):
        if self.image[y, x] != WHITE_PIXEL:
            self.seen_pixels_cache[y, x] = UNSEEN
            return False

        box.push_pixel(y, x, self.is_edge(y, x))
        self.seen_pixels_cache[y, x] = ALREADY_SEEN
        return True

    def get_connected_neighbours_indexes(self, y: int, x: int):
        if self.is_at_image_border(y, x):
            return []

        connected_neighbours_indexes = []
        neighbour_indexes = [(i, j) for i in range(y - 1, y + 2)
                             for j in range(x - 1, x + 2)]
        for neighbour_index in neighbour_indexes:
            if self.seen_pixels_cache[neighbour_index] == UNSEEN and self.image[neighbour_index] == WHITE_PIXEL:
                connected_neighbours_indexes.append(neighbour_index)

        return connected_neighbours_indexes

    def is_edge(self, y: int, x: int):
        if self.is_at_image_border(y, x):
            return False
        neighbour_pixels = [(i, j) for i in range(y - 1, y + 2)
                            for j in range(x - 1, x + 2)]
        for neighbour_pixel in neighbour_pixels:
            if self.image[neighbour_pixel] != WHITE_PIXEL:
                return True

        return False

    def is_at_image_border(self, y: int, x: int):
        return x <= 0 or x >= self.width - 1 or y <= 0 or y >= self.height - 1
