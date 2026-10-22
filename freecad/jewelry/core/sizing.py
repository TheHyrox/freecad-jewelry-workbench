# SPDX-License-Identifier: LGPL-2.1-or-later
"""Ring sizing standards and conversion utilities."""

import math

# Common US sizes with quarter sizes
US_SIZES = [
    "3.0", "3.25", "3.5", "3.75",
    "4.0", "4.25", "4.5", "4.75",
    "5.0", "5.25", "5.5", "5.75",
    "6.0", "6.25", "6.5", "6.75",
    "7.0", "7.25", "7.5", "7.75",
    "8.0", "8.25", "8.5", "8.75",
    "9.0", "9.25", "9.5", "9.75",
    "10.0", "10.25", "10.5", "10.75",
    "11.0", "11.25", "11.5", "11.75",
    "12.0", "12.25", "12.5", "12.75",
    "13.0", "13.5", "14.0",
]

# Standard US size to inner diameter in mm (ISO 8653 compliant)
# D = 11.63 + 0.8128 * size
def _us_to_diameter(size_val: float) -> float:
    return round(11.63 + 0.8128 * size_val, 2)

# UK letter size to inner diameter in mm
UK_SIZES = {
    "A": 12.04, "B": 12.45, "C": 12.85, "D": 13.26, "E": 13.67,
    "F": 14.07, "G": 14.48, "H": 14.88, "I": 15.29, "J": 15.49,
    "K": 15.90, "L": 16.31, "M": 16.71, "N": 17.12, "O": 17.53,
    "P": 17.93, "Q": 18.34, "R": 18.75, "S": 19.15, "T": 19.56,
    "U": 19.96, "V": 20.37, "W": 20.78, "X": 21.18, "Y": 21.59,
    "Z": 21.79, "Z+1": 22.20, "Z+2": 22.61, "Z+3": 23.01
}

# EU / ISO metric sizes (size number is circumference in mm)
EU_SIZES = [str(x) for x in range(44, 73)]

# Japanese sizes (1 to 27)
JP_SIZES = {
    str(n): round(13.0 + (n - 1) * 0.333, 2) for n in range(1, 28)
}


def list_available_sizes(standard: str = "US") -> list:
    """Return a list of size strings for the given standard."""
    std = standard.upper()
    if std == "US":
        return list(US_SIZES)
    elif std in ("UK", "AU"):
        return list(UK_SIZES.keys())
    elif std in ("EU", "ISO"):
        return list(EU_SIZES)
    elif std in ("JP", "JAPAN"):
        return list(JP_SIZES.keys())
    return ["Custom"]


def get_inner_diameter(size_str: str, standard: str = "US") -> float:
    """Convert size identifier into inner ring diameter in millimeters."""
    std = standard.upper()
    
    try:
        # If user directly passed a custom numeric float or 'Custom'
        if std == "CUSTOM" or standard.startswith("Custom"):
            return float(size_str)
    except (ValueError, TypeError):
        pass

    if std == "US":
        try:
            val = float(size_str)
            return _us_to_diameter(val)
        except ValueError:
            return 16.92  # Default to US 6.5

    elif std in ("UK", "AU"):
        key = str(size_str).strip().upper()
        return UK_SIZES.get(key, 16.71)  # Default M

    elif std in ("EU", "ISO"):
        try:
            circ = float(size_str)
            return round(circ / math.pi, 2)
        except ValueError:
            return 16.55  # EU 52

    elif std in ("JP", "JAPAN"):
        key = str(size_str).strip()
        return JP_SIZES.get(key, 16.66)  # Size 12

    # Fallback to US 6.5
    return 16.92


def get_inner_radius(size_str: str, standard: str = "US") -> float:
    """Return inner radius in mm."""
    return get_inner_diameter(size_str, standard) / 2.0


def get_circumference(size_str: str, standard: str = "US") -> float:
    """Return inner circumference in mm."""
    return round(math.pi * get_inner_diameter(size_str, standard), 2)
