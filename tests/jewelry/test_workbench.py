# SPDX-License-Identifier: LGPL-2.1-or-later
"""Comprehensive unit tests for the FreeCAD Jewelry Workbench v1."""

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

from freecad.jewelry.core import sizing, metals
from freecad.jewelry.gem import cuts, gem_feature
from freecad.jewelry.shank import shank_feature
from freecad.jewelry.settings import prong_feature, vprong_feature
from freecad.jewelry.cutter import cutter_feature
from freecad.jewelry.foliate import leaf_feature
from freecad.jewelry.metal import calculator


class TestJewelryWorkbench(unittest.TestCase):

    def setUp(self):
        self.doc = FreeCAD.newDocument("UnitTest_Jewelry")

    def tearDown(self):
        FreeCAD.closeDocument(self.doc.Name)

    def test_shank_feature_and_alloy(self):
        shank = shank_feature.make_shank(
            self.doc, label="ShankTest",
            standard="US", ring_size="6.5",
            width_bottom=2.0, width_shoulder=1.4,
            thickness_bottom=1.6, thickness_shoulder=1.2,
            profile_type="ComfortFit", alloy="14k_Yellow",
            open_head=True, head_gap_angle=30.0
        )
        self.doc.recompute()
        self.assertFalse(shank.Shape.isNull())
        self.assertTrue(shank.Shape.isValid())
        self.assertGreater(shank.Shape.Volume, 100.0)

        # Test alloy change and weight calculation
        shank.Alloy = "18k_White"
        self.doc.recompute()
        self.assertAlmostEqual(shank.WeightGrams, metals.calculate_metal_weight(shank.Shape.Volume, "18k_White"), places=2)

    def test_gem_feature_and_species(self):
        topaz = gem_feature.make_gem(
            self.doc, label="TopazTest",
            cut_type="Oval", length=9.0, width=7.0, depth=4.3,
            species="Topaz"
        )
        self.doc.recompute()
        self.assertTrue(topaz.Shape.isValid())
        self.assertAlmostEqual(topaz.Carats, 1.71, delta=0.2)

        # Test flat-back option
        topaz_flat = gem_feature.make_gem(
            self.doc, label="TopazFlat",
            cut_type="Oval", length=9.0, width=7.0, depth=2.5,
            flat_back=True, species="Topaz"
        )
        self.doc.recompute()
        self.assertTrue(topaz_flat.Shape.isValid())
        self.assertGreater(topaz_flat.Shape.Volume, 40.0)

        # Test changing species recalculates carats
        topaz.Species = "Diamond"
        self.doc.recompute()
        self.assertAlmostEqual(topaz.Carats, metals.calculate_carat_weight(topaz.Shape.Volume, "Diamond"), places=2)

    def test_prongs_claw_style_and_targeting_gem(self):
        gem = gem_feature.make_gem(
            self.doc, label="TargetGem",
            cut_type="Oval", length=8.0, width=6.0, depth=3.8
        )
        self.doc.recompute()

        # Create claw style prongs targeting gem
        prongs = prong_feature.make_prong_setting(
            self.doc, label="ClawProngs", gem=gem,
            prong_dia=0.9, count=4, corner_prongs=True,
            style="Claw", base_rail=True
        )
        self.doc.recompute()

        self.assertFalse(prongs.Shape.isNull())
        self.assertTrue(prongs.Shape.isValid())
        self.assertGreater(prongs.Shape.Volume, 10.0)

        # Verify dimension properties are grayed out (ReadOnly) when targeting a gem
        for p in ("Length", "Width", "Height", "ZBase"):
            mode = prongs.getEditorMode(p)
            self.assertEqual(mode, ["ReadOnly"], f"Property {p} should be ReadOnly when gem is targeted")

        # Untarget gem -> properties should become editable again
        prongs.TargetGem = None
        self.doc.recompute()
        for p in ("Length", "Width", "Height", "ZBase"):
            mode = prongs.getEditorMode(p)
            self.assertEqual(mode, [], f"Property {p} should be editable when gem is untargeted")

    def test_vprong_feature(self):
        vp = vprong_feature.make_vprong(
            self.doc, label="VProngTest",
            tip_x=2.0, tip_y=0.0, height=1.2, z_base=-0.8,
            alloy="18k_Yellow"
        )
        self.doc.recompute()
        self.assertFalse(vp.Shape.isNull())
        self.assertTrue(vp.Shape.isValid())
        self.assertGreater(vp.Shape.Volume, 1.0)

    def test_seat_cutter_feature(self):
        gem = gem_feature.make_gem(
            self.doc, label="GemForCutter",
            cut_type="Round", length=6.5, width=6.5, depth=4.0
        )
        self.doc.recompute()

        cutter = cutter_feature.make_seat_cutter(
            self.doc, label="CutterTest", gem=gem
        )
        self.doc.recompute()
        self.assertFalse(cutter.Shape.isNull())
        self.assertTrue(cutter.Shape.isValid())
        self.assertGreater(cutter.Shape.Volume, 15.0)

    def test_leaf_feature_forms_and_flat_back(self):
        # Pear form without flat back
        leaf1 = leaf_feature.make_botanical_leaf(
            self.doc, label="LeafPear",
            length=5.0, max_width=2.2, form_type="Pear", flat_back=False
        )
        self.doc.recompute()
        self.assertTrue(leaf1.Shape.isValid())

        # Elliptical form with flat back
        leaf2 = leaf_feature.make_botanical_leaf(
            self.doc, label="LeafEllipticalFlatBack",
            length=5.0, max_width=2.2, bend=0.0, crease=0.3, form_type="Elliptical", flat_back=True
        )
        self.doc.recompute()
        self.assertTrue(leaf2.Shape.isValid())
        self.assertGreater(leaf2.Shape.Volume, 5.0)

    def test_bom_calculator(self):
        # Add a shank and 2 gems
        shank_feature.make_shank(self.doc, label="BOM_Shank", alloy="14k_Yellow")
        gem_feature.make_gem(self.doc, label="BOM_Topaz", cut_type="Oval", species="Topaz")
        gem_feature.make_gem(self.doc, label="BOM_Diamond", cut_type="Round", species="Diamond")
        self.doc.recompute()

        bom = calculator.calculate_document_bom(self.doc, "14k_Yellow")
        self.assertGreater(bom["metal_volume_mm3"], 100.0)
        self.assertGreater(bom["default_weight_grams"], 1.0)
        self.assertEqual(bom["total_gems_count"], 2)
        self.assertGreater(bom["total_carats"], 0.5)


suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestJewelryWorkbench)
runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(suite)
if not result.wasSuccessful():
    sys.exit(1)
