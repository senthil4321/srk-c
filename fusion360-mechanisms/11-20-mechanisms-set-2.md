# Set 2: ten more printable mechanisms (11–20)

This file continues mechanisms 01–10. Everything in
[00-printing-and-modeling-rules.md](00-printing-and-modeling-rules.md)
applies here too: millimeters, user parameters first, one component per
printed part, joints instead of overlaps, and the clearance parameters
(`clr_rot`, `clr_slide`, `clr_press`, `clr_pip`, `clr_axial`,
`backlash`, `wall_min`). Add those clearance parameters to every design
before the mechanism's own parameters.

Each mechanism has the same sections as set 1: what it does, user
parameters, parts, modeling steps, joints, verify, and printing.

| # | Mechanism | Motion it creates | Difficulty |
|---|-----------|-------------------|------------|
| 11 | [Lead screw and nut](#11--lead-screw-and-nut) | Rotation → slow, strong straight line | Easy |
| 12 | [Oldham coupling](#12--oldham-coupling) | Joins two offset parallel shafts | Easy |
| 13 | [Pantograph](#13--pantograph) | Copies a drawing at 2× scale | Easy |
| 14 | [Compliant bistable switch](#14--compliant-bistable-switch) | Snaps between two stable positions | Easy |
| 15 | [Toggle clamp](#15--toggle-clamp) | Locks over center with high force | Medium |
| 16 | [Universal (Cardan) joint](#16--universal-cardan-joint) | Joins two shafts at an angle | Medium |
| 17 | [Quick-return mechanism](#17--quick-return-mechanism) | Slow working stroke, fast return | Medium |
| 18 | [Chebyshev lambda linkage](#18--chebyshev-lambda-linkage) | Rotation → near-straight line | Medium |
| 19 | [Worm drive](#19--worm-drive) | High ratio, 90° turn, self-locking | Hard |
| 20 | [Cycloidal drive](#20--cycloidal-drive) | High ratio, compact, low backlash | Hard |

To use with Claude Desktop + Fusion 360, use the README prompt and name
the section, for example: *"Read `00-printing-and-modeling-rules.md` and
section 17 of `11-20-mechanisms-set-2.md`, then build it…"*

---

## 11 – Lead screw and nut

### What it does

Turning a threaded rod moves a nut along it in a straight line. Each turn
moves the nut one thread pitch (2 mm here), so it's slow, precise and
strong, and the nut can't push the screw backwards. Used in 3D printer Z
axes, vises and jacks.

### User parameters

| Name | Expression | Unit | Notes |
|---|---|---|---|
| `screw_d` | 16 | mm | Nominal thread diameter |
| `pitch` | 2 | mm | Travel per turn |
| `screw_l` | 100 | mm | Threaded length |
| `clr_thread` | 0.2 | mm | Removed from screw thread faces |
| `nut_w` | 30 | mm | Nut carriage width |
| `nut_h` | 16 | mm | Nut length along the screw (8 threads) |
| `rail_d` | 8 | mm | Anti-rotation guide rod |
| `frame_t` | 6 | mm | |
| `knob_d` | 35 | mm | |

### Parts

`Frame` (grounded: base + two end plates + guide rod), `Screw` (with
knob), `Nut_Carriage`.

### Modeling steps

The screw axis runs along X at height Z = 25.

1. **Screw.** Cylinder `screw_d` × `screw_l`. **Create → Thread**, type
   *ISO Metric profile*, size 16, designation **M16x2**, **Modeled**
   checked, full length. Then **Modify → Offset Face** on all thread
   faces by −`clr_thread`. Add plain journal ends 10 mm long, diameter
   10 mm, at both ends, and a knob (`knob_d`, 10 mm thick, 12 grip
   notches) on one end.
2. **Nut_Carriage.** Block `nut_w` × `nut_w` × `nut_h` around the screw.
   Hole `screw_d`, then **Thread**, internal, same M16x2, Modeled. A
   second hole `rail_d + 2 * clr_slide` 20 mm below the screw axis, for
   the guide rod.
3. **Frame.** Base plate `screw_l + 2 * frame_t + 20` × 40 × `frame_t`.
   Two end plates at the screw ends, each with a journal hole `10 + 2 *
   clr_rot` (teardrop). Guide rod `rail_d` between the end plates, one
   body with the frame, at the guide-hole position.
4. Snap-ring groove: a 1 mm deep, 1.2 mm wide groove on each journal just
   outside the end plates, and a printed C-clip for each (13 mm OD,
   1.2 mm thick, with a 7 mm opening).

### Joints

| Joint | Between |
|---|---|
| Revolute | Screw ↔ Frame (axis X) |
| Slider | Nut_Carriage ↔ Frame (along X) |
| Motion Link | Screw 360° ↔ Nut 2 mm |

### Verify

- Section view through the nut: a gap of about `clr_thread` on the
  thread flanks, no overlap.
- One screw turn moves the nut 2 mm.

### Printing

| Part | Orientation | Supports | Notes |
|---|---|---|---|
| Screw | **Standing up** (knob down) | No | 60° threads print fine vertically; 0.16 mm layers; brim |
| Nut_Carriage | Thread axis vertical | No | |
| Frame | Base down | No | Teardrop journal holes |

If the nut binds, raise `clr_thread` to 0.3 mm and reprint only the
screw.

---

## 12 – Oldham coupling

### What it does

Connects two parallel shafts that are slightly offset sideways. A middle
disc with two crossed tongues slides in slots in both hubs, so rotation
passes through at exactly 1:1 even with the offset. Used in motor-to-
leadscrew couplings.

### User parameters

| Name | Expression | Unit | Notes |
|---|---|---|---|
| `hub_d` | 30 | mm | |
| `hub_l` | 15 | mm | Hub length |
| `shaft_d` | 8 | mm | Shaft bore |
| `slot_w` | 8 | mm | |
| `slot_depth` | 4 | mm | |
| `disc_t` | 10 | mm | Middle disc thickness, tongues included |
| `offset` | 2 | mm | Max shaft offset to test |
| `base_t` | 5 | mm | |

### Parts

`Hub_A`, `Hub_B`, `Middle_Disc`, `Stand` (grounded test frame with two
bearings, offset by `offset`), `Shaft` ×2.

### Modeling steps

1. **Hub_A.** Cylinder `hub_d` × `hub_l`, axis along X. Bore `shaft_d +
   2 * clr_rot` with a D-flat (0.5 mm) to grip a D-shaft, or an M3 grub
   screw hole. On the inner face, a slot across the full diameter,
   width `slot_w + 2 * clr_slide`, depth `slot_depth`, **along Y**.
2. **Hub_B.** Same, slot **along Z** (90° to Hub_A's).
3. **Middle_Disc.** Disc `hub_d`, thickness `disc_t - 2 * slot_depth`.
   On one face a tongue `slot_w` wide, `slot_depth - clr_axial` high,
   along Y; on the other face a tongue along Z. Tongue ends chamfered
   0.5 mm.
4. **Stand.** Base plate with two uprights. Shaft holes `shaft_d + 2 *
   clr_rot` (teardrop): one at Z = 30, the other at Z = 30 + `offset`.
5. **Shafts.** `shaft_d` × 50 mm with a matching D-flat; a crank handle
   on the input shaft.

### Joints

| Joint | Between |
|---|---|
| Revolute | Hub_A ↔ Stand (input axis) |
| Revolute | Hub_B ↔ Stand (output axis, offset) |
| Planar (or two Sliders) | Middle_Disc ↔ Hub_A (along Hub_A's slot) and ↔ Hub_B (along Hub_B's slot) |

Fusion may struggle to solve two slider joints in a loop; if so, check
positions by hand at 0°, 45° and 90°.

### Verify

- With the offset, the middle disc slides `offset` back and forth in
  each slot per half turn; slot length must allow ≥ `offset` + 1 mm.
- Input and output turn the same angle.

### Printing

| Part | Orientation | Supports | Notes |
|---|---|---|---|
| Hubs | Slot face up | No | |
| Middle_Disc | One tongue down | No | Tongue prints as a solid bar on the bed |
| Stand | Base down | No | |
| Shafts | Flat on the D-flat | No | Or use 8 mm steel rod |

---

## 13 – Pantograph

### What it does

Four bars joined as a parallelogram. Trace a drawing with the tracer
point and a pen draws it **twice as large**. Used in copy machines,
engraving and signal-drawing.

### Geometry

Fixed pivot **O**. Long bar 1 runs O → A → B (O–A = A–B = `L`). Long
bar 2 runs B → C → Q (B–C = C–Q = `L`). Short bar 3 runs A → P (length
`L`), short bar 4 runs C → P (length `L`). A–B–C–P is a parallelogram,
so P is always exactly halfway between O and Q: **tracer at P, pen at
Q, scale 2×**.

### User parameters

| Name | Expression | Unit | Notes |
|---|---|---|---|
| `L` | 80 | mm | Half-length of the long bars |
| `bar_w` | 12 | mm | |
| `bar_t` | 5 | mm | |
| `pin_d` | 5 | mm | |
| `pen_d` | 10 | mm | Pen holder bore (fit your pen) |

### Parts

`Anchor` (grounded, clamps to a table edge or has a rubber pad), `Bar_1`
(2L), `Bar_2` (2L), `Bar_3` (L), `Bar_4` (L), `Tracer` (stylus), `Pen_Holder`,
`Pin` ×5.

### Modeling steps

1. Sketch the skeleton on XY in a starting pose: O at origin, B at (`L`,
   `L * 1.4`) (any comfortable angle), C and Q so that B–C–Q is straight
   and B–Q = `2 * L`, P = (O + Q) / 2. Use **construction lines** and
   constrain the parallelogram with equal lengths.
2. **Bars:** slot-shaped links (`bar_w` wide, `bar_t` thick) built on the
   skeleton lines; holes `pin_d + 2 * clr_rot` at each joint. Put bars 1
   and 3 on layer 1, bars 2 and 4 on layer 2 (`bar_t + clr_axial` higher)
   so they cross freely.
3. **Pins:** press-fit into the lower bar, cap on top (see set 1, 04).
4. **Tracer:** a 20 mm cone point under P, joined to bar 3/4 joint.
5. **Pen_Holder:** a tube `pen_d + 0.4` bore at Q with an M3 thumbscrew
   hole, joined to bar 2. Pen tip and tracer tip at the same height.
6. **Anchor:** block with the O pivot and a C-clamp jaw or a 3 mm pocket
   for a rubber foot.

### Joints

Revolute joints at O, A, B, C, P (5). Ground the Anchor.

### Verify

- Drag P around: Q always stays on the line O–P at twice the distance.
  Measure O–P and O–Q in three poses.
- Bars never collide (two layers).

### Printing

All bars flat, no supports, 3 walls, 30 % infill. Pins standing. Tracer
cone standing on its base.

---

## 14 – Compliant bistable switch

### What it does

A one-piece printed part: a slider held by two curved thin beams. Push
it and it **snaps** to a second stable position; push back and it snaps
back. No hinges, no springs. Used in compliant mechanisms, switches and
latches.

### User parameters

| Name | Expression | Unit | Notes |
|---|---|---|---|
| `beam_l` | 40 | mm | Beam span |
| `beam_t` | 0.8 | mm | Beam thickness (two 0.4 mm lines) |
| `beam_h` | 3 | mm | Arch height (the beam's curve) |
| `beam_gap` | 6 | mm | Distance between the two parallel beams |
| `part_h` | 6 | mm | Extrusion height of the whole part |
| `shuttle_w` | 10 | mm | |
| `frame_wall` | 6 | mm | |

`beam_h / beam_t` = 3.75; it must stay above ~2.5 for clean
bistability. Don't thin the beam below 0.8 mm.

### Parts

One component, `Switch` (frame + beams + shuttle, one body).

### Modeling steps

1. Sketch on XY. Beam centerline shape (cosine arch), for x from 0 to
   `beam_l`: **y = beam_h / 2 · (1 − cos(2π · x / beam_l))**. Draw it as
   a fit-point spline through 11 points (every `beam_l / 10`):
   y = 0, 0.29, 1.03, 1.97, 2.71, 3.00, 2.71, 1.97, 1.03, 0.29, 0.
2. Offset the spline ±`beam_t / 2` to get the beam outline.
3. Copy the beam `beam_gap` in +Y (second, parallel beam).
4. **Shuttle:** a block `shuttle_w` wide joining both beams at their
   middles (x = `beam_l / 2`), extending 15 mm above the top beam as a
   push button.
5. **Frame:** a rectangle around everything, wall `frame_wall`, joined
   to both ends of both beams. Leave ≥ `beam_h * 2 + 2` mm of free space
   above and below the shuttle so it can snap through.
6. Extrude all `part_h`. Fillet the beam-to-frame and beam-to-shuttle
   joints 0.5 mm (vertical edges only) to reduce stress.
7. Add mechanical stops on the frame at ± `beam_h` from the shuttle's
   rest position so it can't overshoot.

### Joints

None (one body). Optionally do a **Simulation → Static Stress** with a
displacement on the shuttle to see the force curve.

### Verify

- Beam thickness measures `beam_t` everywhere (no thin spots from the
  spline).
- Free space for the shuttle to travel `2 * beam_h` = 6 mm.

### Printing

Flat, no supports. **PETG or PLA**, 0.2 mm layers, 2+ walls so the beams
are solid walls. The beams print as vertical walls along their length,
which is the strong direction.

---

## 15 – Toggle clamp

### What it does

A handle drives a short link past a straight line ("over center"). Near
that point the force multiplies hugely and the clamp locks itself shut
until you pull the handle back. Used in jigs, latches and clamps.

### Geometry (side view, sketch on XZ)

| Point | Position | Meaning |
|---|---|---|
| A | (0, 0) | Clamp arm pivot on the base |
| B | (25, 0) | Handle pivot on the clamp arm |
| D | (25, −30) | Link pivot on the base |
| C | (26, −12) | Handle–link joint, **1 mm past** the line B–D |

So B–C = 12.04 mm (on the handle) and C–D = 18.03 mm (the link). When
clamped, C is just past the line B–D, and a stop on the handle keeps it
there.

### User parameters

| Name | Expression | Unit | Notes |
|---|---|---|---|
| `arm_l` | 70 | mm | Clamp arm, A to the pad, toward −X |
| `L_bc` | 12.04 | mm | |
| `L_cd` | 18.03 | mm | |
| `handle_l` | 90 | mm | |
| `part_t` | 6 | mm | Thickness of each plate |
| `pin_d` | 5 | mm | |
| `pad_d` | 16 | mm | Clamp pad diameter |

### Parts

`Base` (two side plates + floor, grounded), `Clamp_Arm`, `Handle` (two
plates joined by a grip bar), `Link`, `Pad`, `Pin` ×4.

### Modeling steps

1. Sketch the skeleton points A, B, C, D on XZ with the coordinates
   above.
2. **Base:** U-channel: floor 80 × 30 × 5 with two side plates (`part_t`)
   holding pins A and D; inner gap = `part_t + 2 * clr_axial` for the arm.
   Two screw holes in the floor for mounting.
3. **Clamp_Arm:** a bar from the pad end (−`arm_l`, 0) through A to B,
   between the side plates. Pad hole at the end (M6 for a screw-in rubber
   pad, or a printed `Pad` with TPU).
4. **Link:** short bar C–D, between the side plates beside the arm.
5. **Handle:** a **forked handle**: two plates that straddle the arm at
   B and the link at C, joined by a grip bar `handle_l` from B. Add a **stop**: a tab on the
   handle that touches the arm when C reaches 1 mm past line B–D.
6. Holes: `pin_d + 2 * clr_rot` in moving parts, `pin_d` press fit in the
   part holding each pin.

### Joints

Revolute at A (arm–base), B (handle–arm), C (handle–link), D
(link–base). Set the handle revolute's limit at the stop.

### Verify

- Drag the handle: the arm swings up to open and comes down to clamp.
- At the clamped position, measure the angle B–C–D: ~172° (C is 1 mm
  past the line B–D). Pushing the pad up should push the handle against its stop,
  not open it.
- Interference: none, except intended contact at the stop.

### Printing

All plates flat, no supports, 4 walls, 40 % infill (these parts carry
force). Use M5 screws + nylock nuts as pins for real clamping. PETG
preferred.

---

## 16 – Universal (Cardan) joint

### What it does

Two forked yokes linked by a cross. Transmits rotation between two
shafts meeting at an angle (up to ~35°). Used in car drive shafts and
steering columns.

### User parameters

| Name | Expression | Unit | Notes |
|---|---|---|---|
| `yoke_d` | 24 | mm | Yoke outside diameter |
| `yoke_gap` | 13 | mm | Space between fork arms |
| `arm_t` | 4 | mm | Fork arm thickness |
| `cross_w` | 8 | mm | Cross body (square) |
| `cross_pin_d` | 5 | mm | Cross journal diameter |
| `cross_span` | yoke_gap + 2 * arm_t - 1 | mm | Tip to tip |
| `shaft_d` | 8 | mm | Shaft bore |
| `hub_l` | 20 | mm | |

### Parts

`Yoke_A`, `Yoke_B`, `Cross`, `Stand` (optional, two bearings at 30°).

### Modeling steps

1. **Yoke_A** (axis along X). Cylinder hub `yoke_d` × `hub_l` with bore
   `shaft_d + 2 * clr_rot` and an M3 grub screw. Two fork arms extend
   20 mm in +X, `arm_t` thick, `yoke_gap` apart (inner faces at Y =
   ±`yoke_gap / 2`). Round the arm ends (full radius). Holes through the
   arms along Y: `cross_pin_d + 2 * clr_rot`, at X = hub end + 12.
   Chamfer the inner hole edges 0.8 mm (lead-in for snapping the cross in).
2. **Yoke_B.** Copy Yoke_A, rotate 180° about Z and 90° about X, so its
   fork faces Yoke_A's and its holes are along Z.
3. **Cross.** Cube `cross_w` with four journals `cross_pin_d`, two along
   Y, two along Z, tip to tip `cross_span`. Chamfer journal tips 0.8 mm.
   Center at the meeting point of the two hole axes.
4. Check the gap between each yoke's fork and the cross body: ≥
   `clr_axial`.

### Joints

| Joint | Between |
|---|---|
| Revolute | Cross ↔ Yoke_A (axis Y) |
| Revolute | Cross ↔ Yoke_B (axis Z) |
| Revolute | each yoke ↔ Stand (optional) |

### Verify

- Bend the joint to 30° and rotate: no collision between fork arms and
  the other yoke (check every 45°).
- Interference: none.

### Printing

| Part | Orientation | Supports | Notes |
|---|---|---|---|
| Yokes | Hub face down, arms up | No | Holes horizontal → teardrop |
| Cross | One journal down (standing) | No | 100 % infill; 2 journals print round, 2 slightly oval; sand lightly |

Assemble by flexing a fork arm open and snapping the journal in. PETG
flexes more safely than PLA.

---

## 17 – Quick-return mechanism

### What it does

A crank pin slides in a slotted lever (crank-shaper / Whitworth type).
The lever swings forward slowly (240° of crank turn) and returns fast
(120°): ratio 2:1. Used in shaping machines and sewing machines.

### User parameters

| Name | Expression | Unit | Notes |
|---|---|---|---|
| `r_crank` | 15 | mm | Crank pin radius |
| `d_pivot` | 30 | mm | Crank center to lever pivot (lever pivot below) |
| `L_lever` | 75 | mm | Lever pivot to top end |
| `pin_d` | 6 | mm | |
| `lever_w` | 14 | mm | |
| `part_t` | 5 | mm | |

Time ratio: the return stroke uses crank angle 2 · acos(`r_crank` /
`d_pivot`) = 120°, so forward/return = 240° / 120° = **2:1**. The lever
swings ± asin(`r_crank` / `d_pivot`) = ±30°.

### Parts

`Base` (grounded), `Crank_Disc` (with crank pin), `Lever` (slotted),
`Ram` (slides horizontally, driven by the lever top), `Pin` ×3.

### Modeling steps

Lever pivot at the origin; crank center at (0, `d_pivot`) — vertical
layout, sketch on XY, base lying flat.

1. **Crank_Disc** centered at (0, `d_pivot`): disc `2 * r_crank + 14`,
   crank pin `pin_d` standing at radius `r_crank`.
2. **Lever:** a bar from the origin to (0, `L_lever`), width `lever_w`,
   above the crank disc layer. Central slot along its length, width
   `pin_d + 2 * clr_slide`, from Y = `d_pivot - r_crank - pin_d / 2 - 1`
   to `d_pivot + r_crank + pin_d / 2 + 1`. Pivot hole at the origin. A
   second short slot (`pin_d + 2 * clr_slide`, 10 mm long, along the
   lever) at the top end for the ram pin.
3. **Ram:** a bar sliding along X at Y = `L_lever` in guides on the
   base, with a pin that rides in the lever's top slot. Travel ≈ 2 ·
   `L_lever` · sin 30° = 75 mm, so make the ram ≥ 120 mm long and the
   guides allow 85 mm travel.
4. **Base:** plate with the lever pivot pin, crank pivot, two ram guides
   (diamond-roof tunnels, `clr_slide`) and end stops.

### Joints

Revolute: crank ↔ base, lever ↔ base. Pin-Slot: crank pin ↔ lever slot,
ram pin ↔ lever top slot. Slider: ram ↔ base.

### Verify

- Turn the crank: lever swings ±30°, ram travels ≈ 75 mm.
- Time ratio: the ram moves one way during 240° of crank, back during
  120° (check positions at crank angles where the crank is
  perpendicular to the lever).
- Crank pin stays inside the slot with ≥ 1 mm at both ends.

### Printing

All parts flat, no supports. Pins standing, 100 % infill. Light graphite
in the slots.

---

## 18 – Chebyshev lambda linkage

### What it does

A four-bar linkage whose extended coupler point traces an almost
perfectly straight line for about two-thirds of every crank turn, then
lifts and returns. Basis of walking machines (Chebyshev's "plantigrade
machine").

### Geometry

Ratios 1 : 2 : 2.5 : 2.5 : 5 with `u` = 12 mm per unit:

| Link | Ratio | Length |
|---|---|---|
| Crank (O → A) | 1 | 12 mm |
| Ground (O → O4) | 2 | 24 mm |
| Rocker (O4 → B) | 2.5 | 30 mm |
| Coupler (A → B) | 2.5 | 30 mm |
| Coupler extended (A → P) | 5 | 60 mm (P is 30 mm past B) |

Simulated: P runs on a line at 4 · `u` = 48 mm from the ground line,
straight within 0.6 mm over ≈ 56 mm, during ≈ 230° of crank rotation.

### User parameters

| Name | Expression | Unit |
|---|---|---|
| `u` | 12 | mm |
| `L_crank` | u | mm |
| `L_ground` | 2 * u | mm |
| `L_rocker` | 2.5 * u | mm |
| `L_coupler` | 2.5 * u | mm |
| `L_foot` | 5 * u | mm |
| `link_w` | 10 | mm |
| `link_t` | 4 | mm |
| `pin_d` | 5 | mm |

### Parts

`Base`, `Crank` (with handle), `Rocker`, `Coupler` (length `L_foot`,
with a pen or foot at P), `Pin` ×4.

### Modeling steps

O at origin, O4 at (`L_ground`, 0). The straight line is on the side
where B is (choose B above the ground line; the line is at Y = +48).

1. Links as slot shapes (see set 1, 04), holes `pin_d + 2 * clr_rot`.
   The coupler has three holes: A (0), B (`L_coupler`), and P at
   `L_foot` with a pen holder (10 mm bore) or a rounded foot.
2. Layers: crank and rocker on layer 1, coupler on layer 2.
3. Base: plate with O and O4 pins; cut a window under the path of P (or
   let P hang past the base edge) so the pen can reach the paper.

### Joints

Revolute at O, O4, A, B.

### Verify

- Drag the crank 360°: no lockup (crank shortest; 12 + 30 ≤ 24 + 30 ✔).
- Trace P with **Motion Study → trace path** (or sample positions): flat
  segment ≈ 56 mm long.

### Printing

All links flat, no supports. Pins standing.

---

## 19 – Worm drive

### What it does

A screw-like worm turns a gear (worm wheel) at 90°. One worm turn
advances the wheel one tooth, so a 20-tooth wheel gives **20:1**. It's
self-locking: the wheel can't turn the worm. Used in tuning pegs, lifts
and gate openers.

### User parameters

| Name | Expression | Unit | Notes |
|---|---|---|---|
| `m` | 2 | mm | Axial module |
| `z_wheel` | 20 | – | |
| `starts` | 1 | – | Single-start worm |
| `d_worm` | 16 | mm | Worm pitch diameter |
| `worm_l` | 40 | mm | Threaded length |
| `face_w` | 8 | mm | Wheel width |
| `pitch_ax` | PI * m | mm | Worm axial pitch = 6.283 |
| `lead_angle` | atan(m * starts / d_worm) | deg | 7.1° |
| `center_dist` | (d_worm + m * z_wheel) / 2 + backlash | mm | 28.2 |
| `twist` | face_w * tan(lead_angle) / (m * z_wheel / 2) | rad | 0.05 rad = 2.86° |

### Parts

`Frame` (grounded), `Worm` (with knob), `Worm_Wheel`, `Pin` ×1.

### Modeling steps

Worm axis along X at Z = 0 (the frame raises it); wheel axis along Y,
at X = 0, Z = `center_dist`, so the wheel sits **above** the worm.

1. **Worm.** Core cylinder diameter `d_worm - 2.5 * m` (11 mm). Thread:
   **Create → Coil**, type *Revolution and Pitch*, diameter `d_worm`,
   pitch `pitch_ax`, revolutions `worm_l / pitch_ax`, section
   **Triangular (External)**, section size `2.25 * m` (4.5 mm),
   operation **Join**. Truncate the sharp crests by cutting a cylinder
   at diameter `d_worm + 2 * m` (20 mm). Journals 8 mm at both ends,
   knob on one.
2. **Worm_Wheel.** Make a spur gear sketch (SpurGear script or involute,
   module `m`, `z_wheel` teeth). Copy the sketch profile to a plane
   `face_w` above, rotated about the wheel axis by `twist`.
   **Create → Loft** between the two profiles: a helical gear with the
   lead angle. The twist direction must match the worm (right-hand worm
   → right-hand wheel); if they clash, reverse the twist. Hole for pin.
3. **Frame.** Two bearing blocks for the worm journals (teardrop holes),
   one tower for the wheel pin at `center_dist` above the worm axis.

### Joints

Revolute Worm ↔ Frame (X), revolute Wheel ↔ Frame (Y), Motion Link:
worm 360° ↔ wheel 360° / `z_wheel` (18°).

### Verify

- Section view: worm thread sits in the wheel's tooth gaps at the
  contact point with a visible gap.
- Interference: small edge contact at the wheel's outer corners is
  normal for a non-throated wheel; if more than ~0.2 mm, raise
  `backlash` to 0.3.

### Printing

| Part | Orientation | Supports | Notes |
|---|---|---|---|
| Worm | Standing (knob down) | No | 0.12 mm layers, brim |
| Worm_Wheel | Flat | No | 0.15 mm layers |
| Frame | Base down | No | |

Grease the worm. Expect lower efficiency (~40 %): that's what makes it
self-locking.

---

## 20 – Cycloidal drive

### What it does

An eccentric shaft wobbles a lobed disc inside a ring of pins. The disc
has one lobe fewer than there are pins, so each input turn rotates the
disc backwards by one lobe: ratio = (N − 1) : 1 = **9:1** here. Output
pins in oversized holes take off the disc's slow rotation. Compact,
strong and low-backlash; popular in robot joints.

### User parameters

| Name | Expression | Unit | Notes |
|---|---|---|---|
| `N` | 10 | – | Number of ring pins |
| `R` | 30 | mm | Ring pin circle radius |
| `Rr` | 3 | mm | Ring pin radius (6 mm pins) |
| `e` | 1.5 | mm | Eccentricity; keep `e` < `R / N` |
| `disc_t` | 8 | mm | |
| `ecc_d` | 18 | mm | Eccentric cam diameter |
| `out_n` | 6 | – | Output pins |
| `out_r` | 15 | mm | Output pin circle radius |
| `out_pin_d` | 6 | mm | |
| `out_hole_d` | out_pin_d + 2 * e + 2 * clr_rot | mm | 9.5 mm |
| `clr_disc` | 0.15 | mm | Disc profile offset (inward) |

### Disc profile

For t from 0 to 2π (sketch about the **disc's own center**):

- ψ = atan2( sin((1 − N) t), R / (e · N) − cos((1 − N) t) )
- x = R cos t − Rr cos(t + ψ) − e cos(N t)
- y = −R sin t + Rr sin(t + ψ) + e sin(N t)

This gives a disc with N − 1 = 9 lobes, radius 25.5 → 28.5 mm.
Generate ~360 points and draw a closed fit-point spline (through the
Fusion API this is easiest as a script; by hand, use 90 points with a
spreadsheet and **Insert → Insert CSV points** if available, or the
*ImportSplineCSV* sample script). Then **Offset** the closed curve
inward by `clr_disc`.

Placement: when the eccentric points along +X, the disc center is at
(`e`, 0) from the ring center, and the ring pins sit at angles 0°, 36°,
72° … around the ring center. In that pose the profile touches all
pins with zero overlap (checked numerically: the closest approach of
the curve to every pin center is exactly `Rr`).

### Parts

`Housing` (grounded, ring pins printed in), `Input_Shaft` (with
eccentric), `Disc`, `Output_Plate` (with output pins), `Lid`.

### Modeling steps

1. **Housing.** Cylinder radius `R + Rr + 6`, floor 3 mm. Ring pins:
   `N` cylinders radius `Rr` at radius `R`, height `disc_t + 2 *
   clr_axial`, joined to the housing (circular pattern). Center bearing
   hole for the input shaft.
2. **Input_Shaft.** Shaft 8 mm with the eccentric cam (`ecc_d`, length
   `disc_t`), offset `e` from the shaft axis. Hex or knob on the input
   end.
3. **Disc.** The profile above, extruded `disc_t`. Center hole `ecc_d +
   2 * clr_rot` on the disc center. `out_n` holes `out_hole_d` on radius
   `out_r` around the disc center.
4. **Output_Plate.** Disc above the cycloid disc, with `out_n` pins
   `out_pin_d` at radius `out_r` around the **housing** center, pointing
   down into the disc's holes. Output shaft on top.
5. **Lid** holds the output plate, screws to the housing.

### Joints

Revolute: input ↔ housing, output ↔ housing (same axis). Disc: revolute
on the eccentric. Motion Links: input 360° ↔ output −40° (= 360° / 9,
opposite direction). Use Contact Sets between disc and ring pins for a
true motion check.

### Verify

- Disc lobe count = 9; pins = 10.
- At input angles 0°, 90°, 180°: disc touches pins with ≈ `clr_disc`
  gap, no overlap.
- Each output pin sits in its hole touching one side: hole is exactly
  `2 * e` larger than the pin (plus clearance).
- 9 input turns = 1 output turn, opposite direction.

### Printing

| Part | Orientation | Supports | Notes |
|---|---|---|---|
| Housing | Floor down, pins up | No | Pins print round, 100 % infill on pins |
| Disc | Flat | No | 0.12–0.16 mm layers |
| Input_Shaft | Eccentric face down | No | |
| Output_Plate | Pins up | No | |
| Lid | Flat | No | |

Grease the pins. For a balanced drive, add a second disc rotated 180° on
a second eccentric (offset −`e`).
