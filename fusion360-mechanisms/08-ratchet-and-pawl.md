# 08 – Ratchet and pawl

## What it does

A toothed wheel turns freely one way, but a springy finger (pawl) drops
into the teeth and blocks the other way. It clicks as it turns. Used in
wrenches, winches, zip ties and clocks. Here the spring is printed as
part of the pawl (a flexure), so no metal spring is needed.

## User parameters

| Name | Expression | Unit | Notes |
|---|---|---|---|
| `teeth` | 12 | – | |
| `r_out` | 22 | mm | Tooth tip radius |
| `tooth_h` | 4 | mm | Tooth depth |
| `r_root` | r_out - tooth_h | mm | 18 mm |
| `wheel_t` | 6 | mm | |
| `pin_d` | 6 | mm | |
| `pawl_t` | 6 | mm | Pawl height (same as the wheel) |
| `flex_t` | 1.2 | mm | Spring arm thickness |
| `flex_l` | 30 | mm | Spring arm length |
| `clr_rot` | 0.25 | mm | |
| `clr_axial` | 0.4 | mm | |
| `base_t` | 5 | mm | |

## Parts

`Base` (grounded, the pawl is part of it), `Ratchet_Wheel`, `Axle_Pin`,
`Knob` (joined to the wheel).

## Modeling steps

Wheel axis at the origin, along Z. The wheel turns freely
counter-clockwise (seen from above) and locks clockwise. To reverse
this, mirror the tooth sketch.

1. **Ratchet_Wheel.**
   - Sketch one tooth on XY (sawtooth): start at the root circle at
     angle 0° (point A at radius `r_root`), go **straight out radially**
     to the tip at radius `r_out` (point B, also at 0°) — this is the
     locking face; then a **straight line** from B back down to the root
     circle at angle 360° / `teeth` = 30° (point C) — the sloping face.
     Close along the root circle arc C → A.
   - Draw a circle at `r_root` for the body. Extrude the body and the
     tooth `wheel_t`; **Circular Pattern** the tooth `teeth` times.
   - Hole `pin_d + 2 * clr_rot`. Hub boss on the bottom (`pin_d + 6`,
     `clr_axial` high).
   - Small 0.3 mm fillet on tooth tips (prints cleaner).
2. **Knob.** On top of the wheel, a 30 mm-diameter, 8 mm cylinder with a
   wing (grip bar 30 × 6 × 8 mm), joined to the wheel (same body).
3. **Base with the flexure pawl.** One body:
   - Plate, ~80 × 60 mm, `base_t` thick, wheel center at 20 mm from one
     edge. Axle hole `pin_d` (press fit).
   - **Pawl anchor:** a block 10 × 10 × (`clr_axial` + `pawl_t`) on the
     plate, placed so the flexure runs roughly tangent to the wheel.
   - **Flexure arm:** a thin wall `flex_t` thick, `flex_l` long, height
     `pawl_t`, from the anchor towards the wheel. Its bottom must clear
     the plate by `clr_axial` everywhere except at the anchor (so model
     it at the wheel's height, with the anchor block supporting one end).
   - **Pawl tip:** at the free end, a wedge whose flat face matches the
     wheel's radial locking face. Position it so the tip sits 1 mm deep
     into a tooth gap at rest (`r_out - 1` from the center), touching the
     locking face of one tooth.
   - The arm floats `clr_axial` above the plate. Its first layer is a
     short bridge out from the anchor block; to avoid it, add a
     sacrificial 0.2 mm-thick tab under the arm tip connected to the
     plate, and cut it with a knife after printing.
   - Add a slight preload: rotate the flexure 2° towards the wheel so it
     presses into the teeth.
4. **Axle_Pin.** `pin_d`, cap 2 mm.

## Assembly (joints)

| Joint | Between | Notes |
|---|---|---|
| Revolute | Ratchet_Wheel ↔ Base | axis Z |
| Rigid | Axle_Pin ↔ Base | |

Fusion can't simulate the flexure bending; check it with the steps
below. (Optional: model the pawl as a separate rigid part on its own
revolute joint, plus Contact Sets, to watch it click.)

## Verify

- Measure the pawl tip depth: it overlaps the tooth tip circle by ≈ 1 mm.
- The flexure's deflection to clear a tooth tip is about 1–1.5 mm. For a
  1.2 mm thick, 30 mm long PLA/PETG arm this is safe (strain well under
  2 %). Don't make the arm shorter than 25 mm or thicker than 1.6 mm.
- The locking face of every tooth is radial (0° angle): pawl force goes
  straight through the axle, so the wheel can't push the pawl out.
- Interference at rest: only the planned pawl preload (accepted).

## Printing

| Part | Orientation | Supports | Notes |
|---|---|---|---|
| Base (with pawl) | Flat | No | **PETG preferred** for the flexure; 100 % infill not needed — the arm is all walls |
| Ratchet_Wheel + Knob | Wheel face down | No | |
| Axle_Pin | Standing | No | 100 % infill |

Print the flexure with walls aligned along its length (the default for a
thin wall). If the click is too weak, increase `flex_t` by 0.2 mm.
