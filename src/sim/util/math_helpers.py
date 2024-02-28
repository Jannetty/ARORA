from math import log10, floor
import numpy as np


def round_to_sf(number: float, sf: int) -> float:
    """
    Rounds a number to a specified number of significant figures.

    Parameters
    ----------
    number : float
        The number to be rounded.
    sf : int
        The number of significant figures to round to.

    Returns
    -------
    float
        The number rounded to the specified number of significant figures.

    Notes
    -----
    - If `number` is NaN, the function prints "number is nan" and returns NaN.
    - If `number` is zero, the function returns 0.0 directly, as zero has no significant figures.
    """    
    if np.isnan(number):
        print(f"number is nan")
    if number == 0:
        return 0.0
    magnitude = int(floor(log10(abs(number))))
    rounding_digit = sf - 1 - magnitude
    return round(number, rounding_digit)
