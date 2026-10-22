# SPDX-License-Identifier: LGPL-2.1-or-later
"""Jewelry Bill of Materials (BOM) and Metal Weight Analysis."""

import FreeCAD
from freecad.jewelry.core import metals


def calculate_document_bom(doc=None, default_alloy="14k_Yellow") -> dict:
    """
    Scan the document for jewelry objects and calculate total metal
    and gemstone statistics.
    """
    if doc is None:
        doc = FreeCAD.ActiveDocument
    if doc is None:
        return {}

    metal_volume = 0.0
    gem_list = []

    for obj in doc.Objects:
        proxy_type = getattr(getattr(obj, "Proxy", None), "Type", "")
        if not hasattr(obj, "Shape") or obj.Shape.isNull():
            continue

        if proxy_type == "Jewelry::Gem":
            species = getattr(obj, "Species", "Diamond")
            cut = getattr(obj, "CutType", "Round")
            vol = obj.Shape.Volume
            carats = getattr(obj, "Carats", metals.calculate_carat_weight(vol, species))
            length = getattr(obj, "Length", getattr(obj, "Width", 0.0))
            width = getattr(obj, "Width", length)
            gem_list.append({
                "label": obj.Label,
                "cut": cut,
                "species": species,
                "dimensions": f"{length:.2f} x {width:.2f} mm",
                "carats": round(carats, 3),
                "volume_mm3": round(vol, 2)
            })
        elif proxy_type in ("Jewelry::Shank", "Jewelry::Prongs", "Jewelry::VProng", "Jewelry::BotanicalLeaf"):
            metal_volume += obj.Shape.Volume
        elif hasattr(obj, "Shape") and obj.Shape.ShapeType == "Solid":
            # Other general solid parts considered metal
            metal_volume += obj.Shape.Volume

    # Calculate weight across standard precious alloys
    metal_weights = {}
    for alloy in metals.list_alloys():
        metal_weights[alloy] = metals.calculate_metal_weight(metal_volume, alloy)

    total_ctw = sum(g["carats"] for g in gem_list)

    return {
        "metal_volume_mm3": round(metal_volume, 2),
        "metal_weights_grams": metal_weights,
        "default_alloy": default_alloy,
        "default_weight_grams": metal_weights.get(default_alloy, 0.0),
        "gems": gem_list,
        "total_gems_count": len(gem_list),
        "total_carats": round(total_ctw, 3),
    }


def format_bom_report(doc=None, alloy="14k_Yellow") -> str:
    """Generate a clean markdown report of jewelry metal and gemstone weights."""
    bom = calculate_document_bom(doc, alloy)
    if not bom:
        return "No active document or jewelry elements found."

    lines = []
    lines.append("## Jewelry Bill of Materials (BOM) Report")
    lines.append("")
    lines.append(f"**Total Metal Volume:** {bom['metal_volume_mm3']} mm³")
    lines.append(f"**Selected Alloy ({alloy}):** {bom['metal_weights_grams'].get(alloy, 0.0)} grams")
    lines.append("")
    lines.append("### Metal Weight by Alloy:")
    lines.append("| Alloy | Density (g/cm³) | Casting Weight (g) |")
    lines.append("| :--- | :---: | :---: |")
    for a in ["14k_Yellow", "14k_White", "14k_Rose", "18k_Yellow", "18k_White", "18k_Rose", "Platinum_950", "Silver_925"]:
        d = metals.get_metal_density(a)
        w = bom["metal_weights_grams"].get(a, 0.0)
        lines.append(f"| {a.replace('_', ' ')} | {d:.2f} | **{w:.2f} g** |")

    lines.append("")
    lines.append(f"### Gemstones ({bom['total_gems_count']} stones, {bom['total_carats']} CTW):")
    if bom["gems"]:
        lines.append("| Stone | Cut | Species | Dimensions | Carats |")
        lines.append("| :--- | :--- | :--- | :--- | :---: |")
        for g in bom["gems"]:
            lines.append(f"| {g['label']} | {g['cut']} | {g['species']} | {g['dimensions']} | {g['carats']} ct |")
    else:
        lines.append("*No gemstones in document.*")

    return "\n".join(lines)
