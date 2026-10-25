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


def solid(part, idx=0, with_holes=False):
    """Part outline as a shapely polygon (world coordinates)."""
    holes = []
    if with_holes:
        holes = [g.tessellate(c) for c in part.contours[1:]]
    return Polygon(g.tessellate(part.contours[idx]), holes)


def link_polygon(a, b, width):
    """Slot-shaped link between pivot points a and b."""
    from shapely.geometry import LineString
    return LineString([a, b]).buffer(width / 2)


def rod_points(part, kinds=("m3",)):
    from shapely.geometry import Point
    return [Point(x, y) for x, y, k in part.rods if k in kinds]


def gap_to_rods(shape, rods, rod_r=1.5):
    return min(shape.distance(r) for r in rods) - rod_r if rods else math.inf


def circle_intersections(p, r1, q, r2):
    dx, dy = q[0] - p[0], q[1] - p[1]
    d = math.hypot(dx, dy)
    if d > r1 + r2 or d < abs(r1 - r2):
        return None
    a = (r1 * r1 - r2 * r2 + d * d) / (2 * d)
    h = math.sqrt(max(0.0, r1 * r1 - a * a))
    mx, my = p[0] + a * dx / d, p[1] + a * dy / d
    return (mx - h * dy / d, my + h * dx / d), (mx + h * dy / d, my - h * dx / d)


def check_rod_assemblies():
    """Examples 08-20: plates joined by rods. Checks the gap leaves room
    for the inner nuts and the moving parts, rod holes line up between
    plates, and nothing that moves hits a rod over its whole motion."""
    import rod_examples as rx
    from shapely.geometry import Point
    print("rod assemblies (08-20)")
    parts = {p.name: p for grp in g.build_parts(normalize=False)
             for p in grp if p.name[:2] >= "08"}
    min_clear = 0.5          # moving part to rod surface

    def report(ok, msg):
        (print("  ok    " + msg) if ok else fail(msg))

    # gap: inner nut + washer on each plate, and room for the moving stack
    stacks = {"08": 0, "09": 0, "10": 0, "11": 0, "12": 8, "13": 6, "14": 6,
              "15": 4, "16": 4, "17": 6, "18": 6, "19": 0, "20": 0}
    inner = 2 * (rx.NUT_H + rx.WASHER_H)
    for num, stack in stacks.items():
        plate = next(p for p in parts.values() if p.name.startswith(num) and "gap" in p.meta)
        gap = plate.meta["gap"]
        report(gap >= inner and gap >= stack + 1,
               f"{num}: gap {gap} mm fits inner nuts ({inner:.1f}) and moving parts ({stack})")

    # 10: upright tabs land in the base slots
    up, base = parts["10-bearing-upright"], parts["10-bearing-base"]
    slots = [Polygon(g.tessellate(c)) for c in base.contours[1:]]
    ok = all(any(s.contains(Polygon(g.tessellate(g.rect_center(tx, sy, g.TAB_W, g.T))))
                 for s in slots)
             for tx in up.meta["tab_x"] for sy in (-up.meta["plate_y"], up.meta["plate_y"]))
    report(ok, "10: both uprights' tabs land inside the base slots")

    # 12: sheave and rope clear the tie rods
    cheek = parts["12-pulley-cheek"]
    sx, sy, sr = cheek.meta["sheave"]
    d = min(math.hypot(x - sx, y - sy) for x, y, k in cheek.rods if k == "m3")
    report(d - 1.5 - sr >= 3.5, f"12: {d - 1.5 - sr:.1f} mm between sheave and tie rods (rope <= 3.5)")

    # 13: gears clear the tie rods and mesh through a full tooth
    plate = parts["13-gear-plate"]
    rods = rod_points(plate)
    for name, c, ra in (("16t", plate.meta["c1"], 22.5), ("32t", plate.meta["c2"], 42.5)):
        gap = gap_to_rods(Point(*c).buffer(ra), rods)
        report(gap >= min_clear, f"13: gear {name} clears the tie rods by {gap:.1f} mm")
    g1, g2 = solid(parts["13-gear-16t"]), solid(parts["13-gear-32t"])
    c1, c2 = plate.meta["c1"], plate.meta["c2"]
    worst = 0.0
    for step in range(16):
        a1 = step * 360 / 16 / 16
        p1 = affinity.rotate(g1, a1, origin=c1)
        p2 = affinity.rotate(g2, -a1 / 2 + 180 / 32, origin=c2)
        worst = max(worst, p1.intersection(p2).area)
    report(worst < 0.01, f"13: gears mesh with no overlap (worst {worst:.3f} mm2)")

    # 14: rack slides +-travel on its guide rods, meshes with the pinion
    plate = parts["14-rack-plate"]
    rack = solid(parts["14-rack"], with_holes=True)
    pin = solid(parts["14-pinion-16t"])
    pc, travel, rp = plate.meta["pinion"], plate.meta["travel"], plate.meta["r_pitch"]
    guides = [Point(x, y) for x, y, k in plate.rods if k == "r3_fix" and (x, y) != pc]
    worst, worst_rod = 0.0, math.inf
    for i in range(-30, 31):
        dx = travel * i / 30
        r = affinity.translate(rack, dx, 0)
        p = affinity.rotate(pin, math.degrees(dx / rp), origin=pc)
        worst = max(worst, r.intersection(p).area)
        worst_rod = min(worst_rod, gap_to_rods(r, guides + rod_points(plate) + [Point(*pc)]))
    report(worst < 0.01, f"14: rack and pinion mesh over +-{travel:g} mm (worst overlap {worst:.3f} mm2)")
    report(worst_rod >= 0, f"14: rack slides +-{travel:g} mm without hitting a rod (closest {worst_rod:.2f} mm)")

    # 15: four-bar through a full crank turn
    plate = parts["15-four-bar-plate"]
    ground, crank, coupler, rocker = plate.meta["lengths"]
    O2, O4 = (0.0, 0.0), (float(ground), 0.0)
    tie = rod_points(plate)
    worst_tie, worst_stub, full = math.inf, math.inf, True
    for deg in range(0, 360, 2):
        A = (crank * math.cos(math.radians(deg)), crank * math.sin(math.radians(deg)))
        sol = circle_intersections(A, coupler, O4, rocker)
        if sol is None:
            full = False
            break
        B = max(sol, key=lambda q: q[1])          # assembled with B above
        links = [link_polygon(O2, A, 10), link_polygon(A, B, 10), link_polygon(O4, B, 10)]
        worst_tie = min(worst_tie, min(gap_to_rods(l, tie) for l in links))
        # layer 1: crank vs rocker stub, rocker vs crank stub
        worst_stub = min(worst_stub, links[0].distance(Point(*O4)) - 1.5,
                         links[2].distance(Point(*O2)) - 1.5)
    report(full, "15: crank turns a full 360 deg")
    report(worst_tie >= min_clear, f"15: links clear the tie rods by {worst_tie:.1f} mm")
    report(worst_stub >= min_clear, f"15: crank and rocker clear each other's stubs by {worst_stub:.1f} mm")

    # 16: slider-crank through a full turn
    plate = parts["16-slider-crank-plate"]
    c, r, L = plate.meta["crank"], plate.meta["r"], plate.meta["L"]
    tie = rod_points(plate)
    slot = Polygon(g.tessellate(plate.contours[1]))
    worst_tie, in_slot = math.inf, True
    disc_gap = gap_to_rods(Point(*c).buffer(21), tie)
    for deg in range(0, 360, 2):
        A = (c[0] + r * math.cos(math.radians(deg)), c[1] + r * math.sin(math.radians(deg)))
        sx = A[0] + math.sqrt(L * L - (A[1] - c[1]) ** 2)
        worst_tie = min(worst_tie, gap_to_rods(link_polygon(A, (sx, c[1]), 8), tie))
        in_slot &= slot.contains(Point(sx, c[1]).buffer(1.5))
    report(disc_gap >= min_clear, f"16: crank disc clears the tie rods by {disc_gap:.1f} mm")
    report(worst_tie >= min_clear, f"16: connecting rod clears the tie rods by {worst_tie:.1f} mm")
    report(in_slot, "16: slider pin stays inside the slot for a full turn")

    # 17: cam lifts the follower 10 mm, guide rods stay in its slot
    plate = parts["17-cam-plate"]
    cam = solid(parts["17-cam"])
    fol = solid(parts["17-follower"], with_holes=True)
    cc, f0 = plate.meta["cam"], plate.meta["follower0"]
    guides = [Point(x, y) for x, y, k in plate.rods if k == "r3_fix"]
    tie = rod_points(plate)
    lifts, ok_slot = [], True
    band = Polygon([(f0[0], 0), (f0[0] + 20, 0), (f0[0] + 20, 200), (f0[0], 200)])
    for deg in range(0, 360, 3):
        cr = affinity.rotate(cam, deg, origin=cc)
        top = cr.intersection(band).bounds[3]      # flat follower rests on the highest point
        lift = top - f0[1]
        lifts.append(lift)
        ok_slot &= all(not affinity.translate(fol, 0, lift).intersects(gd.buffer(1.5))
                       for gd in guides)
    cam_gap = gap_to_rods(Point(*cc).buffer(20 + plate.meta["lift"]), tie)
    report(abs(max(lifts) - min(lifts) - 10) < 0.2,
           f"17: follower lift {max(lifts) - min(lifts):.2f} mm (expect 10)")
    report(ok_slot, "17: follower slides on its guide rods without binding")
    report(cam_gap >= min_clear, f"17: cam clears the tie rods by {cam_gap:.1f} mm")

    # 18: pawl clears the wheel, wheel clears the tie rods
    plate = parts["18-ratchet-plate"]
    wheel, pawl = solid(parts["18-ratchet-wheel"]), solid(parts["18-ratchet-pawl"])
    report(wheel.intersection(pawl).area < 0.01,
           f"18: pawl clears the wheel (gap {wheel.distance(pawl):.2f} mm)")
    wgap = gap_to_rods(Point(0, 0).buffer(22.1), rod_points(plate))
    report(wgap >= min_clear, f"18: wheel clears the tie rods by {wgap:.1f} mm")

    # 19, 20: carriage clears the tie rods; carriage holes line up with the rods
    for num, end_name, car_names in (("19", "19-slide-end-plate", ("19-carriage-outer", "19-carriage-nut")),
                                     ("20", "20-rail-end-plate", ("20-carriage-plate",))):
        end = parts[end_name]
        tie = rod_points(end)
        guides = [(x, y) for x, y, k in end.rods if k != "m3"]
        for cn in car_names:
            car = parts[cn]
            cgap = gap_to_rods(solid(car), tie)
            centers = [(x, y) for x, y, _ in car.circles]
            lined = all(any(math.hypot(x - gx, y - gy) < TOL for x, y in centers)
                        for gx, gy in guides)
            report(cgap >= min_clear and lined,
                   f"{num}: {cn} clears the tie rods by {cgap:.1f} mm, holes on the guide rods")


def main():
    files = sorted(glob.glob(os.path.join(OUT, "dxf", "*.dxf")))
    if not files:
        sys.exit("no DXF files: run generate.py first")
    for f in files:
        check_dxf(f)
    check_assemblies()
    check_rod_assemblies()
    print(f"\n{len(files)} files, {len(errors)} errors, {len(warnings)} warnings")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
