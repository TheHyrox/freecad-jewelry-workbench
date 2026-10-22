# SPDX-License-Identifier: LGPL-2.1-or-later
"""Parametric Prong and Collet Setting Feature for FreeCAD."""

import math
import FreeCAD
import Part
from freecad.jewelry.core import metals

PRONG_STYLES = ["Button", "Claw", "Straight"]


def build_corner_prong_setting(length: float = 9.0, width: float = 7.0,
                               height: float = 2.2, z_base: float = -2.5,
                               prong_diameter: float = 1.0,
                               prong_count: int = 4,
                               corner_prongs: bool = True,
                               style: str = "Button",
                               add_base_rail: bool = True) -> Part.Solid:
    """
    Build a prong collet setting with exact bearing overlap and connected claw tips.
    """
    rx = length / 2.0
    ry = width / 2.0
    r_prong = prong_diameter / 2.0

    if corner_prongs and prong_count == 4:
        angles = [math.pi / 4.0, 3.0 * math.pi / 4.0, 5.0 * math.pi / 4.0, 7.0 * math.pi / 4.0]
    else:
        angles = [i * (2.0 * math.pi / prong_count) for i in range(prong_count)]

    bot_pts = []
    prong_solids = []

    for a in angles:
        # Stone perimeter point at girdle level
        sx = rx * math.cos(a)
        sy = ry * math.sin(a)

        inward = FreeCAD.Vector(-math.cos(a), -math.sin(a), 0).normalize()

        # Center of prong at girdle sits with bearing overlap (hugging the stone tightly)
        p_girdle = FreeCAD.Vector(sx, sy, 0.0) + inward * (r_prong * 0.25)

        # Base sits inward to form tapered basket
        p_bot = FreeCAD.Vector(sx * 0.85, sy * 0.85, z_base)
        bot_pts.append(p_bot)

        if style == "Claw":
            # Elbow knuckle just above stone girdle
            p_elbow = p_girdle + FreeCAD.Vector(0, 0, max(0.3, height * 0.5))

            # Post cylinder from base to elbow
            axis_post = p_elbow - p_bot
            post = Part.makeCylinder(r_prong, axis_post.Length, p_bot, axis_post.normalize())

            # Seamless elbow sphere guaranteeing continuous connection
            elbow_sphere = Part.makeSphere(r_prong, p_elbow)

            # Claw tip curves inward over the stone crown towards table
            claw_reach = r_prong * 1.6
            claw_tip = p_elbow + inward * claw_reach + FreeCAD.Vector(0, 0, -r_prong * 0.35)
            axis_claw = claw_tip - p_elbow

            # Tapered claw cone
            claw_cone = Part.makeCone(r_prong * 0.95, r_prong * 0.2, axis_claw.Length, p_elbow, axis_claw.normalize())
            tip_bead = Part.makeSphere(r_prong * 0.2, claw_tip)

            prong = post.fuse(elbow_sphere).fuse(claw_cone).fuse(tip_bead)

        elif style == "Button":
            # Post leans slightly inward to clasp stone crown
            p_top = p_girdle + inward * (r_prong * 0.2) + FreeCAD.Vector(0, 0, height)
            axis_post = p_top - p_bot
            post = Part.makeCylinder(r_prong, axis_post.Length, p_bot, axis_post.normalize())
            dome = Part.makeSphere(r_prong, p_top)
            prong = post.fuse(dome)

        else:  # Straight
            p_top = p_girdle + FreeCAD.Vector(0, 0, height)
            axis_post = p_top - p_bot
            prong = Part.makeCylinder(r_prong, axis_post.Length, p_bot, axis_post.normalize())

        prong_solids.append(prong)

    parts_to_fuse = list(prong_solids)

    # Base under-gallery rail connecting prongs
    if add_base_rail and len(bot_pts) > 1:
        for i in range(len(bot_pts)):
            p_a = bot_pts[i]
            p_b = bot_pts[(i + 1) % len(bot_pts)]
            vec = p_b - p_a
            rail = Part.makeCylinder(r_prong * 0.75, vec.Length, p_a, vec.normalize())
            parts_to_fuse.append(rail)

    collet = parts_to_fuse[0]
    for p in parts_to_fuse[1:]:
        collet = collet.fuse(p)

    collet.fix(1e-4, 1e-4, 1e-4)
    if collet.Solids:
        return collet.Solids[0]
    return collet


class ProngProxy:
    """Proxy object implementing parametric Prong Setting."""

    def __init__(self, fp):
        fp.Proxy = self
        self.Type = "Jewelry::Prongs"

    def onChanged(self, fp, prop):
        if prop == "TargetGem":
            gem = getattr(fp, "TargetGem", None)
            mode = 1 if (gem is not None) else 0
            for p in ("Length", "Width", "Height", "ZBase"):
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
            height = depth * 0.35 + 0.4
            z_base = -depth * 0.55
            # Sync values to property fields for transparency
            fp.Length = length
            fp.Width = width
            fp.Height = height
            fp.ZBase = z_base
        else:
            length = getattr(fp, "Length", 9.0)
            width = getattr(fp, "Width", 7.0)
            height = getattr(fp, "Height", 2.2)
            z_base = getattr(fp, "ZBase", -2.5)

        dia = getattr(fp, "ProngDiameter", 1.0)
        count = getattr(fp, "ProngCount", 4)
        corner = getattr(fp, "CornerProngs", True)
        style = getattr(fp, "ProngStyle", "Button")
        rail = getattr(fp, "BaseRail", True)

        fp.Shape = build_corner_prong_setting(
            length=length, width=width,
            height=height, z_base=z_base,
            prong_diameter=dia, prong_count=count,
            corner_prongs=corner, style=style,
            add_base_rail=rail
        )

        vol = fp.Shape.Volume if (fp.Shape and not fp.Shape.isNull()) else 0.0
        alloy = getattr(fp, "Alloy", "14k_Yellow")
        if hasattr(fp, "WeightGrams"):
            fp.WeightGrams = metals.calculate_metal_weight(vol, alloy)


class ViewProviderProng:
    """View provider for prong settings."""

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
        return ":/icons/Jewelry_Prongs.svg"

    def getDefaultDisplayMode(self):
        return "Shaded"

    def getDisplayModes(self, vobj):
        return ["Shaded", "Wireframe"]

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None


def make_prong_setting(doc, label="ProngSetting", gem=None, length=9.0, width=7.0,
                       height=2.2, z_base=-2.5, prong_dia=1.0, count=4,
                       corner_prongs=True, style="Button", base_rail=True,
                       alloy="14k_Yellow"):
    """Factory creating a Prong Setting object in the document."""
    obj = doc.addObject("Part::FeaturePython", label)
    ProngProxy(obj)

    obj.addProperty("App::PropertyLink", "TargetGem", "Target", "Optional gem driving dimensions")
    if gem is not None:
        obj.TargetGem = gem

    obj.addProperty("App::PropertyFloatConstraint", "Length", "Dimensions", "Setting length in mm")
    obj.Length = (length, 0.5, 50.0, 0.1)

    obj.addProperty("App::PropertyFloatConstraint", "Width", "Dimensions", "Setting width in mm")
    obj.Width = (width, 0.5, 50.0, 0.1)

    obj.addProperty("App::PropertyFloatConstraint", "Height", "Dimensions", "Prong top elevation in mm")
    obj.Height = (height, 0.1, 20.0, 0.1)

    obj.addProperty("App::PropertyFloatConstraint", "ZBase", "Dimensions", "Base rail elevation in mm")
    obj.ZBase = (z_base, -20.0, 0.0, 0.1)

    # If target gem is already provided, gray out dimension properties
    if gem is not None:
        for p in ("Length", "Width", "Height", "ZBase"):
            obj.setEditorMode(p, 1)

    obj.addProperty("App::PropertyFloatConstraint", "ProngDiameter", "Prongs", "Prong wire diameter in mm")
    obj.ProngDiameter = (prong_dia, 0.4, 4.0, 0.05)

    obj.addProperty("App::PropertyIntegerConstraint", "ProngCount", "Prongs", "Number of prongs")
    obj.ProngCount = (count, 2, 12, 1)

    obj.addProperty("App::PropertyBool", "CornerProngs", "Prongs", "Position prongs at corners (45 deg)")
    obj.CornerProngs = corner_prongs

    obj.addProperty("App::PropertyEnumeration", "ProngStyle", "Prongs", "Tip geometry style")
    obj.ProngStyle = PRONG_STYLES
    obj.ProngStyle = style

    obj.addProperty("App::PropertyBool", "BaseRail", "Gallery", "Include under-gallery base rail")
    obj.BaseRail = base_rail

    obj.addProperty("App::PropertyEnumeration", "Alloy", "Material", "Metal alloy")
    obj.Alloy = metals.list_alloys()
    obj.Alloy = alloy

    obj.addProperty("App::PropertyFloat", "WeightGrams", "Calculations", "Estimated metal weight (grams)", 1)

    if FreeCAD.GuiUp:
        vp = ViewProviderProng(obj.ViewObject)
        vp.update_appearance(obj)

    obj.recompute()
    return obj
