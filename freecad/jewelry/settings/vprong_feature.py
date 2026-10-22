# SPDX-License-Identifier: LGPL-2.1-or-later
"""Parametric V-Prong (Chevron) Setting Feature for Marquise and Pear gemstones."""

import math
import FreeCAD
import Part
from freecad.jewelry.core import metals


def build_vprong_solid(tip_x: float = 2.0, tip_y: float = 0.0,
                       angle_deg: float = 0.0,
                       height: float = 1.4, z_base: float = -1.0,
                       wall_thickness: float = 0.6,
                       wing_length: float = 0.85,
                       wing_angle_deg: float = 35.0) -> Part.Solid:
    """Build a protective V-shaped chevron prong enclosing pointed stone tips."""
    ang_rad = math.radians(wing_angle_deg)

    # Inner V where stone sits
    p_inner_tip = FreeCAD.Vector(0, 0, 0)
    p_inner_left = FreeCAD.Vector(-wing_length * math.cos(ang_rad), wing_length * math.sin(ang_rad), 0)
    p_inner_right = FreeCAD.Vector(-wing_length * math.cos(ang_rad), -wing_length * math.sin(ang_rad), 0)

    # Outer V
    p_outer_tip = FreeCAD.Vector(wall_thickness, 0, 0)
    p_outer_left = p_inner_left + FreeCAD.Vector(0, wall_thickness, 0)
    p_outer_right = p_inner_right + FreeCAD.Vector(0, -wall_thickness, 0)

    poly_pts = [p_inner_left, p_inner_tip, p_inner_right, p_outer_right, p_outer_tip, p_outer_left, p_inner_left]
    wire = Part.makePolygon(poly_pts)
    face = Part.Face(wire)

    total_h = height - z_base
    v_solid = face.extrude(FreeCAD.Vector(0, 0, total_h))
    v_solid.translate(FreeCAD.Vector(0, 0, z_base))

    rot = FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), angle_deg)
    pos = FreeCAD.Vector(tip_x, tip_y, 0)
    v_solid.Placement = FreeCAD.Placement(pos, rot)
    v_solid.fix(1e-4, 1e-4, 1e-4)

    if v_solid.Solids:
        return v_solid.Solids[0]
    return v_solid


class VProngProxy:
    """Proxy object implementing parametric V-Prong Setting."""

    def __init__(self, fp):
        fp.Proxy = self
        self.Type = "Jewelry::VProng"

    def execute(self, fp):
        tx = getattr(fp, "TipX", 2.0)
        ty = getattr(fp, "TipY", 0.0)
        ang = getattr(fp, "Angle", 0.0)
        h = getattr(fp, "Height", 1.4)
        zb = getattr(fp, "ZBase", -1.0)
        wall = getattr(fp, "WallThickness", 0.6)
        wing = getattr(fp, "WingLength", 0.85)

        fp.Shape = build_vprong_solid(
            tip_x=tx, tip_y=ty, angle_deg=ang,
            height=h, z_base=zb,
            wall_thickness=wall, wing_length=wing
        )

        vol = fp.Shape.Volume if (fp.Shape and not fp.Shape.isNull()) else 0.0
        alloy = getattr(fp, "Alloy", "14k_Yellow")
        if hasattr(fp, "WeightGrams"):
            fp.WeightGrams = metals.calculate_metal_weight(vol, alloy)


class ViewProviderVProng:
    """View provider for V-prong setting."""

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
        return ":/icons/Jewelry_VProng.svg"

    def getDefaultDisplayMode(self):
        return "Shaded"

    def getDisplayModes(self, vobj):
        return ["Shaded", "Wireframe"]

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None


def make_vprong(doc, label="VProng", tip_x=2.0, tip_y=0.0, angle_deg=0.0,
                height=1.4, z_base=-1.0, wall_thickness=0.6, wing_length=0.85,
                alloy="14k_Yellow"):
    """Factory creating a V-Prong object in the document."""
    obj = doc.addObject("Part::FeaturePython", label)
    VProngProxy(obj)

    obj.addProperty("App::PropertyFloat", "TipX", "Placement", "Tip X position in mm")
    obj.TipX = tip_x

    obj.addProperty("App::PropertyFloat", "TipY", "Placement", "Tip Y position in mm")
    obj.TipY = tip_y

    obj.addProperty("App::PropertyFloat", "Angle", "Placement", "Rotation angle degrees")
    obj.Angle = angle_deg

    obj.addProperty("App::PropertyFloatConstraint", "Height", "Dimensions", "Prong top elevation in mm")
    obj.Height = (height, 0.1, 10.0, 0.1)

    obj.addProperty("App::PropertyFloatConstraint", "ZBase", "Dimensions", "Prong base elevation in mm")
    obj.ZBase = (z_base, -10.0, 0.0, 0.1)

    obj.addProperty("App::PropertyFloatConstraint", "WallThickness", "Dimensions", "Prong wall thickness in mm")
    obj.WallThickness = (wall_thickness, 0.2, 3.0, 0.05)

    obj.addProperty("App::PropertyFloatConstraint", "WingLength", "Dimensions", "Wing extension length in mm")
    obj.WingLength = (wing_length, 0.2, 5.0, 0.05)

    obj.addProperty("App::PropertyEnumeration", "Alloy", "Material", "Metal alloy")
    obj.Alloy = metals.list_alloys()
    obj.Alloy = alloy

    obj.addProperty("App::PropertyFloat", "WeightGrams", "Calculations", "Estimated metal weight (grams)", 1)

    if FreeCAD.GuiUp:
        vp = ViewProviderVProng(obj.ViewObject)
        vp.update_appearance(obj)

    obj.recompute()
    return obj
