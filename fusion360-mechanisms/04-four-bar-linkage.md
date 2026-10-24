# 04 – Four-bar linkage (crank-rocker)

## What it does

Four links joined in a loop by four pins. The short **crank** turns all
the way round; the **rocker** swings back and forth; the **coupler**
traces a curved path. Used in windshield wipers, pumps, and legged toys.

## User parameters

| Name | Expression | Unit | Notes |
|---|---|---|---|
| `L_ground` | 60 | mm | Distance between the two fixed pivots |
| `L_crank` | 20 | mm | Shortest link, turns fully |
| `L_coupler` | 55 | mm | |
| `L_rocker` | 45 | mm | |
| `link_w` | 10 | mm | Link width |
| `link_t` | 4 | mm | Link thickness |
| `pin_d` | 5 | mm | |
| `clr_rot` | 0.25 | mm | |
| `clr_axial` | 0.4 | mm | |
| `hole_d` | pin_d + 2 * clr_rot | mm | |
| `base_t` | 5 | mm | |

**Grashof check** (so the crank can turn fully): shortest + longest ≤
sum of the other two → 20 + 60 = 80 ≤ 55 + 45 = 100 ✔. If you change
lengths, keep this true and keep the crank the shortest link.

## Parts

`Base` (grounded), `Crank`, `Coupler`, `Rocker`, `Pin` ×4, `Handle`
(optional peg on the crank).

## Modeling steps

Fixed pivots: **O2** (crank) at the origin, **O4** (rocker) at X =
`L_ground`.

1. **Link template** (used for crank, coupler, rocker). In a new
   component, sketch on XY: two circles diameter `link_w`, center
   distance `L_x`, joined by tangent lines (a slot). Two holes
   `hole_d` at the centers. Extrude `link_t`.
2. **Crank**: template with `L_crank`. Layer 1, Z from `base_t +
   clr_axial`.
3. **Coupler**: template with `L_coupler`. Layer 2, Z = `base_t + 2 *
   clr_axial + link_t`.
4. **Rocker**: template with `L_rocker`. Layer 1 (same height as the
   crank — they never cross).
5. **Base.**
   - Plate: rectangle from X −20 to `L_ground + 20`, Y −45 to +60,
     thickness `base_t`. Cut a large pocket in the middle if you want to
     save material, keeping ≥ 8 mm around both pivots.
   - Holes `pin_d` (press fit) at O2 and O4.
   - Small bosses (diameter `pin_d + 4`, height `clr_axial`) at O2 and
     O4 so the links don't rub on the plate.
6. **Pins** (×4). Diameter `pin_d`, cap 2 mm thick, diameter `pin_d +
   4`.
   - Ground pins (O2, O4): length `base_t + clr_axial + link_t + 1`,
     press into the base.
   - Moving pins (crank–coupler, coupler–rocker): length `2 * link_t +
     clr_axial + 1.5`. Press-fit into the lower link (crank or rocker)
     by modeling that lower link's hole as `pin_d` (press) instead of
     `hole_d`. Their caps sit on top of the coupler.
7. **Handle** (optional): 6 mm diameter × 15 mm peg on top of the crank
   at its outer pin, or extend the crank with a knob.

## Assembly (joints)

| Joint | Between | Notes |
|---|---|---|
| Revolute | Crank ↔ Base | at O2 |
| Revolute | Rocker ↔ Base | at O4 |
| Revolute | Coupler ↔ Crank | at crank end |
| Revolute | Coupler ↔ Rocker | at rocker end |
| Rigid | each Pin ↔ the part it's pressed into | |

Fusion solves the closed loop automatically. Start the crank pointing
up (90°) so the initial position is easy to solve.

## Verify

- Drag the crank one full turn: it must rotate 360° with no lockup; the
  rocker swings about 55°.
- **Motion Study**: drive the crank revolute 0 → 360°, play, and turn on
  **Inspect → Interference** along the path (or check several positions).
- The coupler is above the crank and rocker at every angle (they never
  collide because they are on different layers).

## Printing

| Part | Orientation | Supports | Notes |
|---|---|---|---|
| Base | Flat | No | |
| Crank, Coupler, Rocker | Flat | No | 3 walls, 30 % infill |
| Pins | Standing, cap up | No | 100 % infill |

Optional: replace pins with M5 × 12 screws + nylock nuts (not tightened).
