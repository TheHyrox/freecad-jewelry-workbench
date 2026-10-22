# SPDX-License-Identifier: LGPL-2.1-or-later
"""Parametric gemstone cut geometry generators for jewelry modeling."""

import math
import FreeCAD
import Part


def _make_polygon_wire(rx: float, ry: float, z: float, n: int = 24) -> Part.Wire:
    """Generate an elliptical polygon wire with n vertices at elevation z."""
    pts = []
    for i in range(n):
        a = i * (2.0 * math.pi / n)
        pts.append(FreeCAD.Vector(rx * math.cos(a), ry * math.sin(a), z))
    pts.append(pts[0])
    return Part.Wire(Part.makePolygon(pts))


def _make_marquise_wire(rx: float, ry: float, z: float, n_pts: int = 24) -> Part.Wire:
    """Generate a navette/marquise wire with pointed ends at +-X at elevation z."""
    pts = []
    half = n_pts // 2
    for i in range(half):
        t = -1.0 + 2.0 * i / (half - 1)
        x = rx * t
        y = ry * math.cos(t * math.pi / 2.0)
        pts.append(FreeCAD.Vector(x, y, z))
    for i in range(1, half - 1):
        t = 1.0 - 2.0 * i / (half - 1)
        x = rx * t
        y = -ry * math.cos(t * math.pi / 2.0)
        pts.append(FreeCAD.Vector(x, y, z))
    pts.append(pts[0])
    return Part.Wire(Part.makePolygon(pts))


def _make_rounded_pear_wire(rx: float, ry: float, z: float, n_pts: int = 24) -> Part.Wire:
    """Generate a teardrop/pear wire with smooth rounded curvature throughout."""
    pts = []
    for i in range(n_pts):
        a = i * (2.0 * math.pi / n_pts)
        t = (math.cos(a) + 1.0) / 2.0
        x = rx * math.cos(a)
        y = ry * math.sin(a) * (1.0 - 0.42 * t)
        pts.append(FreeCAD.Vector(x, y, z))
    pts.append(pts[0])
    return Part.Wire(Part.makePolygon(pts))


def _make_sharp_pear_wire(rx: float, ry: float, z: float, n_pts: int = 36) -> Part.Wire:
    """
    Generate a true water drop / teardrop contour wire:
    - Bulbous rounded bottom at -X
    - Elegantly curved waist tapering into a crisp sharp pointed apex at +X
    """
    pts = []
    for i in range(n_pts):
        t = -math.pi / 2.0 + (2.0 * math.pi) * i / n_pts
        # Piriform water drop parameterization:
        # u in [0, 1]: u = 0 at sharp tip (+rx), u = 1 at rounded bulb (-rx)
        u = (1.0 + math.sin(t)) / 2.0
        x = rx * (1.0 - 2.0 * u)
        # Smoothly curved droplet waist flowing to pointed apex
        y = ry * math.cos(t) * math.sqrt(u)
        pts.append(FreeCAD.Vector(x, y, z))

    pts.append(pts[0])
    return Part.Wire(Part.makePolygon(pts))


def _make_trillion_wire(r: float, z: float, n_pts: int = 24) -> Part.Wire:
    """Generate an equilateral trillion wire with convexly bowed arcs."""
    verts = [
        FreeCAD.Vector(0, r, z),
        FreeCAD.Vector(-r * math.cos(math.pi / 6.0), -r * math.sin(math.pi / 6.0), z),
        FreeCAD.Vector(r * math.cos(math.pi / 6.0), -r * math.sin(math.pi / 6.0), z)
    ]
    pts = []
    bulge = r * 0.15
    for i in range(3):
        v1 = verts[i]
        v2 = verts[(i + 1) % 3]
        mid = (v1 + v2) * 0.5
        normal = FreeCAD.Vector(mid.x, mid.y, 0).normalize()
        arc_mid = mid + normal * bulge
        arc = Part.Arc(v1, arc_mid, v2)
        for j in range(8):
            param = arc.FirstParameter + (arc.LastParameter - arc.FirstParameter) * j / 8.0
            pts.append(arc.value(param))
    pts.append(pts[0])
    return Part.Wire(Part.makePolygon(pts))


def _make_heart_wire(rx: float, ry: float, z: float, n_pts: int = 28) -> Part.Wire:
    """Generate a heart contour wire with central cleft and sharp pointed apex."""
    pts = []
    for i in range(n_pts):
        t = i * (2.0 * math.pi / n_pts)
        x = rx * (math.cos(t) - 0.4 * abs(math.sin(t)) * (1.0 - math.cos(t)))
        y = ry * math.sin(t) * (0.8 + 0.3 * (1.0 - math.cos(t)))
        pts.append(FreeCAD.Vector(x, y, z))
    pts.append(pts[0])
    return Part.Wire(Part.makePolygon(pts))


def _make_octagon_wire(rx: float, ry: float, z: float, corner_ratio: float = 0.3) -> Part.Wire:
    """Generate an 8-sided polygon wire with diagonal corner chamfers."""
    c = min(rx, ry) * corner_ratio
    pts = [
        FreeCAD.Vector(rx, ry - c, z),
        FreeCAD.Vector(rx - c, ry, z),
        FreeCAD.Vector(-rx + c, ry, z),
        FreeCAD.Vector(-rx, ry - c, z),
        FreeCAD.Vector(-rx, -ry + c, z),
        FreeCAD.Vector(-rx + c, -ry, z),
        FreeCAD.Vector(rx - c, -ry, z),
        FreeCAD.Vector(rx, -ry + c, z),
        FreeCAD.Vector(rx, ry - c, z)
    ]
    return Part.Wire(Part.makePolygon(pts))


def _make_cushion_wire(rx: float, ry: float, z: float, n_pts: int = 24) -> Part.Wire:
    """Generate a squircle/cushion polygon wire with softened pillow sides."""
    pts = []
    for i in range(n_pts):
        a = i * (2.0 * math.pi / n_pts)
        cos_a = math.cos(a)
        sin_a = math.sin(a)
        x = rx * math.copysign(abs(cos_a) ** (2.0 / 2.8), cos_a)
        y = ry * math.copysign(abs(sin_a) ** (2.0 / 2.8), sin_a)
        pts.append(FreeCAD.Vector(x, y, z))
    pts.append(pts[0])
    return Part.Wire(Part.makePolygon(pts))


def _finalize_solid(shape):
    """Ensure the returned shape is a Part.Solid."""
    if shape.Solids:
        s = shape.Solids[0]
    elif isinstance(shape, Part.Solid):
        s = shape
    else:
        s = Part.makeSolid(shape)
    s.fix(1e-4, 1e-4, 1e-4)
    return s


def _build_lofted_gem(wire_func, rx: float, ry: float, depth: float,
                      table_ratio: float = 0.55, crown_ratio: float = 0.14,
                      girdle_ratio: float = 0.035, is_keel: bool = False,
                      flat_back: bool = False) -> Part.Solid:
    """Generic builder that creates a watertight faceted gemstone solid."""
    if flat_back:
        # Flat-back stone (no pavilion): flat base at Z = 0
        h_crown = depth * 0.75 if (depth and depth > 0) else (ry * 2.0 * crown_ratio)
        h_girdle = max(0.2, (ry * 2.0 * girdle_ratio))
        z_gbot = 0.0
        z_gtop = h_girdle
        z_tab = z_gtop + h_crown

        w_tab = wire_func(rx * table_ratio, ry * table_ratio, z_tab)
        w_gtop = wire_func(rx, ry, z_gtop)
        w_gbot = wire_func(rx, ry, z_gbot)

        gem = Part.makeLoft([w_tab, w_gtop, w_gbot], True, True)
        return _finalize_solid(gem)

    h_crown = depth * crown_ratio / 0.14 * 0.33
    h_girdle = depth * girdle_ratio / 0.035 * 0.05
    h_pav = depth - h_crown - h_girdle

    z_gtop = h_girdle / 2.0
    z_gbot = -h_girdle / 2.0
    z_tab = z_gtop + h_crown
    z_culet = z_gbot - h_pav

    w_tab = wire_func(rx * table_ratio, ry * table_ratio, z_tab)
    w_gtop = wire_func(rx, ry, z_gtop)
    w_gbot = wire_func(rx, ry, z_gbot)

    if is_keel and (rx > ry * 1.05):
        w_culet = wire_func(max(0.1, (rx - ry) * 0.55), 0.08, z_culet)
    else:
        w_culet = wire_func(rx * 0.04, ry * 0.04, z_culet)

    crown = Part.makeLoft([w_tab, w_gtop], True, True)
    girdle = Part.makeLoft([w_gtop, w_gbot], True, True)
    pav = Part.makeLoft([w_gbot, w_culet], True, True)

    gem = crown.fuse(girdle).fuse(pav)
    return _finalize_solid(gem)


def make_round_brilliant(diameter: float = 6.5, depth: float = None, flat_back: bool = False) -> Part.Solid:
    """Generate a Round Brilliant gemstone solid."""
    r = diameter / 2.0
    if depth is None or depth <= 0:
        depth = diameter * 0.61
    return _build_lofted_gem(lambda rx, ry, z: _make_polygon_wire(rx, ry, z, 24),
                             r, r, depth, table_ratio=0.57, is_keel=False, flat_back=flat_back)


def make_oval_cut(length: float = 9.0, width: float = 7.0, depth: float = None, flat_back: bool = False) -> Part.Solid:
    """Generate an Oval mixed cut gemstone solid."""
    rx = length / 2.0
    ry = width / 2.0
    if depth is None or depth <= 0:
        depth = width * 0.62
    return _build_lofted_gem(_make_polygon_wire, rx, ry, depth, table_ratio=0.58, is_keel=True, flat_back=flat_back)


def make_marquise_cut(length: float = 4.0, width: float = 2.0, depth: float = None, flat_back: bool = False) -> Part.Solid:
    """Generate a Marquise (navette) cut gemstone solid."""
    rx = length / 2.0
    ry = width / 2.0
    if depth is None or depth <= 0:
        depth = width * 0.60
    return _build_lofted_gem(_make_marquise_wire, rx, ry, depth, table_ratio=0.55, is_keel=True, flat_back=flat_back)


def make_rounded_pear_cut(length: float = 6.0, width: float = 4.0, depth: float = None, flat_back: bool = False) -> Part.Solid:
    """Generate a Rounded Pear (smooth teardrop) cut gemstone solid."""
    rx = length / 2.0
    ry = width / 2.0
    if depth is None or depth <= 0:
        depth = width * 0.62
    return _build_lofted_gem(_make_rounded_pear_wire, rx, ry, depth, table_ratio=0.56, is_keel=False, flat_back=flat_back)


def make_sharp_pear_cut(length: float = 6.0, width: float = 4.0, depth: float = None, flat_back: bool = False) -> Part.Solid:
    """Generate a Sharp Pear (water droplet) cut gemstone solid."""
    rx = length / 2.0
    ry = width / 2.0
    if depth is None or depth <= 0:
        depth = width * 0.62
    return _build_lofted_gem(_make_sharp_pear_wire, rx, ry, depth, table_ratio=0.56, is_keel=False, flat_back=flat_back)


def make_trillion_cut(side: float = 5.0, depth: float = None, flat_back: bool = False) -> Part.Solid:
    """Generate a Trillion (trilliant triangular) cut gemstone solid."""
    r = side / math.sqrt(3.0)
    if depth is None or depth <= 0:
        depth = side * 0.55
    return _build_lofted_gem(lambda rx, ry, z: _make_trillion_wire(rx, z),
                             r, r, depth, table_ratio=0.55, is_keel=False, flat_back=flat_back)


def make_heart_cut(length: float = 6.0, width: float = 6.0, depth: float = None, flat_back: bool = False) -> Part.Solid:
    """Generate a Heart cut gemstone solid with cleft and pointed tip."""
    rx = length / 2.0
    ry = width / 2.0
    if depth is None or depth <= 0:
        depth = width * 0.60
    return _build_lofted_gem(_make_heart_wire, rx, ry, depth, table_ratio=0.54, is_keel=False, flat_back=flat_back)


def make_octagon_cut(length: float = 7.0, width: float = 7.0, depth: float = None, flat_back: bool = False) -> Part.Solid:
    """Generate an Octagon cut gemstone solid."""
    rx = length / 2.0
    ry = width / 2.0
    if depth is None or depth <= 0:
        depth = width * 0.62
    return _build_lofted_gem(lambda rx, ry, z: _make_octagon_wire(rx, ry, z, corner_ratio=0.3),
                             rx, ry, depth, table_ratio=0.58, is_keel=False, flat_back=flat_back)


def make_emerald_cut(length: float = 8.0, width: float = 6.0, depth: float = None, flat_back: bool = False) -> Part.Solid:
    """Generate a classic Emerald step-cut gemstone solid."""
    rx = length / 2.0
    ry = width / 2.0
    if depth is None or depth <= 0:
        depth = width * 0.65
    return _build_lofted_gem(lambda rx, ry, z: _make_octagon_wire(rx, ry, z, corner_ratio=0.25),
                             rx, ry, depth, table_ratio=0.60, is_keel=True, flat_back=flat_back)


def make_cushion_cut(length: float = 6.0, width: float = 6.0, depth: float = None, flat_back: bool = False) -> Part.Solid:
    """Generate a Cushion cut gemstone solid."""
    rx = length / 2.0
    ry = width / 2.0
    if depth is None or depth <= 0:
        depth = width * 0.65
    return _build_lofted_gem(_make_cushion_wire, rx, ry, depth, table_ratio=0.60, is_keel=False, flat_back=flat_back)


CUT_FACTORIES = {
    "Round": make_round_brilliant,
    "Oval": make_oval_cut,
    "Marquise": make_marquise_cut,
    "Rounded Pear": make_rounded_pear_cut,
    "Sharp Pear": make_sharp_pear_cut,
    "Trillion": lambda l, w, d, fb=False: make_trillion_cut(w, d, flat_back=fb),
    "Heart": make_heart_cut,
    "Octagon": make_octagon_cut,
    "Emerald": make_emerald_cut,
    "Cushion": make_cushion_cut,
}
