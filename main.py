import cv2
import numpy as np
import time
import math
from file_utils import *
from image_utils import *
IMAGES_DIR = './test-images'
OUTPUTS_DIR = './outputs'

neighbors = [(-1, -1), (0, -1), (1, -1), (1, 0), (-1, 1), (0, 1), (1, 1)]
extended_neighbors = [(-2, -1), (-2, 0), (-2, 1), (-1, -2), (0, -2), (1, -2), (2, -1), (2, 0),
                      (2, 1), (-1, 2), (0, 2), (1, 2), (-1, -1), (0, -1), (1, -1), (1, 0), (-1, 1), (0, 1), (1, 1)]
merge_threshold = -3


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

    def check_pixel(self, pixel):
        width, height = pixel
        self.max_width = max(self.max_width, width)
        self.min_width = min(self.min_width, width)
        self.max_height = max(self.max_height, height)
        self.min_height = min(self.min_height, height)

    def compare(self, compare_boundaries):
        return (self.min_width == compare_boundaries.min_width) and (self.min_height == compare_boundaries.min_height) \
            and (self.max_width == compare_boundaries.max_width) and (self.max_height == compare_boundaries.max_height)


def merge_boundaries(rect1: Boundaries, rect2: Boundaries):
    min_width = min(rect1.min_width, rect2.min_width)
    min_height = min(rect1.min_height, rect2.min_height)
    max_width = max(rect1.max_width, rect2.max_width)
    max_height = max(rect1.max_height, rect2.max_height)

    return Boundaries(min_width, min_height, max_width, max_height)


def isOverlapping1D(xmin1, xmin2, xmax1, xmax2):
    return ((xmax1 - xmin2) >= merge_threshold) and ((xmax2 - xmin1) >= merge_threshold)


def do_overlap(rect1: Boundaries, rect2: Boundaries):
    return isOverlapping1D(rect1.min_width, rect2.min_width, rect1.max_width, rect2.max_width) and \
        isOverlapping1D(rect1.min_height, rect2.min_height,
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


def threshold(input_img, binarize=False):
    img = cv2.cvtColor(input_img, cv2.COLOR_BGR2HSV)
    width, height, colors = img.shape

    start_time = time.time()

    for i in range(width):
        for j in range(height):
            hue = img[i, j, 0]
            sat = img[i, j, 1]
            val = img[i, j, 2]
            y_correct_hue = (hue < 27 and hue > 11)
            y_correct_sat = sat > 50
            y_correct_val = val > 40
            not_yellow_condition = (not y_correct_hue) or (
                not y_correct_sat) or (not y_correct_val)
            r_correct_hue = (hue < 182 and hue > 172)
            r_correct_sat = sat > 40
            r_correct_val = val > 35
            not_red_condition = (not r_correct_hue) or (
                not r_correct_sat) or (not r_correct_val)

            if not_yellow_condition:
                img[i, j] = [0, 0, 0]
            elif binarize:
                img[i, j] = [250, 255, 255]

    print("--- Color thresholding completed in %s seconds ---" %
          (time.time() - start_time))

    return cv2.cvtColor(img, cv2.COLOR_HSV2BGR)


def erosion(input_img):
    img = input_img.copy()
    width, height, colors = img.shape

    start_time = time.time()

    for i in range(width - 2):
        for j in range(height - 2):
            if all(np.sum(input_img[i + neighbor[0], j + neighbor[1]]) != 0 for neighbor in ([(0, 0)] + extended_neighbors)):
                img[i, j] = [0, 0, 0]

    print("--- Erosion completed in %s seconds ---" %
          (time.time() - start_time))

    return img


def find_regions(input_img):
    img = input_img.copy()
    width, height, colors = img.shape
    seg_start_time = time.time()

    valid_pixels = {}
    region_id = 0

    for i in range(width - 1):
        for j in range(height - 1):
            if np.sum(img[i, j]) == 0:
                continue

            index = f'{i}_{j}'
            curr_region = None
            if not (index in valid_pixels):
                valid_pixels[index] = region_id
                curr_region = region_id
                region_id += 1
            else:
                curr_region = valid_pixels[index]

            for neighbor in neighbors:
                if np.sum(img[i + neighbor[0], j + neighbor[1]]) == 0:
                    continue
                neighbor_index = f'{i + neighbor[0]}_{j + neighbor[1]}'

                if not (neighbor_index in valid_pixels):
                    valid_pixels[index] = curr_region
                    continue

                if valid_pixels[neighbor_index] == curr_region:
                    continue

                for key in valid_pixels:
                    if key == neighbor_index:
                        continue
                    if valid_pixels[key] == valid_pixels[neighbor_index]:
                        valid_pixels[key] = curr_region

                valid_pixels[neighbor_index] = curr_region

    inv_valid_pixels = {v: k for k, v in valid_pixels.items()}
    found_regions = []
    minimal_area = 0.002 * width * height

    for region in range(region_id):
        if not region in inv_valid_pixels:
            continue

        boundaries = Boundaries(width, height)

        for pixel in valid_pixels:
            if (valid_pixels[pixel] != region):
                continue
            i, j = pixel.split('_')
            i = int(i)
            j = int(j)
            boundaries.check_pixel((i, j))

        ratio = boundaries.getRatio()
        has_valid_ratio = ratio <= 2 and ratio > 0.2
        if (boundaries.getArea() > minimal_area and has_valid_ratio):
            found_regions.append(boundaries)

    results = merge_overlapping_boundaries(found_regions)

    print("--- Region separation completed in %s seconds ---" %
          (time.time() - seg_start_time))

    return results


def process_colors(input_img):
    img = threshold(input_img)

    img_threshold = img.copy()

    img = erosion(img)
    boundaries_list = find_regions(img)

    color = (30, 100, 200)
    thickness = 1

    for boundaries in boundaries_list:
        start_point = (boundaries.min_height, boundaries.min_width)
        end_point = (boundaries.max_height, boundaries.max_width)
        img_threshold = cv2.rectangle(
            img_threshold, start_point, end_point, color, thickness)

    return img_threshold


if __name__ == '__main__':
    start_time = time.time()

    images = load_images_from_folder(IMAGES_DIR)
    img_num = 0
    for img, filename in images:
        img_start_time = time.time()
        img_num = img_num + 1
        # while max(img.shape[0], img.shape[1]) > 1000:
        #     img = cv2.resize(img, (0, 0), fx=0.95, fy=0.95)
        img = process_colors(img)
        cv2.imwrite(f'{OUTPUTS_DIR}/{filename}-processed.png', img)
        print(
            f"==> {filename} processed in {(time.time() - img_start_time)} seconds <==")

    print("==> Program completed in %s seconds <==" %
          (time.time() - start_time))
