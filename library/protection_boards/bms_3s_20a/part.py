"""3S Li-ion BMS, 20 A.

DIY Electronics' Li-Ion/LiPo 3S cell pack protection module: a printed
circuit board carrying the protection chip and the MOSFETs that switch the
pack's negative lead, with solder pads for the pack and the load.

Assumptions where the description is silent:
- the 64 x 20 x 3.4 mm is the board and its parts: a 1.6 mm FR-4 board with
  every part on top, the tallest 1.8 mm high (SOP-8 MOSFETs);
- eight SOP-8 MOSFETs (5 x 6 x 1.8 mm over their leads) in two rows of four
  along the middle of the board, the 20 A path shared between them;
- the protection chip is a smaller SOP-8 (5 x 4 x 1.5 mm) between the
  balance pads and the MOSFETs;
- a large B- pad (for the pack's negative) across the -x end and a large P-
  pad (for the load and charger's negative) across the +x end, each
  5 x 16 mm; the pack's positive goes straight to the load and passes the
  board only through the B+ balance pad;
- three balance pads, B1, B2 and B+ (the taps at 3.7, 7.4 and 11.1 V), each
  3 x 2.5 mm, along the +y edge inside the B- pad;
- pads are 0.1 mm thick copper; the parts' sizes and places are typical, not
  measured;
- x runs along the board, y across it, z up; the board is centred on x and
  y and its underside is on z = 0.
"""
import cadquery as cq

# the board, in mm
length = 64.0  # along x
width = 20.0  # along y
height = 3.4  # overall, board and parts
pcb_t = 1.6  # board thickness

# the parts
mosfet = (5.0, 6.0, 1.8)  # SOP-8 over its leads: along x, along y, high
mosfets_per_row = 4
mosfet_pitch = 7.0  # along x, centre to centre
mosfet_rows = 8.0  # the two rows, centre to centre along y
chip = (5.0, 4.0, 1.5)  # the protection chip, SOP-8: along x, along y, high

# the pads
power_pad = (5.0, 16.0)  # B- and P-: along x, along y
pad_margin = 1.0  # power pads from the board's ends
balance_pad = (3.0, 2.5)  # B1, B2, B+: along x, along y
balance_pitch = 4.0  # along x, centre to centre
balance_margin = 1.0  # from the +y edge
pad_t = 0.1  # copper thickness

board = cq.Workplane("XY").box(length, width, pcb_t, centered=(True, True, False))
top = cq.Workplane("XY", origin=(0, 0, pcb_t))

b_minus_x = -length / 2 + pad_margin + power_pad[0] / 2
p_minus_x = length / 2 - pad_margin - power_pad[0] / 2
power_pads = (
    top.pushPoints([(b_minus_x, 0), (p_minus_x, 0)])
    .rect(*power_pad)
    .extrude(pad_t)
)

balance_x0 = b_minus_x + power_pad[0] / 2 + 1.0 + balance_pad[0] / 2  # just inside B-
balance_y = width / 2 - balance_margin - balance_pad[1] / 2
balance_pads = (
    top.pushPoints([(balance_x0 + i * balance_pitch, balance_y) for i in range(3)])
    .rect(*balance_pad)
    .extrude(pad_t)
)

chip_x = balance_x0 + balance_pitch  # under B2, nearer the middle
chip_y = -width / 2 + 1.5 + chip[1] / 2
ic = (
    cq.Workplane("XY", origin=(chip_x, chip_y, pcb_t))
    .box(*chip, centered=(True, True, False))
)

mosfets_x0 = (p_minus_x - power_pad[0] / 2 + chip_x + chip[0] / 2) / 2 \
    - (mosfets_per_row - 1) * mosfet_pitch / 2  # the block centred between chip and P-
fets = (
    top.pushPoints([(mosfets_x0 + i * mosfet_pitch, s * mosfet_rows / 2)
                    for i in range(mosfets_per_row) for s in (-1, 1)])
    .rect(mosfet[0], mosfet[1])
    .extrude(mosfet[2])
)

result = board.union(power_pads).union(balance_pads).union(ic).union(fets)

pad_top = pcb_t + pad_t


def pads_at(xs, y):
    """The top faces of the pads centred at (x, y) for each x."""
    return result.faces("+Z").filter(
        lambda f: abs(f.Center().z - pad_top) < 1e-6 and abs(f.Center().y - y) < 1e-6
        and any(abs(f.Center().x - x) < 1e-6 for x in xs))


regions = {
    "b_minus_pad": pads_at([b_minus_x], 0),  # the pack's negative
    "p_minus_pad": pads_at([p_minus_x], 0),  # the load and charger's negative
    "balance_pads": pads_at([balance_x0 + i * balance_pitch for i in range(3)], balance_y),  # B1, B2, B+
    "bottom": result.faces("<Z"),
}

if "show_object" in globals():  # CQ-editor
    show_object(result, name="part")
