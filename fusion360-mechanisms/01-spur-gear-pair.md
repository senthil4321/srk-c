# 01 – Spur gear pair

## What it does

Two meshing gears on a base plate. Turning the small gear (pinion) turns
the large gear slower, in the opposite direction, with more torque.
Ratio = `z_gear / z_pinion` = 2:1. Used in clocks, gearboxes, and toys.

## User parameters

| Name | Expression | Unit | Notes |
|---|---|---|---|
| `m` | 2 | mm | Module |
| `z_pinion` | 15 | – | Teeth, small gear |
| `z_gear` | 30 | – | Teeth, large gear |
| `gear_t` | 8 | mm | Gear thickness |
| `pin_d` | 6 | mm | Shaft pin diameter |
| `clr_rot` | 0.25 | mm | See rules |
| `clr_axial` | 0.4 | mm | |
| `backlash` | 0.2 | mm | |
| `center_dist` | m * (z_pinion + z_gear) / 2 + backlash | mm | 45.2 mm |
| `base_t` | 5 | mm | Base plate thickness |
| `boss_h` | 1 | mm | Spacer boss height |
| `cap_d` | pin_d + 4 | mm | Pin cap diameter |

## Parts

| Component | Count |
|---|---|
| `Base` | 1 |
| `Pinion` | 1 |
| `Gear` | 1 |
| `Pin` | 2 |
| `Crank_Handle` | 1 (joined to Pinion, optional) |

## Modeling steps

1. **Base** (ground it).
   - Sketch `sk_base` on XY: a slot shape (two circles of diameter
     `m * z_gear / 2 + 10` and `m * z_pinion / 2 + 10`, center distance
     `center_dist`, joined by tangent lines). Pinion center at the
     origin, gear center on the +X axis at `center_dist`.
   - Extrude `base_t`.
   - Two holes, diameter `pin_d` (press fit), through, at both centers.
   - On the top face, two bosses: circle diameter `pin_d + 4`, height
     `boss_h`, at both centers (keeps gears off the base).
2. **Pinion.** Use the SpurGear script (or the involute method in the
   rules): module `m`, `z_pinion` teeth, 20°, thickness `gear_t`.
   - Center hole diameter `pin_d + 2 * clr_rot`.
   - Move it so its bottom face sits on top of the boss (Z = `base_t +
     boss_h`), centered on the origin.
   - Optional: extrude a 6 mm diameter, 15 mm tall crank peg 12 mm from
     the center on the top face.
3. **Gear.** Same, with `z_gear` teeth. Center at X = `center_dist`.
   - Cut 5 lightening holes (circle pattern) between hub and teeth to
     save material; keep ≥ `2 * m` of rim below the tooth root.
   - Rotate the gear by half a tooth (180° / `z_gear`) if the teeth
     overlap the pinion's teeth; a tooth of one must sit in a gap of the
     other.
4. **Pin** (×2). Cylinder diameter `pin_d`, length `base_t + boss_h +
   gear_t + clr_axial + 2`. Add a cap on top: diameter `cap_d`, 2 mm
   high. 0.5 mm chamfer on the bottom end.

## Assembly (joints)

| Joint | Between | Notes |
|---|---|---|
| Rigid | Pin 1 ↔ Base | At the pinion hole |
| Rigid | Pin 2 ↔ Base | At the gear hole |
| Revolute | Pinion ↔ Base | Axis Z, at origin |
| Revolute | Gear ↔ Base | Axis Z, at gear center |
| Motion Link | Pinion ↔ Gear | Pinion 360° ↔ Gear −180° (reversed) |

## Verify

- **Inspect → Interference** on all components: no overlap (the
  clearance gaps only).
- Drag the pinion: the gear turns half as far, opposite direction.
- **Inspect → Measure** the center distance: 45.2 mm.
- Section view through the teeth: a visible gap (≈ backlash) between
  meshing teeth.

## Printing

| Part | Orientation | Supports | Notes |
|---|---|---|---|
| Base | Flat, bottom down | No | |
| Pinion, Gear | Flat face down | No | 0.15 mm layers, 4 walls, 40 % infill |
| Pin | Standing, cap up | No | 100 % infill; press into base |

Hardware: none. (An M6 bolt can replace each printed pin.)
