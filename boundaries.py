class Boundaries:
    def __init__(self, min_width=1000, min_height=1000, max_width=0, max_height=0):
        self.min_width = min_width
        self.min_height = min_height
        self.max_width = max_width
        self.max_height = max_height
        self.seen_pixels = []

    def getArea(self):
        width = self.max_width - self.min_width
        height = self.max_height - self.min_height
        return width * height

    def getRatio(self):
        width = self.max_width - self.min_width
        height = self.max_height - self.min_height
        if width == 0:
            return 10000
        return height / width

    def get_width(self):
        return self.max_width - self.min_width

    def get_height(self):
        return self.max_height - self.min_height

    def get_dimensions(self):
        return self.max_width - self.min_width, self.max_height - self.min_height

    def check_pixel(self, pixel):
        width, height = pixel
        self.max_width = max(self.max_width, width)
        self.min_width = min(self.min_width, width)
        self.max_height = max(self.max_height, height)
        self.min_height = min(self.min_height, height)

    def compare(self, compare_boundaries):
        return (self.min_width == compare_boundaries.min_width) and (self.min_height == compare_boundaries.min_height) \
            and (self.max_width == compare_boundaries.max_width) and (self.max_height == compare_boundaries.max_height)

    def apply_to_image(self, image):
        return image[self.min_width:self.max_width, self.min_height:self.max_height]


MERGE_THRESHOLD = -6


def merge_boundaries(rect1: Boundaries, rect2: Boundaries):
    min_width = min(rect1.min_width, rect2.min_width)
    min_height = min(rect1.min_height, rect2.min_height)
    max_width = max(rect1.max_width, rect2.max_width)
    max_height = max(rect1.max_height, rect2.max_height)

    return Boundaries(min_width, min_height, max_width, max_height)


def do_overlap_in_1d(xmin1, xmin2, xmax1, xmax2):
    return ((xmax1 - xmin2) >= MERGE_THRESHOLD) and ((xmax2 - xmin1) >= MERGE_THRESHOLD)


def do_overlap(rect1: Boundaries, rect2: Boundaries):
    return do_overlap_in_1d(rect1.min_width, rect2.min_width, rect1.max_width, rect2.max_width) and \
        do_overlap_in_1d(rect1.min_height, rect2.min_height,
                         rect1.max_height, rect2.max_height)


def check_has_valid_ratio(boundaries: Boundaries):
    ratio = boundaries.getRatio()
    return ratio <= 1.1 and ratio > 0.4


def merge_overlapping_boundaries(boundariesList):
    curr_results = boundariesList.copy()
    did_merge = True
    max_merges = 2
    i = 0
    while did_merge:
        results = []
        did_merge = False
        for boundaries in curr_results:
            for compare_boundaries in curr_results:
                if boundaries == compare_boundaries:
                    continue
                if do_overlap(boundaries, compare_boundaries):
                    did_merge = True
                    new_boundaries = merge_boundaries(
                        boundaries, compare_boundaries)
                    if (not any(other.compare(boundaries) for other in results)):
                        results.append(new_boundaries)

            if not any(other.compare(boundaries) or do_overlap(other, boundaries) for other in results):
                results.append(boundaries)

        curr_results = results.copy()
        if max_merges > 2:
            break
        i += 1

    return filter(check_has_valid_ratio, curr_results)
