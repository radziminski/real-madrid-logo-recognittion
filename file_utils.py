import cv2
import os


def load_images_from_folder(dir):
    images = []
    for filename in os.listdir(dir):
        img = cv2.imread(os.path.join(dir, filename))
        if img is not None:
            images.append((img, filename))
    return images
