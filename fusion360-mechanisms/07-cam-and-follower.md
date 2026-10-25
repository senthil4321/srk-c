# 07 – Cam and follower

## What it does

A shaped disc (cam) rotates; a follower resting on its edge rises and
falls following the cam's shape. This one lifts 10 mm smoothly over 120°,
holds for 60°, falls over 120°, and rests for 60°. Used in engine
valves, automata and toys.

## User parameters

| Name | Expression | Unit | Notes |
|---|---|---|---|
| `r_base` | 20 | mm | Base circle radius (lowest point) |
| `lift` | 10 | mm | Total rise |
| `cam_t` | 6 | mm | Cam thickness |
| `follower_w` | 8 | mm | Follower stem width (square) |
| `follower_l` | 50 | mm | Stem length |
| `foot_r` | 4 | mm | Round tip radius on the follower |
| `pin_d` | 6 | mm | |
| `clr_rot` | 0.25 | mm | |
| `clr_slide` | 0.3 | mm | |
| `clr_axial` | 0.4 | mm | |
| `base_t` | 5 | mm | |

## Cam profile

Radius r(θ) (θ in degrees from the start of the rise). Uses a cosine
(simple harmonic) rise, which is smooth:

| θ range | r(θ) |
|---|---|
| 0° – 120° (rise) | `r_base + lift/2 · (1 − cos(180° · θ / 120°))` |
| 120° – 180° (dwell high) | `r_base + lift` |
| 180° – 300° (fall) | `r_base + lift/2 · (1 + cos(180° · (θ − 180°) / 120°))` |
| 300° – 360° (dwell low) | `r_base` |

Pre-computed points every 15° (x = r · cos θ, y = r · sin θ):

| θ | r | θ | r |
|---|---|---|---|
| 0 | 20.00 | 180 | 30.00 |
| 15 | 20.38 | 195 | 29.62 |
| 30 | 21.46 | 210 | 28.54 |
| 45 | 23.09 | 225 | 26.91 |
| 60 | 25.00 | 240 | 25.00 |
| 75 | 26.91 | 255 | 23.09 |
| 90 | 28.54 | 270 | 21.46 |
| 105 | 29.62 | 285 | 20.38 |
| 120 | 30.00 | 300 | 20.00 |
| 135 | 30.00 | 315 | 20.00 |
| 150 | 30.00 | 330 | 20.00 |
| 165 | 30.00 | 345 | 20.00 |

When scripting through the Fusion API, compute points every 5° from the
formulas for a smoother curve.

## Parts

`Base` (grounded), `Cam`, `Follower`, `Axle_Pin`, `Handle` (optional).

## Modeling steps

Cam axis at the origin, along Z. The follower moves along +Y, above the
cam.

1. **Cam.**
   - Sketch `sk_cam` on XY: a **fit-point spline** through the points
     from 0° to 120°, an **arc** (radius `r_base + lift`) from 120° to
     180°, a spline through 180° to 300°, an **arc** (radius `r_base`)
     from 300° to 360°. Make the spline ends tangent to the arcs.
   - Extrude `cam_t`. Center hole `pin_d + 2 * clr_rot`.
   - Add a hub boss on the bottom (`pin_d + 6`, height `clr_axial`).
   - Optional handle peg near the edge, on top.
2. **Follower.**
   - A square stem `follower_w × follower_w × follower_l`, standing
     along Y, lying flat in the XY plane at the cam's height.
   - At its bottom end (towards the cam), a round tip: fillet the end
     to radius `foot_r` (seen from above it's a half circle).
   - Place it so the tip touches the cam at the 0° point when the cam is
     rotated so that 0° points along +Y.
   - A small T-head on the top end (wider than the guide) to stop it
     falling through.
3. **Base.**
   - Plate under the cam, plus a strip extending in +Y for the guide.
   - Axle hole `pin_d` (press fit) at the origin.
   - **Follower guide:** a block on the plate at Y from `r_base + lift +
     6` to `r_base + lift + 22`, with a square tunnel `follower_w + 2 *
     clr_slide` along Y at the follower's height. Diamond (45° peak) roof
     for supportless printing.
   - The follower rests on the cam by gravity if the model is stood on
     its side, **or** add a rubber-band hook on the follower head and
     another on the base.
4. **Axle_Pin.** `pin_d`, cap 2 mm, length through base + cam + 1 mm.

## Assembly (joints)

| Joint | Between | Notes |
|---|---|---|
| Revolute | Cam ↔ Base | axis Z |
| Slider | Follower ↔ Base | along Y |
| Rigid | Axle_Pin ↔ Base | |
| Motion Link | optional | Fusion has no cam joint; use **Contact Sets** (Assemble → Enable Contact Sets) between the follower tip and cam to see the follower ride the cam while dragging |

## Verify

- Measure the cam: radius 20 mm at 0°, 30 mm at 120°–180°.
- With contact sets enabled, rotate the cam: follower rises 10 mm.
- **Pressure angle:** the slope of the rise should not be steep; with
  these values the max pressure angle is ≈ 15°, well under 30°. If you
  increase `lift` or shorten the rise angle, check the follower doesn't
  jam.

## Printing

| Part | Orientation | Supports | Notes |
|---|---|---|---|
| Base | Flat | No | |
| Cam | Flat | No | 0.15 mm layers for a smooth edge |
| Follower | Flat (on its side) | No | Square stem prints flat cleanly |
| Axle_Pin | Standing | No | 100 % infill |

Lightly sand the cam edge and the follower tip for smoother motion.
