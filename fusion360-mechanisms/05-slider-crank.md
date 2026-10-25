# 05 – Slider-crank

## What it does

A rotating crank pushes a connecting rod, which slides a piston back and
forth in a straight guide. Stroke = 2 × crank radius. It's the mechanism
in every piston engine and many pumps and compressors.

## User parameters

| Name | Expression | Unit | Notes |
|---|---|---|---|
| `r_crank` | 15 | mm | Stroke = 30 mm |
| `L_rod` | 50 | mm | Keep ≥ 3 × `r_crank` |
| `slider_w` | 16 | mm | Slider width (Y) |
| `slider_l` | 22 | mm | Slider length (X) |
| `slider_h` | 10 | mm | Slider height (Z) |
| `link_w` | 10 | mm | |
| `link_t` | 4 | mm | |
| `pin_d` | 5 | mm | |
| `clr_rot` | 0.25 | mm | |
| `clr_slide` | 0.3 | mm | |
| `clr_axial` | 0.4 | mm | |
| `base_t` | 5 | mm | |
| `wheel_d` | 2 * r_crank + 14 | mm | Crank disc diameter |

## Parts

`Base` (grounded), `Crank_Disc`, `Rod`, `Slider`, `Pin` ×3.

## Modeling steps

Crank axis at the origin (vertical, Z). The slider moves along +X; its
path passes through the crank center (inline slider-crank).

1. **Crank_Disc.** Disc diameter `wheel_d`, thickness `link_t + 2`, on
   a hub boss (`pin_d + 6` diameter, `clr_axial` high) at the bottom.
   Center hole `pin_d + 2 * clr_rot`. Crank pin hole `pin_d` (press fit)
   at radius `r_crank`. Optional handle peg near the rim.
2. **Rod.** Slot-shaped link: center distance `L_rod`, width `link_w`,
   thickness `link_t`, holes `pin_d + 2 * clr_rot` at both ends. Sits on
   top of the crank disc.
3. **Slider.** Block `slider_l × slider_w × slider_h`.
   - Pin hole `pin_d` (press fit), vertical, at the slider's center, with
     its top at the rod's height.
   - The rod lies on top of the slider; the wrist pin goes through both,
     with its cap on top.
   - Chamfer the leading/trailing edges 0.5 mm.
4. **Base.**
   - Plate covering X from `-wheel_d / 2 - 8` to `r_crank + L_rod +
     slider_l / 2 + 15`, Y ± (`wheel_d / 2 + 8`), thickness `base_t`.
   - Crank pin hole `pin_d` (press fit) at the origin.
   - **Guide channel** for the slider: two rails along X, from X =
     `L_rod - r_crank - slider_l / 2 - 3` to `L_rod + r_crank + slider_l
     / 2 + 3`, gap between rails = `slider_w + 2 * clr_slide`, height
     `slider_h * 0.7`.
   - Set the slider's bottom on the plate, and the slider's height so
     the rod (on top of the crank disc) lines up with the slider top; add
     a raised floor in the channel to match, so the rod is level.
   - Add an end stop at each end of the channel.
5. **Pins** (×3): crank axis pin (press into base), crank pin (press into
   disc, through rod), wrist pin (press into slider, through rod). Each
   with a 2 mm cap.

## Assembly (joints)

| Joint | Between | Notes |
|---|---|---|
| Revolute | Crank_Disc ↔ Base | axis Z at origin |
| Slider | Slider ↔ Base | along X |
| Revolute | Rod ↔ Crank_Disc | at crank pin |
| Revolute | Rod ↔ Slider | at wrist pin |
| Rigid | each Pin ↔ its press-fit part | |

## Verify

- Turn the crank 360°: slider moves exactly `2 * r_crank` (30 mm).
  Measure slider position at 0° and 180°.
- The slider never hits the end stops (≥ 3 mm left at each end).
- Interference: none, especially rod vs. rail tops at 90° and 270°.

## Printing

| Part | Orientation | Supports | Notes |
|---|---|---|---|
| Base | Flat | No | Rails print upright |
| Crank_Disc | Flat, hub down | No | |
| Rod | Flat | No | |
| Slider | Flat (largest face down) | No | Light sanding of sides if tight |
| Pins | Standing | No | 100 % infill |

Rub a little dry PTFE lube or pencil graphite into the channel.
