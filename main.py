import cv2
import numpy as np

from file_utils import *
from image_utils import *
from find_regions import find_regions
from constants import extended_neighbors
from color_name import get_color_name
from moments import Moments
from thresholding import thresholding
from kernels import get_cross_kernel, get_filled_kernel, get_star_kernel
from image_utils import get_sub_image
from time_passed import TimePassed
from validator import crown_validator_v1, emblem_validator_v1

IMAGES_DIR = './test-images'
OUTPUTS_DIR = './outputs'


def edge_detection(input_img):
    img = input_img.copy()
    width, height = img.shape
    kernel = get_star_kernel(5)

    time = TimePassed('Edge detection')

    for i in range(2, width - 3):
        for j in range(2, height - 3):
            if np.sum(get_sub_image(input_img, (i, j), 5) * kernel) == (255 * np.sum(kernel)):
                img[i, j] = 0

    time.finish()

    return img


def erode(input_img):
    img = input_img.copy()
    width, height = img.shape
    kernel = get_star_kernel(5)

    time = TimePassed('Erode')

    for i in range(2, width - 3):
        for j in range(2, height - 3):
            if img[i, j] == 0:
                continue
            if np.sum(get_sub_image(input_img, (i, j), 5) * kernel) < (0.25 * 255 * np.sum(kernel)):
                img[i, j] = 0

    time.finish()

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
    img = thresholding(input_img)

    img_threshold = img.copy()

    img = edge_detection(img)

    boundaries_list = find_regions(img)

    img = erode(img)
    img_edged = img.copy()

    thickness = 1

    red_color = ('red', (0, 0, 255))
    colors = [('green', (0, 255, 0), ),
              ('blue', (255, 0, 0)), ('white', (255, 255, 255)),
              ('lightblue', (255, 255, 0)), ('yellow', (0, 255, 255)),
              ('pink', (255, 0, 255)), ('purple', (255, 0, 128)),
              ('orange', (0, 128, 255))]

    color_id = 0
    colors = colors + colors + colors

    img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    for boundaries in boundaries_list:
        color_name, color = colors[color_id]
        color_id += 1
        print(color_name)

        img_threshold = cv2.morphologyEx(
            img_threshold, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3)))

        image_region = boundaries.apply_to_image(img_threshold)
        image_region_edged = boundaries.apply_to_image(img_edged)

        image_region_height, _ = image_region.shape

        crown_limit = int(image_region_height / 3)

        crown_region = image_region[0:crown_limit, :]
        emblem_region = image_region[crown_limit:, :]
        crown_region_edge = image_region_edged[0:crown_limit, :]
        emblem_region_edge = image_region_edged[crown_limit:, :]

        cv2.imwrite(f'curr_crown.png', crown_region)
        cv2.imwrite(f'curr_emblem.png', emblem_region)

        # coffs_edged = Moments(image_region_edged, image_region_edged)

        moments_crown = Moments(crown_region, crown_region_edge)
        moments_emblem = Moments(emblem_region, emblem_region_edge)
        moments_crown.save_file(f'params/{filename}-{color_name}-crown.txt')
        moments_emblem.save_file(f'params/{filename}-{color_name}-emblem.txt')

        # boundaries_limit = int(boundaries.get_width() / 3)
        # start_point_crown = (boundaries.min_height, boundaries.min_width)
        # end_point_crown = (boundaries.max_height,
        #                    boundaries.min_width + boundaries_limit)

        # start_point_emblem = (boundaries.min_height + 2,
        #                       boundaries.min_width + boundaries_limit - 2)
        # end_point_emblem = (boundaries.max_height + 2, boundaries.max_width)

        start_point = (boundaries.min_height - 2, boundaries.min_width - 2)
        end_point = (boundaries.max_height + 2, boundaries.max_width + 2)

        input_img = cv2.rectangle(
            input_img, start_point, end_point, color, thickness)

        is_crown_valid = crown_validator_v1.validate_moments(moments_crown)
        is_emblem_valid = emblem_validator_v1.validate_moments(moments_emblem)
        print(
            f'For {filename}-{color_name}: crown is {is_crown_valid}, emblem is {is_emblem_valid}')

        if is_crown_valid and is_emblem_valid:
            start_point = (boundaries.min_height - 5, boundaries.min_width - 5)
            end_point = (boundaries.max_height + 3, boundaries.max_width + 3)
            input_img = cv2.rectangle(
                input_img, start_point, end_point, (0, 0, 255), 3)

    return input_img


if __name__ == '__main__':
    program_time = TimePassed("Program")

    images = load_images_from_folder(IMAGES_DIR)
    img_num = 0
    for img, filename in images:
        print(f'\n--> Processing {filename}...')

        img_time = TimePassed(filename)
        img_num = img_num + 1

        while max(img.shape[0], img.shape[1]) > 1200:
            img = cv2.resize(img, (0, 0), fx=0.8, fy=0.8)

        img = process_colors(img, filename)
        cv2.imwrite(f'{OUTPUTS_DIR}/{filename}-processed.png', img)

        img_time.finish()

    program_time.finish()
