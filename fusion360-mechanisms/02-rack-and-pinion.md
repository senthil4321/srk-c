# 02 – Rack and pinion

## What it does

A round gear (pinion) meshes with a straight toothed bar (rack). Turning
the pinion slides the rack in a straight line. One pinion turn moves the
rack `π · m · z_pinion` (≈ 75 mm here). Used in steering, CNC axes, and
camera sliders.

## User parameters

| Name | Expression | Unit | Notes |
|---|---|---|---|
| `m` | 1.5 | mm | Module |
| `z_pinion` | 16 | – | |
| `pa` | 20 | deg | Pressure angle |
| `face_w` | 8 | mm | Gear and rack face width |
| `rack_teeth` | 30 | – | |
| `rack_len` | rack_teeth * PI * m | mm | ≈ 141.4 mm |
| `rack_body_h` | 8 | mm | Rack height below the pitch line |
| `pin_d` | 6 | mm | |
| `clr_rot` | 0.25 | mm | |
| `clr_slide` | 0.3 | mm | |
| `backlash` | 0.2 | mm | |
| `pitch_r` | m * z_pinion / 2 | mm | 12 mm |
| `guide_wall` | 4 | mm | |
| `base_t` | 4 | mm | |

## Parts

`Frame` (grounded), `Pinion`, `Rack`, `Pin`, `Knob` (optional).

## Modeling steps

1. **Rack** (sketch on XZ, extrude `face_w` in Y).
   - The pitch line is horizontal at Z = `base_t + clr_slide +
     rack_body_h`.
   - Draw one tooth as a trapezoid: height `m` above the pitch line
     (addendum), `1.25 * m` below (dedendum); flanks tilted `pa` (20°)
     from vertical; width at the pitch line `PI * m / 2`.
   - Draw the body rectangle under the teeth: length `rack_len`, from
     Z = `base_t + clr_slide` up to the tooth roots.
   - Extrude the body and one tooth, then **Rectangular Pattern** the
     tooth: `rack_teeth` copies, spacing `PI * m`.
   - Chamfer both ends of the rack 1 mm so it enters the guide easily.
2. **Frame.**
   - Base plate: length `rack_len + 40`, width `face_w + 2 * guide_wall
     + 2 * clr_slide`, height `base_t`.
   - Two guide walls along the long sides, height `rack_body_h + 2`,
     with a gap `face_w + 2 * clr_slide` between them for the rack.
   - Over the walls, two 3 mm wide lips that overhang the rack body by
     1.5 mm (stop it lifting). Model the lips with a 45° chamfer
     underneath so they print without supports.
   - A vertical bracket plate on one side of the guide, 4 mm thick,
     with a horizontal hole `pin_d`
     (teardrop) whose center is at height `pitch line + pitch_r +
     backlash`, at the middle of the rack length.
3. **Pinion.** SpurGear script: module `m`, `z_pinion`, 20°, thickness
   `face_w`. Hole `pin_d + 2 * clr_rot`. Place its axis on the bracket
   hole (axis along Y), over the rack.
4. **Pin.** Diameter `pin_d`, length through bracket + pinion +
   `clr_axial` + 3 mm, with a 2 mm cap.
5. **Knob** (optional). Cylinder 25 mm diameter, 8 mm, knurled with a
   pattern of 24 small 1 mm half-cylinders, joined to the pinion's
   outer face.

## Assembly (joints)

| Joint | Between |
|---|---|
| Rigid | Pin ↔ Frame (bracket hole) |
| Revolute | Pinion ↔ Frame, axis = pin axis |
| Slider | Rack ↔ Frame, along the rack length |
| Motion Link | Pinion revolute ↔ Rack slider: 360° = `PI * m * z_pinion` mm |

Set slider limits so the rack can't leave the pinion: ± (`rack_len` / 2
− 15 mm).

## Verify

- Interference check: none.
- Drag the pinion one full turn: rack moves ≈ 75.4 mm.
- Measure: pinion pitch circle touches (is tangent to) the rack pitch
  line, plus `backlash`.

## Printing

| Part | Orientation | Supports | Notes |
|---|---|---|---|
| Frame | Base down | No (lips are chamfered) | Teardrop hole |
| Rack | On its side (teeth sideways) | No | Gives cleaner tooth flanks than teeth-up |
| Pinion | Flat | No | 0.15 mm layers |
| Pin | Standing | No | 100 % infill |
