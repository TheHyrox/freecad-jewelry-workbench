# SPDX-License-Identifier: LGPL-2.1-or-later
"""Parametric Gemstone Bearing and Seat Cutter Feature for FreeCAD."""

import math
import FreeCAD
import Part


def build_seat_cutter(length: float = 6.5, width: float = 6.5,
                      depth: float = 4.0, clearance: float = 0.08,
                      girdle_height: float = 0.4,
                      drill_radius: float = 0.5,
                      drill_depth: float = 5.0) -> Part.Solid:
    """
    Build a solid cutter tool representing the gemstone seat:
    - Girdle notch disk with clearance margin
    - Pavilion clearance cone
    - Culet piercing drill
    """
    rx = (length / 2.0) + clearance
    ry = (width / 2.0) + clearance
    z_gtop = girdle_height / 2.0
    z_gbot = -girdle_height / 2.0
    z_culet = -depth * 0.60

    pts_gtop = []
    pts_gbot = []
    for i in range(24):
        a = i * (2.0 * math.pi / 24.0)
        pts_gtop.append(FreeCAD.Vector(rx * math.cos(a), ry * math.sin(a), z_gtop))
        pts_gbot.append(FreeCAD.Vector(rx * math.cos(a), ry * math.sin(a), z_gbot))
    pts_gtop.append(pts_gtop[0])
    pts_gbot.append(pts_gbot[0])

    w_gtop = Part.Wire(Part.makePolygon(pts_gtop))
    w_gbot = Part.Wire(Part.makePolygon(pts_gbot))
    girdle_cutter = Part.makeLoft([w_gtop, w_gbot], True, True)

    pts_culet = []
    for i in range(24):
        a = i * (2.0 * math.pi / 24.0)
        pts_culet.append(FreeCAD.Vector(drill_radius * math.cos(a), drill_radius * math.sin(a), z_culet))
    pts_culet.append(pts_culet[0])
    w_culet = Part.Wire(Part.makePolygon(pts_culet))
    pav_cutter = Part.makeLoft([w_gbot, w_culet], True, True)

    drill = Part.makeCylinder(drill_radius, drill_depth, FreeCAD.Vector(0, 0, z_culet - drill_depth + 0.1), FreeCAD.Vector(0, 0, 1))

    cutter = girdle_cutter.fuse(pav_cutter).fuse(drill)
    cutter.fix(1e-4, 1e-4, 1e-4)
    if cutter.Solids:
        return cutter.Solids[0]
    return cutter


class CutterProxy:
    """Proxy object implementing parametric Seat Cutter."""

    def __init__(self, fp):
        fp.Proxy = self
        self.Type = "Jewelry::SeatCutter"

    def onChanged(self, fp, prop):
        if prop == "TargetGem":
            gem = getattr(fp, "TargetGem", None)
            mode = 1 if (gem is not None) else 0
            for p in ("Length", "Width", "Depth"):
                if hasattr(fp, p):
                    fp.setEditorMode(p, mode)

    def execute(self, fp):
        gem = getattr(fp, "TargetGem", None)
        if gem is not None and hasattr(gem, "Width"):
            length = getattr(gem, "Length", gem.Width)
            width = gem.Width
            depth = getattr(gem, "Depth", width * 0.6)
            if depth <= 0:
                depth = width * 0.6
            fp.Length = length
            fp.Width = width
            fp.Depth = depth
        else:
            length = getattr(fp, "Length", 6.5)
            width = getattr(fp, "Width", 6.5)
            depth = getattr(fp, "Depth", 4.0)

        clearance = getattr(fp, "Clearance", 0.08)
        gh = getattr(fp, "GirdleHeight", 0.4)
        dr = getattr(fp, "DrillRadius", 0.5)

        fp.Shape = build_seat_cutter(
            length=length, width=width, depth=depth,
            clearance=clearance, girdle_height=gh,
            drill_radius=dr
        )


class ViewProviderCutter:
    """View provider for gemstone seat cutter tool."""

    def __init__(self, vobj):
        vobj.Proxy = self

    def attach(self, vobj):
        self.ViewObject = vobj
        self.update_appearance(vobj)

    def updateData(self, fp, prop):
        if prop == "Shape" and hasattr(fp, "ViewObject") and fp.ViewObject is not None:
            self.update_appearance(fp.ViewObject)

    def update_appearance(self, vobj):
        # Display as a translucent orange/coral cutting tool
        vobj.ShapeColor = (1.0, 0.40, 0.20)
        vobj.Transparency = 50
        vobj.DisplayMode = "Shaded"
        vobj.Visibility = True

    def onChanged(self, vobj, prop):
        pass

    def getIcon(self):
        return ":/icons/Jewelry_Cutter.svg"

    def getDefaultDisplayMode(self):
        return "Shaded"

    def getDisplayModes(self, vobj):
        return ["Shaded", "Wireframe"]

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None


def make_seat_cutter(doc, label="SeatCutter", gem=None, length=6.5, width=6.5, depth=4.0, clearance=0.08):
    """Factory creating a Seat Cutter object in the document."""
    obj = doc.addObject("Part::FeaturePython", label)
    CutterProxy(obj)

    obj.addProperty("App::PropertyLink", "TargetGem", "Target", "Optional gem driving dimensions")
    if gem is not None:
        obj.TargetGem = gem

    obj.addProperty("App::PropertyFloatConstraint", "Length", "Dimensions", "Cutter length in mm")
    obj.Length = (length, 0.5, 50.0, 0.1)

    obj.addProperty("App::PropertyFloatConstraint", "Width", "Dimensions", "Cutter width in mm")
    obj.Width = (width, 0.5, 50.0, 0.1)

    obj.addProperty("App::PropertyFloatConstraint", "Depth", "Dimensions", "Cutter depth in mm")
    obj.Depth = (depth, 0.5, 50.0, 0.1)

    if gem is not None:
        for p in ("Length", "Width", "Depth"):
            obj.setEditorMode(p, 1)

    obj.addProperty("App::PropertyFloatConstraint", "Clearance", "Tolerances", "Girdle offset clearance in mm")
    obj.Clearance = (clearance, 0.0, 1.0, 0.01)

    obj.addProperty("App::PropertyFloatConstraint", "GirdleHeight", "Dimensions", "Girdle cut height in mm")
    obj.GirdleHeight = (0.4, 0.1, 2.0, 0.05)

    obj.addProperty("App::PropertyFloatConstraint", "DrillRadius", "Dimensions", "Culet pierce drill radius in mm")
    obj.DrillRadius = (0.5, 0.1, 3.0, 0.05)

    if FreeCAD.GuiUp:
        vp = ViewProviderCutter(obj.ViewObject)
        vp.update_appearance(obj.ViewObject)

    obj.recompute()
    return obj
