"""Clamping beam for the 3S BMS.

A flat beam that screws onto two of the end strip's pillars, with the BMS
resting on it: two of them carry the board, each stretching from one side of
the board to the other. Its length comes from the BMS's width, and its holes
from the strip's pillars and the M1.2 countersunk screw, all through
load_library, so it follows a change to any of them. Past each of the
board's edges the beam goes on far enough to take an M1.2 tap hole, and
there it rises by the board's thickness to a post level with the board's
top, for a clamp that will screw on and hold the board's edge (the clamps
themselves are left for later).

Assumptions where the description is silent:
- the beam runs across the board, centred on it; the board rests on its
  middle, 20 mm long, with 0.2 mm clearance to the posts at either side;
- each post is the strip's pillar profile along the beam: the 0.95 mm M1.2
  tap drill plus a 0.6 mm wall each side, 2.15 mm, and the beam's width
  across it; it stands 1.2 mm above the beam's top (the board's
  thickness), so its top is level with the board's top; the tap hole runs
  down through the post and the beam (2.7 mm), the thread formed in it;
- so the beam is 24.7 mm long overall;
- 1.5 mm thick, as the strip: an M1.2 x 6 screw, flush in its countersink,
  then reaches 4.5 mm into the pillar's 5.3 mm tap hole;
- 3.4 mm wide: the 2.4 mm countersink with 0.5 mm of material either side
  (wider than the 2.15 mm pillar it sits on);
- two countersunk holes, as far apart as the pillars they sit on (7.85 mm) and
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
width = 2 * (strip.countersink_radius + margin)  # along y
board_clearance = 0.2  # from the board's edges to the posts, along x
post_length = strip.pillar_side  # along x: the pillars' M1.2 tap hole and wall
post_height = bms.pcb_t  # above the beam's top: level with the board's top
post_tap = strip.pillar_tap  # M1.2
seat = bms.width + 2 * board_clearance  # between the posts, along x
length = seat + 2 * post_length  # overall
post_xs = [side * (seat + post_length) / 2 for side in (-1, 1)]
post_points = [(x, 0) for x in post_xs]

hole_pitch = strip.pillar_zs[-1] - strip.pillar_zs[0]  # the pillars' spacing, across the strip
hole_xs = [-hole_pitch / 2, hole_pitch / 2]

result = (cq.Workplane("XY").box(length, width, thickness, centered=(True, True, False))
          .union(cq.Workplane("XY", origin=(0, 0, thickness)).pushPoints(post_points)
                 .rect(post_length, width).extrude(post_height))
          .cut(cq.Workplane("XY").pushPoints(post_points)
               .circle(post_tap / 2).extrude(thickness + post_height)))
for x in hole_xs:
    for cut in strip.countersunk_hole((x, 0, thickness), (0, 0, 1), thickness):
        result = result.cut(cq.Workplane("XY").add(cut))

regions = {
    "top": result.faces("+Z").filter(  # where the board rests, between the posts
        lambda f: abs(f.Center().z - thickness) < 1e-6),
    "post_tops": result.faces(">Z"),  # level with the board's top, for the clamps
    "post_holes": result.faces("%CYLINDER").filter(  # the clamps' M1.2 tap holes
        lambda f: abs(f.BoundingBox().zlen - thickness - post_height) < 1e-6),
    "bottom": result.faces("<Z"),  # on the pillars
    "countersinks": result.faces("%CONE"),
}

if "show_object" in globals():  # CQ-editor
    show_object(result, name="part")
