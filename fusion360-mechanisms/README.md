# 10 printable mechanisms for Fusion 360

Step-by-step build instructions for ten classic mechanical mechanisms,
designed in Fusion 360 and tuned for FDM 3D printing. They're written so
Claude Desktop with a Fusion 360 connection can follow them directly,
but a person can follow them by hand too.

| # | Mechanism | Motion it creates | Difficulty |
|---|-----------|-------------------|------------|
| 01 | [Spur gear pair](01-spur-gear-pair.md) | Rotation → rotation, speed change | Easy |
| 02 | [Rack and pinion](02-rack-and-pinion.md) | Rotation → straight line | Easy |
| 03 | [Print-in-place hinge](03-print-in-place-hinge.md) | Pivot, no assembly | Easy |
| 04 | [Four-bar linkage](04-four-bar-linkage.md) | Full rotation → rocking | Medium |
| 05 | [Slider-crank](05-slider-crank.md) | Rotation → back-and-forth | Medium |
| 06 | [Scotch yoke](06-scotch-yoke.md) | Rotation → pure sine motion | Medium |
| 07 | [Cam and follower](07-cam-and-follower.md) | Rotation → custom lift profile | Medium |
| 08 | [Ratchet and pawl](08-ratchet-and-pawl.md) | One-way rotation | Medium |
| 09 | [Geneva drive](09-geneva-drive.md) | Continuous → stepped rotation | Hard |
| 10 | [Planetary gearbox](10-planetary-gearbox.md) | High-ratio compact reduction | Hard |

**Set 2** (mechanisms 11–20, all in one file):
[11-20-mechanisms-set-2.md](11-20-mechanisms-set-2.md): lead screw,
Oldham coupling, pantograph, compliant bistable switch, toggle clamp,
universal joint, quick-return, Chebyshev lambda linkage, worm drive,
cycloidal drive.

Read [00-printing-and-modeling-rules.md](00-printing-and-modeling-rules.md)
first. Every mechanism file refers back to its clearances and print rules.

## How to use with Claude Desktop + Fusion 360

1. Open a new, empty Fusion 360 design.
2. Give Claude this repository folder (or paste the files).
3. Use this prompt, changing the number:

   > Read `fusion360-mechanisms/00-printing-and-modeling-rules.md` and
   > `fusion360-mechanisms/04-four-bar-linkage.md`. Build the mechanism in
   > the open Fusion 360 design exactly as described: create the user
   > parameters first, then one component per part, then the joints. After
   > each part, check its size against the parameter table. When done, run
   > the checks in the "Verify" section and report the results. Don't
   > export until I confirm.

4. Review the model, test the motion (drag the parts, or use Motion Study),
   then ask Claude to export each body as 3MF/STL.

Build one mechanism per design file. To change a size later, edit the
user parameter (**Modify → Change Parameters**) instead of the sketch.

## Structure of every mechanism file

Each file has the same sections, so they're easy to follow step by step:

1. **What it does**: the motion and where it's used.
2. **User parameters**: a table to enter in **Change Parameters**, with
   names, expressions and units. All geometry refers to these names.
3. **Parts**: one Fusion component per printed part.
4. **Modeling steps**: sketch plane, geometry, constraints, features.
5. **Assembly (joints)**: how the parts connect and move.
6. **Verify**: motion and interference checks before printing.
7. **Printing**: orientation, supports, settings and hardware per part.

## Hardware used across the set

- Metal pins are optional: every pin hole is sized for a printed pin
  **or** an M3 screw / 3 mm rod. Printed pins are the default.
- Some builds suggest M3 × 10–20 screws and M3 nuts.
- Nothing else is required.
