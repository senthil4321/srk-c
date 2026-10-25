# Laser-cut sheet metal examples (2 mm)

Seven ready-to-cut examples for **2 mm sheet** (mild steel, stainless or
aluminium). Each comes in three formats:

| Format | Folder | Use it for |
|---|---|---|
| **DXF** (R2000, mm, true arcs) | `dxf/` | **Sending to the laser / job shop.** One file per part. |
| **SVG** (1:1, sized in mm) | `svg/` | Hobby laser software (LightBurn, LaserGRBL, Inkscape). |
| **PDF** (A4, 1:1, scale bars) | `pdf/paper-check-A4.pdf` | **Printing on paper** to check sizes before cutting. Not for cutting. |

All files are produced by `generate.py` and verified by `check.py`.

## The examples

| # | Example | Parts (qty) | Teaches |
|---|---|---|---|
| 01 | Test coupon | `01-test-coupon` 120×55, `01-test-tab` | Real hole sizes (2–6.6 mm) and slot widths (2.0–2.5 mm) from **your** laser; tab fit |
| 02 | L-bracket | `02-l-bracket` 30×66.52 flat | Bend line, bend allowance, holes away from the bend |
| 03 | Spur gear pair | `03-gear-16t`, `03-gear-32t`, `03-gear-plate` | Involute gears (module 2.5, 2:1), center distance 60.2 |
| 04 | Four-bar linkage | `04-four-bar-base`, `-crank`, `-coupler`, `-rocker` | Same lengths as Fusion mechanism 04, in metal |
| 05 | Tab-and-slot box | `05-box-bottom`, `05-box-front-back` (×2), `05-box-side` (×2) | Self-locating tabs and slots, no welding needed to align |
| 06 | Ratchet | `06-ratchet-wheel`, `06-ratchet-pawl`, `06-ratchet-base` | One-way mechanism, spring holes |
| 07 | Name plate | `07-nameplate` 80×30 | Engraving on a separate layer |

## Layers and colors

| DXF layer | SVG color | Meaning |
|---|---|---|
| `CUT` | red | Cut through. Closed contours only. |
| `BEND` | blue, dashed | Bend line for the press brake. **Do not cut.** Note gives direction, angle, radius. |
| `ETCH` | green | Engrave / mark only. Delete the layer if you don't want marking. |

Most shops cut only the `CUT` layer and read `BEND` for bending. Tell
them what to do with `ETCH`. Some shops need text converted to outlines:
if so, open the DXF in Fusion 360 / Inkscape / QCAD and explode the text.

## Workflow: paper → test cut → metal

1. **Print the paper check.** Open `pdf/paper-check-A4.pdf` and print at
   **100 % / "Actual size"** (turn off "Fit to page"). Measure both
   100 mm scale bars with a ruler. If either is off, fix the print
   setting and print again. A paper check is useless at the wrong scale.
2. **Check against real hardware.** On the paper:
   - Lay your bolts, shafts, pins and nuts on the holes (M3 → 3.4, M5
     → 5.5, 5 mm pin → 5.2, 8 mm shaft → 8.2).
   - Cut out the four-bar links with scissors, pin them with
     thumbtacks on cardboard, and turn the crank.
   - Cut out both gears and lay them on the axle plate: the teeth should
     mesh with a small gap.
   - Fold the bracket along the blue line: legs should measure 40 and 30
     (paper is thin, so expect ±1 mm).
   - Check the parts fit your enclosure or machine.
3. **Optional cheap test cut.** Cut the same SVG/DXF in **2 mm card,
   greyboard, MDF or acrylic** on a hobby laser. This tests the box tabs
   and slots for real, because the thickness matches.
4. **Cut the test coupon in metal first** (`01-test-coupon` +
   `01-test-tab`). Push the tab into each slot. Note the narrowest slot
   the tab fits and the hole sizes that fit your bolts.
   - If the tab doesn't fit 2.2 mm, change `SLOT_W` in `generate.py`
     (for example `T + 0.3`) and run `python3 generate.py` again.
5. **Order or cut the parts.** Send the DXF files (see the next section).
6. **After cutting:** deburr all edges, bend the bracket (bend line on
   the inside of the bend, 90° up), assemble the box (tabs through
   slots; then tack-weld, glue or twist the tabs).

## What to send to a laser-cutting shop

- The `dxf/*.dxf` files you need. Units are millimeters (`$INSUNITS = 4`);
  every part starts at (0, 0).
- **Material and thickness**, for example: *2 mm mild steel (S235/DC01)*,
  *2 mm stainless 304*, or *2 mm aluminium 5052* (5052 bends well; avoid
  6061-T6 for the bracket, it cracks).
- **Quantity** per part (in the table above; `05-box-front-back` and
  `05-box-side` are ×2).
- "Layer CUT = cut, BEND = bend lines (90° up, inside radius 2 mm),
  ETCH = engrave or ignore."
- Kerf: **don't** compensate it in the drawing. The files are nominal
  size; the shop's CAM offsets for the beam.

## Design rules used (2 mm sheet)

| Rule | Value | Why |
|---|---|---|
| Smallest hole or slot | ≥ thickness (2 mm) | Smaller holes don't cut cleanly in metal |
| Web (metal between two cuts, or a cut and the edge) | ≥ thickness (2 mm) | Thinner webs warp and burn |
| Slot for a 2 mm tab | 2.2 × 10.2 mm for a 10 mm tab | 0.1 mm play per side |
| Clearance holes | M3 3.4, M4 4.5, M5 5.5, M6 6.6; pins +0.2 | ISO medium fit |
| Hole to bend zone | ≥ 2 × t + R = 6 mm | Holes near a bend stretch into ovals |
| Inside bend radius | R = t = 2 mm | Common press-brake tooling |
| K-factor | 0.44 (mild steel, air bending) | |
| Bend allowance (90°) | BA = π/2 · (R + K·t) = **4.52 mm** | |
| Flat length | (leg A − R − t) + BA + (leg B − R − t) | 40/30 bracket → 66.52 mm |
| Bend line position | In the middle of the bend zone | 38.26 mm from the leg A end |

If your shop uses a different K-factor or radius, change `K_FACTOR` /
`BEND_R` in `generate.py`: the flat length and bend line move
automatically.

## Regenerate and check

```
pip install ezdxf reportlab shapely
python3 generate.py     # writes dxf/, svg/, pdf/
python3 check.py        # verifies the DXF files
```

`check.py` reads each DXF back and checks units, closed contours, hole
and slot widths, web thickness and narrow spots. It also checks how the
parts fit together: the gears mesh without overlap through a full tooth,
the pawl clears the ratchet teeth, every box tab lands in its slot, and
the bracket holes are clear of the bend. Current result: **17 files,
0 errors, 1 warning** (the pawl's pointed tip is narrower than 2 mm,
which is intended).

## Using with Fusion 360

- To view or edit a part: **Insert → Insert DXF**, pick the file, units
  mm. Then extrude 2 mm to see it in 3D.
- To make your own sheet-metal parts the same way: create a **Sheet
  Metal Rule** with thickness 2 mm, K-factor 0.44, bend radius 2 mm;
  model the part; **Create Flat Pattern**; right-click the flat pattern
  → **Export DXF**. Run it past the design rules above (or `check.py`).
