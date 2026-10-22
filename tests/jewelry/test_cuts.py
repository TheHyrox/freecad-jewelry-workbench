# SPDX-License-Identifier: LGPL-2.1-or-later
"""Tests for parametric gemstone cut geometries."""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

for stale in [name for name in list(sys.modules.keys()) if name.split(".")[0] == "freecad"]:
    del sys.modules[stale]

import freecad
freecad_pkg_dir = os.path.join(ROOT, "freecad")
if freecad_pkg_dir not in freecad.__path__:
    freecad.__path__.append(freecad_pkg_dir)

import unittest
import FreeCAD
import Part
from freecad.jewelry.gem import cuts


class TestGemCuts(unittest.TestCase):

    def test_round_brilliant(self):
        gem = cuts.make_round_brilliant(diameter=6.5)
        self.assertIsInstance(gem, Part.Solid)
        self.assertTrue(gem.isValid(), "Round brilliant solid must be valid")
        self.assertGreater(gem.Volume, 30.0)

    def test_oval_cut(self):
        gem = cuts.make_oval_cut(length=9.0, width=7.0)
        self.assertIsInstance(gem, Part.Solid)
        self.assertTrue(gem.isValid(), "Oval cut solid must be valid")
        self.assertGreater(gem.Volume, 80.0)

    def test_marquise_cut(self):
        gem = cuts.make_marquise_cut(length=4.0, width=2.0)
        self.assertIsInstance(gem, Part.Solid)
        self.assertTrue(gem.isValid(), "Marquise cut solid must be valid")
        self.assertGreater(gem.Volume, 1.0)

    def test_rounded_pear_cut(self):
        gem = cuts.make_rounded_pear_cut(length=6.0, width=4.0)
        self.assertIsInstance(gem, Part.Solid)
        self.assertTrue(gem.isValid(), "Rounded pear solid must be valid")
        self.assertGreater(gem.Volume, 10.0)

    def test_sharp_pear_cut(self):
        gem = cuts.make_sharp_pear_cut(length=6.0, width=4.0)
        self.assertIsInstance(gem, Part.Solid)
        self.assertTrue(gem.isValid(), "Sharp pear solid must be valid")
        self.assertGreater(gem.Volume, 5.0)

    def test_trillion_cut(self):
        gem = cuts.make_trillion_cut(side=6.0)
        self.assertIsInstance(gem, Part.Solid)
        self.assertTrue(gem.isValid(), "Trillion cut solid must be valid")
        self.assertGreater(gem.Volume, 10.0)

    def test_heart_cut(self):
        gem = cuts.make_heart_cut(length=6.0, width=6.0)
        self.assertIsInstance(gem, Part.Solid)
        self.assertTrue(gem.isValid(), "Heart cut solid must be valid")
        self.assertGreater(gem.Volume, 20.0)

    def test_octagon_cut(self):
        gem = cuts.make_octagon_cut(length=7.0, width=7.0)
        self.assertIsInstance(gem, Part.Solid)
        self.assertTrue(gem.isValid(), "Octagon cut solid must be valid")
        self.assertGreater(gem.Volume, 40.0)

    def test_emerald_cut(self):
        gem = cuts.make_emerald_cut(length=8.0, width=6.0)
        self.assertIsInstance(gem, Part.Solid)
        self.assertTrue(gem.isValid(), "Emerald cut solid must be valid")
        self.assertGreater(gem.Volume, 60.0)

    def test_cushion_cut(self):
        gem = cuts.make_cushion_cut(length=6.0, width=6.0)
        self.assertIsInstance(gem, Part.Solid)
        self.assertTrue(gem.isValid(), "Cushion cut solid must be valid")
        self.assertGreater(gem.Volume, 30.0)


suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestGemCuts)
runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(suite)
if not result.wasSuccessful():
    sys.exit(1)
