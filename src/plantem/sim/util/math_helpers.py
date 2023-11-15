from math import log10, floor


def round_to_sf(number, sf):
    #print(f"number: {number}, sf: {sf}")
    if number == 0:
        return 0.0
    if number == float('inf'):
        return float('inf')
    if number == float('-inf'):
        return float('-inf')
    magnitude = int(floor(log10(abs(number))))
    rounding_digit = sf - 1 - magnitude
    return round(number, rounding_digit)