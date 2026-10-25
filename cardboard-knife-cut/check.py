#!/usr/bin/env python3
"""
check.py - verify the cardboard templates before printing

Checks:
  - every cut outline is a simple closed shape; holes sit inside it
  - slots are exactly the board thickness T wide
  - cross-slot joints: the two slot depths add up to the crossing
    height, and the part is tall enough where the slot is
  - no strip of cardboard narrower than 5 mm (tears when cut by knife)
  - gears mesh without overlap through a full tooth
  - four-bar crank can turn all the way round
  - catapult tabs fit the base slots, the arm fits between the uprights
  - the A4 sheets cover the whole drawing, with overlap

Requires: shapely, reportlab   (pip install shapely reportlab)
Run:      python3 check.py
"""
import math
import sys

from shapely import affinity
from shapely.geometry import Polygon

import generate as g

errors, warnings = [], []


def ok(cond, msg):
    if cond:
        print("  ok    " + msg)
    else:
        errors.append(msg)
        print("  FAIL  " + msg)


def warn(msg):
    warnings.append(msg)
    print("  WARN  " + msg)


def solid(p):
    outer = Polygon(p.cuts[0])
    for h in p.cuts[1:]:
        outer = outer.difference(Polygon(h))
    return outer


def check_part(p):
    outer = Polygon(p.cuts[0])
    ok(outer.is_valid, f"{p.name}: outline is a simple closed shape")
    for h in p.cuts[1:]:
        hole = Polygon(h)
        if not (hole.is_valid and outer.contains(hole)):
            ok(False, f"{p.name}: a cut-out is outside the outline")
    if p.name != "test-strip":
        for edge, c, wd, d in p.slots:
            if abs(wd - g.T) > 1e-6:
                ok(False, f"{p.name}: slot at {c:g} is {wd} wide, not {g.T}")
    material = solid(p)
    thin = material.difference(material.buffer(-2.5).buffer(2.5))
    pieces = [q for q in getattr(thin, "geoms", [thin]) if q.area > 3]
    if pieces:
        warn(f"{p.name}: {len(pieces)} spot(s) narrower than 5 mm "
             f"(largest {max(q.area for q in pieces):.0f} mm2): cut slowly there")


def main():
    for num, parts, info, W, H in g.build():
        print(info["title"])
        by = {p.name: p for p in parts}
        for p in parts:
            check_part(p)

        for a, ia, b, ib, height in info.get("joints", []):
            pa, pb = by[a], by[b]
            da, db = pa.slots[ia][3], pb.slots[ib][3]
            ok(abs(da + db - height) < 1e-6,
               f"joint {a}/{b}: slot depths {da:g} + {db:g} = {height:g} (crossing height)")
            h_at = pa.meta.get("height_at_slot")
            if h_at is not None:
                h_at = h_at[ia] if isinstance(h_at, list) else h_at
                ok(h_at >= height, f"joint {a}/{b}: {a} is {h_at:.0f} mm tall at the slot (needs {height:g})")

        if num == "07":
            ground, crank, coupler, rocker = by["base"].meta["lengths"]
            s, l = min(ground, crank, coupler, rocker), max(ground, crank, coupler, rocker)
            ok(s + l <= ground + crank + coupler + rocker - s - l and crank == s,
               "four-bar: Grashof (shortest + longest <= other two), crank is shortest: turns fully")

        if num == "08":
            base = by["gear-base"].meta
            z1, z2 = base["z"]
            g1, g2 = Polygon(by["gear-12t"].cuts[0]), Polygon(by["gear-24t"].cuts[0])
            g2 = affinity.translate(g2, base["cd"], 0)
            worst = 0.0
            for k in range(24):
                a1 = k * (360 / z1) / 24
                p1 = affinity.rotate(g1, a1, origin=(0, 0))
                p2 = affinity.rotate(g2, -a1 * z1 / z2 + 180 / z2, origin=(base["cd"], 0))
                worst = max(worst, p1.intersection(p2).area)
            ok(worst < 0.5, f"gears mesh at {base['cd']:.1f} mm with no overlap (worst {worst:.2f} mm2)")

        if num == "09":
            m = by["catapult-base"].meta
            up = by["upright"].meta
            sx0, sx1 = m["slot_x"]
            ok(sx0 <= up["tab_center"] - 15 and up["tab_center"] + 15 <= sx1,
               "catapult: upright tabs (30 mm) fit the base slots (31 mm)")
            inner = (m["slot_y"][1] - m["slot_y"][0]) - g.T
            ok(m["arm_w"] + 4 <= inner, f"catapult: arm ({m['arm_w']} mm) swings freely between uprights ({inner:.0f} mm)")

        cols, rows = g.tiles_for(W, H)
        cover_w = cols * (g.UW - g.OV) + g.OV if cols > 1 else g.UW
        cover_h = rows * (g.UH - g.OV) + g.OV if rows > 1 else g.UH
        ok(cover_w >= W and cover_h >= H,
           f"{cols * rows} A4 sheet(s) cover the {W:.0f} x {H:.0f} mm drawing")

    print(f"\n{len(errors)} errors, {len(warnings)} warnings")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
