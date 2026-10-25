# Cardboard templates to cut with a knife

Ten printable templates for **3 mm corrugated cardboard** (and one for
thin card). Print them on **A4**, glue the paper on the board, and cut
with a craft knife and a steel ruler. Parts bigger than A4 are split over
several sheets that you tape together.

Everything is drawn for a knife:
- **Straight lines only.** Even the gears have straight-sided teeth, and
  "round" holes are squares.
- **Slots are exactly the board thickness** (3 mm), so cross-slot joints
  hold without glue.
- **No strip narrower than 5 mm**, so the board doesn't tear.

## Files

| File | What |
|---|---|
| `pdf/<example>.pdf` | The template for one example, 1:1 on A4. Big examples start with a **sheet map**. |
| `pdf/all-examples.pdf` | All ten in one file (28 pages). |
| `svg/<example>.svg` | Full-size drawing in one piece: for a cutting machine (Cricut, Silhouette, laser) or a copy shop's large-format printer. |
| `generate.py` | Makes all the files (Python + ReportLab). |
| `check.py` | Checks joints, gears, sheet coverage, thin spots (Shapely). |

## The examples

| # | Example | Pages | Joins with | Extra things |
|---|---|---|---|---|
| 01 | Test strip: find your slot width | 1 | – | – |
| 02 | Phone stand | 1 | Cross slots | – |
| 03 | Desk organizer box 100×80×90 | 4 + map | Folds + glue flaps | Glue |
| 04 | Laptop stand | 2 + map | Cross slots | Double-wall board is better |
| 05 | Drawer divider grid 240×160×50 | 2 + map | Cross slots | – |
| 06 | Tuck-end box 60×40×80 | 2 + map | Folds + one glue flap | **Thin card** (cereal box) |
| 07 | Four-bar linkage toy | 1 | Split pins | 4 split pins (paper fasteners) |
| 08 | Gear pair 12T / 24T (2:1) | 3 + map | Pencil axles | 2 pencils or split pins |
| 09 | Catapult | 2 + map | Tabs in slots, pencil axle | Pencil, rubber band, tape |
| 10 | Small shelf 250×150×220 | 3 + map | Cross slots | Double-wall board for real use |

## Line types

| On the template | Meaning |
|---|---|
| **Solid black** | CUT through |
| **Dashed blue** | SCORE, then FOLD: press a groove along a ruler with the back of the knife or an empty ballpoint pen, then fold away from the groove |
| **Gray area** | GLUE here |
| **+** | Punch a hole (pencil, skewer, or the split pin itself) |
| **Red ⊕ crosses** | Alignment marks for taping sheets together |

## Printing

1. Print at **100 % / "Actual size"**. Turn off "Fit to page" (or
   "Shrink oversized pages").
2. Measure the **100 mm scale bar** at the bottom of a page with a ruler.
   It must be exactly 100 mm. The light gray grid on tiled sheets is
   50 mm.

## Joining sheets (big examples)

The first page of a big example is a **map** that shows which sheet goes
where (A1, B1, … with columns A, B, C left to right and rows 1, 2 top to
bottom).

1. On every sheet except column A, trim the **left** edge along the gray
   frame. On every sheet except the bottom row, trim the **bottom** edge
   along the gray frame. (Each sheet's footer says which edge overlaps
   which sheet.)
2. Lay the trimmed sheet over its neighbour so the **red crosses sit
   exactly on top of each other**, and the lines continue straight. Tape
   it.
3. Join each row first, then the rows to each other.
4. Glue the finished template to the cardboard with a glue stick, or
   tape the corners, and cut.

## Cutting tips

- Use a sharp blade (snap off a fresh segment) and a **steel ruler**. Make
  2–3 light passes instead of one hard one.
- Cut slots by making the two long cuts first, then the short end cut.
- **Flutes** (the waves inside corrugated board) matter:
  - For **slotted parts** (stands, shelf, grid), run the flutes across the
    slot, up-down in the standing parts. They're much stiffer that way.
  - For **folds**, folding along the flutes is easiest and cleanest.
- If the slots are loose or too tight, cut the **test strip (01)** first.
  Then set `T` in `generate.py` to the slot that fits and run
  `python3 generate.py` again. Every slot in every example updates.

## Regenerate and check

```
pip install reportlab shapely
python3 generate.py     # writes pdf/ and svg/
python3 check.py        # checks the designs
```

`check.py` confirms that:
- Every outline is a clean closed shape and every slot is `T` wide.
- The two slot depths of each cross joint add up to the crossing height,
  and the part is tall enough where the slot is.
- The gears mesh without overlap through a full tooth.
- The four-bar crank turns all the way round.
- The catapult tabs fit their slots and the arm swings freely.
- The A4 sheets cover each drawing.

Current result: **0 errors, 1 warning** (a sharp corner on the phone
stand: cut it slowly).

## Changing sizes

Each example is a short function in `generate.py` with its sizes at the
top. For example, change `L, S, H` in `ex05_drawer_grid` to fit your
drawer, or `W, D, H` in `ex03_desk_organizer` for a different box. Run
`generate.py` again and the PDFs, sheet tiling and SVGs all update.
