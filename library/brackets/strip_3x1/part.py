"""End strip for three single 18650 holders.

A flat strip that bolts across the end faces of three single 18650 holders
standing side by side in one row (a 3S pack), held by six M1.2 x 6
countersunk screws, one into each bottom triangle's threaded hole, the heads
flush in the strip. The holes are placed from the holder body's width and
screw positions, and the countersinks sized from the screw, both through
load_library, so the strip follows a change to either. No tabs or pillars
yet.

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
points = [  # (y, z) of each screw, two per holder
    (column_y + side * holder.screw_y, holder.screw_inset)
    for column_y in column_ys
    for side in (1, -1)
]


def countersunk_hole(y, z):
    """A clearance hole through the strip, countersunk on its front (+x) for
    the screw's head: the head's short cylindrical edge, then its 90 degree cone."""
    out = cq.Vector(1, 0, 0)
    at = cq.Vector(thickness, y, z)
    return [
        cq.Solid.makeCylinder(clearance_hole / 2, thickness, at - out * thickness, out),
        cq.Solid.makeCylinder(countersink_radius, screw.edge_height,
                              at - out * screw.edge_height, out),
        cq.Solid.makeCone(clearance_hole / 2, countersink_radius, cone_height,
                          at - out * (screw.edge_height + cone_height), out),
    ]


result = cq.Workplane("XY").box(thickness, length, height, centered=(False, True, False))
for y, z in points:
    for cut in countersunk_hole(y, z):
        result = result.cut(cq.Workplane("XY").add(cut))

regions = {
    "back": result.faces("<X"),  # against the holders' end faces
    "front": result.faces(">X"),  # where the screw heads sit flush
    "countersinks": result.faces("%CONE"),  # one per screw
}

if "show_object" in globals():  # CQ-editor
    show_object(result, name="part")
