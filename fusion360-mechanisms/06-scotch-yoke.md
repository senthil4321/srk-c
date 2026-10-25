# 06 – Scotch yoke

## What it does

A pin on a rotating disc slides inside a slot in a sliding frame (the
yoke). The yoke moves back and forth in pure sine motion (x = r · cos θ)
with a stroke of 2r. Used in valve actuators, test rigs, and engines with
no connecting rod. More compact than a slider-crank (05).

## User parameters

| Name | Expression | Unit | Notes |
|---|---|---|---|
| `r_crank` | 15 | mm | Stroke = 30 mm |
| `pin_d` | 6 | mm | Crank pin diameter |
| `disc_d` | 2 * r_crank + 16 | mm | |
| `disc_t` | 5 | mm | |
| `yoke_slot_w` | pin_d + 2 * clr_slide | mm | Slot the pin runs in |
| `yoke_slot_l` | 2 * r_crank + pin_d + 2 | mm | |
| `yoke_wall` | 4 | mm | Material around the slot |
| `yoke_t` | 5 | mm | |
| `rod_w` | 8 | mm | Sliding rods on both sides |
| `rod_l` | 40 | mm | Each side |
| `clr_rot` | 0.25 | mm | |
| `clr_slide` | 0.3 | mm | |
| `clr_axial` | 0.4 | mm | |
| `base_t` | 5 | mm | |

## Parts

`Base` (grounded), `Crank_Disc`, `Yoke`, `Axle_Pin`.

## Modeling steps

Disc axis at the origin, vertical (Z). Yoke slides along X. The slot in
the yoke runs along Y.

1. **Crank_Disc.**
   - Disc `disc_d`, thickness `disc_t`, hub boss on the bottom
     (`pin_d + 6`, `clr_axial` high). Center hole `pin_d + 2 * clr_rot`.
   - Crank pin: cylinder `pin_d`, standing on the top face at radius
     `r_crank` on +X, height `yoke_t + clr_axial + 1`, with 0.4 mm top
     chamfer. Model it as part of the disc (one body).
2. **Yoke.**
   - Sketch on XY: a frame rectangle `yoke_slot_w + 2 * yoke_wall` (X)
     by `yoke_slot_l + 2 * yoke_wall` (Y), with the slot `yoke_slot_w ×
     yoke_slot_l` cut through the middle (rounded slot ends).
   - Two rods of width `rod_w`, length `rod_l`, extend from the frame in
     +X and −X.
   - Extrude `yoke_t`. Place it at Z = `base_t + clr_axial + disc_t +
     clr_axial` so it sits over the disc, around the crank pin.
3. **Base.**
   - Plate covering the disc plus yoke travel: X ± (`r_crank +
     yoke_slot_w / 2 + yoke_wall + rod_l + 5`), Y ± (`disc_d / 2 + 10`).
   - Center hole `pin_d` (press fit) for the axle pin.
   - Two **guide blocks**, one on each side, each with a rectangular
     tunnel the rod passes through: tunnel width `rod_w + 2 * clr_slide`,
     height `yoke_t + 2 * clr_slide`, at the yoke's height. Place them
     beyond the yoke frame's full travel (at X = ±(`r_crank +
     (yoke_slot_w / 2 + yoke_wall) + 4`) to ± that + 12).
   - Make the tunnel roof a 45° peak (diamond-top) so it prints without
     supports, or leave the guide open-top and add a separate snap-on
     cap.
4. **Axle_Pin.** Diameter `pin_d`, length through base + disc + 1 mm,
   2 mm cap.

## Assembly (joints)

| Joint | Between | Notes |
|---|---|---|
| Revolute | Crank_Disc ↔ Base | axis Z at origin |
| Slider | Yoke ↔ Base | along X |
| Pin-Slot | Crank pin ↔ Yoke slot | slot along Y |
| Rigid | Axle_Pin ↔ Base | |

If Pin-Slot is awkward to set up, use a **Motion Link** instead and let
the yoke follow visually; the physical part works the same way.

## Verify

- Turn the disc a full turn: yoke moves 30 mm total; at 90° and 270°
  the pin is at the slot ends with ≥ 1 mm left.
- Rod ends never leave the guide tunnels (≥ 5 mm stays inside).
- Interference: none.

## Printing

| Part | Orientation | Supports | Notes |
|---|---|---|---|
| Base | Flat | No (diamond-top tunnels) | |
| Crank_Disc | Flat, pin up | No | Pin prints round standing up |
| Yoke | Flat | No | |
| Axle_Pin | Standing | No | 100 % infill |

Assembly: drop the disc on the axle pin, then slide the yoke rods through
the guides while placing the slot over the crank pin.
