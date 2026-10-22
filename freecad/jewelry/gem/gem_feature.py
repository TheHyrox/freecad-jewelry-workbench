# SPDX-License-Identifier: LGPL-2.1-or-later
"""Parametric Jewelry Gemstone Feature for FreeCAD."""

import FreeCAD
import Part
from freecad.jewelry.core import metals
from freecad.jewelry.gem import cuts

GEM_CUT_TYPES = [
    "Round",
    "Oval",
    "Marquise",
    "Rounded Pear",
    "Sharp Pear",
    "Trillion",
    "Heart",
    "Octagon",
    "Emerald",
    "Cushion",
]
GEM_SPECIES = metals.list_gem_species()


class GemProxy:
    """Proxy object implementing parametric gemstone behavior."""

    def __init__(self, fp):
        fp.Proxy = self
        self.Type = "Jewelry::Gem"

    def execute(self, fp):
        cut_type = getattr(fp, "CutType", "Round")
        species = getattr(fp, "Species", "Diamond")
        flat_back = getattr(fp, "FlatBack", False)

        length = getattr(fp, "Length", 6.5)
        width = getattr(fp, "Width", 6.5)
        depth = getattr(fp, "Depth", 0.0)
        if depth <= 0:
            depth = None

        factory = cuts.CUT_FACTORIES.get(cut_type, cuts.make_round_brilliant)
        if cut_type == "Round":
            fp.Shape = factory(diameter=width, depth=depth, flat_back=flat_back)
        elif cut_type == "Trillion":
            fp.Shape = factory(length, width, depth, fb=flat_back)
        else:
            fp.Shape = factory(length=length, width=width, depth=depth, flat_back=flat_back)

        # Update Carat weight based on exact B-Rep volume
        vol = fp.Shape.Volume if (fp.Shape and not fp.Shape.isNull()) else 0.0
        carats = metals.calculate_carat_weight(vol, species)
        if hasattr(fp, "Carats"):
            fp.Carats = carats


class ViewProviderGem:
    """View provider giving gemstones appearance and transparency."""

    def __init__(self, vobj):
        vobj.Proxy = self

    def attach(self, vobj):
        self.ViewObject = vobj
        if hasattr(vobj, "Object") and vobj.Object is not None:
            self.update_appearance(vobj.Object)

    def updateData(self, fp, prop):
        """Called by FreeCAD GUI whenever an App property changes."""
        if prop in ("Species", "Shape"):
            self.update_appearance(fp)

    def update_appearance(self, fp):
        if not hasattr(fp, "ViewObject") or fp.ViewObject is None:
            return
        vobj = fp.ViewObject
        species = getattr(fp, "Species", "Diamond")
        color = metals.GEM_COLORS.get(species, (0.95, 0.98, 1.0, 0.25))
        r, g, b, alpha = color
        vobj.ShapeColor = (r, g, b)
        vobj.Transparency = int(alpha * 100)
        vobj.DisplayMode = "Shaded"
        vobj.Visibility = True

    def onChanged(self, vobj, prop):
        pass

    def getIcon(self):
        return ":/icons/Jewelry_Gem.svg"

    def getDefaultDisplayMode(self):
        return "Shaded"

    def getDisplayModes(self, vobj):
        return ["Shaded", "Wireframe"]

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None


def make_gem(doc, label="Gem", cut_type="Round", length=6.5, width=6.5, depth=0.0,
             flat_back=False, species="Diamond"):
    """Factory creating a Jewelry Gem object in the document."""
    obj = doc.addObject("Part::FeaturePython", label)
    GemProxy(obj)

    obj.addProperty("App::PropertyEnumeration", "CutType", "Gemstone", "Cut geometry style")
    obj.CutType = GEM_CUT_TYPES
    obj.CutType = cut_type if cut_type in GEM_CUT_TYPES else "Round"

    obj.addProperty("App::PropertyFloatConstraint", "Length", "Dimensions", "Gemstone length in mm")
    obj.Length = (length, 0.1, 100.0, 0.1)

    obj.addProperty("App::PropertyFloatConstraint", "Width", "Dimensions", "Gemstone width in mm")
    obj.Width = (width, 0.1, 100.0, 0.1)

    obj.addProperty("App::PropertyFloatConstraint", "Depth", "Dimensions", "Gemstone depth/height in mm (0 = auto)")
    obj.Depth = (depth, 0.0, 100.0, 0.1)

    obj.addProperty("App::PropertyBool", "FlatBack", "Dimensions", "Make underside flat (cabochon / rose-cut style)")
    obj.FlatBack = flat_back

    obj.addProperty("App::PropertyEnumeration", "Species", "Material", "Mineral species")
    obj.Species = GEM_SPECIES
    obj.Species = species

    obj.addProperty("App::PropertyFloat", "Carats", "Calculations", "Estimated carat weight", 1)

    if FreeCAD.GuiUp:
        vp = ViewProviderGem(obj.ViewObject)
        vp.update_appearance(obj)

    obj.recompute()
    return obj
