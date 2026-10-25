# 10 – Planetary gearbox

## What it does

A central **sun** gear drives three **planet** gears that roll inside a
fixed **ring** gear (internal teeth). The planets carry a **carrier**
that turns slowly. With the ring fixed, input on the sun and output on
the carrier: ratio = 1 + Z_ring / Z_sun = **4:1**. Compact, strong, and
used in drills, robot joints and car transmissions.

## User parameters

| Name | Expression | Unit | Notes |
|---|---|---|---|
| `m` | 1.5 | mm | Module |
| `z_sun` | 12 | – | |
| `z_planet` | 12 | – | |
| `z_ring` | z_sun + 2 * z_planet | – | = 36 (required) |
| `n_planets` | 3 | – | (z_sun + z_ring) / n_planets must be a whole number: 48 / 3 = 16 ✔ |
| `gear_t` | 8 | mm | Face width |
| `orbit_r` | m * (z_sun + z_planet) / 2 | mm | = 18 mm, sun → planet center |
| `ring_wall` | 5 | mm | Material outside the ring teeth |
| `pin_d` | 5 | mm | Planet pins |
| `shaft` | 5 | mm | Sun shaft (hex 5 mm across flats) |
| `clr_rot` | 0.25 | mm | |
| `clr_axial` | 0.4 | mm | |
| `backlash` | 0.15 | mm | Applied as tooth thinning (see below) |
| `carrier_t` | 4 | mm | |

## Parts

`Ring_Housing` (grounded), `Sun` (with input knob), `Planet` ×3,
`Carrier` (output, with planet pins), `Lid`.

## Modeling steps

Axis along Z at the origin. All gears sit on the same layer, Z from
`carrier_t + clr_axial` up `gear_t`.

1. **Sun.** SpurGear script: m 1.5, 12 teeth, 20°, thickness `gear_t`.
   Add a hex shaft (5 mm across flats) extruding 15 mm upward through the
   lid for a knob or a drill bit. Center at origin.
2. **Planet** (make one, pattern later). SpurGear: m 1.5, 12 teeth.
   Hole `pin_d + 2 * clr_rot`. Center at (`orbit_r`, 0). Rotate it so its
   teeth mesh with the sun (a tooth in a gap; with 12/12 teeth, rotate the
   planet 15° = half a tooth).
3. **Ring_Housing** (internal gear).
   - The internal gear's tooth space is the shape of an external gear's
     tooth. Make a temporary 36-tooth external gear with the SpurGear
     script (m 1.5, 36 teeth) and **enlarge** it for clearance (scale
     the sketch/body by (`m * z_ring / 2 + backlash`) / (`m * z_ring /
     2`) ≈ 1.006).
   - Draw the housing: cylinder radius `m * z_ring / 2 + m * 1.25 +
     ring_wall` (≈ 33.9 mm), height `carrier_t + clr_axial + gear_t +
     clr_axial + 3`.
   - **Combine → Cut** the enlarged 36-tooth gear from the housing at
     the gear layer height. The result is the ring with internal teeth.
     Delete/hide the tool body.
   - Below the gear layer, open the housing bore to radius `orbit_r +
     pin_d / 2 + 6` for the carrier, and add a 2 mm floor with a center
     hole for the carrier output shaft.
   - Rotate the ring so its teeth mesh with the planet at (`orbit_r`, 0).
   - Three screw ears for M3 (or snap tabs) on the outside to fix the lid.
4. **Carrier** (below the gears).
   - Disc radius `orbit_r + pin_d / 2 + 5`, thickness `carrier_t`.
   - Three pins `pin_d`, height `gear_t + clr_axial`, at radius
     `orbit_r`, 120° apart (circular pattern), on the top face.
     Chamfer pin tips 0.4 mm.
   - Output shaft: 8 mm hex (or round with a flat) down through the
     housing floor.
5. **Planet pattern.** Circular pattern the Planet **component** 3 times
   around Z. Check each copy meshes with both the sun and the ring (the
   assembly condition above guarantees it when the first one does).
6. **Lid.** Disc that covers the ring top, thickness 3 mm, with a center
   hole `shaft` hex + 0.5 mm, sits `clr_axial` above the gears. Screw
   holes matching the ears.

### Backlash note

The ring is enlarged slightly (step 3) and printed gears always shrink a
little, so leave sun and planets at nominal size. If it's tight, sand
lightly or raise `backlash` to 0.25 mm and re-cut the ring.

## Assembly (joints)

| Joint | Between | Notes |
|---|---|---|
| Revolute | Sun ↔ Ring_Housing | axis Z |
| Revolute | Carrier ↔ Ring_Housing | axis Z |
| Revolute | each Planet ↔ Carrier | at each pin |
| Rigid | Lid ↔ Ring_Housing | |
| Motion Link | Sun ↔ Carrier | Sun 360° ↔ Carrier 90° (same direction) |
| Motion Link | Sun ↔ each Planet | Planet spin relative to carrier: Sun 360° ↔ Planet −270° (= −z_sun / z_planet × (sun − carrier)); optional, for a visual check |

## Verify

- Interference: none (gears only touch with the clearance gap).
- Section view through the gear layer: sun–planet and planet–ring teeth
  mesh at all three planets.
- Turn the sun 4 full turns: the carrier turns exactly 1 turn, same
  direction.

## Printing

| Part | Orientation | Supports | Notes |
|---|---|---|---|
| Ring_Housing | Floor down | No | 0.15 mm layers, 4 walls |
| Sun | Gear face down, shaft up | No | 4 walls, 40 % infill |
| Planets ×3 | Flat | No | Print all three together |
| Carrier | Pins up | No | 100 % infill for the pins (use a modifier) |
| Lid | Flat | No | |

Hardware: 3 × M3 × 8 screws for the lid (or snap tabs). Add a drop of
light grease (PTFE or silicone) to the gears.
