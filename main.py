import cv2
import numpy as np

from edge_detection import edge_detection
from erode import erode
from file_utils import *
from image_utils import *
from find_regions import find_regions
from moments import Moments
from thresholding import thresholding, colors_set_2, colors_set_1
from image_utils import get_sub_image
from time_passed import TimePassed
from validator import validate_region

IMAGES_DIR = './test-images'
OUTPUTS_DIR = './outputs'


def closing(input_img):
    img = input_img.copy()
    width, height = img.shape

    for i in range(1, width - 2):
        for j in range(1, height - 2):
            if np.sum(get_sub_image(input_img, (i, j), 3)) > (3 * 255):
                img[i, j] = 255

    return img


def detect_real_madrid_logo(input_img, filename):
    img = thresholding(input_img)
    img_threshold = closing(img)

    img = edge_detection(img)

    boundaries_list = find_regions(img)

    img = erode(img)
    img_edged = img.copy()

    thickness = 1

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

        crown_moments = Moments(crown_region, crown_region_edge)
        emblem_moments = Moments(emblem_region, emblem_region_edge)
        crown_moments.save_file(f'params/{filename}-{color_name}-crown.txt')
        emblem_moments.save_file(f'params/{filename}-{color_name}-emblem.txt')

        start_point = (boundaries.min_height - 2, boundaries.min_width - 2)
        end_point = (boundaries.max_height + 2, boundaries.max_width + 2)

        input_img = cv2.rectangle(
            input_img, start_point, end_point, color, thickness)

        is_crown_valid, is_emblem_valid = validate_region(
            crown_moments, emblem_moments)

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
            img = cv2.resize(img, (0, 0), fx=0.7, fy=0.7)

        cv2.imwrite(f'inputs/{filename}', img)

        img = detect_real_madrid_logo(img, filename)
        cv2.imwrite(f'{OUTPUTS_DIR}/{filename}-processed.png', img)

        img_time.finish()

    program_time.finish()
