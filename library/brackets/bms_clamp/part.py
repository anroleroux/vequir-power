"""BMS edge clamp.

A small flat plate that sits on a clamping beam's post, level with the top
of the BMS, and reaches over the board's edge to hold it down on the beam.
An M1.2 x 3 countersunk screw through it, flush with its top, goes into the
post's tap hole. Its size comes from the beam's post and the screw through
load_library, so it follows a change to either.

Assumptions where the description is silent:
- 1.0 mm thick: the screw's 0.72 mm head sits flush, leaving 0.28 mm under
  the countersink, and its 3 mm length then reaches 2 mm into the post's
  2.7 mm tap hole, short of the beam's underside;
- as wide as the beam (3.4 mm), so the 2.4 mm countersink keeps 0.5 mm of
  material to either side;
- the hole is over the post's tap hole; behind it the plate keeps the same
  0.5 mm round the countersink, so it overhangs the post's outer end by
  about 0.4 mm;
- towards the board it covers the post, the 0.2 mm gap and 0.6 mm of the
  board's edge: the board's parts start about 0.7 mm in from its edges at
  the beams;
- the countersink and clearance hole are the end strip's (1.3 mm through,
  matching the head with 0.05 mm radial clearance);
- flat underneath: post and board top are level, so it bears on both;
- modelled with the hole on the z axis, standing on z = 0 (its underside),
  the board towards +x.
"""
import cadquery as cq

beam = load_library("brackets/clamp_beam")  # post_length, board_clearance, width
strip = load_library("brackets/end_strip")  # countersunk_hole, countersink_radius
screw = load_library("hardware/m1_2x3_countersunk")  # length

# parameters, in mm
thickness = 1.0  # along z
margin = 0.5  # round the countersink, to the plate's sides and back
board_overlap = 0.6  # over the board's edge, along x
width = beam.width  # along y

back = strip.countersink_radius + margin  # behind the hole, along -x
reach = beam.post_length / 2 + beam.board_clearance + board_overlap  # in front, along +x
length = back + reach

result = (cq.Workplane("XY", origin=((reach - back) / 2, 0, 0))
          .box(length, width, thickness, centered=(True, True, False)))
for cut in strip.countersunk_hole((0, 0, thickness), (0, 0, 1), thickness):
    result = result.cut(cq.Workplane("XY").add(cut))

regions = {
    "top": result.faces(">Z"),  # the screw head flush here
    "bottom": result.faces("<Z"),  # on the post and the board's edge
    "countersink": result.faces("%CONE"),
}

if "show_object" in globals():  # CQ-editor
    show_object(result, name="part")
