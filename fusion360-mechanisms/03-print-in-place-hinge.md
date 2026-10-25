# 03 – Print-in-place hinge

## What it does

Two leaves joined by interlocking knuckles that come off the printer
already assembled and moving. Cone-shaped pins replace a metal rod, so
no supports are needed. Used for box lids, flaps and test prints.

## User parameters

| Name | Expression | Unit | Notes |
|---|---|---|---|
| `leaf_w` | 40 | mm | Along the hinge axis |
| `leaf_l` | 30 | mm | Each leaf, away from the axis |
| `leaf_t` | 3 | mm | |
| `knuckle_d` | 8 | mm | Outer diameter |
| `knuckles` | 5 | – | Odd number |
| `clr_pip` | 0.4 | mm | Gap between moving parts |
| `knuckle_len` | (leaf_w - (knuckles - 1) * clr_pip) / knuckles | mm | 7.68 mm |
| `cone_d` | 4.4 | mm | Cone base diameter |
| `cone_h` | 2.2 | mm | Cone height (45° sides) |

## Parts

`Leaf_A` (knuckles 1, 3, 5) and `Leaf_B` (knuckles 2, 4). Two components,
modeled in place in one design.

## Modeling steps

The hinge axis runs along X, at height Z = `knuckle_d / 2`. Both leaves
lie flat (Z = 0 bottom) for printing — the hinge is printed open at 180°.

1. **Leaf_A.**
   - Sketch on XY: rectangle X 0 → `leaf_w`, Y `-leaf_l` →
     `-knuckle_d / 2 - clr_pip`. Extrude `leaf_t`.
   - Sketch on YZ (plane at X = 0): circle diameter `knuckle_d` centered
     at Y = 0, Z = `knuckle_d / 2`. Extrude `knuckle_len` in +X: knuckle 1.
   - Connect knuckle to leaf with a rectangle bridging the gap: only for
     Leaf_A's own knuckles, from the leaf edge to the knuckle center.
   - Knuckles 3 and 5: copy knuckle 1 at offsets `2 * (knuckle_len +
     clr_pip)` and `4 * (knuckle_len + clr_pip)` (Rectangular Pattern,
     3 copies, spacing `2 * (knuckle_len + clr_pip)`).
2. **Leaf_B.** Mirror the leaf plate to +Y. Knuckles 2 and 4 at X
   offsets `knuckle_len + clr_pip` and `3 * (knuckle_len + clr_pip)`,
   connected to Leaf_B's plate only.
3. **Cones (the pins).** On each face where a Leaf_A knuckle meets a
   Leaf_B knuckle:
   - Add a cone to one knuckle face: **Create → Revolve** a right
     triangle (base `cone_d / 2`, height `cone_h`) around the hinge axis.
   - Cut the matching cone pocket in the opposite knuckle face, offset
     outward by `clr_pip` (use **Modify → Offset Face** or revolve a
     triangle of base `cone_d / 2 + clr_pip`).
   - Point all cones along +X, so every cone is "male on the left".
4. **Ground clearance.** The knuckles must not touch the bed under the
   other leaf: cut a `clr_pip` gap between each knuckle and the plate of
   the *other* leaf.
5. Chamfer 0.4 mm on all bottom edges.

## Assembly (joints)

| Joint | Between | Notes |
|---|---|---|
| Revolute | Leaf_B ↔ Leaf_A | Axis = hinge axis; limits 0° to 180° |

Ground Leaf_A.

## Verify

- **Interference:** none. Measure the smallest gap between leaves: must
  be ≥ `clr_pip` everywhere (cone tips included).
- Section view along the axis: the cone overhangs are 45° (printable).
- Rotate Leaf_B through 180°: no collision.

## Printing

| Part | Orientation | Supports | Notes |
|---|---|---|---|
| Whole hinge (both leaves as one print) | Flat, open, as modeled | **No** | 0.12–0.16 mm layers, 3 walls, no ironing |

After printing, flex the hinge gently a few times to break any thin
strings. If it's fused, increase `clr_pip` to 0.5 mm. Export both
bodies into one 3MF so they print together.
