import cv2
import numpy as np
from dilate import dilate
from draw_rectangle import draw_rectangle

from edge_detection import edge_detection
from erode import erode
from file_utils import *
from image_utils import *
from find_regions import find_regions
from moments import Moments
from thresholding import thresholding, colors_set_2, colors_set_1, colors_set_4, colors_set_3
from image_utils import get_sub_image
from time_passed import TimePassed
from validator import validate_region

IMAGES_DIR = './inputs'
OUTPUTS_DIR = './outputs'


def detect_real_madrid_logo(input_img, filename, colors=colors_set_1):
    img = thresholding(input_img, colors)
    img_threshold = dilate(img)

    img = edge_detection(img)

    boundaries_list = find_regions(img)

    img = erode(img)
    img_edged = img.copy()

    colors = [('green', (0, 255, 0), ),
              ('blue', (255, 0, 0)), ('white', (255, 255, 255)),
              ('lightblue', (255, 255, 0)), ('yellow', (0, 255, 255)),
              ('pink', (255, 0, 255)), ('purple', (255, 0, 128)),
              ('orange', (0, 128, 255))]

    color_id = 0
    colors = colors + colors + colors

    for boundaries in boundaries_list:
        color_name, color = colors[color_id]
        color_id += 1

        image_region = boundaries.apply_to_image(img_threshold)
        image_region_edged = boundaries.apply_to_image(img_edged)

        # Splitting into crown and emblem regions

        image_region_height, _ = image_region.shape
        crown_limit = int(image_region_height / 3)
        crown_region = image_region[0:crown_limit, :]
        emblem_region = image_region[crown_limit:, :]
        crown_region_edge = image_region_edged[0:crown_limit, :]
        emblem_region_edge = image_region_edged[crown_limit:, :]

        crown_moments = Moments(crown_region, crown_region_edge)
        emblem_moments = Moments(emblem_region, emblem_region_edge)
        crown_moments.save_file(f'params/{filename}-{color_name}-crown.txt')
        emblem_moments.save_file(f'params/{filename}-{color_name}-emblem.txt')

        # # Marking potential region
        # start_point = (boundaries.min_width - 2, boundaries.min_height - 2)
        # end_point = (boundaries.max_width + 2, boundaries.max_height + 2)
        # input_img = draw_rectangle(
        #     input_img, start_point, end_point, color, 1)

        is_crown_valid, is_emblem_valid = validate_region(
            crown_moments, emblem_moments)

        # Marking valid logo
        if is_crown_valid and is_emblem_valid:
            start_point = (boundaries.min_width - 5,
                           boundaries.min_height - 5)
            end_point = (boundaries.max_width + 3, boundaries.max_height + 3)
            input_img = draw_rectangle(
                input_img, start_point, end_point, (0, 0, 255), 3)

    return input_img


if __name__ == '__main__':
    program_time = TimePassed("Program")
    img_num = 0
    thresholding_values = {
        1: colors_set_1,
        2: colors_set_2,
        3: colors_set_3,
        4: colors_set_4,
    }

    for i in range(4):
        images = load_images_from_folder(f'{IMAGES_DIR}/{i + 1}')

        for img, filename in images:
            print(f'\n--> Processing {filename}...')

            img_time = TimePassed(filename)
            img_num = img_num + 1

            img = detect_real_madrid_logo(
                img, filename, thresholding_values[i + 1])

            cv2.imwrite(f'{OUTPUTS_DIR}/{filename}-processed.png', img)

            img_time.finish()

    program_time.finish()
