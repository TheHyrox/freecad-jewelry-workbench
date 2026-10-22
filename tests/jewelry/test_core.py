# SPDX-License-Identifier: LGPL-2.1-or-later
"""Tests for sizing and metals core modules."""

import unittest
from freecad.jewelry.core import sizing, metals


class TestJewelryCore(unittest.TestCase):

    def test_sizing_us(self):
        d_6_5 = sizing.get_inner_diameter("6.5", "US")
        # 11.63 + 0.8128 * 6.5 = 16.9132 -> 16.91 or 16.92
        self.assertAlmostEqual(d_6_5, 16.91, delta=0.05)
        r_6_5 = sizing.get_inner_radius("6.5", "US")
        self.assertAlmostEqual(r_6_5, 16.91 / 2.0, delta=0.05)

    def test_sizing_eu(self):
        d_52 = sizing.get_inner_diameter("52", "EU")
        self.assertAlmostEqual(d_52, 52.0 / 3.14159, delta=0.05)

    def test_metals_weight(self):
        # 1000 mm^3 = 1 cm^3
        vol = 1000.0
        w_14k = metals.calculate_metal_weight(vol, "14k_Yellow")
        self.assertAlmostEqual(w_14k, 13.07, places=2)
        w_18k = metals.calculate_metal_weight(vol, "18k_Yellow")
        self.assertAlmostEqual(w_18k, 15.58, places=2)

    def test_gem_carat(self):
        # Topaz density is 3.53 g/cm^3
        # 100 mm^3 = 0.1 cm^3 -> 0.353 g -> 0.353 / 0.2 = 1.765 carats
        carats = metals.calculate_carat_weight(100.0, "Topaz")
        self.assertAlmostEqual(carats, 1.765, places=2)


if __name__ == "__main__":
    unittest.main()
