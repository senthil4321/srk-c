"""
rod_examples.py - examples 08-20: two 2 mm plates joined by rods

Every example is two plates held apart by M3 threaded rod: each plate is
clamped between two nuts (with washers), which sets the gap S between
the plates. 3 mm smooth rods (silver steel / dowel pins) are used as
axles, pivots, locating pins and slide guides; example 20 uses 8 mm
smooth rods with LM8UU linear bearings.

All geometry is in world coordinates of the example (the plate at its
working position), so check.py can test how the parts move and fit.
Used by generate.py; run `python3 generate.py`.
"""
import math

from generate import (T, Part, involute_gear, obround, polar, rect_center,
                      rounded_rect, tabbed_rect, SLOT_L, SLOT_W)

# hole sizes for 2 mm laser-cut plate
HOLE = {
    "m3": 3.4,      # M3 threaded rod / screw, clearance
    "r3_fix": 3.1,  # 3 mm smooth rod held still (snug; glue or e-clip)
    "r3_run": 3.2,  # 3 mm smooth rod that turns or slides in the hole
    "r8_fix": 8.1,  # 8 mm smooth rod held still
    "r8_run": 8.2,  # 8 mm smooth rod that turns or slides
}
NUT_H, WASHER_H = 2.4, 0.5   # M3 nut and washer thickness
NUT_AF = 5.7                 # hex hole for a captive M3 nut (5.5 + 0.2)


def rod(part, x, y, kind):
    part.hole(x, y, HOLE[kind])
    part.rods.append((x, y, kind))
    return part


def m3_len(gap):
    """M3 threaded rod length: gap + both plates + nut and washer on
    each outer side + 2 mm spare, rounded up."""
    return math.ceil(gap + 2 * T + 2 * (NUT_H + WASHER_H) + 2)


def corner_rods(part, x0, y0, w, h, inset=6.0):
    for x in (x0 + inset, x0 + w - inset):
        for y in (y0 + inset, y0 + h - inset):
            rod(part, x, y, "m3")
    return part


def hexagon(cx, cy, af):
    r = af / math.sqrt(3)
    return [(cx + r * math.cos(math.radians(60 * k)),
             cy + r * math.sin(math.radians(60 * k)), 0) for k in range(6)]


def handle(num):
    """Crank handle that sits outside a plate: glue it to the 3 mm axle
    and put a 3 mm rod in the outer hole as the grip."""
    p = Part(f"{num}-handle", f"{num} Crank handle (outside the plate)")
    p.contour(obround(0, 0, 25, 10))
    p.hole(0, 0, HOLE["r3_fix"]).hole(25, 0, HOLE["r3_fix"])
    return p


def cam_profile(cx, cy, r_base=20.0, lift=10.0, step_deg=2):
    """Cosine rise 0-120 deg, dwell to 180, fall to 300, dwell to 360
    (same cam as Fusion mechanism 07)."""
    verts = []
    for d in range(0, 360, step_deg):
        if d < 120:
            r = r_base + lift / 2 * (1 - math.cos(math.pi * d / 120))
        elif d < 180:
            r = r_base + lift
        elif d < 300:
            r = r_base + lift / 2 * (1 + math.cos(math.pi * (d - 180) / 120))
        else:
            r = r_base
        a = math.radians(d + 90)   # start of the rise points up
        verts.append((cx + r * math.cos(a), cy + r * math.sin(a), 0))
    return verts


# ------------------------------------------------------------------- 08

def ex08_sandwich():
    """The basic pattern: two identical plates, four M3 tie rods at the
    corners, two 3 mm locating rods so the plates line up exactly."""
    gap = 30
    p = Part("08-sandwich-plate", "08 Two-plate sandwich plate", qty=2)
    p.contour(rounded_rect(0, 0, 80, 60, 4))
    corner_rods(p, 0, 0, 80, 60)
    rod(p, 40, 6, "r3_fix")
    rod(p, 40, 54, "r3_fix")
    p.hole(40, 30, 20)                       # cable / weight-saving hole
    p.meta["gap"] = gap
    return [p]


# ------------------------------------------------------------------- 09

def ex09_electronics():
    """Board sandwich: Raspberry Pi 4 hole pattern (58 x 49, M2.5) on
    both plates, vent slots, M3 tie rods at the corners."""
    gap = 25
    p = Part("09-electronics-plate", "09 Electronics stack plate", qty=2)
    p.contour(rounded_rect(0, 0, 100, 80, 4))
    corner_rods(p, 0, 0, 100, 80)
    for x in (21, 79):
        for y in (15.5, 64.5):
            p.hole(x, y, 2.7)                # M2.5 board standoffs
    for y in (28, 36, 44, 52):
        p.contour(obround(32, y, 36, 4))     # vent slots
    p.meta["gap"] = gap
    return [p]


# ------------------------------------------------------------------- 10

def ex10_bearing_block():
    """Two upright plates each holding a 608 bearing, joined by M3 rods
    and standing in a base plate with tabs and slots. Carries an 8 mm
    shaft."""
    gap = 20
    yp = gap / 2 + T / 2                     # plate center lines at y = +-11
    up = Part("10-bearing-upright", "10 Bearing upright (608)", qty=2)
    up.contour(tabbed_rect(50, 55, [("bottom", 13, 10), ("bottom", 37, 10)]))
    up.hole(25, 33, 22.1)                    # 608 bearing, 22 mm OD
    for x, y in ((6, 8), (44, 8), (6, 49), (44, 49)):
        rod(up, x, y, "m3")
    base = Part("10-bearing-base", "10 Bearing block base")
    base.contour(rounded_rect(-35, -25, 70, 50, 4))
    for sy in (-yp, yp):
        for sx in (-12, 12):                 # upright tabs at x 13, 37 -> -12, +12
            base.contour(rect_center(sx, sy, SLOT_L, SLOT_W))
    for x in (-29, 29):
        for y in (-19, 19):
            base.hole(x, y, 4.5)
    up.meta.update(gap=gap, tab_x=[13 - 25, 37 - 25], plate_y=yp)
    return [up, base]


# ------------------------------------------------------------------- 11

def ex11_spool_holder():
    """Two triangular side plates, three M3 tie rods, and an 8 mm smooth
    rod axle that drops into U-notches at the top."""
    gap = 80
    p = Part("11-spool-side", "11 Spool holder side", qty=2)
    p.contour([(1.8, 4, 0), (4, 0, 0), (116, 0, 0), (118.2, 4, 0), (75, 100, 0), (64.2, 100, 0),
               (64.2, 90, -1), (55.8, 90, 0), (55.8, 100, 0), (45, 100, 0)])
    p.hole(60, 40, 40)                       # lightening hole
    for x, y in ((14, 6), (106, 6), (60, 75)):
        rod(p, x, y, "m3")
    p.meta.update(gap=gap)
    return [p]


# ------------------------------------------------------------------- 12

def ex12_pulley_block():
    """Rope pulley block: two cheek plates, a sheave built from four
    discs turning on a 3 mm axle, a hook hole at the top."""
    gap = 10
    cheek = Part("12-pulley-cheek", "12 Pulley block cheek", qty=2)
    cheek.contour(obround(25, 25, 50, 50, angle=90))   # 50 x 100, round ends
    rod(cheek, 25, 35, "r3_fix")             # sheave axle
    rod(cheek, 25, 6, "m3")
    rod(cheek, 25, 72, "m3")
    cheek.hole(25, 88, 10)                   # hook / shackle
    flange = Part("12-sheave-flange", "12 Sheave flange disc 44", qty=2)
    flange.contour([(-22, 0, 1), (22, 0, 1)]).hole(0, 0, HOLE["r3_run"])
    core = Part("12-sheave-core", "12 Sheave core disc 32 (rope groove)", qty=2)
    core.contour([(-16, 0, 1), (16, 0, 1)]).hole(0, 0, HOLE["r3_run"])
    cheek.meta.update(gap=gap, sheave=(25, 35, 22))
    return [cheek, flange, core]


# ------------------------------------------------------------------- 13

def ex13_gear_train():
    """16T / 32T gears (module 2.5, 2:1) turning on fixed 3 mm axles
    between two plates. Each gear is three laminations pinned together."""
    gap, m = 10, 2.5
    cd = m * (16 + 32) / 2 + 0.2
    c1, c2 = (25.0, 30.0), (25.0 + cd, 30.0)
    plate = Part("13-gear-plate", f"13 Gear train plate, CD {cd:.1f}", qty=2)
    plate.contour(rounded_rect(0, 0, 135, 60, 4))
    corner_rods(plate, 0, 0, 135, 60)
    rod(plate, *c1, "r3_fix")
    rod(plate, *c2, "r3_fix")
    g1 = Part("13-gear-16t", "13 Gear 16T, 3 layers", qty=3)
    g1.contour([(x + c1[0], y + c1[1], b) for x, y, b in involute_gear(m, 16)])
    g1.hole(*c1, HOLE["r3_run"]).hole(c1[0] + 11, c1[1], HOLE["r3_fix"])
    g2 = Part("13-gear-32t", "13 Gear 32T, 3 layers", qty=3)
    g2.contour([(x + c2[0], y + c2[1], b) for x, y, b in involute_gear(m, 32)])
    g2.hole(*c2, HOLE["r3_run"]).hole(c2[0] + 10, c2[1], HOLE["r3_fix"])
    for k in range(4):
        x, y = polar(22, k * math.pi / 2 + math.pi / 4)
        g2.hole(c2[0] + x, c2[1] + y, 14)
    plate.meta.update(gap=gap, c1=c1, c2=c2)
    return [plate, g1, g2]


# ------------------------------------------------------------------- 14

def rack_contour(x0, y0, length, m, root_h, n_teeth):
    """Straight rack: body from y0 to y0+root_h, teeth above. Dedendum
    1.1 m so the tooth gaps stay wider than the sheet thickness."""
    p = math.pi * m
    root = y0 + root_h
    pitch = root + 1.1 * m
    tip = pitch + m
    tan_a = math.tan(math.radians(20))
    hw_root = p / 4 + 1.1 * m * tan_a
    hw_tip = p / 4 - m * tan_a
    first = x0 + (length - (n_teeth - 1) * p) / 2
    top = [(x0, root)]
    for k in range(n_teeth):
        c = first + k * p
        top += [(c - hw_root, root), (c - hw_tip, tip), (c + hw_tip, tip), (c + hw_root, root)]
    top.append((x0 + length, root))
    pts = [(x0, y0), (x0 + length, y0)] + top[::-1]
    return [(x, y, 0) for x, y in pts], pitch


def ex14_rack_pinion():
    """Rack sliding on two fixed 3 mm rods (through slots in the rack),
    driven by a 16T pinion on a 3 mm axle. Turn the pinion by its rim,
    which sticks out above the plates."""
    gap, m = 10, 2.5
    rack_len, rod_dx, travel = 160.0, 40.0, 30.0
    mid = 70.0                               # rack middle at plate x = 70
    y0, root_h = 4.0, 8.0
    verts, pitch_y = rack_contour(mid - rack_len / 2, y0, rack_len, m, root_h, 20)
    pin_c = (mid, pitch_y + m * 16 / 2 + 0.1)
    rods_x = (mid - rod_dx, mid + rod_dx)
    slot_y = y0 + root_h / 2

    plate = Part("14-rack-plate", "14 Rack and pinion plate", qty=2)
    plate.contour(rounded_rect(0, 0, 140, 50, 4))
    rod(plate, 6, 44, "m3")
    rod(plate, 134, 44, "m3")
    for x in rods_x:
        rod(plate, x, slot_y, "r3_fix")      # rack guide rods
    rod(plate, *pin_c, "r3_fix")             # pinion axle
    rack = Part("14-rack", "14 Rack m2.5, 3 layers", qty=3)
    rack.contour(verts)
    for x in rods_x:                         # slots: rod at the middle at mid travel
        rack.contour(obround(x - travel, slot_y, 2 * travel, HOLE["r3_run"] + 0.1))
    pinion = Part("14-pinion-16t", "14 Pinion 16T, 3 layers", qty=3)
    pinion.contour([(x + pin_c[0], y + pin_c[1], b) for x, y, b in involute_gear(m, 16)])
    pinion.hole(*pin_c, HOLE["r3_run"]).hole(pin_c[0] + 11, pin_c[1], HOLE["r3_fix"])
    plate.meta.update(gap=gap, pinion=pin_c, travel=travel, r_pitch=m * 16 / 2)
    return [plate, rack, pinion]


# ------------------------------------------------------------------- 15

def ex15_four_bar():
    """Four-bar crank-rocker (20 / 55 / 45, ground 60) working between
    two plates. Crank and rocker on layer 1, coupler on layer 2. The
    crank axle and rocker pivot are short stubs in the bottom plate only,
    so the coupler can pass over them; handle under the bottom plate."""
    gap = 8
    plate = Part("15-four-bar-plate", "15 Four-bar plate", qty=2)
    plate.contour(rounded_rect(-28, -25, 116, 92, 4))
    corner_rods(plate, -28, -25, 116, 92)
    rod(plate, 0, 0, "r3_run")               # crank axle (turns)
    rod(plate, 60, 0, "r3_fix")              # rocker pivot
    parts = [plate]
    for name, L in (("crank", 20), ("coupler", 55), ("rocker", 45)):
        p = Part(f"15-four-bar-{name}", f"15 Four-bar {name}, {L} mm")
        p.contour(obround(0, 0, L, 10))
        p.hole(0, 0, HOLE["r3_fix"] if name == "crank" else HOLE["r3_run"])
        p.hole(L, 0, HOLE["r3_run"] if name == "crank" else HOLE["r3_fix"])
        parts.append(p)
    plate.meta.update(gap=gap, lengths=(60, 20, 55, 45))
    return parts + [handle("15")]


# ------------------------------------------------------------------- 16

def ex16_slider_crank():
    """Slider-crank between two plates: the slider is a 3 mm rod
    running in a straight slot cut in both plates. The crank axle is a
    short stub (handle, bottom plate, disc) because the connecting rod
    passes over the crank center at bottom dead center."""
    gap, r, L = 8, 15.0, 50.0
    c = (25.0, 25.0)
    plate = Part("16-slider-crank-plate", "16 Slider-crank plate", qty=2)
    plate.contour(rounded_rect(0, 0, 115, 50, 4))
    corner_rods(plate, 0, 0, 115, 50)
    rod(plate, *c, "r3_run")                 # crank axle (turns)
    plate.contour(obround(c[0] + L - r, c[1], 2 * r, HOLE["r3_run"] + 0.1))
    disc = Part("16-crank-disc", "16 Crank disc 42, throw 15")
    disc.contour([(c[0] - 21, c[1], 1), (c[0] + 21, c[1], 1)])
    disc.hole(*c, HOLE["r3_fix"]).hole(c[0] + r, c[1], HOLE["r3_fix"])
    conrod = Part("16-con-rod", "16 Connecting rod 50")
    conrod.contour(obround(c[0] + r, c[1], L, 8))
    conrod.hole(c[0] + r, c[1], HOLE["r3_run"]).hole(c[0] + r + L, c[1], HOLE["r3_run"])
    plate.meta.update(gap=gap, crank=c, r=r, L=L)
    return [plate, disc, conrod, handle("16")]


# ------------------------------------------------------------------- 17

def ex17_cam_follower():
    """Cam on a 3 mm axle lifts a flat follower 10 mm. The follower has
    a long slot that rides on two fixed 3 mm rods. Stand the plates
    upright: gravity returns the follower."""
    gap = 8
    cam_c = (40.0, 35.0)
    plate = Part("17-cam-plate", "17 Cam and follower plate", qty=2)
    plate.contour(rounded_rect(0, 0, 80, 110, 4))
    corner_rods(plate, 0, 0, 80, 110)
    rod(plate, *cam_c, "r3_run")             # cam axle (turns)
    rod(plate, 40, 75, "r3_fix")             # follower guide rods
    rod(plate, 40, 95, "r3_fix")
    cam = Part("17-cam", "17 Cam, lift 10, 3 layers", qty=3)
    cam.contour(cam_profile(*cam_c))
    cam.hole(*cam_c, HOLE["r3_fix"]).hole(cam_c[0] + 10, cam_c[1], HOLE["r3_fix"])
    f0 = (30.0, cam_c[1] + 20)               # follower at its lowest point
    fol = Part("17-follower", "17 Follower, 3 layers", qty=3)
    fol.contour(rounded_rect(f0[0], f0[1], 20, 50, 2))
    fol.contour(obround(f0[0] + 10, f0[1] + 9, 32, HOLE["r3_run"] + 0.1, angle=90))
    plate.meta.update(gap=gap, cam=cam_c, follower0=f0, lift=10)
    return [plate, cam, fol, handle("17")]


# ------------------------------------------------------------------- 18

def ex18_ratchet():
    """Ratchet between two plates: the wheel is fixed to a turning 3 mm
    axle, the pawl swings on a fixed 3 mm rod and is pulled into the
    teeth by a spring (or rubber band) to a third rod."""
    gap = 8
    teeth, ro, rr = 12, 22.0, 18.0
    plate = Part("18-ratchet-plate", "18 Ratchet plate", qty=2)
    plate.contour(rounded_rect(-30, -30, 80, 86, 4))
    corner_rods(plate, -30, -30, 80, 86)
    P, spring = (32.0, 30.0), (20.0, 49.0)
    rod(plate, 0, 0, "r3_run")
    rod(plate, *P, "r3_fix")
    rod(plate, *spring, "r3_fix")
    wheel = Part("18-ratchet-wheel", "18 Ratchet wheel 12T, 3 layers", qty=3)
    verts, land = [], 1.5 / ro
    for k in range(teeth):
        a = math.pi / 2 + k * 2 * math.pi / teeth
        verts += [(*polar(rr, a), 0), (*polar(ro, a), math.tan(land / 4)),
                  (*polar(ro, a + land), 0)]
    wheel.contour(verts)
    wheel.hole(0, 0, HOLE["r3_fix"]).hole(10, 0, HOLE["r3_fix"])
    A, B = (0.3, 18.6), (0.3, 21.4)
    M = ((A[0] + B[0]) / 2, (A[1] + B[1]) / 2)
    d = (P[0] - M[0], P[1] - M[1])
    dl = math.hypot(*d)
    n = (-d[1] / dl * 6, d[0] / dl * 6)
    pawl = Part("18-ratchet-pawl", "18 Ratchet pawl, 3 layers", qty=3)
    pawl.contour([(A[0], A[1], 0), (P[0] - n[0], P[1] - n[1], 1),
                  (P[0] + n[0], P[1] + n[1], 0), (B[0], B[1], 0)])
    pawl.hole(*P, HOLE["r3_run"]).hole(20, 26.2, HOLE["r3_fix"])
    plate.meta.update(gap=gap)
    return [plate, wheel, pawl, handle("18")]


# ------------------------------------------------------------------- 19

def ex19_lead_screw_slide():
    """Slide driven by M3 threaded rod: a three-layer carriage with a
    captive M3 nut runs on two 3 mm guide rods between two end plates.
    One knob turn = 0.5 mm (M3 pitch)."""
    gap = 80
    end = Part("19-slide-end-plate", "19 Lead-screw slide end plate", qty=2)
    end.contour(rounded_rect(0, 0, 60, 40, 4))
    corner_rods(end, 0, 0, 60, 40)
    rod(end, 15, 20, "r3_fix")
    rod(end, 45, 20, "r3_fix")
    end.hole(30, 20, HOLE["m3"])             # lead screw (turns)
    outer = Part("19-carriage-outer", "19 Carriage outer plate", qty=2)
    mid = Part("19-carriage-nut", "19 Carriage middle plate (captive nut)")
    for p in (outer, mid):
        p.contour(rounded_rect(10, 8, 40, 24, 2))
        rod(p, 15, 20, "r3_run")
        rod(p, 45, 20, "r3_run")
        for x in (15, 45):
            for y in (12, 28):
                p.hole(x, y, HOLE["m3"])     # M3 x 10 screws clamp the 3 layers
    outer.hole(30, 20, HOLE["m3"])
    mid.contour(hexagon(30, 20, NUT_AF))
    knob = Part("19-knob", "19 Knob (holds a nut)")
    knob.contour([(-15, 0, 1), (15, 0, 1)])
    knob.contour(hexagon(0, 0, NUT_AF))
    for k in range(6):
        knob.hole(*polar(10, k * math.pi / 3 + math.pi / 6), 4)
    end.meta.update(gap=gap)
    return [end, outer, mid, knob]


# ------------------------------------------------------------------- 20

def ex20_linear_rail():
    """Linear rail: two 8 mm smooth rods between end plates, a carriage
    of two plates holding two LM8UU bearings (15 mm OD, 24 mm long)."""
    gap = 150
    end = Part("20-rail-end-plate", "20 Linear rail end plate", qty=2)
    end.contour(rounded_rect(0, 0, 90, 50, 4))
    corner_rods(end, 0, 0, 90, 50)
    rod(end, 20, 25, "r8_fix")
    rod(end, 70, 25, "r8_fix")
    car = Part("20-carriage-plate", "20 Carriage plate (LM8UU)", qty=2)
    car.contour(rounded_rect(8.5, 12, 73, 26, 3))
    car.hole(20, 25, 15.0).hole(70, 25, 15.0)   # LM8UU, snug
    for x in (37, 53):
        for y in (18, 32):
            car.hole(x, y, HOLE["m3"])        # tie the two carriage plates / mount
    end.meta.update(gap=gap)
    return [end, car]


EXAMPLES = [ex08_sandwich, ex09_electronics, ex10_bearing_block,
            ex11_spool_holder, ex12_pulley_block, ex13_gear_train,
            ex14_rack_pinion, ex15_four_bar, ex16_slider_crank,
            ex17_cam_follower, ex18_ratchet, ex19_lead_screw_slide,
            ex20_linear_rail]

TITLES = {
    "08": "08 Two-plate sandwich (the basic pattern)",
    "09": "09 Electronics stack (Raspberry Pi 4 pattern)",
    "10": "10 Bearing block: two 608 bearings, 8 mm shaft",
    "11": "11 Spool holder with 8 mm axle",
    "12": "12 Rope pulley block",
    "13": "13 Gear train between plates (16T / 32T)",
    "14": "14 Rack and pinion, rack sliding on rods",
    "15": "15 Four-bar linkage between plates",
    "16": "16 Slider-crank with slot-guided slider",
    "17": "17 Cam and rod-guided follower",
    "18": "18 Ratchet between plates",
    "19": "19 Lead-screw slide (M3 threaded rod drive)",
    "20": "20 Linear rail: 8 mm rods + LM8UU carriage",
}

# Hardware per example. Plates are clamped between nut pairs on the M3
# rods: "gap" is the space between the two plates.
BOM = {
    "08": [f"Gap 30 mm. 4x M3 threaded rod {m3_len(30)} mm, 16x M3 nut, 16x M3 washer",
           "2x 3 mm smooth rod 34 mm (locating pins, snug fit)"],
    "09": [f"Gap 25 mm. 4x M3 threaded rod {m3_len(25)} mm, 16x M3 nut, 16x M3 washer",
           "4x M2.5 x 11 standoffs + 8x M2.5 x 6 screws for the board"],
    "10": [f"Gap 20 mm. 4x M3 threaded rod {m3_len(20)} mm, 16x M3 nut, 16x M3 washer",
           "2x 608 bearing (F608 flanged is easier), 8 mm shaft, retaining compound"],
    "11": [f"Gap 80 mm. 3x M3 threaded rod {m3_len(80)} mm, 12x M3 nut, 12x M3 washer",
           "1x 8 mm smooth rod 100 mm (spool axle)"],
    "12": [f"Gap 10 mm. 2x M3 threaded rod {m3_len(10)} mm, 8x M3 nut, 8x M3 washer",
           "1x 3 mm smooth rod 14 mm (axle, glue or e-clips); rope up to 3.5 mm; shackle"],
    "13": [f"Gap 10 mm. 4x M3 threaded rod {m3_len(10)} mm, 16x M3 nut, 16x M3 washer",
           "2x 3 mm smooth rod 14 mm (axles), 2x 3 mm rod 6 mm (lamination pins), 4x washer"],
    "14": [f"Gap 10 mm. 2x M3 threaded rod {m3_len(10)} mm, 8x M3 nut, 8x M3 washer",
           "3x 3 mm smooth rod 14 mm (2 rack guides + pinion axle), 1x 3 mm rod 6 mm (pin)"],
    "15": [f"Gap 8 mm. 4x M3 threaded rod {m3_len(8)} mm, 16x M3 nut, 16x M3 washer",
           "3 mm smooth rod: 1x 9 mm crank stub (handle + bottom plate + crank), 1x 5 mm",
           "rocker stub (bottom plate + rocker), 2x 5 mm coupler pins, 1x 15 mm handle grip"],
    "16": [f"Gap 8 mm. 4x M3 threaded rod {m3_len(8)} mm, 16x M3 nut, 16x M3 washer",
           "3 mm smooth rod: 1x 9 mm crank stub (handle + bottom plate + disc), 1x 5 mm crank",
           "pin, 1x 16 mm slider pin (both slots, e-clips), 1x 15 mm handle grip"],
    "17": [f"Gap 8 mm. 4x M3 threaded rod {m3_len(8)} mm, 16x M3 nut, 16x M3 washer",
           "3 mm smooth rod: 1x 24 mm (cam axle + handle), 2x 12 mm (follower guides),",
           "1x 6 mm (cam lamination pin), 1x 15 mm (handle grip)"],
    "18": [f"Gap 8 mm. 4x M3 threaded rod {m3_len(8)} mm, 16x M3 nut, 16x M3 washer",
           "3 mm smooth rod: 1x 24 mm (wheel axle + handle), 2x 12 mm (pawl pivot, spring",
           "anchor), 2x 6 mm (pins); small extension spring or rubber band"],
    "19": [f"Gap 80 mm. 4x M3 threaded rod {m3_len(80)} mm, 16x M3 nut, 16x M3 washer",
           "1x M3 threaded rod 110 mm (lead screw) + 5x M3 nut, 2x 3 mm smooth rod 84 mm,",
           "4x M3 x 10 screw + nut (carriage)"],
    "20": [f"Gap 150 mm. 4x M3 threaded rod {m3_len(150)} mm, 16x M3 nut, 16x M3 washer",
           "2x 8 mm smooth rod 154 mm, 2x LM8UU, 4x M3 threaded rod 36 mm + 16 nuts (carriage)"],
}
