from math import log10, floor
import numpy as np


def round_to_sf(number: float, sf: int) -> float:
    if np.isnan(number):
        print(f"number is nan")
    if number == 0:
        return 0.0
    magnitude = int(floor(log10(abs(number))))
    rounding_digit = sf - 1 - magnitude
    return round(number, rounding_digit)
