#!/usr/bin/env python3
"""
check.py - verify the generated laser files before sending them out

Reads every dxf/*.dxf back and checks:
  - units are millimeters
  - every CUT entity is a closed contour (closed polyline or circle)
  - every hole / slot is at least the sheet thickness wide
  - web (metal between two cuts, or a cut and the edge) >= thickness
  - narrow strips of material (e.g. gear tooth tips) are reported
Then checks that the parts fit together:
  - gears mesh without overlap at the plate's center distance
  - the ratchet pawl clears the wheel teeth
  - box tabs line up with their slots
  - bracket holes are far enough from the bend

Requires: ezdxf, shapely   (pip install ezdxf shapely)
Run:      python3 check.py      (after generate.py)
"""
import glob
import math
import os
import sys

import ezdxf
from ezdxf import path as ezpath
from shapely import affinity
from shapely.geometry import Polygon

import generate as g

T = g.T
TOL = 0.01
OUT = os.path.dirname(os.path.abspath(__file__))

errors = []
warnings = []


def fail(msg):
    errors.append(msg)
    print("  FAIL  " + msg)


def warn(msg):
    warnings.append(msg)
    print("  WARN  " + msg)


def ring_polygons(doc):
    rings = []
    for e in doc.modelspace():
        if e.dxf.layer != "CUT":
            continue
        if e.dxftype() == "LWPOLYLINE":
            if not e.closed:
                return None, f"open polyline on CUT ({len(e)} vertices)"
        elif e.dxftype() != "CIRCLE":
            return None, f"{e.dxftype()} on CUT layer (only closed contours allowed)"
        pts = list(ezpath.make_path(e).flattening(0.005))
        rings.append(Polygon([(p.x, p.y) for p in pts]))
    return rings, None


def check_dxf(path):
    name = os.path.basename(path)
    print(name)
    doc = ezdxf.readfile(path)
    if doc.header.get("$INSUNITS") != 4:
        fail(f"{name}: units are not millimeters")
    rings, err = ring_polygons(doc)
    if err:
        fail(f"{name}: {err}")
        return
    rings.sort(key=lambda r: r.area, reverse=True)
    outer, holes = rings[0], rings[1:]
    if not outer.is_valid:
        fail(f"{name}: outer contour intersects itself")
    material = outer
    min_hole, min_web = math.inf, math.inf
    for i, h in enumerate(holes):
        if not outer.contains(h):
            fail(f"{name}: a hole is outside or touching the outer contour")
        # narrowest width of the hole: it vanishes when shrunk by half of it
        lo, hi = 0.0, 50.0
        for _ in range(30):
            mid = (lo + hi) / 2
            if h.buffer(-mid).is_empty:
                hi = mid
            else:
                lo = mid
        min_hole = min(min_hole, 2 * lo)
        min_web = min(min_web, h.exterior.distance(outer.exterior))
        for h2 in holes[i + 1:]:
            min_web = min(min_web, h.distance(h2))
        material = material.difference(h)
    if holes:
        msg = f"smallest hole/slot width {min_hole:.2f} mm, smallest web {min_web:.2f} mm"
        if min_hole < T - TOL:
            fail(f"{name}: {msg} (hole narrower than thickness {T})")
        elif min_web < T - TOL:
            fail(f"{name}: {msg} (web thinner than thickness {T})")
        else:
            print("  ok    " + msg)
    # narrow material: what disappears when opening by half the thickness
    narrow = material.difference(material.buffer(-T / 2 + TOL).buffer(T / 2 - TOL))
    # a plain square corner loses 0.21 mm2 here; anything bigger is a real
    # thin feature (sharp tooth tip, thin strip)
    pieces = [p for p in getattr(narrow, "geoms", [narrow]) if p.area > 0.3]
    if pieces:
        warn(f"{name}: {len(pieces)} spots narrower than {T} mm "
             f"(largest {max(p.area for p in pieces):.2f} mm2): they cut fine but "
             "run hot; check them on the paper print")
    print(f"  ok    {len(rings)} closed contours, "
          f"{outer.bounds[2] - outer.bounds[0]:.2f} x {outer.bounds[3] - outer.bounds[1]:.2f} mm")


def world_polygon(part, idx=0):
    pts = g.tessellate(part.contours[idx])
    return Polygon(pts)


def check_assemblies():
    print("assemblies")
    groups = {p.name: p for grp in g.build_parts(normalize=False) for p in grp}

    # gears: 16T at the origin, 32T at the plate's center distance,
    # rotated half a tooth so a gap faces the pinion
    g1 = world_polygon(groups["03-gear-16t"])
    g2 = world_polygon(groups["03-gear-32t"])
    plate = groups["03-gear-plate"]
    cd = plate.circles[1][0] - plate.circles[0][0]
    worst = 0.0
    for step in range(16):                       # rotate through one tooth pitch
        a1 = step * (360 / 16) / 16
        a2 = -a1 * 16 / 32 + 180 / 32
        p1 = affinity.rotate(g1, a1, origin=(0, 0))
        p2 = affinity.translate(affinity.rotate(g2, a2, origin=(0, 0)), cd, 0)
        worst = max(worst, p1.intersection(p2).area)
    if worst > 0.01:
        fail(f"gears overlap by {worst:.3f} mm2 at center distance {cd:.1f}")
    else:
        print(f"  ok    gears 16T/32T mesh at {cd:.1f} mm with no overlap through one tooth")

    # ratchet: pawl must not cut into the wheel
    wheel = world_polygon(groups["06-ratchet-wheel"])
    pawl = world_polygon(groups["06-ratchet-pawl"])
    ov = wheel.intersection(pawl).area
    gap = wheel.distance(pawl)
    if ov > 0.01:
        fail(f"ratchet pawl overlaps the wheel by {ov:.3f} mm2")
    else:
        print(f"  ok    pawl clears the wheel (closest gap {gap:.2f} mm)")

    # box: tabs inside slots (positions measured from each part's middle)
    li, wi, h, e = 60.0, 40.0, 30.0, 5.0
    lf = li + 2 * T + 2 * e
    xs = li / 2 + T / 2
    bottom = groups["05-box-bottom"]
    slots = [Polygon(g.tessellate(c)).bounds for c in bottom.contours[1:]]
    ok = True
    for tab_x in (-18, 18):                      # front/back bottom tabs
        if not any(b[0] <= tab_x - g.TAB_W / 2 and tab_x + g.TAB_W / 2 <= b[2]
                   and b[3] - b[1] >= T for b in slots):
            ok = False
    for sx in (-xs, xs):                         # side bottom tabs
        if not any(b[1] <= -g.TAB_W / 2 and g.TAB_W / 2 <= b[3]
                   and abs((b[0] + b[2]) / 2 - sx) < TOL for b in slots):
            ok = False
    front = groups["05-box-front-back"]
    fslots = [Polygon(g.tessellate(c)).bounds for c in front.contours[1:]]
    for sx in (lf / 2 - xs, lf / 2 + xs):        # side wall tabs, at mid height
        if not any(abs((b[0] + b[2]) / 2 - sx) < TOL and b[1] <= h / 2 - g.TAB_W / 2
                   and h / 2 + g.TAB_W / 2 <= b[3] for b in fslots):
            ok = False
    if ok:
        print("  ok    box: every tab lands inside its slot")
    else:
        fail("box: a tab does not line up with its slot")

    # bracket: features at least 2T + R from the bend zone
    br = groups["02-l-bracket"]
    ba = math.pi / 2 * (g.BEND_R + g.K_FACTOR * T)
    zone = (40 - (g.BEND_R + T), 40 - (g.BEND_R + T) + ba)
    min_d = math.inf
    for cx, cy, r in br.circles:
        min_d = min(min_d, zone[0] - (cy + r) if cy < zone[0] else (cy - r) - zone[1])
    for c in br.contours[1:]:
        b = Polygon(g.tessellate(c)).bounds
        min_d = min(min_d, b[1] - zone[1] if b[1] > zone[1] else zone[0] - b[3])
    need = 2 * T + g.BEND_R
    if min_d < need:
        fail(f"bracket: a hole is {min_d:.2f} mm from the bend zone (need {need:g})")
    else:
        print(f"  ok    bracket: holes {min_d:.2f} mm from the bend zone (need >= {need:g})")


def main():
    files = sorted(glob.glob(os.path.join(OUT, "dxf", "*.dxf")))
    if not files:
        sys.exit("no DXF files: run generate.py first")
    for f in files:
        check_dxf(f)
    check_assemblies()
    print(f"\n{len(files)} files, {len(errors)} errors, {len(warnings)} warnings")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
