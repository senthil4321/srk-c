# 09 – Geneva drive (4-slot)

## What it does

A continuously turning drive wheel with one pin steps a slotted wheel
exactly 90° per turn, then locks it still while the drive keeps turning.
Used in film projectors, indexing tables, and watches.

## User parameters

| Name | Expression | Unit | Notes |
|---|---|---|---|
| `n_slots` | 4 | – | Steps per turn of the Geneva wheel |
| `a` | 25 | mm | Drive pin radius (drive center → pin center) |
| `C` | a / sin(180 deg / n_slots) | mm | Center distance = 35.36 mm |
| `R` | sqrt(C^2 - a^2) | mm | Geneva wheel radius = 25 mm |
| `pin_d` | 6 | mm | Drive pin diameter |
| `clr_slide` | 0.3 | mm | |
| `clr_rot` | 0.25 | mm | |
| `clr_axial` | 0.4 | mm | |
| `slot_w` | pin_d + 2 * clr_slide | mm | |
| `slot_depth` | a + R - C + pin_d / 2 + 1 | mm | From the wheel rim inward |
| `lock_r` | R - 6 | mm | Locking disc radius on the drive |
| `wheel_t` | 6 | mm | Both wheels |
| `axle_d` | 6 | mm | |
| `base_t` | 5 | mm | |

These formulas make the pin enter and leave each slot straight along the
slot (tangentially), which gives smooth starts and stops.

## Parts

`Base` (grounded), `Drive_Wheel`, `Geneva_Wheel`, `Axle_Pin` ×2.

## Modeling steps

Drive center at the origin. Geneva center at X = `C`. Both axes vertical.

1. **Geneva_Wheel** (center at (`C`, 0)).
   - Circle radius `R`.
   - Four slots, pointing at the wheel center, at 0°, 90°, 180°, 270°
     **rotated 45°** so that one slot points at the drive center at the
     start position (the slot at 180° points along −X towards the
     origin). Each slot: width `slot_w`, from the rim inward `slot_depth`,
     rounded inner end.
   - **Locking arcs:** between each pair of slots, cut a concave arc of
     radius `lock_r + clr_slide` centered at the **drive** center as seen
     when that gap faces the drive. Do it once for the gap facing −X
     (centered at the origin), then circular-pattern the cut 4 times
     around the Geneva center.
   - Extrude `wheel_t`. Hole `axle_d + 2 * clr_rot`. Hub boss below.
2. **Drive_Wheel** (center at origin).
   - A **locking disc**: circle radius `lock_r`, extruded `wheel_t`, at
     the Geneva wheel's height.
   - **Clearance cut-out** in the locking disc, on the pin's side, so
     the Geneva wheel can turn while the pin is engaged: with the pin at
     angle 0°, sketch a circle of radius `R + clr_slide` centered at
     (`C`, 0) and cut it from the locking disc.
   - **Drive plate** below the locking disc: circle radius `a + pin_d`,
     thickness 4 mm, at Z just below the Geneva wheel (`clr_axial` gap).
   - **Drive pin:** cylinder `pin_d` standing on the plate at radius `a`,
     angle 0° (pointing at the Geneva center), height up through the
     Geneva wheel thickness.
   - Hole `axle_d + 2 * clr_rot`. Handle peg on the drive plate.
3. **Base.** Plate covering both wheels + 10 mm margin. Two axle holes
   `axle_d` (press fit) at (0, 0) and (`C`, 0). Bosses `clr_axial` high.
   Give the Geneva wheel a 4 mm spacer hub underneath, so its working
   layer is at the same height as the locking disc (which sits on the
   4 mm drive plate).
4. **Axle_Pins** (×2): `axle_d`, caps, press into base.

## Assembly (joints)

| Joint | Between |
|---|---|
| Revolute | Drive_Wheel ↔ Base at origin |
| Revolute | Geneva_Wheel ↔ Base at (`C`, 0) |
| Rigid | Axle_Pins ↔ Base |

Use **Contact Sets** between the drive pin and the Geneva wheel, and
between the locking disc and the locking arcs, to watch it index while
dragging the drive wheel. (Or step through key positions by hand.)

## Verify

- Check positions at drive angles −45°, 0°, +45°: the pin enters a slot
  at −45° moving straight along it, is at the bottom of the slot at 0°,
  and leaves at +45°. Geneva wheel turns 90° during these 90° of the
  drive.
- For the other 270° of drive rotation the locking disc sits in a locking
  arc with ≈ `clr_slide` gap: the Geneva wheel can't turn.
- Interference: none in any position (check every 15°).

## Printing

| Part | Orientation | Supports | Notes |
|---|---|---|---|
| Base | Flat | No | |
| Geneva_Wheel | Flat | No | 0.15 mm layers |
| Drive_Wheel | Plate down, pin up | No | Pin prints round |
| Axle_Pins | Standing | No | 100 % infill |

If it binds, increase `clr_slide` to 0.4 mm and reprint the Geneva wheel
only.
