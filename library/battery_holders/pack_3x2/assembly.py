"""Six-cell 18650 pack.

Six single 18650 holders, each with its cell and its two clips: three side by
side along y, in two rows bottom to bottom, the lower row turned upside down
about x. An end strip across each end face joins them, with twelve M1.2 x 6
countersunk screws at each end, flush in the strip, into the holders' tap
holes. Two clamping beams screw onto the front strip's pillars, one across
each of two pairs (the middle slot's -y end and the +y outer slot's inside
end), with an M1.2 x 6 countersunk screw into each pillar, and the 3S BMS
rests on the beams, which stretch from one side of it to the other; a
little clamp on each of the beams' four posts, with an M1.2 x 3 screw,
holds the board's edges down. Every piece comes from the parts library
through load_library, so the pack follows any change to the holder, the
strip or the screw.

The summary's interference lists each screw against its holder or, for the
beams' four, against the front strip's pillars, or, for the clamps' four,
against the beams' posts: that is the screw's 1.2 mm shank forming its
thread in the 0.95 mm tap hole, as intended.

Assumptions where the description is silent:
- the pack stands on z = 0 on the lower row's open tops, the joint between
  the rows at the holders' height; centred along x and y;
- the strip at -x is the +x strip turned half a turn about z, so its tabs
  stay at the bottom and stick out away from the holders at both ends;
- the screws in the strips' tabs (which fix the pack to something else) are
  left out; the tabs' footprints and holes are exported (tab_z, tab_top,
  tab_length, tab_width, tab_centres, tab_holes) for what the pack is fixed to;
- the beams run along z, across the board: the -y one on the pillars at
  the middle slot's -y end (y = -5), the +y one on the pillars at the +y
  outer slot's inside end (y = +16); the other four pillars are left free;
  each beam is centred on its pillars, their countersinks facing away from
  the holders, under the board;
- the BMS stands on the beams, its parts facing away from the holders, its
  length along y and its width along z, centred on the strip (y = 0, the
  joint between the rows); its MOSFET and B- end is at -y; the clamps that
  hold it are on the beams' posts;
- a clamp on each post (four in all), reaching over the board's edge, held
  by an M1.2 x 3 countersunk screw flush in its top, into the post.
"""
import cadquery as cq

holder = load_library("battery_holders/single_18650_holder")  # body, cell and clips
body = load_library("battery_holders/single_18650_holder/body")  # length, width, height
strip = load_library("battery_holders/end_strip")  # points, thickness, joint
screw = load_library("fasteners/m1_2x6_countersunk")  # standing up: tip on z = 0
bms = load_library("protection_boards/bms_3s_20a")  # lying flat, its underside on z = 0
beam = load_library("battery_holders/clamp_beam")  # along x, its countersinks on top
clamp = load_library("battery_holders/bms_clamp")  # its hole on the z axis, the board towards +x
short_screw = load_library("fasteners/m1_2x3_countersunk")  # standing up: tip on z = 0

joint = body.height  # where the two rows' bottoms meet
end = body.length / 2  # each end face, from the centre

result = cq.Assembly(name="pack_3x2")
for c, y in enumerate(strip.column_ys):
    result.add(holder.result, name=f"upper_{c + 1}", loc=cq.Location((0, y, joint)))
    result.add(holder.result, name=f"lower_{c + 1}",
               loc=cq.Location(cq.Vector(0, y, joint), cq.Vector(1, 0, 0), 180))

strip_color = cq.Color(0.30, 0.33, 0.38)
screw_color = cq.Color(0.70, 0.70, 0.72)
strip_z = joint - strip.joint  # the strip's own z = 0
for side, label in ((1, "front"), (-1, "back")):
    turn = 0 if side == 1 else 180  # about z: the back strip faces -x
    result.add(strip.result, name=f"strip_{label}",
               loc=cq.Location(cq.Vector(side * end, 0, strip_z), cq.Vector(0, 0, 1), turn),
               color=strip_color)
    # each screw: head flush with the strip's front, along x into the holders
    head = side * (end + strip.thickness)
    for i, (y, z) in enumerate(strip.points, start=1):
        result.add(screw.result, name=f"screw_{label}_{i:02d}",
                   loc=cq.Location(cq.Vector(head - side * screw.length, side * y, strip_z + z),
                                   cq.Vector(0, 1, 0), side * 90),
                   color=screw_color)

# the clamping beams on the front strip's pillars, along z, their tops (and the
# countersinks) facing +x; then the BMS on the beams: its x along y, its y
# along z and its z (up from its underside) along +x, away from the holders
inner = min(abs(y) for y in strip.pillar_ys)
# the beams' pillars: the middle slot's -y end, and the next pair out on +y
pillar_ys = [-inner, min(y for y in strip.pillar_ys if y > inner)]
pillar_z = strip_z + sum(strip.pillar_zs) / len(strip.pillar_zs)
beam_x = end + strip.pillar_top  # the beams' undersides, on the pillars' tops
beam_top = beam_x + beam.thickness
post_top = beam.thickness + beam.post_height  # in the beam's own coordinates
for i, y in enumerate(pillar_ys, start=1):
    beam_loc = cq.Location(cq.Vector(beam_x, y, pillar_z), cq.Vector(0, 1, 0), 90)
    result.add(beam.result, name=f"beam_{i}", loc=beam_loc, color=strip_color)
    # a clamp on each post, reaching in over the board's edge, and its screw
    for j, px in enumerate(beam.post_xs, start=1):
        turn = 180 if px > 0 else 0  # the clamp's +x towards the board
        result.add(clamp.result, name=f"clamp_{i}_{j}",
                   loc=beam_loc * cq.Location(cq.Vector(px, 0, post_top), cq.Vector(0, 0, 1), turn),
                   color=strip_color)
        result.add(short_screw.result, name=f"screw_clamp_{i}_{j}",
                   loc=beam_loc * cq.Location(
                       cq.Vector(px, 0, post_top + clamp.thickness - short_screw.length)),
                   color=screw_color)
    # a screw into each pillar: head flush with the beam's top, along -x
    for j, x in enumerate(beam.hole_xs, start=1):
        result.add(screw.result, name=f"screw_beam_{i}_{j}",
                   loc=cq.Location(cq.Vector(beam_top - screw.length, y, pillar_z - x),
                                   cq.Vector(0, 1, 0), 90),
                   color=screw_color)
result.add(bms.result, name="bms",
           loc=cq.Location(cq.Vector(beam_top, 0, pillar_z),
                           cq.Vector(1, 1, 1), 120),
           color=cq.Color(0.10, 0.45, 0.20))

# where the strips' tabs are, in the pack's own coordinates, for whatever the
# pack is fixed down to: each tab's footprint (its underside, a rectangle
# from the holders' end face out to the tab's tip) and its two holes
tab_z = strip_z  # the tabs' undersides
tab_top = strip_z + strip.tab_top  # the tabs' tops, where the countersinks open
tab_length = strip.thickness + strip.tab_reach  # each tab's footprint, along x
tab_width = strip.tab_width  # along y
tab_centres = [(side * (end + tab_length / 2), side * y)  # each footprint's centre
               for side in (1, -1) for y in strip.tab_ys]
tab_holes = [(side * (end + strip.tab_hole_x), side * (y + dy))
             for side in (1, -1) for y in strip.tab_ys for dy in strip.tab_hole_offsets]

regions = {}

if "show_object" in globals():  # CQ-editor (load_part runs under the CAD tool only)
    show_object(result, name="pack_3x2")
