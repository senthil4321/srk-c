# Set 3: ten more printable mechanisms (21–30)

This file continues sets 1 (01–10) and 2 (11–20). Everything in
[00-printing-and-modeling-rules.md](00-printing-and-modeling-rules.md)
applies: millimeters, user parameters first, one component per printed
part, joints instead of overlaps, and the clearance parameters
(`clr_rot`, `clr_slide`, `clr_press`, `clr_pip`, `clr_axial`,
`backlash`, `wall_min`). Add those clearance parameters to every design
before the mechanism's own parameters.

Pins, slot-shaped links and layers work as in set 1, mechanism 04
(four-bar linkage): link holes `pin_d + 2 * clr_rot`, pins press-fit
(`pin_d`) into one part with a 2 mm cap, moving links on separate layers
`link_t + clr_axial` apart.

| # | Mechanism | Motion it creates | Difficulty |
|---|-----------|-------------------|------------|
| 21 | [Elliptical trammel](#21--elliptical-trammel) | Rotation → ellipse | Easy |
| 22 | [Scissor lift](#22--scissor-lift) | Small push → large lift | Easy |
| 23 | [Watt's linkage](#23--watts-linkage) | Rocking → near-straight line | Easy |
| 24 | [Sarrus linkage](#24--sarrus-linkage) | Exact straight up-and-down (3D) | Medium |
| 25 | [Peaucellier–Lipkin linkage](#25--peaucellierlipkin-linkage) | Rotation → exact straight line | Medium |
| 26 | [Timing belt drive (GT2)](#26--timing-belt-drive-gt2) | Rotation at a distance, 3:1 | Medium |
| 27 | [Barrel cam](#27--barrel-cam) | Rotation → back-and-forth along the axis | Medium |
| 28 | [Herringbone gears](#28--herringbone-gears) | Quiet, self-centering gear pair | Medium |
| 29 | [Straight bevel gears](#29--straight-bevel-gears) | Rotation turned 90°, 2:1 | Hard |
| 30 | [Strain wave (harmonic) drive](#30--strain-wave-harmonic-drive) | 24:1 in one stage with a flexible gear | Hard |

To use with Claude Desktop + Fusion 360, use the README prompt and name
the section, for example: *"Read `00-printing-and-modeling-rules.md` and
section 25 of `21-30-mechanisms-set-3.md`, then build it…"*

---

## 21 – Elliptical trammel

### What it does

Two sliders run in crossed grooves; a bar joins them. A point on the bar
traces an ellipse (the "Trammel of Archimedes"). Turning the bar end
like a crank makes a nice desk toy, or holds a pen to draw ellipses.

### Geometry

Slider A runs on the X groove, slider B on the Y groove, distance A–B =
`c`. Point P on the bar beyond B, with A–P = `a` and B–P = `b` (so `c`
= `a − b`). P traces an ellipse with semi-axes `b` along X and `a` along
Y: P = (−b cos θ, a sin θ).

### User parameters

| Name | Expression | Unit | Notes |
|---|---|---|---|
| `a` | 60 | mm | Ellipse Y semi-axis |
| `b` | 30 | mm | Ellipse X semi-axis |
| `c` | a - b | mm | Slider pin spacing = 30 |
| `groove_w` | 10 | mm | Groove width at the top |
| `groove_d` | 6 | mm | Groove depth |
| `block_l` | 14 | mm | Slider block length |
| `bar_w` | 10 | mm | |
| `bar_t` | 5 | mm | |
| `pin_d` | 5 | mm | |
| `base_t` | 10 | mm | |

### Parts

`Base` (grounded), `Slider_A`, `Slider_B`, `Bar`, `Pin` ×2, `Handle`.

### Modeling steps

1. **Base.** Square `2 * c + block_l + 30` per side, thickness `base_t`.
   Cut two crossed **dovetail grooves** through the center, along X and
   along Y: top width `groove_w`, depth `groove_d`, walls at 45° (wider
   at the bottom). 45° walls print without supports and hold the
   sliders in.
2. **Sliders.** Dovetail blocks matching the groove, made smaller by
   `clr_slide` on every side, length `block_l`, top flush with the base
   surface. Vertical pin hole `pin_d` (press fit) in the middle.
   Chamfer both ends 1 mm so they pass the crossing smoothly.
3. **Bar.** Slot-shaped link from A, through B, to P: holes at 0 and
   `c` (`pin_d + 2 * clr_rot`), and at `a` a pen hole (10 mm) or a
   handle peg. Sits `clr_axial` above the base.
4. **Pins.** Press into sliders, through the bar, cap on top.

The sliders never collide at the crossing: both would have to be within
`block_l / 2 + groove_w / 2` = 12 mm of the center at once, which needs
`c` < 17 mm.

### Joints

Slider: Slider_A ↔ Base (X), Slider_B ↔ Base (Y). Revolute: Bar ↔ each
slider.

### Verify

- Drag P around: it follows an ellipse 60 mm wide (X) and 120 mm tall
  (Y). Measure P at θ = 0° and 90°.
- Sliders stay inside their grooves: travel ±`c` = ±30 mm from center;
  groove length ≥ `2 * c + block_l` + 4 mm.

### Printing

Base groove side up, no supports (45° dovetails). Sliders on their wide
face. Bar flat. Pins standing.

---

## 22 – Scissor lift

### What it does

Crossed pairs of links (lazy tongs) stacked in stages. Pushing the two
bottom ends together raises the top a long way. Used in lift tables,
extending arms and toys.

### User parameters

| Name | Expression | Unit | Notes |
|---|---|---|---|
| `L` | 80 | mm | Link length, hole to hole |
| `stages` | 3 | – | |
| `link_w` | 10 | mm | |
| `link_t` | 4 | mm | |
| `pin_d` | 5 | mm | |
| `theta_min` | 10 | deg | Collapsed angle from horizontal |
| `theta_max` | 60 | deg | Extended angle |
| `screw_d` | 8 | mm | Optional lead screw drive |

Height = `stages` · `L` · sin θ: about 42 mm collapsed, 208 mm
extended.

### Parts

`Base` (grounded, with one fixed pivot and one slider track), `Link` ×
(4 · `stages`) (two parallel scissor sides), `Top_Plate`, `Pin` × many,
`Cross_Rod` ×2 (tie both sides together), optional `Lead_Screw` (see set
2, mechanism 11).

### Modeling steps

1. Sketch the skeleton in side view (XZ): `stages` X-shapes stacked,
   each made of two lines of length `L` crossing at their midpoints, at
   angle θ = 30° (start pose). Make θ a driving dimension.
2. **Links:** slot shape, three holes each: both ends and the center.
   Model one link, then place copies on the skeleton (or use a
   **Rectangular Pattern** per stage). Alternate layers so crossing links
   don't rub: the two links of each X are `link_t + clr_axial` apart in Y.
3. **Second side:** mirror all links to the other side, 60 mm away in Y.
4. **Cross_Rods:** two rods (`pin_d`) across the bottom pivots and two
   across the top pivots, linking both sides.
5. **Base:** plate with a fixed pivot block at one bottom end and a
   **slot track** (`pin_d + 2 * clr_slide` wide, length `L` · (cos
   `theta_min` − cos `theta_max`) + 6) for the other bottom end.
6. **Top_Plate:** same pattern: one fixed pivot, one slot.

### Joints

Revolute at every link pin. Slider (or Pin-Slot) for the sliding bottom
and top ends. Fusion solves the stack from the skeleton; if it's slow,
build and check one stage first.

### Verify

- Drag the sliding end: the top rises and falls straight up, from ~42 to
  ~208 mm.
- At `theta_min` no two links collide (check the link ends near the base).

### Printing

All links flat, no supports (print a full plate at once). Pins standing,
100 % infill. Use M5 screws for a stronger lift.

---

## 23 – Watt's linkage

### What it does

Two equal rockers pointing in opposite directions are joined by a short
coupler. The coupler's midpoint moves in an almost straight line. James
Watt used it to guide steam-engine pistons; cars use it to locate rear
axles.

### Geometry

Pivots O1 = (0, `c / 2`) and O2 = (`2 * r`, −`c / 2`). In the middle
pose both rockers are horizontal (O1 → A along +X, O2 → B along −X) and
the coupler A–B is vertical, its midpoint M at (`r`, 0). M moves along
X = `r`.

Simulated for r = 40, c = 30: M stays straight within **0.03 mm** over
±10 mm and within **1.1 mm** over ±20 mm of travel.

### User parameters

| Name | Expression | Unit |
|---|---|---|
| `r` | 40 | mm |
| `c` | 30 | mm |
| `link_w` | 10 | mm |
| `link_t` | 4 | mm |
| `pin_d` | 5 | mm |

### Parts

`Base` (grounded), `Rocker_1`, `Rocker_2`, `Coupler` (with a pen hole or
a pointer at M), `Slider_Demo` (optional block in a straight slot at M,
to prove the line), `Pin` ×4.

### Modeling steps

1. Sketch the skeleton in the middle pose with the points above.
2. Rockers on layer 1, coupler on layer 2. Coupler gets a third hole at
   M: a 10 mm pen hole or a 3 mm pointer tip.
3. Base: plate with pins at O1 and O2, and a printed ruler line (0.6 mm
   deep groove) along X = `r` for ±25 mm to show the straight path.
4. Optional: a straight slot along X = `r` (width `pin_d + 2 *
   clr_slide`) with a pin at M riding in it; it must move freely over
   ±20 mm.

### Joints

Revolute at O1, O2, A, B.

### Verify

- Drag M along the groove: deviation ≤ 1.1 mm over ±20 mm (measure M
  at −20, 0, +20).
- Beyond ±30 mm the path curves into a figure-8; set joint limits on
  the rockers at ±30° to stay in the straight zone.

### Printing

All flat, no supports. Pins standing.

---

## 24 – Sarrus linkage

### What it does

A top plate is joined to a bottom plate by two hinged "legs" set at 90°
to each other. Each leg alone would let the top swing, but together
they allow only **straight up-and-down** motion — the first exact
straight-line mechanism (1853), and it's 3D. Printed here in place with
print-in-place hinges (set 1, mechanism 03).

### User parameters

| Name | Expression | Unit | Notes |
|---|---|---|---|
| `plate_s` | 50 | mm | Square top and bottom plates |
| `plate_t` | 4 | mm | |
| `leg_l` | 30 | mm | Each leg segment, hinge to hinge |
| `leg_w` | 30 | mm | Width of each leg (along its hinges) |
| `leg_t` | 4 | mm | |
| `knuckle_d` | 8 | mm | Hinge knuckle outer diameter |
| `clr_pip` | 0.4 | mm | |

### Parts

One print (all in place): `Bottom_Plate`, `Top_Plate`, `Leg_A_Lower`,
`Leg_A_Upper`, `Leg_B_Lower`, `Leg_B_Upper` — six components joined by
**six** print-in-place hinges.

### Modeling steps

Print pose: **folded flat is not possible**, so model it in a
**partly-raised pose** that prints without supports — each leg forms a
"<" shape with 45° segments.

1. Bottom plate `plate_s` square, `plate_t` thick, on the bed.
2. **Leg A** on the front edge (hinge axes along X): lower segment hinged
   to the bottom plate's front edge, going up and outward at 45°; upper
   segment hinged to the lower one, going up and inward at 45°, hinged
   to the top plate's front edge. Hinge style: knuckles and cones as in
   mechanism 03, with `clr_pip`.
3. **Leg B** on the right edge (hinge axes along Y), the same.
4. The top plate is then at height ≈ 2 · `leg_l` · sin 45° + knuckles
   (≈ 46 mm) — it's a bridge over the bottom plate. To print it without
   supports, make the top plate a **frame** (ring 8 mm wide) whose inner
   edges are supported by the legs, and bridge the remaining spans (≤ 35
   mm bridges print fine), or add a single breakaway support column in
   the center.
5. Leave `clr_pip` between every pair of parts that aren't hinged
   together.

### Joints

Revolute at all six hinges. Fusion will only let the top move straight
up and down (both legs together) — that's the check.

### Verify

- Drag the top plate: it moves only along Z, without tilting or
  twisting. Measure that it stays parallel to the bottom.
- Collapse it until a leg segment is 10° from horizontal and raise it to
  80°: no collisions.

### Printing

One piece, as modeled, 0.16 mm layers, no supports except an optional
breakaway column. Flex every hinge gently after printing.

---

## 25 – Peaucellier–Lipkin linkage

### What it does

The first planar linkage that draws an **exact** straight line from
rotation (1864). A rhombus and two long arms "invert" a circle into a
line: when point A moves on a circle through the fixed pivot O, point C
moves on a perfect straight line.

### Geometry

- Fixed pivot **O** at the origin. Two long arms of length `R` from O to
  **B** and **D**.
- Rhombus **A–B–C–D**, all four sides `s`.
- Crank: fixed pivot **Q** at (`k`, 0), crank Q–A of length `k` (so A's
  circle passes through O).
- Then OA · OC = `R`² − `s`², and C runs on the line X = (`R`² − `s`²)
  / (2 · `k`).

With R = 70, s = 30, k = 25: the line is at **X = 80 mm**. Checked at
crank angles giving OA direction 0°, 15°, 30°, 36°: C = (80, 0), (80,
21.4), (80, 46.2), (80, 58.1) — all exactly on the line.

Range: OA must stay between `R − s` (40) and `2k` (50), so the OA
direction can swing ±36.9°; use joint limits of ±30° (C moves ±46 mm).

### User parameters

| Name | Expression | Unit |
|---|---|---|
| `R` | 70 | mm |
| `s` | 30 | mm |
| `k` | 25 | mm |
| `link_w` | 10 | mm |
| `link_t` | 4 | mm |
| `pin_d` | 5 | mm |
| `line_x` | (R^2 - s^2) / (2 * k) | mm |

### Parts

`Base` (grounded, pivots O and Q), `Arm_OB`, `Arm_OD` (length `R`),
`Rhombus_AB`, `Rhombus_AD`, `Rhombus_CB`, `Rhombus_CD` (length `s`),
`Crank` (length `k`), `Pen_Holder` at C, `Pin` ×7.

### Modeling steps

1. Sketch the skeleton in the pose where OA is along +X (OA = 50, OC =
   80): A = (50, 0), C = (80, 0), B and D are the two intersections of
   circle(O, `R`) and circle(A, `s`).
2. **Layers.** Links that share a joint must be on different layers,
   and links on the same layer must never cross. This assignment does
   both (layer 0 lowest, each `link_t + clr_axial` apart):
   - Layer 0: `Crank`.
   - Layer 1: `Arm_OB`, `Rhombus_CD`.
   - Layer 2: `Rhombus_AB`, `Arm_OD`.
   - Layer 3: `Rhombus_AD`, `Rhombus_CB`.
   The two links on each layer stay on opposite sides of the O–C line,
   so they never meet. Pins at shared joints are long enough for the
   layers they pass through.
3. Base: plate with pins at O and Q, and a straight slot along X = 80
   (`pin_d + 2 * clr_slide` wide, ±50 mm) that guides a pin at C — it
   should never bind, which proves the line is straight.

### Joints

Revolute at O (two arms), Q (crank), A (crank + two rhombus links), B,
C, D. Limit the crank to keep OA direction within ±30°.

### Verify

- Drag the crank: C moves along X = 80.0 mm. Measure C's X at three
  positions; it must not change.
- No links collide in the ±30° range.

### Printing

All links flat, no supports. Pins standing, 100 % infill.

---

## 26 – Timing belt drive (GT2)

### What it does

A toothed belt connects two toothed pulleys, transmitting rotation over
a distance without slip. 20 → 60 teeth gives **3:1**. Used in 3D
printers and CNC machines. Uses a standard 6 mm GT2 closed belt (200 mm,
100 teeth).

### User parameters

| Name | Expression | Unit | Notes |
|---|---|---|---|
| `belt_pitch` | 2 | mm | GT2 |
| `belt_len` | 200 | mm | Standard closed loop |
| `z_small` | 20 | – | |
| `z_big` | 60 | – | |
| `pd_small` | z_small * belt_pitch / PI | mm | 12.73 pitch diameter |
| `pd_big` | z_big * belt_pitch / PI | mm | 38.20 |
| `od_small` | pd_small - 0.508 | mm | Pulley outside diameter |
| `od_big` | pd_big - 0.508 | mm | |
| `center_nom` | 58.6 | mm | Solved for a 200 mm belt |
| `tension_adj` | 3 | mm | ± slot for tensioning |
| `belt_w` | 6 | mm | |
| `flange_h` | 1.5 | mm | Flange height above tooth tips |
| `shaft_d` | 5 | mm | |

Center distance from the belt length formula L = 2C + π(D + d)/2 +
(D − d)² / (4C), solved for L = 200: **C = 58.6 mm**.

### Parts

`Plate` (grounded), `Pulley_20T`, `Pulley_60T`, `Tensioner_Block`,
`Shaft` ×2, `Belt` (bought, modeled as a reference body only).

### Modeling steps

1. **Pulley tooth profile (approximation of GT2).** Circle `od`; cut
   `z` grooves around it: each groove is a circle of radius 0.555 mm
   centered on a circle of diameter `od - 0.38`, plus 0.15 mm fillets at
   the groove edges. Circular-pattern `z` grooves. Extrude `belt_w + 1`.
2. Add flanges each side: diameter `od + 2 * flange_h`, 1 mm thick,
   with a 45° chamfer on the inner side (prints without supports on the
   top flange). Hub with bore `shaft_d + 2 * clr_rot` and an M3 grub
   screw.
3. **Plate.** Small pulley shaft hole fixed; big pulley shaft in a
   **slot** along X, length `2 * tension_adj`, centered at `center_nom`.
   A tensioner screw (M3) pushes the big pulley's block along the slot.
4. **Belt reference:** sketch the belt path (two tangent lines + arcs on
   the pitch circles) and extrude a 1.4 mm thick, `belt_w` wide body,
   for visual checking only (don't print it).

### Joints

Revolute: each pulley ↔ plate. Slider: Tensioner_Block ↔ plate.
Motion Link: small 360° ↔ big 120°.

### Verify

- Measure the belt reference path length at nominal center: 200 mm.
- Pulley tooth count and pitch diameters match the table.

### Printing

Pulleys flat, 0.12 mm layers (small teeth), 4 walls, 100 % infill for
the 20T. Plate flat. If the belt skips teeth, increase the groove
radius to 0.6 mm. Bought metal 20T pulleys can replace the printed one.

---

## 27 – Barrel cam

### What it does

A cylinder with a wavy groove cut around it. A follower pin in the
groove moves back and forth **along the cylinder's axis** as it turns:
one stroke out and back per turn. Used in sewing machines (bobbin
winders), fishing reels and automatic machines.

### User parameters

| Name | Expression | Unit | Notes |
|---|---|---|---|
| `drum_d` | 40 | mm | |
| `drum_l` | 45 | mm | |
| `stroke` | 20 | mm | |
| `groove_w` | follower_d + 2 * clr_slide | mm | |
| `groove_depth` | 3 | mm | |
| `follower_d` | 5 | mm | Follower pin diameter |
| `shaft_d` | 8 | mm | |

Groove path (unwrapped): along the circumference s from 0 to π · `drum_d`
(125.7 mm), axial position z = `stroke` / 2 · (1 − cos(2π · s /
(π · `drum_d`))). Max slope = (stroke/2) / (drum_d/2) = 0.5, so the max
pressure angle is **26.6°** (under 30°: no jamming).

### Parts

`Frame` (grounded), `Drum` (with shaft and knob), `Follower` (slider rod
with pin), `Shaft`.

### Modeling steps

1. **Drum.** Cylinder `drum_d` × `drum_l`, axis along X, with shaft bore
   or integral 8 mm journals.
2. **Groove.** On a plane tangent to the drum, sketch the groove
   centerline as a fit-point spline in the unwrapped coordinates (s
   horizontal 0 → 125.66 mm, z vertical, offset so the stroke is
   centered on the drum length), 17 points every 7.85 mm:
   z = 0, 0.76, 2.93, 6.17, 10, 13.83, 17.07, 19.24, 20, 19.24, 17.07,
   13.83, 10, 6.17, 2.93, 0.76, 0. Offset the spline ±`groove_w / 2`
   and close the ends with arcs.
3. **Create → Emboss**, select the groove profile and the drum's
   cylindrical face, **Wrap**, **Deboss**, depth `groove_depth`. (The
   two ends of the unwrapped path meet seamlessly because the curve ends
   at the same height with zero slope.)
4. **Follower.** A square rod sliding along X parallel to the drum,
   above it, in guides on the frame (`clr_slide`), with a pin
   `follower_d` pointing down into the groove; pin end chamfered 0.5 mm
   and 0.3 mm short of the groove bottom.
5. **Frame.** Two end plates holding the drum journals (teardrop holes),
   and two guides for the follower rod with diamond (45°) roofs.

### Joints

Revolute: Drum ↔ Frame. Slider: Follower ↔ Frame. Fusion has no cam
joint; use **Contact Sets** between the follower pin and the groove to
watch it move, or check by hand at 0°, 90°, 180°.

### Verify

- Follower moves 20 mm per half turn and returns in the other half.
- Groove width is constant (no pinching where the slope is steepest).

### Printing

| Part | Orientation | Supports | Notes |
|---|---|---|---|
| Drum | Standing (axis vertical) | No | Groove walls are horizontal-ish ledges: keep `groove_depth` ≤ 3 mm so the 90° overhang bridges cleanly; 0.12 mm layers |
| Follower | On its side | No | |
| Frame | Base down | No | |

---

## 28 – Herringbone gears

### What it does

Two helical gears joined in a "V" so their sideways forces cancel. They
run more smoothly and quietly than spur gears, and the V keeps them
centered on each other — great for printing because each gear holds the
other in line.

### User parameters

| Name | Expression | Unit | Notes |
|---|---|---|---|
| `m` | 2 | mm | Transverse module (as in the gear sketch) |
| `z_pinion` | 15 | – | |
| `z_gear` | 30 | – | |
| `face_w` | 12 | mm | Total width (two 6 mm halves) |
| `helix` | 30 | deg | Helix angle |
| `twist_pinion` | (face_w / 2) * tan(helix) / (m * z_pinion / 2) | rad | 0.231 rad = 13.2° |
| `twist_gear` | (face_w / 2) * tan(helix) / (m * z_gear / 2) | rad | 0.115 rad = 6.6° |
| `center_dist` | m * (z_pinion + z_gear) / 2 + backlash | mm | 45.2 |
| `pin_d` | 6 | mm | |

### Parts

`Base`, `Pinion`, `Gear`, `Pin` ×2 (same layout as set 1, mechanism 01).

### Modeling steps

1. Make the 2D gear profile sketch (involute method from the rules
   file, or project the top face of a SpurGear-script body into a new
   sketch and delete the body).
2. **Pinion:** three sketch planes at Z = 0, `face_w / 2`, `face_w`.
   Profile at Z = 0 at 0°; at Z = `face_w / 2` rotated +`twist_pinion`;
   at Z = `face_w` back at 0°. **Loft** 0 → mid (new body), **Loft** mid
   → top (join). That makes the V.
3. **Gear:** same with `twist_gear`, but rotated **the other way**
   (−`twist_gear` at mid): meshing helical gears have opposite hands.
4. Center holes `pin_d + 2 * clr_rot`. Place at `center_dist`; rotate
   the gear by half a tooth if the teeth clash.

### Joints

Revolute: each gear ↔ base. Motion Link: pinion 360° ↔ gear −180°.

### Verify

- Section view at Z = 0, `face_w / 4`, `face_w / 2`: teeth mesh with a
  small gap at every section. If they clash at mid, the twists are the
  same hand — reverse one.
- Interference: none.

### Printing

Flat, no supports. 0.15 mm layers, 4 walls. The helix overhang is 30°
from vertical — fine. Herringbones can't slide in or out axially once
meshed: assemble both on their pins at the same time.

---

## 29 – Straight bevel gears

### What it does

Cone-shaped gears that mesh at 90°. A 15-tooth pinion drives a 30-tooth
gear at **2:1** and turns the motion through a right angle. Used in hand
drills, differentials and right-angle drives.

### Geometry

| Quantity | Pinion | Gear |
|---|---|---|
| Teeth | 15 | 30 |
| Pitch diameter (large end) | 30 mm | 60 mm |
| Pitch cone angle δ | atan(15/30) = **26.57°** | **63.43°** |
| Cone distance (apex → pitch circle) | 33.54 mm | 33.54 mm |
| Face width F | 10 mm (≤ cone distance / 3) | 10 mm |
| Small-end scale | (33.54 − 10) / 33.54 = **0.702** | 0.702 |

Both cones share the **apex** at the origin. Pinion axis along Z: its
large-end pitch circle (r 15) is at Z = 15 / tan 26.57° = 30. Gear axis
along X: its large-end pitch circle (r 30) is at X = 30 / tan 63.43° =
15. The two pitch circles touch at (15, 0, 30).

### User parameters

| Name | Expression | Unit |
|---|---|---|
| `m` | 2 | mm |
| `z_pinion` | 15 | – |
| `z_gear` | 30 | – |
| `delta_p` | atan(z_pinion / z_gear) | deg |
| `delta_g` | 90 deg - delta_p | deg |
| `cone_dist` | (m * z_pinion / 2) / sin(delta_p) | mm |
| `F` | 10 | mm |
| `k_small` | (cone_dist - F) / cone_dist | – |
| `pin_d` | 6 | mm |

### Parts

`Frame` (grounded, holds both axles at 90°), `Pinion`, `Gear`,
`Axle` ×2, `Knob`.

### Modeling steps (loft approximation)

1. **Pinion.** On a plane perpendicular to Z at Z = `m * z_pinion / 2 /
   tan(delta_p)` (= 30), draw the 15-tooth gear profile (module `m`).
   On a plane `F * cos(delta_p)` (8.94 mm) closer to the apex, draw the
   same profile **scaled by `k_small`** about the axis (Sketch → Scale).
   **Loft** between them. Then add a hub on the back (large end) side
   with the axle hole.
2. **Gear.** Same method on planes perpendicular to X: large profile
   (30 teeth) at X = 15, small profile scaled `k_small` at X = 15 − `F *
   cos(delta_g)` (15 − 4.47 = 10.53). Hub on the back.
3. Rotate the gear about its axis until a pinion tooth sits in a gear
   gap at the contact point (15, 0, 30). Then move the gear `backlash`
   (0.2 mm) away from the apex along its axis for clearance.
4. **Frame.** An L-shaped bracket with two bearing bosses: one for the
   pinion axle (along Z), one for the gear axle (along X), both through
   the apex lines. Thrust faces behind each gear hub (`clr_axial`) to
   hold the gears in mesh.

This loft method gives a slightly simplified tooth (true bevel teeth are
defined on the back cone), which is fine for printed gears.

### Joints

Revolute: Pinion ↔ Frame (Z), Gear ↔ Frame (X). Motion Link: pinion
360° ↔ gear 180°.

### Verify

- Measure: both large-end pitch circles touch at (15, 0, 30); apex lines
  meet at the origin.
- Section view through the contact point: tooth gap visible, no overlap.

### Printing

Each gear standing on its **large-end back face**, teeth pointing up —
the cone narrows upward, so no supports. 0.12–0.15 mm layers. Frame on
its largest flat face.

---

## 30 – Strain wave (harmonic) drive

### What it does

A thin flexible gear (flexspline) with 48 teeth sits inside a rigid ring
(circular spline) with 50 teeth. An oval wave generator pushes the
flexspline out so it meshes only at two opposite points. Each input
turn shifts the flexspline by 2 teeth: ratio = 48 / (50 − 48) = **24:1**,
output opposite to input. Used in robot arms and satellite mechanisms.
**Experimental for printing:** expect to tune it.

### User parameters

| Name | Expression | Unit | Notes |
|---|---|---|---|
| `m` | 1.25 | mm | Module |
| `z_flex` | 48 | – | Flexspline teeth (external) |
| `z_circ` | 50 | – | Circular spline teeth (internal) |
| `r_flex` | m * z_flex / 2 | mm | 30 mm pitch radius |
| `r_circ` | m * z_circ / 2 | mm | 31.25 mm |
| `w0` | r_circ - r_flex | mm | 1.25 mm radial deflection |
| `flex_wall` | 1.2 | mm | Wall under the teeth |
| `flex_cup_h` | 30 | mm | Cup length (longer = easier flexing) |
| `flex_tooth_w` | 8 | mm | Toothed band width at the cup's open end |
| `r_flex_in` | r_flex - 1.25 * m - flex_wall | mm | 27.24 mm inner radius |
| `wg_a` | r_flex_in + w0 - clr_rot | mm | Wave generator major semi-axis |
| `wg_b` | r_flex_in - w0 - clr_rot | mm | Minor semi-axis |

### Parts

`Circular_Spline` (grounded ring + housing), `Flexspline` (cup with
teeth at the open end, output flange at the closed end), `Wave_Generator`
(oval cam on the input shaft), `Lid`, `Input_Shaft`.

### Modeling steps

1. **Circular_Spline.** Internal gear with `z_circ` teeth, module `m`
   (method from set 1, mechanism 10: cut an enlarged external gear out
   of a cylinder). Width `flex_tooth_w`. Housing around it with bolt
   holes.
2. **Flexspline.** A cup: outer radius at the tooth band = gear profile
   with `z_flex` teeth (module `m`), width `flex_tooth_w`; behind it a
   thin cylindrical wall (radius `r_flex_in + flex_wall`) of length
   `flex_cup_h`; closed end is a 4 mm flange with output bolt holes and
   an output shaft. Inner radius `r_flex_in`.
3. **Wave_Generator.** An ellipse with semi-axes `wg_a` and `wg_b`,
   extruded `flex_tooth_w`, on the input shaft. Optional: use a thin
   printed ring (1.2 mm) between the cam and the flexspline as a sliding
   "bearing", greased.
4. In Fusion, the flexspline is a rigid body, so the model shows its
   **free (round) shape**. Check fit with two sketches instead (below).

### Joints

Revolute: Wave_Generator ↔ Circular_Spline, Flexspline ↔ Circular_Spline
(same axis). Motion Link: input 360° ↔ output −15° (= −360° / 24).

### Verify

- Sketch check: draw the flexspline pitch circle deformed into an
  ellipse with semi-axes `r_flex + w0` and ≈ `r_flex - w0`. At the major
  axis it must touch the circular spline's pitch circle (`r_circ`).
- Perimeter of the wave generator ellipse ≈ perimeter of the flexspline
  inner circle (within 1 %), so the cup isn't stretched.

### Printing

| Part | Orientation | Supports | Notes |
|---|---|---|---|
| Flexspline | Closed end down, teeth at the top | No | **TPU 95A** (best) or PETG with 2 walls; 0.12 mm layers |
| Circular_Spline | Flat | No | 0.12 mm layers, 4 walls |
| Wave_Generator | Flat | No | Sand the oval smooth; grease |

If the teeth skip, increase `w0` slightly (deeper engagement) or use a
TPU flexspline; if it's too stiff to turn, lengthen `flex_cup_h`.
