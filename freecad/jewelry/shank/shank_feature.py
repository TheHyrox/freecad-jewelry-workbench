# SPDX-License-Identifier: LGPL-2.1-or-later
"""Parametric Ring Shank Feature for FreeCAD."""

import math
import FreeCAD
import Part
from freecad.jewelry.core import sizing, metals

PROFILE_TYPES = ["ComfortFit", "HalfRound", "RoundWire", "Flat"]
SIZING_STANDARDS = ["US", "EU", "UK", "Custom"]


def _make_profile_wire(cx, cz, nx, nz, w, t, profile_type="ComfortFit"):
    radial = FreeCAD.Vector(nx, 0, nz)
    axial = FreeCAD.Vector(0, 1, 0)
    p1 = FreeCAD.Vector(cx, -w / 2.0, cz)
    p2 = FreeCAD.Vector(cx, w / 2.0, cz)

    if profile_type == "RoundWire":
        c = FreeCAD.Vector(cx, 0, cz) + radial * (t / 2.0)
        circ = Part.Circle(c, FreeCAD.Vector(nx, 0, nz).cross(axial), t / 2.0)
        return Part.Wire(circ.toShape())

    elif profile_type == "ComfortFit":
        p_mid_outer = FreeCAD.Vector(cx, 0, cz) + radial * t
        p3 = FreeCAD.Vector(cx, w / 2.0, cz) + radial * (t * 0.65)
        p4 = FreeCAD.Vector(cx, -w / 2.0, cz) + radial * (t * 0.65)

        arc_outer = Part.Arc(p4, p_mid_outer, p3).toShape()
        e_right = Part.makeLine(p3, p2)
        e_inner = Part.makeLine(p2, p1)
        e_left = Part.makeLine(p1, p4)
        return Part.Wire([e_inner, e_right, arc_outer, e_left])

    elif profile_type == "HalfRound":
        p_mid_outer = FreeCAD.Vector(cx, 0, cz) + radial * t
        arc_outer = Part.Arc(p2, p_mid_outer, p1).toShape()
        e_inner = Part.makeLine(p1, p2)
        return Part.Wire([e_inner, arc_outer])

    else:  # Flat
        p3 = FreeCAD.Vector(cx, w / 2.0, cz) + radial * t
        p4 = FreeCAD.Vector(cx, -w / 2.0, cz) + radial * t
        return Part.makePolygon([p1, p2, p3, p4, p1])


def build_shank_solid(inner_radius: float = 8.46,
                       width_bottom: float = 2.0, width_shoulder: float = 1.4,
                       thickness_bottom: float = 1.6, thickness_shoulder: float = 1.2,
                       profile_type: str = "ComfortFit",
                       open_head: bool = False, head_gap_degrees: float = 30.0) -> Part.Solid:
    """Build a tapered, smooth ring shank solid."""
    max_theta = math.pi / 2.0
    if open_head:
        max_theta -= math.radians(head_gap_degrees / 2.0)

    n_steps = 14
    wires = []
    for i in range(n_steps):
        theta = -math.pi / 2.0 + (max_theta + math.pi / 2.0) * i / (n_steps - 1)
        k = (theta + math.pi / 2.0) / (max_theta + math.pi / 2.0)
        t_blend = (1.0 - math.cos(k * math.pi)) / 2.0
        w = width_bottom * (1.0 - t_blend) + width_shoulder * t_blend
        t = thickness_bottom * (1.0 - t_blend) + thickness_shoulder * t_blend

        cx = inner_radius * math.cos(theta)
        cz = inner_radius * math.sin(theta)
        nx = math.cos(theta)
        nz = math.sin(theta)

        wire = _make_profile_wire(cx, cz, nx, nz, w, t, profile_type)
        wires.append(wire)

    half = Part.makeLoft(wires, True, False)
    mirrored = half.mirror(FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(1, 0, 0))
    shank = half.fuse(mirrored)
    shank.fix(1e-4, 1e-4, 1e-4)
    if shank.Solids:
        return shank.Solids[0]
    return shank


class ShankProxy:
    """Proxy object implementing parametric Ring Shank."""

    def __init__(self, fp):
        fp.Proxy = self
        self.Type = "Jewelry::Shank"

    def execute(self, fp):
        standard = getattr(fp, "SizeStandard", "US")
        size_str = getattr(fp, "RingSize", "6.5")
        r_in = sizing.get_inner_radius(str(size_str), standard)

        wb = getattr(fp, "WidthBottom", 2.0)
        ws = getattr(fp, "WidthShoulder", 1.4)
        tb = getattr(fp, "ThicknessBottom", 1.6)
        ts = getattr(fp, "ThicknessShoulder", 1.2)
        pt = getattr(fp, "ProfileType", "ComfortFit")
        oh = getattr(fp, "OpenHead", False)
        gap = getattr(fp, "HeadGapAngle", 30.0)

        fp.Shape = build_shank_solid(
            inner_radius=r_in,
            width_bottom=wb, width_shoulder=ws,
            thickness_bottom=tb, thickness_shoulder=ts,
            profile_type=pt, open_head=oh, head_gap_degrees=gap
        )

        vol = fp.Shape.Volume if (fp.Shape and not fp.Shape.isNull()) else 0.0
        alloy = getattr(fp, "Alloy", "14k_Yellow")
        if hasattr(fp, "WeightGrams"):
            fp.WeightGrams = metals.calculate_metal_weight(vol, alloy)


class ViewProviderShank:
    """View provider for ring shank."""

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
        return ":/icons/Jewelry_Shank.svg"

    def getDefaultDisplayMode(self):
        return "Shaded"

    def getDisplayModes(self, vobj):
        return ["Shaded", "Wireframe"]

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None


def make_shank(doc, label="Shank", standard="US", ring_size="6.5",
               width_bottom=2.0, width_shoulder=1.4,
               thickness_bottom=1.6, thickness_shoulder=1.2,
               profile_type="ComfortFit", alloy="14k_Yellow",
               open_head=False, head_gap_angle=30.0):
    """Factory creating a Ring Shank object in the document."""
    obj = doc.addObject("Part::FeaturePython", label)
    ShankProxy(obj)

    obj.addProperty("App::PropertyEnumeration", "SizeStandard", "Finger Sizing", "Ring sizing standard")
    obj.SizeStandard = SIZING_STANDARDS
    obj.SizeStandard = standard

    obj.addProperty("App::PropertyString", "RingSize", "Finger Sizing", "Ring size string (e.g. 6.5 or 52)")
    obj.RingSize = str(ring_size)

    obj.addProperty("App::PropertyEnumeration", "ProfileType", "Profile", "Cross-section shape")
    obj.ProfileType = PROFILE_TYPES
    obj.ProfileType = profile_type

    obj.addProperty("App::PropertyFloatConstraint", "WidthBottom", "Dimensions", "Band width at finger base (mm)")
    obj.WidthBottom = (width_bottom, 0.5, 20.0, 0.1)

    obj.addProperty("App::PropertyFloatConstraint", "WidthShoulder", "Dimensions", "Band width at shoulders (mm)")
    obj.WidthShoulder = (width_shoulder, 0.5, 20.0, 0.1)

    obj.addProperty("App::PropertyFloatConstraint", "ThicknessBottom", "Dimensions", "Band thickness at base (mm)")
    obj.ThicknessBottom = (thickness_bottom, 0.5, 10.0, 0.1)

    obj.addProperty("App::PropertyFloatConstraint", "ThicknessShoulder", "Dimensions", "Band thickness at shoulders (mm)")
    obj.ThicknessShoulder = (thickness_shoulder, 0.5, 10.0, 0.1)

    obj.addProperty("App::PropertyBool", "OpenHead", "Head Setting", "Leave opening at the top for gemstone cluster")
    obj.OpenHead = open_head

    obj.addProperty("App::PropertyFloatConstraint", "HeadGapAngle", "Head Setting", "Opening angle degrees at top")
    obj.HeadGapAngle = (head_gap_angle, 0.0, 120.0, 1.0)

    obj.addProperty("App::PropertyEnumeration", "Alloy", "Material", "Metal alloy")
    obj.Alloy = metals.list_alloys()
    obj.Alloy = alloy

    obj.addProperty("App::PropertyFloat", "WeightGrams", "Calculations", "Estimated metal weight (grams)", 1)

    if FreeCAD.GuiUp:
        vp = ViewProviderShank(obj.ViewObject)
        vp.update_appearance(obj)

    obj.recompute()
    return obj
