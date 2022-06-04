import cv2
import numpy as np
import time
from file_utils import *
from image_utils import *
from find_regions import find_regions
from constants import extended_neighbors
from color_name import get_color_name
from coefficients import Coefficients

IMAGES_DIR = './test-images'
OUTPUTS_DIR = './outputs'

sat_limit = 50
val_limit = 40
hue_lower_limit = 11
hue_upper_limit = 27


def threshold(input_img, binarize=False):
    img = cv2.cvtColor(input_img, cv2.COLOR_BGR2HSV)

    start_time = time.time()

    img[np.where(np.logical_not(np.logical_and(img > [hue_lower_limit, sat_limit, val_limit], img < [
                 hue_upper_limit, 255, 255]).all(axis=2)))] = 0

    img[np.where(np.logical_and(img > [hue_lower_limit, sat_limit, val_limit], img < [
        hue_upper_limit, 255, 255]).all(axis=2))] = 255

    print("--- Color thresholding completed in %s seconds ---" %
          (time.time() - start_time))

    return img


def erosion(input_img):
    img = input_img.copy()
    width, height, colors = img.shape

    start_time = time.time()

    for i in range(1, width - 2):
        for j in range(1, height - 2):
            if all((input_img[i + neighbor[0], j + neighbor[1]] != 0).all() for neighbor in extended_neighbors):
                img[i, j] = 0

    print("--- Erosion completed in %s seconds ---" %
          (time.time() - start_time))

    return img


def calculate_area(image):
    return np.sum(image[:, :, 0]) / 255


def calculate_params(image, edge_image):
    area = calculate_area(image)
    print(f'Area: {area}')

    for key, value in cv2.moments(image[:, :, 0]).items():
        print(f'{key}: {value} ({value / (image.shape[0] * image.shape[1])}')

    radius = calculate_area(edge_image)
    print(f'Radius: {radius}')

    area_to_box = calculate_area(image) / (image.shape[0] * image.shape[1])
    radius_squared_to_area = radius * radius / area
    return area_to_box, radius_squared_to_area


def process_colors(input_img, filename):
    img = threshold(input_img)

    img_threshold = img.copy()

    img = erosion(img)

    boundaries_list = find_regions(img)

    thickness = 1

    colors = [('red', (0, 0, 255)), ('green', (0, 255, 0), ),
              ('blue', (255, 0, 0)), ('white', (255, 255, 255)),
              ('lightblue', (255, 255, 0)), ('yellow', (0, 255, 255)),
              ('pink', (255, 0, 255)), ('purple', (255, 0, 128)),
              ('orange', (0, 128, 255))]
    color_id = 0
    colors = colors + colors + colors
    for boundaries in boundaries_list:
        color_name, color = colors[color_id]
        color_id += 1
        print(color_name)

        start_point = (boundaries.min_height, boundaries.min_width)
        end_point = (boundaries.max_height, boundaries.max_width)

        img_threshold = cv2.morphologyEx(
            img_threshold, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3)))

        image_region = boundaries.apply_to_image(img_threshold)
        image_region_edged = boundaries.apply_to_image(img)

        img_threshold = cv2.rectangle(
            img_threshold, start_point, end_point, color, thickness)

        b, g, r = cv2.split(image_region)
        coffs = Coefficients(b)
        coffs.write_to_file(f'{filename}-{color_name}.txt')
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
        # img = cv2.resize(img, (0, 0), fx=0.5, fy=0.5)
        img = process_colors(img, filename)
        cv2.imwrite(f'{OUTPUTS_DIR}/{filename}-processed.png', img)

        print(
            f"==> {filename} processed in {(time.time() - img_start_time)} seconds <==")

    print("==> Program completed in %s seconds <==" %
          (time.time() - start_time))
