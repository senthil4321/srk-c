# Laser-cut sheet metal examples (2 mm)

Twenty ready-to-cut examples for **2 mm sheet** (mild steel, stainless or
aluminium): seven single-sheet parts (01–07) and thirteen **two-plate
assemblies joined by M3 threaded rod and smooth rods** (08–20). Each
comes in three formats:

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

## Two plates joined by rods (08–20)

Each of these is **two plates held apart by M3 threaded rod**. Every
plate is clamped between two nuts with washers, so the nuts set the gap
between the plates. **3 mm smooth rods** (silver steel, ground rod or
dowel pins) are the axles, pivots, locating pins and slide guides.
Example 20 uses **8 mm smooth rods** with LM8UU linear bearings. Each
page of the paper-check PDF lists the hardware for that example.

| # | Example | What moves | Gap | Hardware (main) |
|---|---|---|---|---|
| 08 | Two-plate sandwich | – (the basic pattern) | 30 | 4× M3 rod 42, 2× 3 mm locating rod 34 |
| 09 | Electronics stack | – (Raspberry Pi 4 hole pattern, vents) | 25 | 4× M3 rod 37, M2.5 standoffs |
| 10 | Bearing block | 8 mm shaft in two 608 bearings | 20 | 4× M3 rod 32, 2× 608, base with tabs/slots |
| 11 | Spool holder | spool on an 8 mm axle in U-notches | 80 | 3× M3 rod 92, 8 mm rod 100 |
| 12 | Rope pulley block | sheave of 4 discs on a 3 mm axle | 10 | 2× M3 rod 22, 3 mm rod 14 |
| 13 | Gear train | 16T / 32T gears (2:1) on fixed 3 mm axles | 10 | 4× M3 rod 22, 2× 3 mm rod 14 |
| 14 | Rack and pinion | rack slides ±30 mm on two 3 mm rods | 10 | 2× M3 rod 22, 3× 3 mm rod 14 |
| 15 | Four-bar linkage | crank turns, rocker swings | 8 | 4× M3 rod 20, 3 mm stubs and pins |
| 16 | Slider-crank | 3 mm slider pin runs in slots in both plates | 8 | 4× M3 rod 20, 3 mm stub, pins |
| 17 | Cam and follower | follower lifts 10 mm, slides on two 3 mm rods | 8 | 4× M3 rod 20, 3 mm rods |
| 18 | Ratchet | wheel turns one way, pawl on a 3 mm rod | 8 | 4× M3 rod 20, 3 mm rods, spring |
| 19 | Lead-screw slide | carriage on two 3 mm rods, driven by M3 rod | 80 | 4× M3 rod 92, M3 rod 110 lead screw |
| 20 | Linear rail | carriage on two 8 mm rods, LM8UU bearings | 150 | 4× M3 rod 162, 2× 8 mm rod 154 |

**M3 threaded-rod length** = gap + 2 × 2 mm plate + 2 × (nut 2.4 + washer
0.5) + 2 mm spare, rounded up. For example a 30 mm gap needs 42 mm rods.

### Rod hole sizes

| Hole | Size | For |
|---|---|---|
| M3 threaded rod / screw | 3.4 | Clearance |
| 3 mm smooth rod, held still | 3.1 | Snug fit; glue (retaining compound) or e-clips |
| 3 mm smooth rod, turning or sliding | 3.2 | Running fit |
| Slot for a 3 mm sliding rod | 3.3 wide | Slides along the slot |
| 8 mm smooth rod, held still | 8.1 | |
| 608 bearing (22 mm OD) | 22.1 | Plus retaining compound |
| LM8UU bearing (15 mm OD) | 15.0 | Snug; check with the test coupon |
| Captive M3 nut | 5.7 hex across flats | Nut can't turn |

Cut the test coupon (01) first and adjust `HOLE` in `rod_examples.py`
if the rods are too tight or too loose in your laser's holes.

### Assembling a two-plate example

1. On each M3 rod: nut, washer, **first plate**, washer, nut. Leave the
   nuts loose.
2. Thread the inner nuts of the second plate so the gap matches the
   table, using calipers or a spacer block. Fit the **second plate**,
   washer and outer nut.
3. Put in the 3 mm smooth rods and the moving parts before tightening.
   Where a part is "3 layers", stack the three cut layers on the axle
   and pin them together with the small pin through the second hole.
4. Tighten the nuts in pairs, keeping the plates parallel (measure the
   gap at all corners). Check everything still turns or slides freely.
5. Fix the "held still" smooth rods with retaining compound or e-clips.

Design notes:
- **15 and 16** use a short **stub axle**: it goes only through the
  bottom plate and the crank (with the handle underneath). A full-length
  axle would block the coupler or connecting rod when it swings over the
  crank center.
- **19:** one knob turn moves the carriage **0.5 mm** (the M3 thread
  pitch): slow and precise. Lock the lead screw in one end plate with
  two nuts, one each side of the plate.
- **17:** stand it upright so gravity pulls the follower down onto the cam.

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
