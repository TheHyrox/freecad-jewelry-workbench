# SPDX-License-Identifier: LGPL-2.1-or-later
"""FreeCAD GUI Commands for Jewelry Workbench."""

import os
import FreeCAD
import FreeCADGui as Gui

from freecad.jewelry.shank import shank_feature
from freecad.jewelry.gem import gem_feature
from freecad.jewelry.settings import prong_feature, vprong_feature
from freecad.jewelry.cutter import cutter_feature
from freecad.jewelry.foliate import leaf_feature
from freecad.jewelry.metal import calculator

ICON_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "icons")


class CmdMakeShank:
    """Create a parametric Ring Shank."""

    def GetResources(self):
        return {
            "Pixmap": os.path.join(ICON_DIR, "Jewelry_Shank.svg"),
            "MenuText": "Ring Shank",
            "ToolTip": "Create a parametric ring shank with comfort-fit profile, standard sizing and shoulder taper",
        }

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None

    def Activated(self):
        doc = FreeCAD.ActiveDocument
        shank_feature.make_shank(doc)
        doc.recompute()


class CmdMakeGem:
    """Create a parametric Jewelry Gemstone."""

    def GetResources(self):
        return {
            "Pixmap": os.path.join(ICON_DIR, "Jewelry_Gem.svg"),
            "MenuText": "Gemstone",
            "ToolTip": "Insert a parametric faceted gemstone (Round, Oval, Marquise, Rounded/Sharp Pear, Trillion, Heart, Octagon, Emerald, Cushion)",
        }

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None

    def Activated(self):
        doc = FreeCAD.ActiveDocument
        gem_feature.make_gem(doc)
        doc.recompute()


class CmdMakeProngs:
    """Create a prong collet setting."""

    def GetResources(self):
        return {
            "Pixmap": os.path.join(ICON_DIR, "Jewelry_Prongs.svg"),
            "MenuText": "Prong Setting",
            "ToolTip": "Create corner or radial prongs with rounded button/claw tips and under-gallery rail",
        }

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None

    def Activated(self):
        doc = FreeCAD.ActiveDocument
        sel = Gui.Selection.getSelection()
        target_gem = sel[0] if (sel and getattr(getattr(sel[0], "Proxy", None), "Type", "") == "Jewelry::Gem") else None
        prong_feature.make_prong_setting(doc, gem=target_gem)
        doc.recompute()


class CmdMakeVProng:
    """Create a V-prong / chevron cap."""

    def GetResources(self):
        return {
            "Pixmap": os.path.join(ICON_DIR, "Jewelry_VProng.svg"),
            "MenuText": "V-Prong (Chevron)",
            "ToolTip": "Create a protective V-shaped chevron prong for marquise or pear stone points",
        }

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None

    def Activated(self):
        doc = FreeCAD.ActiveDocument
        vprong_feature.make_vprong(doc)
        doc.recompute()


class CmdMakeCutter:
    """Create a gemstone bearing / seat cutter."""

    def GetResources(self):
        return {
            "Pixmap": os.path.join(ICON_DIR, "Jewelry_Cutter.svg"),
            "MenuText": "Seat Cutter",
            "ToolTip": "Generate a negative gemstone seat cutter tool (girdle notch, pavilion bearing, culet hole)",
        }

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None

    def Activated(self):
        doc = FreeCAD.ActiveDocument
        sel = Gui.Selection.getSelection()
        target_gem = sel[0] if (sel and getattr(getattr(sel[0], "Proxy", None), "Type", "") == "Jewelry::Gem") else None
        cutter_feature.make_seat_cutter(doc, gem=target_gem)
        doc.recompute()


class CmdMakeLeaf:
    """Create a sculpted botanical foliate leaf."""

    def GetResources(self):
        return {
            "Pixmap": os.path.join(ICON_DIR, "Jewelry_Leaf.svg"),
            "MenuText": "Botanical Leaf",
            "ToolTip": "Create a sculpted, dimensional organic leaf with natural arch, central crease, twist, form type and optional flat back",
        }

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None

    def Activated(self):
        doc = FreeCAD.ActiveDocument
        leaf_feature.make_botanical_leaf(doc)
        doc.recompute()


class CmdCalculateBOM:
    """Calculate precious metal weights and gemstone BOM report."""

    def GetResources(self):
        return {
            "Pixmap": os.path.join(ICON_DIR, "Jewelry_BOM.svg"),
            "MenuText": "Metal & Carat Report (BOM)",
            "ToolTip": "Calculate casting weights for 14k/18k Gold, Platinum, Silver and total gemstone carats",
        }

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None

    def Activated(self):
        doc = FreeCAD.ActiveDocument
        rep = calculator.format_bom_report(doc)
        FreeCAD.Console.PrintMessage("\n" + rep + "\n")
        try:
            from PySide6 import QtWidgets
            dlg = QtWidgets.QMessageBox()
            dlg.setWindowTitle("Jewelry Bill of Materials")
            dlg.setText(rep)
            dlg.exec()
        except Exception:
            pass


COMMANDS = {
    "Jewelry_MakeShank": CmdMakeShank,
    "Jewelry_MakeGem": CmdMakeGem,
    "Jewelry_MakeProngs": CmdMakeProngs,
    "Jewelry_MakeVProng": CmdMakeVProng,
    "Jewelry_MakeCutter": CmdMakeCutter,
    "Jewelry_MakeLeaf": CmdMakeLeaf,
    "Jewelry_CalculateBOM": CmdCalculateBOM,
}
