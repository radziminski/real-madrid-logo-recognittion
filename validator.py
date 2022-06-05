from cmath import inf
from moments import Moments


class Validator:
    def __init__(self, intervals: dict):
        self.intervals = intervals

    def set_interval(self, intervals, name):
        if intervals[name]:
            self.intervals[name] = intervals[name]
        else:
            self.intervals[name] = (-inf, inf)

    def validate_moments(self, moments: Moments):
        moments_dict = moments.get_params()

        for key in moments_dict:
            curr_moment = moments_dict[key]
            low, high = self.intervals[key]
            if curr_moment < low or curr_moment > high:
                # print(f'{key} is not valid! {curr_moment} not in {low} - {high}')
                return False

        return True


intervals_example = {
    'M1': (0, 1000),
    'M2': (-100, 1000),
    'M3': (-100, 1000),
    'M4': (-100, 1000),
    'M5': (-100, 1000),
    'M6': (-100, 1000),
    'M7': (-100, 1000),
    'M8': (-100, 1000),
    'M9': (-100, 1000),
    'W1': (-100, 1000),
    'W2': (-100, 1000),
    'W3': (-100, 1000),
    'W4': (-100, 1000),
    'W9': (-100, 1000),
    'pa': (0.0, 0.1),
}

crown_intervals_v1 = {
    'M1': (0.4, 1.5),
    'M2': (0.0001, 1.9),
    'M3': (0.00001, 0.2),
    'M4': (0.000001, 0.21),
    'M5': (-0.000001, inf),
    'M6': (-inf, 0.24),
    'M7': (0.02, 0.11),
    'M8': (-0.003, 0.0015),
    'M9': (-inf, inf),
    'W1': (5, 300),
    'W2': (20, 3000),
    'W3': (0.9, 20),
    'W4': (0.157, 0.49),
    'W9': (0.03, 0.53),
    'pa': (0.1, 0.88),
}

crown_validator_v1 = Validator(crown_intervals_v1)


emblem_intervals_v1 = {
    'M1': (-0.1, 0.81),
    'M2': (0, 0.51),
    'M3': (0.00001, 0.007),
    'M4': (0.000001, 0.021),
    'M5': (-2, 0.00005),
    'M6': (-0.01, 0.0031),
    'M7': (-0.13, 0.16),
    'M8': (-0.0003, 0.00035),
    'M9': (-0.00002, inf),
    'W1': (10, 300),
    'W2': (70, 5000),
    'W3': (2, 20),
    'W4': (0.23, 0.7),
    'W9': (0.04, 0.235),
    'pa': (0.05, 0.96),
}

emblem_validator_v1 = Validator(emblem_intervals_v1)


def validate_region(crown_moments, emblem_moments):
    is_crown_valid = crown_validator_v1.validate_moments(crown_moments)
    is_emblem_valid = emblem_validator_v1.validate_moments(emblem_moments)

    return is_crown_valid, is_emblem_valid
