# SPDX-License-Identifier: LGPL-2.1-or-later
"""Precious metals, alloys, and gemstone density tables and weight calculators."""

# Specific gravities / densities in g/cm^3
METAL_DENSITIES = {
    "14k_Yellow": 13.07,
    "14k_White": 12.90,
    "14k_Rose": 13.10,
    "18k_Yellow": 15.58,
    "18k_White": 14.70,
    "18k_Rose": 15.40,
    "24k_Gold": 19.32,
    "Platinum_950": 21.45,
    "Platinum_900": 20.00,
    "Silver_925": 10.36,
    "Silver_Fine_999": 10.49,
    "Brass_Jewelry": 8.50,
    "Bronze_Casting": 8.80,
    "Titanium": 4.51,
}

# Gemstone specific gravity (g/cm^3)
GEM_DENSITIES = {
    "Diamond": 3.52,
    "Topaz": 3.53,
    "Sapphire": 4.00,
    "Ruby": 4.00,
    "Emerald": 2.72,
    "Aquamarine": 2.68,
    "Quartz": 2.65,
    "Amethyst": 2.65,
    "Citrine": 2.65,
    "Garnet": 3.85,
    "Peridot": 3.34,
    "Spinel": 3.60,
    "Tanzanite": 3.35,
    "Tourmaline": 3.06,
    "Zircon": 4.65,
    "Moissanite": 3.22,
    "Cubic_Zirconia": 5.80,
    "Opal": 2.10,
}

# Standard display colors for 3D viewport (RGBA tuples 0.0 to 1.0)
GEM_COLORS = {
    "Diamond": (0.95, 0.98, 1.0, 0.25),
    "Topaz": (0.35, 0.70, 0.95, 0.35),       # Sky Blue Topaz
    "Blue_Topaz": (0.15, 0.55, 0.85, 0.35),  # Swiss / London Blue
    "Sapphire": (0.08, 0.22, 0.78, 0.30),
    "Ruby": (0.85, 0.05, 0.20, 0.30),
    "Emerald": (0.05, 0.75, 0.30, 0.30),
    "Aquamarine": (0.65, 0.90, 0.95, 0.35),
    "Quartz": (0.95, 0.95, 0.95, 0.25),
    "Amethyst": (0.60, 0.20, 0.75, 0.30),
    "Citrine": (0.95, 0.65, 0.15, 0.30),
    "Garnet": (0.65, 0.05, 0.10, 0.25),
    "Peridot": (0.65, 0.85, 0.20, 0.30),
    "Spinel": (0.80, 0.10, 0.40, 0.30),
    "Tanzanite": (0.30, 0.25, 0.85, 0.30),
    "Tourmaline": (0.15, 0.65, 0.45, 0.30),
    "Zircon": (0.40, 0.80, 0.85, 0.30),
    "Moissanite": (0.95, 0.98, 0.98, 0.25),
    "Cubic_Zirconia": (0.98, 0.98, 1.0, 0.20),
    "Opal": (0.92, 0.95, 0.90, 0.40),
}

METAL_COLORS = {
    "14k_Yellow": (0.95, 0.80, 0.35, 0.0),
    "18k_Yellow": (0.98, 0.83, 0.25, 0.0),
    "24k_Gold": (1.00, 0.82, 0.10, 0.0),
    "14k_White": (0.90, 0.90, 0.92, 0.0),
    "18k_White": (0.92, 0.92, 0.94, 0.0),
    "14k_Rose": (0.95, 0.70, 0.62, 0.0),
    "18k_Rose": (0.96, 0.68, 0.58, 0.0),
    "Platinum_950": (0.88, 0.90, 0.92, 0.0),
    "Platinum_900": (0.86, 0.88, 0.90, 0.0),
    "Silver_925": (0.93, 0.94, 0.95, 0.0),
    "Silver_Fine_999": (0.96, 0.96, 0.97, 0.0),
    "Brass_Jewelry": (0.88, 0.75, 0.28, 0.0),
    "Bronze_Casting": (0.80, 0.55, 0.30, 0.0),
    "Titanium": (0.65, 0.67, 0.70, 0.0),
}


def list_alloys() -> list:
    """Return all supported metal alloys."""
    return list(METAL_DENSITIES.keys())


def list_gem_species() -> list:
    """Return all supported gemstone species."""
    return list(GEM_DENSITIES.keys())


def get_metal_density(alloy: str) -> float:
    """Get density in g/cm^3."""
    return METAL_DENSITIES.get(alloy, 13.07)  # default 14k yellow


def get_gem_density(species: str) -> float:
    """Get gemstone density in g/cm^3."""
    return GEM_DENSITIES.get(species, 3.52)  # default diamond


def calculate_metal_weight(volume_mm3: float, alloy: str = "14k_Yellow") -> float:
    """
    Calculate weight in grams from volume in cubic millimeters.
    1 cm^3 = 1000 mm^3.
    """
    density = get_metal_density(alloy)
    volume_cm3 = volume_mm3 / 1000.0
    return round(volume_cm3 * density, 3)


def calculate_carat_weight(volume_mm3: float, species: str = "Diamond") -> float:
    """
    Calculate gemstone weight in carats from volume in mm^3.
    1 carat = 0.200 grams.
    """
    density = get_gem_density(species)
    weight_g = (volume_mm3 / 1000.0) * density
    carats = weight_g / 0.200
    return round(carats, 3)
