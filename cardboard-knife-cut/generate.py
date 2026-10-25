#!/usr/bin/env python3
"""
generate.py - cardboard templates to print on A4 and cut with a knife

Writes:
  pdf/<example>.pdf      1:1 templates on A4. Parts bigger than one sheet
                         are split over several sheets (tiles) with
                         overlap strips and alignment crosses to tape
                         them together. Tiled examples start with a map.
  pdf/all-examples.pdf   every example in one file
  svg/<example>.svg      full-size drawing (for a cutting machine, or to
                         print at a copy shop on one big sheet)

Line types:
  solid black    CUT
  dashed blue    SCORE and FOLD (press a line with a blunt tool, then fold)
  gray area      GLUE
  +              punch a hole (pencil, skewer, or a split pin)

Designed for 3 mm single-wall corrugated cardboard: every slot is 3 mm
wide. Measure your board and change T below if it is different.

Requires: reportlab   (pip install reportlab)
Run:      python3 generate.py
"""
import math
import os

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

T = 3.0          # board thickness = slot width
OUT = os.path.dirname(os.path.abspath(__file__))

# A4 page layout (mm)
PAGE_W, PAGE_H = A4[0] / mm, A4[1] / mm
CX, CY = 12.0, 22.0                # content window origin on the page
UW, UH = 186.0, 254.0              # content window size
OV = 12.0                          # overlap between neighbouring sheets
GAP = 12.0                         # space between parts


# ------------------------------------------------------------- geometry

class Part:
    """A flat part. cuts[0] is the outline, other cuts are holes to cut
    out. All lines are straight so they can be cut with a knife and a
    ruler."""

    def __init__(self, name, qty=1, note=""):
        self.name = name
        self.qty = qty
        self.note = note
        self.cuts = []      # closed polygons [(x, y), ...]
        self.scores = []    # fold lines ((x1, y1), (x2, y2))
        self.glues = []     # glue areas (polygons)
        self.punch = []     # (x, y) holes to punch
        self.slots = []     # (edge, center, width, depth) for check.py
        self.meta = {}
        self.pos = (0.0, 0.0)   # where the layout puts it

    def bbox(self):
        pts = [p for c in self.cuts for p in c]
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        return min(xs), min(ys), max(xs), max(ys)


def rect(x, y, w, h):
    return [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]


def notched_rect(w, h, notches, chamfer=0.0):
    """Rectangle 0..w x 0..h with slots cut in from the edges.
    notches: (edge, center, width, depth); edge is 'bottom', 'right',
    'top' or 'left'; center is measured from x=0 or y=0."""
    by = {e: sorted((c, wd, d) for ed, c, wd, d in notches if ed == e)
          for e in ("bottom", "right", "top", "left")}
    ch = chamfer
    pts = [(ch, 0)]
    for c, wd, d in by["bottom"]:
        pts += [(c - wd / 2, 0), (c - wd / 2, d), (c + wd / 2, d), (c + wd / 2, 0)]
    pts += [(w - ch, 0), (w, ch)]
    for c, wd, d in by["right"]:
        pts += [(w, c - wd / 2), (w - d, c - wd / 2), (w - d, c + wd / 2), (w, c + wd / 2)]
    pts += [(w, h - ch), (w - ch, h)]
    for c, wd, d in reversed(by["top"]):
        pts += [(c + wd / 2, h), (c + wd / 2, h - d), (c - wd / 2, h - d), (c - wd / 2, h)]
    pts += [(ch, h), (0, h - ch)]
    for c, wd, d in reversed(by["left"]):
        pts += [(0, c + wd / 2), (d, c + wd / 2), (d, c - wd / 2), (0, c - wd / 2)]
    pts.append((0, ch))
    clean = []
    for p in pts:                       # drop repeated points (chamfer 0)
        if not clean or abs(p[0] - clean[-1][0]) > 1e-9 or abs(p[1] - clean[-1][1]) > 1e-9:
            clean.append(p)
    if abs(clean[0][0] - clean[-1][0]) < 1e-9 and abs(clean[0][1] - clean[-1][1]) < 1e-9:
        clean.pop()
    return clean


def slot_part(name, w, h, notches, qty=1, note="", chamfer=0.0):
    p = Part(name, qty, note)
    p.cuts.append(notched_rect(w, h, notches, chamfer))
    p.slots = list(notches)
    p.meta["size"] = (w, h)
    return p


def square_hole(cx, cy, s):
    return rect(cx - s / 2, cy - s / 2, s, s)


def straight_gear(m, z, center=(0.0, 0.0), flank_deg=14.5):
    """Gear with straight-sided (trapezoid) teeth: easy to cut with a
    knife. Tooth thickness 0.42 of the pitch, so the gaps stay wide."""
    r = m * z / 2
    ra, rf = r + 0.9 * m, r - 1.1 * m
    p = math.pi * m
    s = 0.42 * p
    tan_f = math.tan(math.radians(flank_deg))

    def half(rho):                          # half tooth thickness at radius rho
        return s / 2 - (rho - r) * tan_f

    pts = []
    for k in range(z):
        a = 2 * math.pi * k / z
        for rho, sign in ((rf, -1), (ra, -1), (ra, 1), (rf, 1)):
            ang = a + sign * half(rho) / rho
            pts.append((center[0] + rho * math.cos(ang), center[1] + rho * math.sin(ang)))
    return pts


# ------------------------------------------------------------- examples

def ex01_test_strip():
    """Find the right slot width for your cardboard before cutting the
    real parts."""
    widths = [2.0, 2.5, 3.0, 3.5, 4.0, 4.5]
    notches = [("top", 15 + i * 30, wd, 25) for i, wd in enumerate(widths)]
    strip = slot_part("test-strip", 180, 50, notches,
                      note="slot widths 2.0 2.5 3.0 3.5 4.0 4.5")
    key = slot_part("test-key", 60, 50, [("bottom", 30, T, 25)],
                    note=f"slot {T:g}: push into each strip slot")
    return [strip, key], {
        "title": "01 Test strip: find your slot width",
        "steps": ["Cut both parts. Push the key into each slot of the strip.",
                  "The right slot is the narrowest one that goes in fully without tearing.",
                  "If it is not 3.0, change T in generate.py and run it again."],
    }


def ex02_phone_stand():
    """Two side profiles and a brace, joined by cross slots."""
    h_brace = 60
    profile = Part("side", qty=2, note="phone stand side x2")
    profile.cuts.append([(0, 0), (63.5, 0), (63.5, 30), (66.5, 30), (66.5, 0),
                         (130, 0), (92, 135), (78, 135), (22, 15), (8, 15),
                         (8, 35), (0, 35)])
    profile.slots = [("bottom", 65, T, 30)]
    profile.meta["height_at_slot"] = 15 + (65 - 22) * (135 - 15) / (78 - 22)  # support edge
    brace = slot_part("brace", 110, h_brace, [("top", 20, T, 30), ("top", 90, T, 30)],
                      note="brace")
    return [profile, brace], {
        "title": "02 Phone stand",
        "steps": ["Cut 2 sides and 1 brace. Flutes (the waves inside the board) running up-down.",
                  "Slide the brace slots down onto the side slots. The phone sits on the 14 mm ledge.",
                  "Phone up to 12 mm thick with a case; for thicker, move the front lip forward."],
        "joints": [("side", 0, "brace", 0, h_brace)],
    }


def ex03_desk_organizer():
    """Open box 100 x 80 x 90 folded from one piece, with glue flaps."""
    W, D, H, F = 100.0, 80.0, 90.0, 15.0
    x0, x1 = H, H + W               # base x range
    y0, y1 = H, H + D               # base y range
    p = Part("organizer-net", note="desk organizer, one piece")
    out = [(x0, 0), (x1, 0),
           (x1, 2), (x1 + F, 2 + F), (x1 + F, H - 2 - F), (x1, H - 2),
           (x1, y0), (x1 + H, y0), (x1 + H, y1), (x1, y1),
           (x1, y1 + 2), (x1 + F, y1 + 2 + F), (x1 + F, y1 + H - 2 - F), (x1, y1 + H - 2),
           (x1, y1 + H), (x0, y1 + H),
           (x0, y1 + H - 2), (x0 - F, y1 + H - 2 - F), (x0 - F, y1 + 2 + F), (x0, y1 + 2),
           (x0, y1), (0, y1), (0, y0), (x0, y0),
           (x0, H - 2), (x0 - F, H - 2 - F), (x0 - F, 2 + F), (x0, 2)]
    p.cuts.append(out)
    p.scores += [((x0, y0), (x1, y0)), ((x0, y1), (x1, y1)),
                 ((x0, y0), (x0, y1)), ((x1, y0), (x1, y1)),
                 ((x1, 2), (x1, H - 2)), ((x0, 2), (x0, H - 2)),
                 ((x1, y1 + 2), (x1, y1 + H - 2)), ((x0, y1 + 2), (x0, y1 + H - 2))]
    for sx in (1, -1):
        for yb in (0, y1):
            xe = x1 if sx > 0 else x0
            p.glues.append([(xe, yb + 2), (xe + sx * F, yb + 2 + F),
                            (xe + sx * F, yb + H - 2 - F), (xe, yb + H - 2)])
    p.meta.update(W=W, D=D, H=H)
    return [p], {
        "title": "03 Desk organizer box (100 x 80 x 90)",
        "steps": ["Tape the sheets together, then cut the outline (solid lines).",
                  "Score all dashed lines: press along a ruler with a blunt knife back or an empty pen.",
                  "Fold the four walls up. Fold the gray flaps inward and glue them inside the side walls."],
    }


def ex04_laptop_stand():
    """Two sloped side panels and two crossbars with cross slots."""
    bar_h = 40
    panel = Part("panel", qty=2, note="laptop stand side x2")
    xs = (90, 210)
    out = [(0, 0)]
    for x in xs:
        out += [(x - T / 2, 0), (x - T / 2, bar_h / 2), (x + T / 2, bar_h / 2), (x + T / 2, 0)]
    out += [(250, 0), (250, 95), (34, 37), (34, 50), (20, 50), (20, 30), (0, 30)]
    panel.cuts.append(out)
    panel.slots = [("bottom", x, T, bar_h / 2) for x in xs]
    slope = (95 - 37) / (250 - 34)
    panel.meta["height_at_slot"] = [37 + (x - 34) * slope for x in xs]
    bar = slot_part("crossbar", 300, bar_h, [("top", 40, T, bar_h / 2), ("top", 260, T, bar_h / 2)],
                    qty=2, note="crossbar x2")
    return [panel, bar], {
        "title": "04 Laptop stand",
        "steps": ["Cut 2 panels and 2 crossbars. Use double-wall board if you have it.",
                  "Slide the crossbars into the panel slots (crossbar slots point up).",
                  "The lip at the front stops the laptop sliding off. Panels end up 220 mm apart."],
        "joints": [("panel", 0, "crossbar", 0, bar_h), ("panel", 1, "crossbar", 1, bar_h)],
    }


def ex05_drawer_grid():
    """Egg-crate divider for a drawer 240 x 160 x 50."""
    L, S, H = 240.0, 160.0, 50.0
    long_ = slot_part("long-strip", L, H, [("top", x, T, H / 2) for x in (60, 120, 180)],
                      qty=2, note="long strip x2")
    short = slot_part("short-strip", S, H,
                      [("bottom", y, T, H / 2) for y in (S / 3, 2 * S / 3)],
                      qty=3, note="short strip x3")
    return [long_, short], {
        "title": "05 Drawer divider grid (240 x 160 x 50)",
        "steps": ["Cut 2 long and 3 short strips (flutes running up-down for stiffness).",
                  "Slot the short strips down onto the long strips: 12 compartments.",
                  "Change L, S, H in generate.py to fit your drawer."],
        "joints": [("long-strip", 0, "short-strip", 0, H)],
    }


def ex06_tuck_box():
    """Classic tuck-end box 60 x 40 x 80 from one piece of thin card."""
    W, D, H, G, TK = 60.0, 40.0, 80.0, 12.0, 15.0
    xa, xb, xc, xd, xe = G, G + W, G + W + D, G + 2 * W + D, G + 2 * W + 2 * D
    y0 = TK + D                     # body bottom
    y1 = y0 + H                     # body top
    dust = D / 2
    out = [(xa, y0), (xa, TK), (xa + 5, 0), (xb - 5, 0), (xb, TK), (xb, y0),
           (xb + 5, y0 - dust), (xc - 5, y0 - dust), (xc, y0),
           (xd, y0), (xd + 5, y0 - dust), (xe - 5, y0 - dust), (xe, y0),
           (xe, y1), (xe - 5, y1 + dust), (xd + 5, y1 + dust), (xd, y1),
           (xd, y1 + D), (xd - 5, y1 + D + TK), (xc + 5, y1 + D + TK), (xc, y1 + D),
           (xc, y1), (xc - 5, y1 + dust), (xb + 5, y1 + dust), (xb, y1),
           (xa, y1), (0, y1 - 6), (0, y0 + 6)]
    p = Part("tuck-box-net", note="tuck box, one piece of thin card")
    p.cuts.append(out)
    for x in (xa, xb, xc, xd):
        p.scores.append(((x, y0), (x, y1)))
    p.scores += [((xa, y0), (xb, y0)), ((xa, TK), (xb, TK)),
                 ((xb, y0), (xc, y0)), ((xd, y0), (xe, y0)),
                 ((xc, y1), (xd, y1)), ((xc, y1 + D), (xd, y1 + D)),
                 ((xb, y1), (xc, y1)), ((xd, y1), (xe, y1))]
    p.glues.append([(xa, y0), (xa, y1), (0, y1 - 6), (0, y0 + 6)])
    return [p], {
        "title": "06 Tuck-end box (60 x 40 x 80)",
        "steps": ["Use thin card (cereal box, 0.3-0.5 mm), not corrugated board.",
                  "Cut the outline, score all dashed lines, pre-fold every score.",
                  "Glue the gray flap inside the last side panel. Tuck the lids in at both ends."],
    }


def ex07_four_bar():
    """Four-bar linkage toy: crank turns, rocker rocks. Joints are split
    pins (brass paper fasteners)."""
    W = 24.0
    parts = []
    for name, L in (("crank", 40), ("coupler", 110), ("rocker", 90)):
        p = Part(name, note=f"{name} {L} mm")
        p.cuts.append(notched_rect(L + W, W, [], chamfer=6))
        p.punch += [(W / 2, W / 2), (L + W / 2, W / 2)]
        parts.append(p)
    base = Part("base", note="base board, ground link 120 mm")
    base.cuts.append(notched_rect(170, 70, [], chamfer=8))
    base.punch += [(25, 35), (145, 35)]
    base.meta["lengths"] = (120, 40, 110, 90)
    return [base] + parts, {
        "title": "07 Four-bar linkage toy",
        "steps": ["Cut the base and 3 links. Punch the + marks with a pencil or skewer.",
                  "Join with split pins (paper fasteners): crank and rocker to the base, coupler on top.",
                  "Turn the crank: it goes all the way round, the rocker swings back and forth."],
    }


def ex08_gears():
    """Gear pair 12T / 24T with straight-sided teeth, on split pins or
    pencils."""
    m, z1, z2 = 7.0, 12, 24
    cd = m * (z1 + z2) / 2 + 1.5
    g1 = Part("gear-12t", note="gear 12 teeth")
    g1.cuts.append(straight_gear(m, z1))
    g1.cuts.append(square_hole(0, 0, 7))
    g2 = Part("gear-24t", note="gear 24 teeth")
    g2.cuts.append(straight_gear(m, z2))
    g2.cuts.append(square_hole(0, 0, 7))
    base = Part("gear-base", note=f"base, centers {cd:.1f} mm apart")
    base.cuts.append(notched_rect(cd + 100, 100, [], chamfer=8))
    base.punch += [(50, 50), (50 + cd, 50)]
    base.meta.update(m=m, z=(z1, z2), cd=cd)
    return [g1, g2, base], {
        "title": "08 Gear pair 12T / 24T (2:1)",
        "steps": ["Cut both gears: each tooth is 4 straight cuts. Cut the 7 mm square center holes.",
                  "Push a pencil through each gear into the base marks (or use split pins).",
                  "Turn the small gear twice: the big gear turns once, the other way."],
    }


def ex09_catapult():
    """Catapult: base with slots, two uprights with tabs, an arm on a
    pencil axle, a folded cup."""
    base = Part("catapult-base", note="base")
    base.cuts.append(notched_rect(200, 80, [], chamfer=10))
    slot_y = (40 - 19, 40 + 19)           # uprights 35 mm apart inside
    for y in slot_y:
        base.cuts.append(rect(114.5, y - T / 2, 31, T))  # tab is 30
    base.cuts.append(rect(20, 37, 12, 6))  # rubber band anchor hole
    upright = Part("upright", qty=2, note="upright x2")
    upright.cuts.append([(0, 0), (15, 0), (15, -T), (45, -T), (45, 0), (60, 0),
                         (60, 85), (45, 100), (15, 100), (0, 85)])
    upright.cuts.append(square_hole(30, 80, 8))
    arm = Part("arm", note="arm, axle hole 40 mm from the back")
    arm.cuts.append(notched_rect(220, 25, [("left", 12.5, 6, 8)]))
    arm.cuts.append(square_hole(40, 12.5, 8))
    cup = Part("cup", note="cup: fold the 4 sides up, tape corners")
    s, h = 30.0, 15.0
    cup.cuts.append([(h, 0), (h + s, 0), (h + s, h), (2 * h + s, h), (2 * h + s, h + s),
                     (h + s, h + s), (h + s, 2 * h + s), (h, 2 * h + s), (h, h + s),
                     (0, h + s), (0, h), (h, h)])
    cup.scores += [((h, h), (h + s, h)), ((h + s, h), (h + s, h + s)),
                   ((h, h + s), (h + s, h + s)), ((h, h), (h, h + s))]
    base.meta.update(slot_y=slot_y, slot_x=(114.5, 145.5), arm_w=25)
    upright.meta.update(tab_x=(15, 45), tab_center=130)
    return [base, upright, arm, cup], {
        "title": "09 Catapult",
        "steps": ["Cut all parts; the base slots and square holes are cut out completely.",
                  "Push the upright tabs into the base slots (tape underneath). Pencil through uprights and arm.",
                  "Glue the cup to the front of the arm. Rubber band from the arm notch to the base hole."],
    }


def ex10_shelf():
    """Small shelf: two sides and two shelves joined by cross slots."""
    depth, height, width = 150.0, 220.0, 250.0
    levels = (30.0, 150.0)
    side = slot_part("shelf-side", depth, height,
                     [("left", y, T, depth / 2) for y in levels], qty=2, note="side x2")
    shelf = slot_part("shelf-board", width, depth,
                      [("top", x, T, depth / 2) for x in (20, width - 20)], qty=2,
                      note="shelf x2")
    return [side, shelf], {
        "title": "10 Small shelf (250 x 150 x 220)",
        "steps": ["Cut 2 sides (flutes up-down) and 2 shelves (flutes left-right).",
                  "Slide each shelf's slots into the side slots from the front.",
                  "Light items only, or use double-wall board."],
        "joints": [("shelf-side", 0, "shelf-board", 0, depth)],
    }


EXAMPLES = [ex01_test_strip, ex02_phone_stand, ex03_desk_organizer, ex04_laptop_stand,
            ex05_drawer_grid, ex06_tuck_box, ex07_four_bar, ex08_gears,
            ex09_catapult, ex10_shelf]


# ------------------------------------------------------------- layout

def tiles_for(w, h):
    cols = 1 if w <= UW else math.ceil((w - OV) / (UW - OV))
    rows = 1 if h <= UH else math.ceil((h - OV) / (UH - OV))
    return cols, rows


def layout(parts):
    """Place parts in rows (shelf packing). Try a few row widths and keep
    the one that needs the fewest A4 sheets. Returns (width, height)."""
    best = None
    widest = max(p.bbox()[2] - p.bbox()[0] for p in parts)
    for n in (1, 2, 3):
        limit = max(widest, n * (UW - OV) + OV)
        x = y = row_h = 0.0
        placed, total_w = [], 0.0
        for p in parts:
            x0, y0, x1, y1 = p.bbox()
            w, h = x1 - x0, y1 - y0
            if x > 0 and x + w > limit:
                x, y, row_h = 0.0, y + row_h + GAP, 0.0
            placed.append((p, x - x0, y - y0))
            x += w + GAP
            row_h = max(row_h, h)
            total_w = max(total_w, x - GAP)
        total_h = y + row_h
        cols, rows = tiles_for(total_w, total_h)
        if best is None or cols * rows < best[0]:
            best = (cols * rows, placed, total_w, total_h)
    _, placed, W, H = best
    # flip so the first row is at the top of the drawing
    for p, ox, oy in placed:
        x0, y0, x1, y1 = p.bbox()
        p.pos = (ox, H - (oy + y0) - (y1 - y0) - y0)
    return W, H


def world(p, pt):
    return pt[0] + p.pos[0], pt[1] + p.pos[1]


# ------------------------------------------------------------- drawing

def draw_parts(c, parts, sx=1.0, ox=0.0, oy=0.0, labels=True):
    """Draw all parts in world mm, scaled by sx and offset by (ox, oy) mm."""
    def P(pt):
        return (ox + pt[0] * sx) * mm, (oy + pt[1] * sx) * mm

    for p in parts:
        c.setFillGray(0.85)
        for g in p.glues:
            path = c.beginPath()
            pts = [P(world(p, q)) for q in g]
            path.moveTo(*pts[0])
            for q in pts[1:]:
                path.lineTo(*q)
            path.close()
            c.drawPath(path, stroke=0, fill=1)
        c.setStrokeColorRGB(0, 0, 0)
        c.setLineWidth(0.35 * mm * min(1, sx * 2))
        for cut in p.cuts:
            path = c.beginPath()
            pts = [P(world(p, q)) for q in cut]
            path.moveTo(*pts[0])
            for q in pts[1:]:
                path.lineTo(*q)
            path.close()
            c.drawPath(path, stroke=1, fill=0)
        c.setStrokeColorRGB(0, 0.2, 0.9)
        c.setDash(3 * mm * sx, 2 * mm * sx)
        for a, b in p.scores:
            c.line(*P(world(p, a)), *P(world(p, b)))
        c.setDash()
        c.setStrokeColorRGB(0, 0, 0)
        for q in p.punch:
            x, y = P(world(p, q))
            d = 3 * mm * sx
            c.line(x - d, y, x + d, y)
            c.line(x, y - d, x, y + d)
        if labels:
            x0, y0, x1, y1 = p.bbox()
            cx, cy = P(world(p, ((x0 + x1) / 2, (y0 + y1) / 2)))
            c.setFillColorRGB(0.3, 0.3, 0.3)
            c.setFont("Helvetica", max(4, 8 * min(1, sx * 2)))
            text = p.note + (f"  (cut {p.qty})" if p.qty > 1 else "")
            c.drawCentredString(cx, cy, text)
        c.setFillColorRGB(0, 0, 0)


def scale_bars(c):
    c.setStrokeColorRGB(0, 0, 0)
    c.setLineWidth(0.3 * mm)
    x0, y0 = 30, 10
    c.line(x0 * mm, y0 * mm, (x0 + 100) * mm, y0 * mm)
    for i in range(11):
        t = 3 if i % 5 == 0 else 1.5
        c.line((x0 + 10 * i) * mm, y0 * mm, (x0 + 10 * i) * mm, (y0 + t) * mm)
    c.setFont("Helvetica", 7)
    c.drawString((x0 + 103) * mm, (y0 - 0.5) * mm, "100 mm: measure it! (print at 100 %)")
    xv, yv = 6, 60
    c.line(xv * mm, yv * mm, xv * mm, (yv + 100) * mm)
    for i in range(11):
        t = 3 if i % 5 == 0 else 1.5
        c.line(xv * mm, (yv + 10 * i) * mm, (xv + t) * mm, (yv + 10 * i) * mm)


def header(c, title, line2):
    c.setFont("Helvetica-Bold", 11)
    c.drawString(CX * mm, (PAGE_H - 10) * mm, title)
    c.setFont("Helvetica", 7.5)
    c.drawString(CX * mm, (PAGE_H - 15) * mm, line2)
    c.drawString(CX * mm, (PAGE_H - 19) * mm,
                 "Solid = CUT    dashed blue = SCORE + FOLD    gray = GLUE    + = punch hole    "
                 f"Board {T:g} mm (slots {T:g} mm)")


def cross(c, x, y, r=4):
    c.setStrokeColorRGB(0.8, 0, 0)
    c.setLineWidth(0.25 * mm)
    c.line((x - r) * mm, y * mm, (x + r) * mm, y * mm)
    c.line(x * mm, (y - r) * mm, x * mm, (y + r) * mm)
    c.circle(x * mm, y * mm, r * 0.5 * mm)
    c.setStrokeColorRGB(0, 0, 0)


def col_name(i):
    return chr(ord("A") + i)


def write_example(c, parts, info, W, H):
    cols, rows = tiles_for(W, H)
    n = cols * rows
    steps = info["steps"]
    title = info["title"]
    if n == 1:
        header(c, title, "Fits on one A4 sheet. " + " ".join(steps)[:150])
        ox = CX + (UW - W) / 2
        oy = CY + UH - H
        draw_parts(c, parts, 1.0, ox, oy)
        c.setFont("Helvetica", 7.5)
        y = CY + UH - H - 8
        for s in steps:
            if y > CY:
                c.drawString(CX * mm, y * mm, s)
                y -= 4
        scale_bars(c)
        c.showPage()
        return 1

    # map page: whole layout scaled down, sheet grid on top
    header(c, title, f"{n} A4 sheets ({cols} across x {rows} down) + this map. "
                     "Print ALL pages at 100 % / actual size.")
    step_x, step_y = UW - OV, UH - OV
    tw, th = cols * step_x + OV, rows * step_y + OV
    sx = min(UW / tw, (UH - 70) / th)
    mx = CX + (UW - tw * sx) / 2
    my = CY + 60
    draw_parts(c, parts, sx, mx, my, labels=False)
    c.setStrokeColorRGB(0.8, 0, 0)
    c.setLineWidth(0.3)
    for i in range(cols):
        for j in range(rows):
            x, y = mx + i * step_x * sx, my + j * step_y * sx
            c.rect(x * mm, y * mm, UW * sx * mm, UH * sx * mm)
            c.setFillColorRGB(0.8, 0, 0)
            c.setFont("Helvetica-Bold", 10)
            c.drawCentredString((x + UW * sx / 2) * mm, (y + UH * sx / 2) * mm,
                                f"{col_name(i)}{rows - j}")
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica", 8)
    lines = ["How to join the sheets:",
             "1. Cut each sheet along its gray frame on the LEFT and BOTTOM side only (not on A-column / bottom row).",
             "2. Lay it over its neighbour so the red crosses sit exactly on top of each other. Tape it.",
             "3. Join a whole row first, then the rows. Then glue the template to the board and cut.",
             "Parts: " + ", ".join(f"{p.note} (x{p.qty})" if p.qty > 1 else p.note for p in parts)] + steps
    y = CY + 50
    for s in lines:
        c.drawString(CX * mm, y * mm, s[:120])
        y -= 4.2
    scale_bars(c)
    c.showPage()

    for j in reversed(range(rows)):           # top row first
        for i in range(cols):
            wx, wy = i * step_x, j * step_y
            header(c, f"{title}  -  sheet {col_name(i)}{rows - j}  ({cols} x {rows})",
                   "Print at 100 %. Trim the LEFT and BOTTOM edge along the gray frame, "
                   "then overlap the neighbour and match the red crosses.")
            c.saveState()
            path = c.beginPath()
            path.rect(CX * mm, CY * mm, UW * mm, UH * mm)
            c.clipPath(path, stroke=0, fill=0)
            # light 50 mm grid, the same on every sheet
            c.setStrokeGray(0.88)
            c.setLineWidth(0.2)
            gx = math.floor(wx / 50) * 50
            while gx <= wx + UW:
                c.line((CX + gx - wx) * mm, CY * mm, (CX + gx - wx) * mm, (CY + UH) * mm)
                gx += 50
            gy = math.floor(wy / 50) * 50
            while gy <= wy + UH:
                c.line(CX * mm, (CY + gy - wy) * mm, (CX + UW) * mm, (CY + gy - wy) * mm)
                gy += 50
            draw_parts(c, parts, 1.0, CX - wx, CY - wy)
            # alignment crosses in the overlap strips
            for k in range(1, cols):
                xs = k * step_x + OV / 2
                for yy in range(int(wy) + 30, int(wy + UH), 60):
                    cross(c, CX + xs - wx, CY + yy - wy)
            for k in range(1, rows):
                ys = k * step_y + OV / 2
                for xx in range(int(wx) + 30, int(wx + UW), 60):
                    cross(c, CX + xx - wx, CY + ys - wy)
            c.restoreState()
            # frame and overlap strips
            c.setStrokeGray(0.55)
            c.setLineWidth(0.3)
            c.rect(CX * mm, CY * mm, UW * mm, UH * mm)
            c.setFillGray(0.4)
            c.setFont("Helvetica", 6.5)
            if i > 0:
                c.drawString(CX * mm, (CY - 4) * mm, f"<- left edge overlaps sheet {col_name(i - 1)}{rows - j}")
            if j > 0:
                c.drawString((CX + UW / 2) * mm, (CY - 4) * mm, f"bottom edge overlaps sheet {col_name(i)}{rows - j + 1}")
            c.setFillColorRGB(0, 0, 0)
            scale_bars(c)
            c.showPage()
    return n + 1


def write_svg(parts, W, H, path, title):
    m = 5
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W + 2 * m:.2f}mm" '
           f'height="{H + 2 * m:.2f}mm" viewBox="0 0 {W + 2 * m:.2f} {H + 2 * m:.2f}">',
           f"<title>{title}</title>"]

    def pt(p, q):
        x, y = world(p, q)
        return f"{x + m:.3f},{H - y + m:.3f}"

    for p in parts:
        out.append(f'<g id="{p.name}">')
        for g in p.glues:
            out.append('<path fill="#d9d9d9" stroke="none" d="M ' + " L ".join(pt(p, q) for q in g) + ' Z"/>')
        for cut in p.cuts:
            out.append('<path fill="none" stroke="#ff0000" stroke-width="0.2" d="M '
                       + " L ".join(pt(p, q) for q in cut) + ' Z"/>')
        for a, b in p.scores:
            out.append(f'<path fill="none" stroke="#0033e6" stroke-width="0.2" '
                       f'stroke-dasharray="3,2" d="M {pt(p, a)} L {pt(p, b)}"/>')
        for q in p.punch:
            x, y = world(p, q)
            out.append(f'<circle cx="{x + m:.3f}" cy="{H - y + m:.3f}" r="1.5" fill="none" stroke="#ff0000" stroke-width="0.2"/>')
        out.append("</g>")
    out.append("</svg>")
    with open(path, "w") as f:
        f.write("\n".join(out) + "\n")


def build():
    result = []
    for ex in EXAMPLES:
        parts, info = ex()
        W, H = layout(parts)
        result.append((ex.__name__[2:4], parts, info, W, H))
    return result


def main():
    os.makedirs(os.path.join(OUT, "pdf"), exist_ok=True)
    os.makedirs(os.path.join(OUT, "svg"), exist_ok=True)
    allc = canvas.Canvas(os.path.join(OUT, "pdf", "all-examples.pdf"), pagesize=A4)
    allc.setTitle("Cardboard knife-cut templates")
    for num, parts, info, W, H in build():
        slug = info["title"].split("(")[0].split(":")[0].strip().lower()
        slug = "".join(ch if ch.isalnum() else "-" for ch in slug).strip("-")
        while "--" in slug:
            slug = slug.replace("--", "-")
        c = canvas.Canvas(os.path.join(OUT, "pdf", slug + ".pdf"), pagesize=A4)
        c.setTitle(info["title"])
        pages = write_example(c, parts, info, W, H)
        c.save()
        write_example(allc, parts, info, W, H)
        write_svg(parts, W, H, os.path.join(OUT, "svg", slug + ".svg"), info["title"])
        cols, rows = tiles_for(W, H)
        print(f"{slug:32s} {W:6.1f} x {H:6.1f} mm  {pages} page(s)"
              + (f"  ({cols} x {rows} sheets + map)" if pages > 1 else ""))
    allc.save()
    print("wrote pdf/ and svg/")


if __name__ == "__main__":
    main()
