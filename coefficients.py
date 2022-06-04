import numpy as np
import math
import constants


class Coefficients:
    def __init__(self, image: np.ndarray):
        self.image = image
        self.m00 = self.get_m_p_q(0, 0)
        self.m10 = self.get_m_p_q(1, 0)
        self.m20 = self.get_m_p_q(2, 0)
        self.m30 = self.get_m_p_q(3, 0)
        self.m01 = self.get_m_p_q(0, 1)
        self.m02 = self.get_m_p_q(0, 2)
        self.m03 = self.get_m_p_q(0, 3)
        self.m11 = self.get_m_p_q(1, 1)
        self.m12 = self.get_m_p_q(1, 2)
        self.m21 = self.get_m_p_q(2, 1)
        self.i = self.m10 / self.m00
        self.j = self.m01 / self.m00
        self.M00 = self.m00
        self.M01 = self.m01 - (self.m01 / self.m00) * self.m00
        self.M10 = self.m10 - (self.m10 / self.m00) * self.m00
        self.M11 = self.m11 - self.m10 * self.m01 / self.m00
        self.M20 = self.m20 - (self.m10 ** 2 / self.m00)
        self.M02 = self.m02 - (self.m10 ** 2 / self.m00)
        self.M21 = self.m21 - 2 * self.m11 * self.i - \
            self.m20 * self.j + 2 * self.m01 * self.i ** 2
        self.M12 = self.m12 - 2 * self.m11 * self.j - \
            self.m02 * self.i + 2 * self.m10 * self.j ** 2
        self.M30 = self.m30 - 3 * self.m20 * self.i + 2 * self.m10 * self.i ** 2
        self.M03 = self.m03 - 3 * self.m02 * self.j + 2 * self.m01 * self.j ** 2
        self.M1 = (self.M20 + self.M02) / self.m00 ** 2
        self.M2 = ((self.M20 - self.M02) ** 2 + 4 *
                   self.M11 ** 2) / self.m00 ** 4
        self.M3 = ((self.M30 - 3 * self.M12) ** 2 +
                   (3 * self.M21 - self.M03) ** 2) / self.m00 ** 5
        self.M4 = ((self.M30 + self.M12) ** 2 +
                   (self.M21 + self.M03) ** 2) / self.m00 ** 5
        self.M5 = ((self.M30 - 3 * self.M12) * (self.M30 + self.M12) * (((self.M30 + self.M12) ** 2) - 3 *
                                                                        ((self.M21 + self.M03) ** 2)) + (
            3 * self.M21 - self.M03) *
            (self.M21 + self.M03) * (
            3 * (self.M30 + self.M12) ** 2 - (self.M21 + self.M03) ** 2)) / self.m00 ** 10
        self.M6 = ((self.M20 - self.M02) * ((self.M30 + self.M12) ** 2 - (self.M21 + self.M03) ** 2) + 4 * self.M11 *
                   (self.M30 + self.M12) * (self.M21 + self.M03)) / self.m00 ** 7
        self.M7 = (self.M20 * self.M02 - self.M11 ** 2) / self.m00 ** 4
        self.M8 = (self.M30 * self.M12 + self.M21 * self.M03 -
                   self.M12 ** 2 - self.M21 ** 2) / self.m00 ** 5
        self.M9 = (self.M20 * (self.M21 * self.M03 - self.M12 ** 2) + self.M02 * (self.M02 * self.M12 - self.M21 ** 2) -
                   self.M11 * (self.M30 * self.M03 - self.M21 * self.M12)) / self.m00 ** 7
        self.perimeter, self.area = self.get_perimeter_and_area()
        self.W3 = self.get_w3()
        self.W4 = self.get_w4()
        self.height, self.width = image.shape

    def get_m_p_q(self, p: int, q: int):
        m = 0
        h, w = self.image.shape

        for j in range(0, w - 1):
            for i in range(0, h - 1):
                binary_val = 0 if self.image[i, j] > 128 else 1
                m += (i ** p) * (j ** q) * binary_val

        return m if m > 0 else 1

    def get_perimeter_and_area(self):
        perimeter = 0
        area = 0
        h, w = self.image.shape

        for y in range(1, w - 1):
            for x in range(1, h - 1):
                if self.image[x, y] > 128:
                    area += 1
                    neighbourhood = self.image[x - 1:x + 2, y - 1:y + 2]
                    if self.is_edge(neighbourhood):
                        perimeter += 1

        return perimeter, area

    def get_brightness(self, pixel: np.array):
        return np.average(pixel)

    def is_edge(self, neighbourhood: np.ndarray):
        center_pixel = neighbourhood[1, 1]
        return np.any(neighbourhood[:, :] != center_pixel)

    def get_w4(self):
        distances_sum = 0
        h, w = self.image.shape

        for j in range(0, w - 1):
            for i in range(0, h - 1):
                distances_sum += self.get_distance_to_center([i, j]) ** 2

        return self.area / math.sqrt(2 * math.pi * distances_sum)

    def get_w3(self):
        if self.area == 0:
            return 0
        return self.perimeter / (2 * math.sqrt(math.pi * self.area)) - 1

    def get_distance_to_center(self, point):
        return math.sqrt((point[0] - self.i) ** 2 + (point[1] - self.j) ** 2)

    def write_to_file(self, file_name: str):
        f = open(file_name, 'w')
        f.write('M1: {0:.10f}\n'.format(self.M1))
        f.write('M2: {0:.10f}\n'.format(self.M2))
        f.write('M3: {0:.10f}\n'.format(self.M3))
        f.write('M4: {0:.10f}\n'.format(self.M4))
        f.write('M5: {0:.10f}\n'.format(self.M5))
        f.write('M6: {0:.10f}\n'.format(self.M6))
        f.write('M7: {0:.10f}\n'.format(self.M7))
        f.write('M8: {0:.10f}\n'.format(self.M8))
        f.write('M9: {0:.10f}\n'.format(self.M9))
        f.write('W3: {0:.10f}\n'.format(self.W3))
        f.write('W4: {0:.10f}\n'.format(self.W4))
        f.write('Perimeter: {0:.10f}\n'.format(self.perimeter))
        f.write('Area: {0:.10f}\n'.format(self.area))
        f.write(
            'Perimeter/area ratio: {0:.10f}\n'.format(self.perimeter / self.area))
        f.write('Aspect ratio {0:.10f}'.format(self.width / self.height))
        f.close()
