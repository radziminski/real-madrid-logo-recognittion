import numpy as np

from time_passed import TimePassed
from boundaries import Boundaries, merge_overlapping_boundaries
from constants import neighbors


def find_valid_pixels(input_img):
    img = input_img.copy()
    width, height = img.shape

    valid_pixels = {}
    region_id = 0

    for i in range(width - 1):
        for j in range(height - 1):
            if img[i, j] == 0:
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
                if img[i + neighbor[0], j + neighbor[1]] == 0:
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

    return valid_pixels, region_id


def find_regions(input_img):
    width, height = input_img.shape

    time = TimePassed('Regions separation')

    valid_pixels, regions_num = find_valid_pixels(input_img)

    inv_valid_pixels = {v: k for k, v in valid_pixels.items()}
    found_regions = []
    minimal_area = 0.002 * width * height

    for region in range(regions_num):
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
        has_valid_ratio = ratio <= 3 and ratio > 0.2

        if (boundaries.getArea() > minimal_area and has_valid_ratio):
            found_regions.append(boundaries)

    results = merge_overlapping_boundaries(found_regions)

    time.finish()

    return results
