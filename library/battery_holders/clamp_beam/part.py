"""Clamping beam for the 3S BMS.

A flat beam that screws onto two of the end strip's pillars, with the BMS
resting on it: two of them carry the board, each stretching from one side of
the board to the other. Its length comes from the BMS's width, and its holes
from the strip's pillars and the M1.2 countersunk screw, all through
load_library, so it follows a change to any of them. Clamps for its ends,
which will hold the board's edges, are left for later.

Assumptions where the description is silent:
- the beam runs across the board, as long as the board is wide (20 mm),
  ending flush with its edges; the clamps will be added at the ends;
- 1.5 mm thick, as the strip: an M1.2 x 6 screw, flush in its countersink,
  then reaches 4.5 mm into the pillar's 5.3 mm tap hole;
- 3.4 mm wide: the 2.4 mm countersink with 0.5 mm of material either side
  (wider than the 2.55 mm pillar it sits on);
- two countersunk holes, as far apart as the pillars they sit on (6 mm) and
  centred on the beam, sized as the strip's: 1.3 mm clearance and a
  countersink matching the head with 0.05 mm radial clearance, opening on
  the top, where the board rests, so the heads sit flush under it;
- square corners, no fillets;
- the beam lies along x, its width along y, standing on z = 0 (the face on
  the pillars), centred on x and y.
"""
import cadquery as cq

strip = load_library("battery_holders/end_strip")  # pillar_points, countersunk_hole
bms = load_library("protection_boards/bms_3s_20a")  # width

# parameters, in mm
thickness = 1.5  # along z
margin = 0.5  # round each countersink, to the beam's sides
length = bms.width  # along x, across the board
width = 2 * (strip.countersink_radius + margin)  # along y

pillar_zs = sorted({z for _, z in strip.pillar_points})
hole_pitch = pillar_zs[-1] - pillar_zs[0]  # the pillars' spacing, across the strip
hole_xs = [-hole_pitch / 2, hole_pitch / 2]

result = cq.Workplane("XY").box(length, width, thickness, centered=(True, True, False))
for x in hole_xs:
    for cut in strip.countersunk_hole((x, 0, thickness), (0, 0, 1), thickness):
        result = result.cut(cq.Workplane("XY").add(cut))

regions = {
    "top": result.faces(">Z"),  # where the board rests
    "bottom": result.faces("<Z"),  # on the pillars
    "countersinks": result.faces("%CONE"),
}

if "show_object" in globals():  # CQ-editor
    show_object(result, name="part")
