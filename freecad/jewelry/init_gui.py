# SPDX-License-Identifier: LGPL-2.1-or-later
"""Jewelry workbench registration: workbench class, toolbars, menus."""

import os
import FreeCADGui as Gui
from freecad.jewelry.version import __version__

ICON_DIR = os.path.join(os.path.dirname(__file__), "resources", "icons")

JEWELRY_COMMANDS = [
    ("Jewelry_MakeShank", "Ring Shank", "Create a parametric ring shank with comfort-fit profile", "Jewelry_Shank.svg"),
    ("Jewelry_MakeGem", "Gemstone", "Insert a parametric faceted gemstone with carat estimation", "Jewelry_Gem.svg"),
    ("Jewelry_MakeProngs", "Prong Setting", "Create corner/radial prongs with rounded button/claw tips and base rail", "Jewelry_Prongs.svg"),
    ("Jewelry_MakeVProng", "V-Prong (Chevron)", "Create protective V-cap chevron prong for marquise/pear points", "Jewelry_VProng.svg"),
    ("Jewelry_MakeCutter", "Seat Cutter", "Create gemstone bearing seat cutter tool", "Jewelry_Cutter.svg"),
    ("Jewelry_MakeLeaf", "Botanical Leaf", "Create sculpted dimensional botanical leaf with optional flat back", "Jewelry_Leaf.svg"),
    ("Jewelry_CalculateBOM", "Metal & Carat Report (BOM)", "Calculate precious metal weights and gemstone carats", "Jewelry_BOM.svg"),
]


class JewelryWorkbench(Gui.Workbench):
    """Jewelry: parametric jewelry design, ring shanks, settings, gems & botanical metalwork."""

    MenuText = "Jewelry"
    ToolTip = "Design fine jewelry: ring shanks, gemstone settings, prongs, foliate metalwork & metal weight calculator"
    Icon = os.path.join(ICON_DIR, "Jewelry_Workbench.svg")

    def Initialize(self):
        """Called once when workbench is activated."""
        from freecad.jewelry.commands.commands import COMMANDS

        cmd_names = []
        for name, menu_text, tooltip, icon_file in JEWELRY_COMMANDS:
            cmd_class = COMMANDS.get(name)
            if cmd_class is not None:
                Gui.addCommand(name, cmd_class())
                cmd_names.append(name)

        self.appendToolbar("Jewelry Design", cmd_names)
        self.appendMenu("Jewelry", cmd_names)

    def Activated(self):
        pass

    def Deactivated(self):
        pass

    def GetClassName(self):
        return "Gui::PythonWorkbench"


Gui.addWorkbench(JewelryWorkbench())
