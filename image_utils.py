def pixels_iterate(image, callback):
    for line in image:
        for pixel in line:
            callback(pixel)


def normalize_value(pixel):
    if pixel > 255:
        return 255

    if pixel < 0:
        return 0

    return pixel


def to_grayscale(pixel):
    new_value = (int(pixel[0]) + int(pixel[1]) + int(pixel[2])) / 3
    return normalize_value(new_value)
