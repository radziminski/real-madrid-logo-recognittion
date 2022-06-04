import cv2
import numpy as np
import time
import math
from file_utils import *
from image_utils import *
IMAGES_DIR = './images'
OUTPUTS_DIR = './outputs'


class Rect:
    def __init__(self, start, end):
        self.start = start
        self.end = end
        self.overlaps = False


def merge_rects(rect1: Rect, rect2: Rect):
    min_width = min(rect1.start[0], rect1.end[0],
                    rect2.start[0], rect2.end[0])
    min_height = min(rect1.start[1], rect1.end[1],
                     rect2.start[1], rect2.end[1])
    max_width = max(rect1.start[0], rect1.end[0],
                    rect2.start[0], rect2.end[0])
    max_height = max(rect1.start[1], rect1.end[1],
                     rect2.start[1], rect2.end[1])

    return Rect((min_width, min_height), (max_width, max_height))


def doOverlap(rect1: Rect, rect2: Rect):
    start1 = rect1.start
    end1 = rect1.end
    start2 = rect2.start
    end2 = rect2.end

    start1x, start1y = start1
    end1x, end1y = end1
    start2x, start2y = start2
    end2x, end2y = end2

    # To check if either rectangle is actually a line
    # For example  :  l1 ={-1,0}  r1={1,1}  l2={0,-1}  r2={0,1}

    # If one rectangle is on left side of other
    if (start1x >= end2x or start2x >= end1x):
        return False

    # If one rectangle is above other
    if (end1y >= start2y or end2y >= start1y):
        return False

    return True


class DetectedObject:
    def __init__(self, first_pixel, id):
        self.pixels = np.array([first_pixel], tuple)
        self.id = id

    def check_pixel(self, pixel):
        width, height = pixel

        near_pixels = self.pixels[abs(self.pixels[:, 0] - width < 2)]

        for my_pixel in near_pixels:
            my_width, my_height = my_pixel
            if (math.pow(width - my_width, 2) + math.pow(height - my_height, 2)) < 9:
                new_pixel = (width, height)
                self.pixels = np.append(self.pixels, [new_pixel], axis=0)
                return True

        return False


class Boundaries:
    def __init__(self, max_width, max_height):
        self.min_width = max_width
        self.min_height = max_height
        self.max_width = 0
        self.max_height = 0
        self.seen_pixels = []

    def getArea(self):
        width = self.max_width - self.min_width
        height = self.max_height - self.min_height
        return width * height

    def is_seen_pixel(self, pixel):
        width, height = pixel
        for pixel in self.seen_pixels:
            if (width == pixel[0]) and (height == pixel[1]):
                return True

        return False

    def mark_seen_pixel(self, pixel):
        self.seen_pixels.append(pixel.copy())

    def check_pixel(self, pixel):
        width, height = pixel
        if width > self.max_width:
            self.max_width = width
        if width < self.min_width:
            self.min_width = width
        if height > self.max_height:
            self.max_height = height
        if height < self.min_height:
            self.min_height = height


def rec_check(img, pixel, boundaries: Boundaries):
    width, height = pixel
    if (width < 0) or (width >= img.shape[0]):
        return
    if (height < 0) or (height >= img.shape[1]):
        return

    if not any(img[width, height]):
        return

    if width > boundaries.max_width:
        boundaries.max_width = width
    if width < boundaries.min_width:
        boundaries.min_width = width
    if height > boundaries.max_height:
        boundaries.max_height = height
    if height < boundaries.min_height:
        boundaries.min_height = height

    neighbors = [[width + 1, height], [width - 1, height],
                 [width, height + 1], [width, height - 1]]

    for pix in neighbors:
        if not boundaries.is_seen_pixel(pix) and any(img[pix[0], pix[1]]):
            boundaries.mark_seen_pixel(pix)
            rec_check(img, pix, boundaries)


class Region:
    def __init__(self, id):
        self.region_id = id


def process_colors(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    width, height, colors = img.shape

    start_time = time.time()

    # color separation
    for line in range(width):
        for pixel in range(height):
            hue = img[line, pixel, 0]
            sat = img[line, pixel, 1]
            val = img[line, pixel, 2]
            y_correct_hue = (hue < 26 and hue > 11)
            y_correct_sat = sat > 20
            y_correct_val = val > 65
            not_yellow_condition = (not y_correct_hue) or (
                not y_correct_sat) or (not y_correct_val)
            r_correct_hue = (hue < 182 and hue > 172)
            r_correct_sat = sat > 40
            r_correct_val = val > 35
            not_red_condition = (not r_correct_hue) or (
                not r_correct_sat) or (not r_correct_val)

            if not_red_condition and not_yellow_condition:
                img[line, pixel] = [0, 0, 0]
            else:
                img[line, pixel] = [250, 255, 255]

    print("--- Color separation completed in %s seconds ---" %
          (time.time() - start_time))
    found_objects = np.array([], DetectedObject)

    id = 0

    valid_pixels = {}

    region_id = 0
    neighbors = [(-1, -1), (0, -1), (1, -1), (1, 0), (-1, 1), (0, 1), (1, 1)]

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
    color = (30, 100, 200)
    thickness = 1
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

        if (boundaries.getArea() > minimal_area):
            found_regions.append(boundaries)

    for boundaries in found_regions:
        for compare in found_regions:
            None
    for boundaries in found_regions:
        start_point = (boundaries.min_height, boundaries.min_width)
        end_point = (boundaries.max_height, boundaries.max_width)
        img = cv2.rectangle(img, start_point, end_point, color, thickness)

    img = cv2.cvtColor(img, cv2.COLOR_HSV2BGR)
    return img

    # OLD segmentation
    for line in range(width):
        for pixel in range(height):
            if np.sum(img[line, pixel]) < 20:
                continue

            belongs_to_any_object = False
            for found_object in found_objects:
                if found_object.check_pixel((line, pixel)):
                    belongs_to_any_object = True

            if not belongs_to_any_object:
                found_objects = np.append(
                    found_objects, DetectedObject((line, pixel), id))
                id = id + 1

    print(found_objects)
    print("--- Segmentation completed in %s seconds ---" %
          (time.time() - start_time))
    print(f"Identified: {len(found_objects)} objects")

    img = cv2.cvtColor(img, cv2.COLOR_HSV2BGR)

    rects = []

    i = 0
    for found_object in found_objects:
        i = i + 32
        temp = found_object.pixels.T
        print(temp)
        min_height = min(temp[0])
        max_height = max(temp[0])
        min_width = min(temp[1])
        max_width = max(temp[1])

        start_point = (min_width, min_height)
        end_point = (max_width, max_height)

        rects.append(Rect(start_point, end_point))

        # print(min_width, max_width)
        # print(min_height, max_height)

        # start_point = (min_width, min_height)

        # # Ending coordinate, here (220, 220)
        # # represents the bottom right corner of rectangle
        # end_point = (max_width, max_height)

        # j = 128 + i
        # # Blue color in BGR
        # color = (j, j/2, j*2)

        # # Line thickness of 2 px
        # thickness = 1

        # # Using cv2.rectangle() method
        # # Draw a rectangle with blue line borders of thickness of 2 px
        # img = cv2.rectangle(img, start_point, end_point, color, thickness)

    merged_rects = []

    for i in range(len(rects)):
        for j in range(i + 1, len(rects)):
            rect = rects[i]
            rect2 = rects[j]

            if doOverlap(rect, rect2):
                print('overlaps!')
                rect.overlaps = True
                rect2.overlaps = True
                new_rec = merge_rects(rect, rect2)
                merged_rects.append(merge_rects(rect, rect2))

    color = (30, 100, 200)

    # Line thickness of 2 px
    thickness = 1

    # Using cv2.rectangle() method
    # Draw a rectangle with blue line borders of thickness of 2 px

    print(merge_rects)
    for rect in merged_rects:
        print('printing overlaped')
        img = cv2.rectangle(img, rect.start, rect.end, color, thickness)

    for rect in rects:
        if not rect.overlaps:
            print('not overlaped')
            img = cv2.rectangle(img, rect.start, rect.end, color, thickness)

    print("--- Found objects processing completed in %s seconds ---" %
          (time.time() - start_time))

    return img


if __name__ == '__main__':
    start_time = time.time()

    images = load_images_from_folder(IMAGES_DIR)
    img_num = 0
    for img in images:
        img_num = img_num + 1
        while max(img.shape[0], img.shape[1]) > 500:
            img = cv2.resize(img, (0, 0), fx=0.8, fy=0.8)
        img = process_colors(img)
        cv2.imwrite(f'{OUTPUTS_DIR}/image-{img_num}.png', img)

    print("==> Program completed in %s seconds <==" %
          (time.time() - start_time))
