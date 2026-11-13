"""Three-cell 18650 pack (3S).

Three single 18650 holders, each with its cell and its two clips, side by
side along y in one row, for three cells in series. A plain strip across
each end face joins them, with six M1.2 x 6 countersunk screws at each end,
flush in the strip, into the holders' tap holes. Two tabs on each strip's
top edge stick out away from the holders, with countersinks on top for
screws going in downward. Every piece comes from the
parts library through load_library, so the pack follows any change to the
holder, the strip or the screw.

The summary's interference lists each screw against its holder: that is the
screw's 1.2 mm shank forming its thread in the 0.95 mm tap hole, as intended.

Assumptions where the description is silent:
- the holders all stand the same way up, on z = 0, cells along x, centred
  along x and y; the cells' series wiring is not modelled;
- the strip at -x is the +x strip turned half a turn about z, so its
  countersinks face outward at both ends and its tabs stay on top;
- the screws in the strips' tabs (which fix something to the pack) are left
  out; their holes are exported (tab_holes, tab_top) for whatever they hold.
"""
import cadquery as cq

holder = load_library("battery_holders/single_18650_holder")  # body, cell and clips
body = load_library("battery_holders/single_18650_holder/body")  # length
strip = load_library("brackets/strip_3x1")  # points, thickness, column_ys
screw = load_library("hardware/m1_2x6_countersunk")  # standing up: tip on z = 0

end = body.length / 2  # each end face, from the centre

result = cq.Assembly(name="pack_3x1")
for c, y in enumerate(strip.column_ys, start=1):
    result.add(holder.result, name=f"holder_{c}", loc=cq.Location((0, y, 0)))

strip_color = cq.Color(0.30, 0.33, 0.38)
screw_color = cq.Color(0.70, 0.70, 0.72)
for side, label in ((1, "front"), (-1, "back")):
    turn = 0 if side == 1 else 180  # about z: the back strip faces -x
    result.add(strip.result, name=f"strip_{label}",
               loc=cq.Location(cq.Vector(side * end, 0, 0), cq.Vector(0, 0, 1), turn),
               color=strip_color)
    # each screw: head flush with the strip's front, along x into the holders
    head = side * (end + strip.thickness)
    for i, (y, z) in enumerate(strip.points, start=1):
        result.add(screw.result, name=f"screw_{label}_{i}",
                   loc=cq.Location(cq.Vector(head - side * screw.length, side * y, z),
                                   cq.Vector(0, 1, 0), side * 90),
                   color=screw_color)

# the strips' tab holes in the pack's own coordinates: (x, y) of each, and
# the tabs' top, where the countersinks open
tab_top = strip.tab_top
tab_holes = [(side * (end + strip.tab_hole_x), side * (y + dy))
             for side in (1, -1) for y in strip.tab_ys for dy in strip.tab_hole_offsets]

regions = {}

if "show_object" in globals():  # CQ-editor (load_part runs under the CAD tool only)
    show_object(result, name="pack_3x1")
