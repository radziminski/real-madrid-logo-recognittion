import numpy as np
import math


class Moments:
    def __init__(self, image, image_edged):
        self.image = image
        self.image_edged = image_edged
        self.m00 = self.calculate_moment(0, 0)

        self.m10 = self.calculate_moment(1, 0)
        self.m01 = self.calculate_moment(0, 1)
        self.m11 = self.calculate_moment(1, 1)

        self.m20 = self.calculate_moment(2, 0)
        self.m02 = self.calculate_moment(0, 2)

        self.m12 = self.calculate_moment(1, 2)
        self.m21 = self.calculate_moment(2, 1)

        self.m30 = self.calculate_moment(3, 0)
        self.m03 = self.calculate_moment(0, 3)

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

        self.perimeter = self.calculate_perimeter()
        self.area = self.calculate_area()

        self.W1 = self.calculate_W1()
        self.W2 = self.calculate_W2()
        self.W3 = self.calculate_W3()
        self.W4 = self.calculate_W4()
        self.W9 = self.calculate_W9()

        self.height, self.width = image.shape

    def calculate_moment(self, x, y):
        m = 0
        height, width = self.image.shape

        for i in range(0, width - 1):
            for j in range(0, height - 1):
                val = 0 if self.image[j, i] > 128 else 1
                m += (j ** x) * (i ** y) * val

        return m if m > 0 else 1

    def calculate_area(self):
        ones = np.array(self.image / 255, dtype=int)
        return np.sum(ones)

    def calculate_perimeter(self):
        ones = np.array(self.image_edged / 255, dtype=int)
        return np.sum(ones)

    def calculate_W4(self):
        distances_sum = 0
        height, width = self.image.shape

        for j in range(0, width - 1):
            for i in range(0, height - 1):
                distances_sum += self.distance_to_point([i, j]) ** 2

        return self.area / math.sqrt(2 * math.pi * distances_sum)

    def calculate_W1(self):
        if self.area == 0:
            return 0

        return (2 * math.sqrt(self.area / math.pi))

    def calculate_W2(self):
        if self.area == 0:
            return 0

        return self.perimeter / math.pi

    def calculate_W3(self):
        if self.area == 0:
            return 0

        return self.perimeter / (2 * math.sqrt(math.pi * self.area)) - 1

    def calculate_W9(self):
        if self.perimeter == 0:
            return 0

        return (2 * math.sqrt(math.pi * self.area)) / self.perimeter

    def distance_to_point(self, point):
        return math.sqrt((point[0] - self.i) ** 2 + (point[1] - self.j) ** 2)

    def format_param(self, name: str, val: int):
        return f'{self.format_value(val)}\n'.replace('.', ',')

    def format_value(self, val):
        return '{0:.10f}'.format(val)

    def save_file(self, file_name: str):
        file = open(file_name, 'w')
        params_map = {
            'M1': self.M1,
            'M2': self.M2,
            'M3': self.M3,
            'M4': self.M4,
            'M5': self.M5,
            'M6': self.M6,
            'M7': self.M7,
            'M8': self.M8,
            'M9': self.M9,
            'W1': self.W1,
            'W2': self.W2,
            'W3': self.W3,
            'W4': self.W4,
            'W9': self.W9,
            'Perimeter/area': self.perimeter / self.area,
        }

        for param in params_map:
            file.write(self.format_param(param, params_map[param]))

        file.close()

    def get_params(self):
        return {
            'M1': self.M1,
            'M2': self.M2,
            'M3': self.M3,
            'M4': self.M4,
            'M5': self.M5,
            'M6': self.M6,
            'M7': self.M7,
            'M8': self.M8,
            'M9': self.M9,
            'W1': self.W1,
            'W2': self.W2,
            'W3': self.W3,
            'W4': self.W4,
            'W9': self.W9,
            'pa': self.perimeter / self.area,
        }
