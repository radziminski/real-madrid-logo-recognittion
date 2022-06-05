from numpy import imag


def draw_rectangle(image_region, start_point, end_point, color, thickness=1):
    start_x, start_y = start_point
    end_x, end_y = end_point
    image_region[start_x:end_x, start_y:(start_y + thickness + 1)] = color
    image_region[start_x:end_x, (end_y - thickness - 1):end_y] = color
    image_region[start_x:(start_x + thickness + 1), start_y:end_y] = color
    image_region[(end_x - thickness - 1):end_x, start_y:end_y] = color

    return image_region
