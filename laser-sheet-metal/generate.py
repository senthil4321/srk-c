#!/usr/bin/env python3
"""
generate.py - laser-cut sheet metal examples for 2 mm sheet

Writes, for every part:
  dxf/<part>.dxf   cut file for the laser (DXF R2000, millimeters, true arcs)
  svg/<part>.svg   same geometry at 1:1 for laser software (LightBurn etc.)
and one multi-page file:
  pdf/paper-check-A4.pdf   every example at 1:1 on A4, with scale bars,
                           to print on paper and check before cutting metal

Layers (DXF) / colors (SVG):
  CUT   red    through-cuts (closed contours only)
  BEND  blue   bend lines, dashed: NOT cut, for the press brake
  ETCH  green  engraving / marking text: NOT cut through

Requires: ezdxf, reportlab   (pip install ezdxf reportlab)
Run:      python3 generate.py
"""
import math
import os

import ezdxf
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

T = 2.0               # sheet thickness
SLOT_W = T + 0.2      # slot width for a 2 mm tab
TAB_W = 10.0          # tab width
SLOT_L = TAB_W + 0.2  # slot length for a tab
K_FACTOR = 0.44       # mild steel, air bending
BEND_R = 2.0          # inside bend radius (= thickness)

OUT = os.path.dirname(os.path.abspath(__file__))
CORNER_BULGE = math.tan(math.radians(90) / 4)  # 90 deg arc


# ---------------------------------------------------------------- geometry

class Part:
    """One flat part. Contours are closed lists of (x, y, bulge), where
    bulge is the arc from that vertex to the next (0 = straight line,
    +1 = CCW half circle). Circles are (cx, cy, r)."""

    def __init__(self, name, title, qty=1, material="2 mm mild steel"):
        self.name = name
        self.title = title
        self.qty = qty
        self.material = material
        self.contours = []
        self.circles = []
        self.bends = []   # ((x1, y1), (x2, y2), note)
        self.texts = []   # (x, y, height, text)
        self.rods = []    # (x, y, kind): holes for threaded / smooth rods
        self.meta = {}    # positions used by check.py (pivots, centers)
        self.offset = (0.0, 0.0)  # world position = local + offset

    def contour(self, verts):
        self.contours.append(list(verts))
        return self

    def hole(self, cx, cy, d):
        self.circles.append((cx, cy, d / 2))
        return self

    def bbox(self):
        pts = [p for c in self.contours for p in tessellate(c)]
        for cx, cy, r in self.circles:
            pts += [(cx - r, cy - r), (cx + r, cy + r)]
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        return min(xs), min(ys), max(xs), max(ys)

    def normalize(self):
        """Move the part so its bounding box starts at (0, 0)."""
        x0, y0, _, _ = self.bbox()
        self.offset = (x0, y0)
        self.contours = [[(x - x0, y - y0, b) for x, y, b in c]
                         for c in self.contours]
        self.circles = [(x - x0, y - y0, r) for x, y, r in self.circles]
        self.bends = [((a[0] - x0, a[1] - y0), (b[0] - x0, b[1] - y0), n)
                      for a, b, n in self.bends]
        self.texts = [(x - x0, y - y0, h, s) for x, y, h, s in self.texts]
        self.rods = [(x - x0, y - y0, k) for x, y, k in self.rods]
        return self


def arc_points(p1, p2, bulge, max_seg_deg=3.0):
    """Points on the arc from p1 to p2 (excluding p1)."""
    if abs(bulge) < 1e-12:
        return [p2]
    (x1, y1), (x2, y2) = p1, p2
    dx, dy = x2 - x1, y2 - y1
    c = math.hypot(dx, dy)
    theta = 4 * math.atan(bulge)
    off = c * (1 - bulge * bulge) / (4 * bulge)
    cx = (x1 + x2) / 2 - dy / c * off
    cy = (y1 + y2) / 2 + dx / c * off
    r = math.hypot(x1 - cx, y1 - cy)
    a1 = math.atan2(y1 - cy, x1 - cx)
    n = max(2, int(abs(math.degrees(theta)) / max_seg_deg))
    return [(cx + r * math.cos(a1 + theta * i / n),
             cy + r * math.sin(a1 + theta * i / n)) for i in range(1, n + 1)]


def tessellate(verts):
    pts = []
    for i, (x, y, b) in enumerate(verts):
        nx, ny, _ = verts[(i + 1) % len(verts)]
        if not pts:
            pts.append((x, y))
        pts += arc_points((x, y), (nx, ny), b)
    return pts[:-1]  # last point repeats the first


def rounded_rect(x0, y0, w, h, r):
    x1, y1 = x0 + w, y0 + h
    if r <= 0:
        return [(x0, y0, 0), (x1, y0, 0), (x1, y1, 0), (x0, y1, 0)]
    k = CORNER_BULGE
    return [(x0 + r, y0, 0), (x1 - r, y0, k), (x1, y0 + r, 0),
            (x1, y1 - r, k), (x1 - r, y1, 0), (x0 + r, y1, k),
            (x0, y1 - r, 0), (x0, y0 + r, k)]


def obround(x0, y0, length, width, angle=0.0):
    """Slot / link shape: centers of the round ends at (x0, y0) and
    `length` away along `angle` (degrees)."""
    w = width / 2
    local = [(0, -w, 0), (length, -w, 1), (length, w, 0), (0, w, 1)]
    a = math.radians(angle)
    ca, sa = math.cos(a), math.sin(a)
    return [(x0 + x * ca - y * sa, y0 + x * sa + y * ca, b) for x, y, b in local]


def rect_center(cx, cy, w, h):
    return rounded_rect(cx - w / 2, cy - h / 2, w, h, 0)


def polar(r, a):
    return r * math.cos(a), r * math.sin(a)


def involute_gear(m, z, pa_deg=20.0, flank_pts=8):
    """Closed contour of an involute spur gear centered at the origin,
    tooth 0 pointing along +X. Tip and root are true arcs."""
    pa = math.radians(pa_deg)
    r = m * z / 2
    rb = r * math.cos(pa)
    ra = r + m
    rf = r - 1.25 * m

    def inv(a):
        return math.tan(a) - a

    def half_angle(rho):  # angle from tooth center line to the flank
        return math.pi / (2 * z) + inv(pa) - inv(math.acos(min(1.0, rb / rho)))

    r_start = max(rb, rf)
    radii = [r_start + (ra - r_start) * i / flank_pts for i in range(flank_pts + 1)]
    th_a = half_angle(ra)
    th_b = half_angle(r_start)
    pitch = 2 * math.pi / z
    verts = []
    for k in range(z):
        c = k * pitch
        if rf < rb:
            verts.append((*polar(rf, c - th_b), 0))
        for i, rho in enumerate(radii):
            b = math.tan(2 * th_a / 4) if i == len(radii) - 1 else 0
            verts.append((*polar(rho, c - half_angle(rho)), b))
        for i, rho in enumerate(reversed(radii)):
            last = (i == len(radii) - 1) and rf >= rb
            b = math.tan((pitch - 2 * th_b) / 4) if last else 0
            verts.append((*polar(rho, c + half_angle(rho)), b))
        if rf < rb:
            verts.append((*polar(rf, c + th_b), math.tan((pitch - 2 * th_b) / 4)))
    return verts


def tabbed_rect(w, h, tabs):
    """Rectangle (0,0)-(w,h) with tabs sticking out by T.
    tabs: list of (edge, center, width); edge in 'bottom', 'right',
    'top', 'left'; center measured along the edge from its start
    (bottom: from x=0, right: from y=0, top: from x=0, left: from y=0)."""
    by_edge = {e: sorted((c, tw) for ed, c, tw in tabs if ed == e)
               for e in ("bottom", "right", "top", "left")}
    pts = []
    # bottom edge, left -> right, tabs go -Y
    pts.append((0, 0))
    for c, tw in by_edge["bottom"]:
        pts += [(c - tw / 2, 0), (c - tw / 2, -T), (c + tw / 2, -T), (c + tw / 2, 0)]
    pts.append((w, 0))
    for c, tw in by_edge["right"]:
        pts += [(w, c - tw / 2), (w + T, c - tw / 2), (w + T, c + tw / 2), (w, c + tw / 2)]
    pts.append((w, h))
    for c, tw in sorted(by_edge["top"], reverse=True):
        pts += [(c + tw / 2, h), (c + tw / 2, h + T), (c - tw / 2, h + T), (c - tw / 2, h)]
    pts.append((0, h))
    for c, tw in sorted(by_edge["left"], reverse=True):
        pts += [(0, c + tw / 2), (-T, c + tw / 2), (-T, c - tw / 2), (0, c - tw / 2)]
    return [(x, y, 0) for x, y in pts]


# ---------------------------------------------------------------- examples

def ex01_test_coupon():
    """Hole sizes, slot widths and a tab to check fits and the laser's
    kerf before cutting real parts."""
    p = Part("01-test-coupon", "01 Test coupon: holes, slots, tab fit")
    p.contour(rounded_rect(0, 0, 120, 55, 3))
    holes = [2.0, 2.5, 3.0, 3.4, 4.0, 4.5, 5.0, 5.5, 6.0, 6.6]
    for i, d in enumerate(holes):
        x = 8 + i * 11.5
        p.hole(x, 44, d)
        p.texts.append((x - 3, 36, 2.5, f"{d:g}"))
    slots = [2.0, 2.1, 2.2, 2.3, 2.4, 2.5]
    for i, sw in enumerate(slots):
        x = 12 + i * 19
        p.contour(rect_center(x, 20, SLOT_L, sw))
        p.texts.append((x - 6, 12, 2.5, f"{sw:g}"))
    p.texts.append((4, 4, 3, "HOLE D / SLOT W  mm   T=2"))
    p.texts.append((4, 49.5, 2.5, "SRK LASER TEST"))

    tab = Part("01-test-tab", "01 Test tab (insert into the slots)")
    tab.contour(tabbed_rect(30, 15, [("bottom", 15, TAB_W)]))
    tab.texts.append((3, 6, 3, "TAB 10x2"))
    return [p, tab]


def ex02_l_bracket():
    """90 deg L-bracket: flat pattern with a bend line."""
    leg_a, leg_b, width = 40.0, 30.0, 30.0   # outside dimensions
    ba = math.pi / 2 * (BEND_R + K_FACTOR * T)            # bend allowance
    flat_a = leg_a - (BEND_R + T)
    flat_b = leg_b - (BEND_R + T)
    length = flat_a + ba + flat_b
    p = Part("02-l-bracket", f"02 L-bracket 40x30x30, flat {length:.2f} mm")
    p.contour(rounded_rect(0, 0, width, length, 3))
    p.hole(width / 2 - 8, 16, 5.5).hole(width / 2 + 8, 16, 5.5)
    yb = flat_a + ba + 14
    p.contour(obround(width / 2 - 5, yb, 10, 5.5))  # adjustment slot
    y_bend = flat_a + ba / 2
    p.bends.append(((0, y_bend), (width, y_bend),
                    f"BEND UP 90  Ri={BEND_R:g}  K={K_FACTOR}"))
    p.texts.append((2, 4, 2.5, "LEG A 40"))
    return [p]


def ex03_gear_pair():
    """Spur gear pair m=2.5, 16:32 (2:1), and a plate holding both axles."""
    m, z1, z2 = 2.5, 16, 32
    cd = m * (z1 + z2) / 2 + 0.2  # + backlash
    g1 = Part("03-gear-16t", "03 Spur gear m2.5 16T, bore 8.2")
    g1.contour(involute_gear(m, z1))
    g1.hole(0, 0, 8.2)
    g2 = Part("03-gear-32t", "03 Spur gear m2.5 32T, bore 8.2")
    g2.contour(involute_gear(m, z2))
    g2.hole(0, 0, 8.2)
    for k in range(4):
        x, y = polar(22, k * math.pi / 2 + math.pi / 4)
        g2.hole(x, y, 14)
    plate = Part("03-gear-plate", f"03 Gear plate, center distance {cd:.1f}")
    plate.contour(rounded_rect(-25, -22, cd + 50, 44, 4))
    plate.hole(0, 0, 8.2).hole(cd, 0, 8.2)
    for x in (-18, cd + 18):
        for y in (-15, 15):
            plate.hole(x, y, 4.5)
    plate.texts.append((cd / 2 - 12, -18, 3, f"CD {cd:.1f}"))
    return [g1, g2, plate]


def ex04_four_bar():
    """Four-bar crank-rocker (same lengths as Fusion mechanism 04)."""
    hole, w = 5.2, 12.0
    parts = []
    for name, L in (("crank", 20), ("coupler", 55), ("rocker", 45)):
        p = Part(f"04-four-bar-{name}", f"04 Four-bar {name}, {L} mm")
        p.contour(obround(0, 0, L, w))
        p.hole(0, 0, hole).hole(L, 0, hole)
        parts.append(p)
    base = Part("04-four-bar-base", "04 Four-bar base, pivots 60 mm")
    base.contour(rounded_rect(-20, -25, 100, 70, 4))
    base.hole(0, 0, hole).hole(60, 0, hole)
    for x in (-13, 73):
        for y in (-18, 38):
            base.hole(x, y, 4.5)
    base.texts.append((-2, -8, 3, "O2"))
    base.texts.append((58, -8, 3, "O4"))
    return [base] + parts


def ex05_tab_box():
    """Open box 60 x 40 x 30 inside, held together by tabs and slots."""
    li, wi, h = 60.0, 40.0, 30.0
    e = 5.0                                   # overhang outside the walls
    lf = li + 2 * T + 2 * e                   # front/back wall length (74)
    xs = li / 2 + T / 2                       # side wall center from middle
    yf = wi / 2 + T / 2                       # front wall center from middle

    bottom = Part("05-box-bottom", "05 Box bottom (slots for the walls)")
    bw, bh = lf, wi + 2 * T + 2 * e
    bottom.contour(rounded_rect(-bw / 2, -bh / 2, bw, bh, 3))
    for sy in (-yf, yf):
        for sx in (-18, 18):
            bottom.contour(rect_center(sx, sy, SLOT_L, SLOT_W))
    for sx in (-xs, xs):
        bottom.contour(rect_center(sx, 0, SLOT_W, SLOT_L))

    front = Part("05-box-front-back", "05 Box front / back", qty=2)
    front.contour(tabbed_rect(lf, h, [("bottom", lf / 2 - 18, TAB_W),
                                      ("bottom", lf / 2 + 18, TAB_W)]))
    for sx in (lf / 2 - xs, lf / 2 + xs):
        front.contour(rect_center(sx, h / 2, SLOT_W, SLOT_L))

    side = Part("05-box-side", "05 Box side", qty=2)
    side.contour(tabbed_rect(wi, h, [("bottom", wi / 2, TAB_W),
                                     ("left", h / 2, TAB_W),
                                     ("right", h / 2, TAB_W)]))
    return [bottom, front, side]


def ex06_ratchet():
    """Ratchet wheel, pawl and base plate. The wheel turns freely
    counter-clockwise and locks clockwise."""
    teeth, ro, rr = 12, 22.0, 18.0
    wheel = Part("06-ratchet-wheel", "06 Ratchet wheel 12T, bore 6.2")
    verts = []
    land = 1.5 / ro                                 # 1.5 mm flat tip
    for k in range(teeth):
        a = math.pi / 2 + k * 2 * math.pi / teeth   # locking face at 90 deg
        verts += [(*polar(rr, a), 0), (*polar(ro, a), math.tan(land / 4)),
                  (*polar(ro, a + land), 0)]
    wheel.contour(verts)
    wheel.hole(0, 0, 6.2)
    for k in range(2):
        wheel.hole(*polar(10, k * math.pi), 3.4)

    P = (32.0, 30.0)                      # pawl pivot
    A, B = (0.3, 18.6), (0.3, 21.4)       # pawl tip face, 0.3 mm from the tooth
    M = ((A[0] + B[0]) / 2, (A[1] + B[1]) / 2)
    d = (P[0] - M[0], P[1] - M[1])
    dl = math.hypot(*d)
    n = (-d[1] / dl * 6, d[0] / dl * 6)   # left normal, boss radius 6
    pawl = Part("06-ratchet-pawl", "06 Ratchet pawl, pivot 5.2")
    pawl.contour([(A[0], A[1], 0), (P[0] - n[0], P[1] - n[1], 1),
                  (P[0] + n[0], P[1] + n[1], 0), (B[0], B[1], 0)])
    pawl.hole(P[0], P[1], 5.2)
    pawl.hole(20, 26.2, 3.2)              # spring hole, on the arm's center line

    base = Part("06-ratchet-base", "06 Ratchet base plate")
    base.contour(rounded_rect(-30, -30, 80, 86, 4))
    base.hole(0, 0, 6.2).hole(P[0], P[1], 5.2).hole(20, 50, 3.2)
    for x in (-24, 44):
        for y in (-24, 50):
            base.hole(x, y, 4.5)
    base.texts.append((23, 49, 2.5, "SPRING"))
    return [wheel, pawl, base]


def ex07_nameplate():
    """Name plate with engraved text (ETCH layer) and four screw holes."""
    p = Part("07-nameplate", "07 Name plate with engraving")
    p.contour(rounded_rect(0, 0, 80, 30, 3))
    for x in (5, 75):
        for y in (5, 25):
            p.hole(x, y, 3.4)
    p.texts.append((14, 12, 10, "SRK-C"))
    p.texts.append((24, 5, 3, "2 mm STEEL"))
    return [p]


TITLES = {
    "01": "01 Test coupon: hole sizes, slot widths, tab fit",
    "02": "02 L-bracket with bend line (flat pattern)",
    "03": "03 Spur gear pair m2.5, 16T / 32T, and axle plate",
    "04": "04 Four-bar linkage: base and three links",
    "05": "05 Tab-and-slot box, 60 x 40 x 30 inside",
    "06": "06 Ratchet wheel, pawl and base plate",
    "07": "07 Name plate with engraving",
}

EXAMPLES = [ex01_test_coupon, ex02_l_bracket, ex03_gear_pair, ex04_four_bar,
            ex05_tab_box, ex06_ratchet, ex07_nameplate]


def all_examples():
    """Examples 01-07 from this file, 08-20 (two plates joined by rods)
    from rod_examples.py. Returns (functions, titles, bills of material)."""
    import rod_examples
    return (EXAMPLES + rod_examples.EXAMPLES,
            {**TITLES, **rod_examples.TITLES}, rod_examples.BOM)


def build_parts(normalize=True):
    groups = [ex() for ex in all_examples()[0]]
    if normalize:
        for g in groups:
            for p in g:
                p.normalize()
    return groups


# ---------------------------------------------------------------- writers

def write_dxf(p, path):
    doc = ezdxf.new("R2000", setup=True)
    doc.units = ezdxf.units.MM
    doc.header["$INSUNITS"] = 4
    doc.header["$MEASUREMENT"] = 1
    doc.layers.add("CUT", color=1)
    doc.layers.add("BEND", color=5, linetype="DASHED")
    doc.layers.add("ETCH", color=3)
    msp = doc.modelspace()
    for c in p.contours:
        msp.add_lwpolyline([(x, y, 0, 0, b) for x, y, b in c],
                           format="xyseb", close=True,
                           dxfattribs={"layer": "CUT"})
    for cx, cy, r in p.circles:
        msp.add_circle((cx, cy), r, dxfattribs={"layer": "CUT"})
    for a, b, note in p.bends:
        msp.add_line(a, b, dxfattribs={"layer": "BEND"})
        msp.add_text(note, height=2.5, dxfattribs={"layer": "BEND"}).set_placement(
            (a[0] + 1, a[1] + 1))
    for x, y, h, s in p.texts:
        msp.add_text(s, height=h, dxfattribs={"layer": "ETCH"}).set_placement((x, y))
    doc.saveas(path)


def write_svg(p, path):
    x0, y0, x1, y1 = p.bbox()
    m = 2.0
    w, h = x1 - x0 + 2 * m, y1 - y0 + 2 * m

    def pt(x, y):  # flip Y: SVG y grows downward
        return f"{x - x0 + m:.4f},{y1 - y + m:.4f}"

    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.3f}mm" '
           f'height="{h:.3f}mm" viewBox="0 0 {w:.3f} {h:.3f}">',
           f"<title>{p.title} - {p.material} - qty {p.qty}</title>",
           '<g id="CUT" fill="none" stroke="#ff0000" stroke-width="0.1">']
    for c in p.contours:
        pts = tessellate(c)
        out.append('<path d="M ' + " L ".join(pt(*q) for q in pts) + ' Z"/>')
    for cx, cy, r in p.circles:
        out.append(f'<circle cx="{cx - x0 + m:.4f}" cy="{y1 - cy + m:.4f}" r="{r:.4f}"/>')
    out.append("</g>")
    out.append('<g id="BEND" fill="none" stroke="#0000ff" stroke-width="0.1" '
               'stroke-dasharray="2,1">')
    for a, b, _ in p.bends:
        out.append(f'<path d="M {pt(*a)} L {pt(*b)}"/>')
    out.append("</g>")
    out.append('<g id="ETCH" fill="#00a000" font-family="Helvetica, Arial, sans-serif">')
    for x, y, th, s in p.texts:
        out.append(f'<text x="{x - x0 + m:.3f}" y="{y1 - y + m:.3f}" '
                   f'font-size="{th:.2f}">{s}</text>')
    out.append("</g></svg>")
    with open(path, "w") as f:
        f.write("\n".join(out) + "\n")


def draw_part_pdf(c, p, ox, oy):
    """Draw part p with its lower-left at (ox, oy) mm on the page."""
    c.setLineWidth(0.15 * mm)
    c.setStrokeColorRGB(0, 0, 0)
    for cont in p.contours:
        pts = tessellate(cont)
        path = c.beginPath()
        path.moveTo((ox + pts[0][0]) * mm, (oy + pts[0][1]) * mm)
        for x, y in pts[1:]:
            path.lineTo((ox + x) * mm, (oy + y) * mm)
        path.close()
        c.drawPath(path, stroke=1, fill=0)
    for cx, cy, r in p.circles:
        c.circle((ox + cx) * mm, (oy + cy) * mm, r * mm, stroke=1, fill=0)
    c.setStrokeColorRGB(0, 0, 1)
    c.setDash(4, 2)
    for a, b, _ in p.bends:
        c.line((ox + a[0]) * mm, (oy + a[1]) * mm, (ox + b[0]) * mm, (oy + b[1]) * mm)
    c.setDash()
    c.setFillColorRGB(0, 0.5, 0)
    for x, y, th, s in p.texts:
        c.setFont("Helvetica", th * mm)
        c.drawString((ox + x) * mm, (oy + y) * mm, s)
    c.setFillColorRGB(0, 0, 0)


def scale_bars(c):
    """100 mm bars in X and Y with 10 mm ticks."""
    c.setLineWidth(0.3 * mm)
    c.setStrokeColorRGB(0, 0, 0)
    x0, y0 = 20, 14
    c.line(x0 * mm, y0 * mm, (x0 + 100) * mm, y0 * mm)
    for i in range(11):
        t = 3 if i % 5 == 0 else 1.5
        c.line((x0 + 10 * i) * mm, y0 * mm, (x0 + 10 * i) * mm, (y0 + t) * mm)
    c.setFont("Helvetica", 8)
    c.drawString((x0 + 103) * mm, (y0 - 1) * mm, "100 mm (X)")
    xv, yv = 12, 30
    c.line(xv * mm, yv * mm, xv * mm, (yv + 100) * mm)
    for i in range(11):
        t = 3 if i % 5 == 0 else 1.5
        c.line(xv * mm, (yv + 10 * i) * mm, (xv + t) * mm, (yv + 10 * i) * mm)
    c.saveState()
    c.translate((xv - 2) * mm, (yv + 30) * mm)
    c.rotate(90)
    c.drawString(0, 0, "100 mm (Y)")
    c.restoreState()


def write_pdf(groups, path):
    pw, ph = A4[0] / mm, A4[1] / mm
    c = canvas.Canvas(path, pagesize=A4)
    c.setTitle("Laser sheet metal examples - paper check 1:1")
    _, titles, boms = all_examples()
    for group in groups:
        num = group[0].name[:2]
        c.setFont("Helvetica-Bold", 12)
        c.drawString(20 * mm, (ph - 15) * mm, titles[num])
        c.setFont("Helvetica", 8)
        c.drawString(20 * mm, (ph - 21) * mm,
                     "PRINT AT 100 % / ACTUAL SIZE (no 'fit to page'). "
                     "Both bars must measure exactly 100 mm.")
        c.drawString(20 * mm, (ph - 25) * mm,
                     "Black = cut, blue dashed = bend line, green = engraving. "
                     f"Material: {group[0].material}.")
        y_text = ph - 25
        if num in boms:
            c.setFont("Helvetica-Bold", 8)
            y_text -= 5
            c.drawString(20 * mm, y_text * mm, "Hardware:")
            c.setFont("Helvetica", 8)
            for line in boms[num]:
                y_text -= 3.6
                c.drawString(22 * mm, y_text * mm, "- " + line)
        scale_bars(c)
        # simple shelf packing, left to right, top to bottom
        x, y_top, row_h = 22.0, y_text - 7, 0.0
        for p in group:
            x0, y0, x1, y1 = p.bbox()
            w, h = x1 - x0, y1 - y0
            if x + w > pw - 10:
                x, y_top, row_h = 22.0, y_top - row_h - 12, 0.0
            if y_top - h < 24:
                raise SystemExit(f"{p.name} does not fit on the page")
            draw_part_pdf(c, p, x - x0, y_top - h - y0)
            c.setFont("Helvetica", 7)
            label = p.name + (f"  x{p.qty}" if p.qty > 1 else "")
            c.drawString(x * mm, (y_top - h - 5) * mm, label)
            x += w + 12
            row_h = max(row_h, h + 6)
        c.showPage()
    c.save()


def main():
    groups = build_parts()
    for sub in ("dxf", "svg", "pdf"):
        os.makedirs(os.path.join(OUT, sub), exist_ok=True)
    for g in groups:
        for p in g:
            write_dxf(p, os.path.join(OUT, "dxf", p.name + ".dxf"))
            write_svg(p, os.path.join(OUT, "svg", p.name + ".svg"))
            x0, y0, x1, y1 = p.bbox()
            print(f"{p.name:24s} {x1 - x0:7.2f} x {y1 - y0:6.2f} mm  qty {p.qty}")
    write_pdf(groups, os.path.join(OUT, "pdf", "paper-check-A4.pdf"))
    print("wrote dxf/, svg/, pdf/paper-check-A4.pdf")


if __name__ == "__main__":
    main()
