"""End strip for three single 18650 holders.

A flat strip that bolts across the end faces of three single 18650 holders
standing side by side in one row (a 3S pack), held by six M1.2 x 6
countersunk screws, one into each bottom triangle's threaded hole, the heads
flush in the strip. The holes are placed from the holder body's width and
screw positions, and the countersinks sized from the screw, both through
load_library, so the strip follows a change to either.

Two tabs come off the strip's top edge and turn 90 degrees to stick out
forward, away from the holders, like bent sheet-metal ears in plastic: one
in line with each joint between neighbouring holders, each long enough for
an M1.2 countersunk head, with two side by side. Their countersinks are on
the tabs' tops, so their screws go in downward. No pillars yet.

Assumptions where the description is silent:
- 1.5 mm thick, as the six-cell end strip: the 6 mm screw, flush in its
  countersink, then reaches 4.5 mm into the holder's 5 mm deep hole;
- 5 mm tall, from the holders' bottom (z = 0) up: the screws sit 1.83 mm up,
  so the 2.4 mm countersinks keep 0.63 mm to the bottom edge and about 2 mm
  to the top, and the strip stays well clear of the clips' solder lugs,
  about 9 mm up;
- three holders long (63 mm), the strip's ends flush with the outer holders'
  sides;
- the countersinks match the six-cell end strip: 0.05 mm radial clearance
  round the head, 90 degrees with its short cylindrical edge so the head sits
  flush, and 1.3 mm clearance holes through (ISO 273 fine, M1.2);
- the tabs are the strip's thickness thick (1.5 mm), their tops flush with
  the strip's top, running forward from the strip's back; each is 10 mm wide
  along y, centred on a joint between holders (y = +/-10.5), so they stay
  clear of the clips' solder lugs, which come out at the holders' centres;
  they keep 0.47 mm to the strip's countersinks below them;
- each tab reaches 3.4 mm out past the strip's front, as on the six-cell
  end strip: its holes' centres 1.7 mm from the strip's front and from the
  tab's end, so each 2.4 mm countersink keeps 0.5 mm of material to both;
  its two holes are a quarter and three quarters across it, along z, the
  countersinks opening on its top and the 1.3 mm clearance holes going down
  through it;
- square corners, no fillets, no material-saving holes;
- modelled as it is bolted on: its back on x = 0 against the holders' end
  faces, the countersinks opening on +x, centred across y, standing on z = 0.
"""
import cadquery as cq

holder = load_library("battery_holders/single_18650_holder/body")  # width, screw_y, screw_inset
screw = load_library("hardware/m1_2x6_countersunk")  # head and length

# parameters, in mm
columns = 3  # holders side by side, along y
height = 5.0  # along z, up from the holders' bottom
clearance_hole = 1.3  # M1.2, ISO 273 fine
head_clearance = 0.05  # radial, round the head in its countersink
engagement = 4.5  # of each screw in the holder's hole
thickness = screw.length - engagement  # along x

length = columns * holder.width  # along y
countersink_radius = screw.head_diameter / 2 + head_clearance
cone_height = countersink_radius - clearance_hole / 2  # 90 degrees: as deep as it narrows
column_ys = [(c - (columns - 1) / 2) * holder.width for c in range(columns)]
tab_margin = 0.5  # round each tab countersink, to the strip's front and to the tab's end
tab_width = 10.0  # along y
tab_thickness = thickness  # along z
tab_reach = 2 * (countersink_radius + tab_margin)  # out past the strip's front, along x
tab_ys = [(c + 0.5 - columns / 2) * holder.width for c in range(columns - 1)]  # the joints
tab_top = height  # flush with the strip's top; the countersinks open here
tab_bottom = tab_top - tab_thickness
tab_hole_x = thickness + tab_reach / 2
tab_hole_offsets = [-tab_width / 4, tab_width / 4]  # along y, from each tab's centre
points = [  # (y, z) of each screw, two per holder
    (column_y + side * holder.screw_y, holder.screw_inset)
    for column_y in column_ys
    for side in (1, -1)
]


def countersunk_hole(face_point, out, depth):
    """A clearance hole through ``depth`` of material, countersunk for the
    screw's head where it opens at ``face_point``, facing along ``out``: the
    head's short cylindrical edge at the face, then its 90 degree cone."""
    at, out = cq.Vector(*face_point), cq.Vector(*out)
    return [
        cq.Solid.makeCylinder(clearance_hole / 2, depth, at - out * depth, out),
        cq.Solid.makeCylinder(countersink_radius, screw.edge_height,
                              at - out * screw.edge_height, out),
        cq.Solid.makeCone(clearance_hole / 2, countersink_radius, cone_height,
                          at - out * (screw.edge_height + cone_height), out),
    ]


result = cq.Workplane("XY").box(thickness, length, height, centered=(False, True, False))
for y in tab_ys:
    result = result.union(cq.Workplane("XY", origin=(0, y, tab_bottom)).box(
        thickness + tab_reach, tab_width, tab_thickness, centered=(False, True, False)))
cuts = [c for y, z in points for c in countersunk_hole((thickness, y, z), (1, 0, 0), thickness)]
# the tabs' countersinks open on their tops: the screws go in downward
cuts += [c for y in tab_ys for dy in tab_hole_offsets
         for c in countersunk_hole((tab_hole_x, y + dy, tab_top), (0, 0, 1), tab_thickness)]
for cut in cuts:
    result = result.cut(cq.Workplane("XY").add(cut))

regions = {
    "back": result.faces("<X"),  # against the holders' end faces
    "front": result.faces("|X").filter(  # where the screw heads sit flush
        lambda f: abs(f.Center().x - thickness) < 1e-6),
    "countersinks": result.faces("%CONE").filter(  # into the holders, along x
        lambda f: f.BoundingBox().xlen < thickness and f.BoundingBox().zlen > thickness),
    "top": result.faces(">Z"),  # the strip's and the tabs' tops, one flat face
    "tab_countersinks": result.faces("%CONE").filter(  # on the tabs' tops, screwing down
        lambda f: f.BoundingBox().zlen < tab_thickness),
}

if "show_object" in globals():  # CQ-editor
    show_object(result, name="part")
