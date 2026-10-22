# SPDX-License-Identifier: LGPL-2.1-or-later
"""Parametric Sculpted Botanical Leaf Feature for FreeCAD."""

import math
import FreeCAD
import Part
from freecad.jewelry.core import metals

LEAF_FORMS = ["Pear", "Elliptical"]


def build_botanical_leaf(length: float = 5.0, max_width: float = 2.2,
                         thickness: float = 0.8, bend: float = 0.6,
                         crease: float = 0.3, twist_deg: float = 10.0,
                         form_type: str = "Pear",
                         flat_back: bool = False) -> Part.Solid:
    """
    Build a sculpted dimensional botanical leaf solid:
    - Form type: 'Pear' (lanceolate/teardrop) or 'Elliptical' (symmetrical oval)
    - Natural arch along spine (bend)
    - Central vein rib crease and upward-cupping margins
    - FlatBack: if True, the underside/back is completely flat in cross-section
      (crease is carved into the top, so the back sits flush on ring bands/bezels)
    - Longitudinal twist
    """
    n_stations = 12
    wires = []

    for i in range(n_stations):
        s = 0.02 + 0.96 * i / (n_stations - 1)
        x = length * s
        z_spine = bend * math.sin(math.pi * s)

        if form_type == "Elliptical":
            w = max_width * math.sin(math.pi * s)
        else:  # "Pear" / Lanceolate
            w = max_width * math.sin(math.pi * (s ** 0.55))

        w = max(0.12, w)

        twist_rad = math.radians(twist_deg * s)
        cos_tw = math.cos(twist_rad)
        sin_tw = math.sin(twist_rad)

        cup = crease * 0.8
        y_l = -w
        z_l = cup
        y_r = w
        z_r = cup
        y_mid = 0.0
        z_mid = -crease

        def rotate_yz(y, z):
            return (y * cos_tw - z * sin_tw, y * sin_tw + z * cos_tw)

        yr_l, zr_l = rotate_yz(y_l, z_l)
        yr_r, zr_r = rotate_yz(y_r, z_r)
        yr_mid, zr_mid = rotate_yz(y_mid, z_mid)

        # Upper surface has sculpted crease and cupped margins
        pt_l_top = FreeCAD.Vector(x, yr_l, z_spine + zr_l)
        pt_mid_top = FreeCAD.Vector(x, yr_mid, z_spine + zr_mid)
        pt_r_top = FreeCAD.Vector(x, yr_r, z_spine + zr_r)

        t_local = thickness * (1.0 - 0.35 * s)

        if flat_back:
            # Bottom surface is flat across width (crease is material carved from top)
            z_bot = z_spine - t_local
            pt_r_bot = FreeCAD.Vector(x, yr_r, z_bot)
            pt_mid_bot = FreeCAD.Vector(x, yr_mid, z_bot)
            pt_l_bot = FreeCAD.Vector(x, yr_l, z_bot)
        else:
            pt_r_bot = pt_r_top - FreeCAD.Vector(0, 0, t_local)
            pt_mid_bot = pt_mid_top - FreeCAD.Vector(0, 0, t_local)
            pt_l_bot = pt_l_top - FreeCAD.Vector(0, 0, t_local)

        wire = Part.makePolygon([pt_l_top, pt_mid_top, pt_r_top, pt_r_bot, pt_mid_bot, pt_l_bot, pt_l_top])
        wires.append(wire)

    leaf = Part.makeLoft(wires, True, False)
    leaf.fix(1e-4, 1e-4, 1e-4)
    if leaf.Solids:
        return leaf.Solids[0]
    return leaf


class LeafProxy:
    """Proxy object implementing parametric Botanical Leaf."""

    def __init__(self, fp):
        fp.Proxy = self
        self.Type = "Jewelry::BotanicalLeaf"

    def execute(self, fp):
        l = getattr(fp, "Length", 5.0)
        w = getattr(fp, "MaxWidth", 2.2)
        t = getattr(fp, "Thickness", 0.8)
        b = getattr(fp, "Bend", 0.6)
        c = getattr(fp, "Crease", 0.3)
        tw = getattr(fp, "Twist", 10.0)
        form = getattr(fp, "FormType", "Pear")
        fb = getattr(fp, "FlatBack", False)

        fp.Shape = build_botanical_leaf(
            length=l, max_width=w, thickness=t,
            bend=b, crease=c, twist_deg=tw,
            form_type=form, flat_back=fb
        )

        vol = fp.Shape.Volume if (fp.Shape and not fp.Shape.isNull()) else 0.0
        alloy = getattr(fp, "Alloy", "14k_Yellow")
        if hasattr(fp, "WeightGrams"):
            fp.WeightGrams = metals.calculate_metal_weight(vol, alloy)


class ViewProviderLeaf:
    """View provider for botanical leaf."""

    def __init__(self, vobj):
        vobj.Proxy = self

    def attach(self, vobj):
        self.ViewObject = vobj
        if hasattr(vobj, "Object") and vobj.Object is not None:
            self.update_appearance(vobj.Object)

    def updateData(self, fp, prop):
        """Called by FreeCAD GUI whenever an App property changes."""
        if prop in ("Alloy", "Shape"):
            self.update_appearance(fp)

    def update_appearance(self, fp):
        if not hasattr(fp, "ViewObject") or fp.ViewObject is None:
            return
        vobj = fp.ViewObject
        alloy = getattr(fp, "Alloy", "14k_Yellow")
        color = metals.METAL_COLORS.get(alloy, (0.95, 0.8, 0.35, 0.0))
        r, g, b, alpha = color
        vobj.ShapeColor = (r, g, b)
        vobj.Transparency = 0
        vobj.DisplayMode = "Shaded"
        vobj.Visibility = True

    def onChanged(self, vobj, prop):
        pass

    def getIcon(self):
        return ":/icons/Jewelry_Leaf.svg"

    def getDefaultDisplayMode(self):
        return "Shaded"

    def getDisplayModes(self, vobj):
        return ["Shaded", "Wireframe"]

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None


def make_botanical_leaf(doc, label="Leaf", length=5.0, max_width=2.2,
                        thickness=0.8, bend=0.6, crease=0.3, twist=10.0,
                        form_type="Pear", flat_back=False, alloy="14k_Yellow"):
    """Factory creating a Botanical Leaf object in the document."""
    obj = doc.addObject("Part::FeaturePython", label)
    LeafProxy(obj)

    obj.addProperty("App::PropertyEnumeration", "FormType", "Form", "Leaf outline form")
    obj.FormType = LEAF_FORMS
    obj.FormType = form_type if form_type in LEAF_FORMS else "Pear"

    obj.addProperty("App::PropertyBool", "FlatBack", "Form", "Make underside flat (crease is carved from top)")
    obj.FlatBack = flat_back

    obj.addProperty("App::PropertyFloatConstraint", "Length", "Dimensions", "Leaf spine length in mm")
    obj.Length = (length, 0.5, 30.0, 0.1)

    obj.addProperty("App::PropertyFloatConstraint", "MaxWidth", "Dimensions", "Maximum leaf width in mm")
    obj.MaxWidth = (max_width, 0.2, 15.0, 0.1)

    obj.addProperty("App::PropertyFloatConstraint", "Thickness", "Dimensions", "Leaf metal thickness in mm")
    obj.Thickness = (thickness, 0.2, 5.0, 0.05)

    obj.addProperty("App::PropertyFloatConstraint", "Bend", "Sculpting", "Spine arch curvature in mm")
    obj.Bend = (bend, -5.0, 5.0, 0.1)

    obj.addProperty("App::PropertyFloatConstraint", "Crease", "Sculpting", "Central vein rib crease depth in mm")
    obj.Crease = (crease, 0.0, 3.0, 0.05)

    obj.addProperty("App::PropertyFloatConstraint", "Twist", "Sculpting", "Spine twist degrees")
    obj.Twist = (twist, -90.0, 90.0, 1.0)

    obj.addProperty("App::PropertyEnumeration", "Alloy", "Material", "Metal alloy")
    obj.Alloy = metals.list_alloys()
    obj.Alloy = alloy

    obj.addProperty("App::PropertyFloat", "WeightGrams", "Calculations", "Estimated metal weight (grams)", 1)

    if FreeCAD.GuiUp:
        vp = ViewProviderLeaf(obj.ViewObject)
        vp.update_appearance(obj)

    obj.recompute()
    return obj
