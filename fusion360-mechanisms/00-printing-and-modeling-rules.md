# Printing and modeling rules (apply to every mechanism)

## Printer assumptions

| Setting | Value |
|---|---|
| Process | FDM, 0.4 mm nozzle |
| Layer height | 0.2 mm (0.12–0.16 mm for gears and print-in-place) |
| Material | PLA or PETG (PETG for parts that flex, like pawls) |
| Walls | 3 perimeters (4 for gears and pins) |
| Top/bottom | 4 layers |
| Infill | 25–40 % gyroid; 100 % for pins under 5 mm |
| Bed | Smooth or textured PEI; brim only for tall thin parts |

If your printer prints tight, raise every clearance below by 0.1 mm.
Print the **clearance test** at the end of this file once per printer and
material.

## Clearances

Put these in every design as user parameters, and use them by name.

| Parameter | Value | Use |
|---|---|---|
| `clr_slide` | 0.3 mm | Gap per side between parts that slide (slider in a channel) |
| `clr_rot` | 0.25 mm | Gap per side (radial) for a pin rotating in a hole |
| `clr_press` | 0.0 mm | Pin pressed into a hole that must not turn |
| `clr_pip` | 0.4 mm | Gap per side for print-in-place moving parts |
| `clr_axial` | 0.4 mm | Gap between stacked parts along a shaft |
| `backlash` | 0.2 mm | Extra gear center distance |
| `wall_min` | 1.6 mm | Thinnest wall (4 lines of 0.4 mm) |

How to apply them:
- **Hole for a rotating pin:** hole diameter = `pin_d + 2 * clr_rot`.
- **Slot for a slider:** slot width = `slider_w + 2 * clr_slide`.
- **Gears:** center distance = theoretical + `backlash`.

## Modeling rules

1. **Units:** millimeters. Set **Document Settings → Units → mm**.
2. **Parameters first:** create every user parameter in the mechanism's
   table before sketching. Dimension sketches with parameter names, never
   typed numbers, so the design can be resized later.
3. **One component per printed part.** Create components with
   **Assemble → New Component**, activate a component before sketching
   in it, and name it as in the file's Parts list. Each component holds
   exactly one solid body.
4. **Ground** the base/frame component (right-click → Ground).
5. **Fully constrain sketches** (all lines turn black). Put the main
   rotation center on the sketch origin where possible.
6. **Joints, not overlaps:** connect parts with joints (Revolute, Slider,
   Pin-Slot, Rigid). Never let solids overlap; leave the clearance gap.
7. **Name features and sketches** as in the steps (e.g. `sk_crank`), so
   they are easy to find and edit.

## Design rules for printing

- **Flat bottom:** every part needs one flat face to sit on the bed.
  The steps say which face is the bottom.
- **Overhangs:** keep under 45° from vertical. Use a 45° chamfer, not a
  fillet, on bottom edges (fillets on the bottom edge droop).
- **Bottom edge chamfer:** 0.4 mm chamfer on edges touching the bed, so
  the "elephant's foot" doesn't fuse parts or block holes.
- **Horizontal holes** (axis parallel to the bed): use a teardrop shape
  (45° point at the top) or accept they print ~0.2 mm undersize.
- **Vertical holes** print about 0.1–0.2 mm small. The `clr_rot` value
  above already allows for this.
- **Pins:** printed pins are strongest printed lying flat, but then
  they're not round. Print them **standing up** with 100 % infill, and a
  0.5 mm chamfer on both ends. Minimum printed pin diameter: 4 mm.
- **Retaining pins:** a pin is held by a cap, a snap ring groove, or a
  press fit at one end (`clr_press`). The steps say which.
- **Gears:** module ≥ 1.0 for printed gears; ≥ 1.5 is more reliable.
  Gear thickness ≥ 6 mm. Keep tooth count ≥ 12 to avoid undercut.
- **Text and small details:** at least 0.8 mm wide and 0.6 mm deep.

## Gears in Fusion 360

Gears appear in mechanisms 01, 02 and 10. Two ways to make the profile:

**A. SpurGear script (built in).** **Utilities → Add-Ins → Scripts and
Add-Ins → SpurGear (Python) → Run.** Enter module, number of teeth,
pressure angle 20°, thickness, and the root fillet. It creates the gear
in a new component. Then rename it and move it to position.

**B. Your own involute sketch (for scripting through the API).** For
module `m`, teeth `z`, pressure angle α = 20°:

| Quantity | Formula |
|---|---|
| Pitch diameter | d = m · z |
| Base diameter | db = d · cos α |
| Outside (tip) diameter | da = d + 2m |
| Root diameter | df = d − 2.5m |
| Circular pitch | p = π · m |
| Tooth thickness at pitch circle | s = p / 2 |

Involute points (for t from 0 to the tip): with rb = db / 2,
`x = rb (cos t + t sin t)`, `y = rb (sin t − t cos t)`. Draw one tooth
flank as a fitted spline through ~10 points, mirror it around the tooth
center line, close it with the tip and root arcs, extrude, then do a
circular pattern of `z` teeth.

For printing: chamfer both faces of every gear 0.4 mm on the tooth tips,
and use the `backlash` parameter when placing gears.

## Exporting for printing

- Right-click each body → **Save As Mesh** → **3MF** (preferred) or STL,
  refinement **High**.
- File name: `<number>-<mechanism>-<part>.3mf`, for example
  `04-four-bar-crank.3mf`.
- Export each part in its print orientation if possible. Otherwise note
  the orientation from the mechanism's Printing table.

## Clearance test coupon (print once)

Build this before the mechanisms to tune the clearance values:

1. Plate 60 × 15 × 4 mm with five 5 mm-diameter-nominal holes, sized
   5.2, 5.3, 5.4, 5.5, 5.6 mm, labeled `.1 .15 .2 .25 .3` (clearance per
   side).
2. A 5.0 mm × 12 mm pin, printed standing up.
3. Use the smallest hole where the pin turns freely as `clr_rot`, and the
   tightest hole where it can be pushed in but does not turn as the press
   fit.
