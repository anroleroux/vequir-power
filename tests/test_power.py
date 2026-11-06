"""The power parts: the single 18650 holder, the six-cell pack and their brackets.

Cells, clips, screws and the BMS come from vequir-standard, which ``libraries.txt``
expects beside this repository (CI clones it there).
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

from cad.catalog import discover_all
from cad.part import build_part

ROOT = Path(__file__).resolve().parents[1]
LIBRARY = ROOT / "library"


def _summary(result):
    assert result.ok, result.error
    return json.loads(result.files["summary"].read_text())


def test_the_library_holds_the_holders_packs_and_brackets():
    assert sorted(e.designation for e in discover_all(ROOT / "products")) == [
        "battery_holders/pack_3x1", "battery_holders/pack_3x2",
        "battery_holders/single_18650_holder", "battery_holders/single_18650_holder/body",
        "brackets/bms_clamp", "brackets/clamp_beam", "brackets/end_strip", "brackets/strip_3x1"]


def test_the_single_18650_holder_cradles_its_cell(tmp_path):
    """The cell lies along x in the body's two rib cradles, inside the open
    frame, clear of every wall."""
    summary = _summary(build_part(LIBRARY / "battery_holders/single_18650_holder/assembly.py",
                                  tmp_path / "out"))
    assert summary["interference"] == []
    body, cell, positive, negative = summary["components"]
    # a clip at each end, from vequir-standard, its spring leaf just off the cell's end
    assert [positive["name"], negative["name"]] == [
        "single_18650_holder/clip_positive", "single_18650_holder/clip_negative"]
    assert positive["bounding_box_min"][0] == pytest.approx(32.7)
    assert negative["bounding_box_max"][0] == pytest.approx(-32.7)
    assert positive["bounding_box_max"][2] < body["bounding_box_max"][2]  # below the rim
    assert {c["b"] for c in summary["contacts"]} == {positive["name"], negative["name"]}
    assert cell["name"].endswith("/battery")
    assert [cell["bounding_box_max"][i] - cell["bounding_box_min"][i] for i in range(3)] == \
        pytest.approx([65.0, 18.4, 18.4])
    assert cell["bounding_box_min"][2] == pytest.approx(1.0)  # on the cradles' bottoms
    for i in range(3):  # inside the body
        assert body["bounding_box_min"][i] <= cell["bounding_box_min"][i]
        assert cell["bounding_box_max"][i] <= body["bounding_box_max"][i]


def test_the_single_18650_holder_takes_m12_screws_in_its_triangles(tmp_path):
    """Four M1.2 tap holes, one in each bottom triangle at each end, entirely in
    material, far enough in that a 2.3 mm countersunk head clears the side and
    the bottom."""
    summary = _summary(build_part(LIBRARY / "battery_holders/single_18650_holder/body/part.py",
                                  tmp_path / "out"))
    assert summary["regions"]["screw_holes"]["count"] == 4
    width = summary["bounding_box"]["size"][1]
    foot = math.sqrt(2) * (18.4 / 2 + 0.1 + 1.0) - (1.0 + 18.4 / 2 + 0.1)  # the 45 face meets z = 0
    inset = (width / 2 - foot) * (2 - math.sqrt(2)) / 2  # the triangle's inradius
    assert inset - 2.3 / 2 == pytest.approx(0.676, abs=1e-3)  # head clear of side and bottom


def test_the_end_strip_spans_three_holders_and_two_rows(tmp_path):
    """The strip: three holders long, twelve countersinks for the M1.2 screws,
    thin enough that a 6 mm screw flush in it reaches 4.5 mm into the holder."""
    strip = _summary(build_part(LIBRARY / "brackets/end_strip/part.py", tmp_path / "strip"))
    # 1.5 mm strip plus the tabs, 3.4 mm out past its front, and the pillars 0.4 mm past them
    assert strip["bounding_box"]["size"] == pytest.approx([1.5 + 3.4 + 0.4, 3 * 21.0, 10.0])
    assert strip["regions"]["countersinks"]["count"] == 12
    assert strip["regions"]["tab_countersinks"]["count"] == 4  # two per tab
    # the tabs sit between the cells, on the joints between holders (y = +/-10.5),
    # their holes a quarter of the 10 mm tab either side of each joint
    import cadquery as cq
    shape = cq.Shape.importBrep(str(tmp_path / "strip" / "part.brep"))
    tab_cones = [f for f in shape.Faces()
                 if f.geomType() == "CONE" and f.BoundingBox().zlen < 1.5]
    assert sorted(round(f.Center().y, 3) for f in tab_cones) == \
        pytest.approx([-13.0, -8.0, 8.0, 13.0])
    # eight square pillars, 2.15 mm across, at the middle slot's ends and the outer
    # slots' inside ends, flush with the strip's edges, each with a 0.95 mm M1.2 tap hole
    assert strip["regions"]["pillar_tops"]["count"] == 8
    assert strip["regions"]["pillar_holes"]["count"] == 8
    # three material-saving slots, 10 x 6 mm with round ends, through the 1.5 mm strip
    full = 1.5 * 3 * 21.0 * 10.0 + 2 * 3.4 * 10.0 * 1.5 + 8 * 2.15 ** 2 * 5.3
    assert strip["volume_mm3"] < full - 3 * (4 * 6 + math.pi * 9) * 1.5


def test_the_strip_3x1_spans_three_holders_in_one_row(tmp_path):
    """The strip: three holders long, 5 mm tall, six countersinks for the M1.2
    screws, 1.5 mm thick so a 6 mm screw flush in it reaches 4.5 mm in, and two
    tabs on its top edge, 3.4 mm out past its front, countersunk on top."""
    strip = _summary(build_part(LIBRARY / "brackets/strip_3x1/part.py", tmp_path / "strip"))
    assert strip["bounding_box"]["size"] == pytest.approx([1.5 + 3.4, 3 * 21.0, 5.0])
    assert strip["regions"]["countersinks"]["count"] == 6
    assert strip["regions"]["tab_countersinks"]["count"] == 4  # two per tab


def test_the_3s_pack_joins_three_holders_with_two_strips(tmp_path):
    """Three holders in a row, a strip and six screws at each end: the only
    overlaps are the 12 screws forming their threads in the holders."""
    summary = _summary(build_part(LIBRARY / "battery_holders/pack_3x1/assembly.py", tmp_path / "out"))
    names = [c["name"] for c in summary["components"]]
    assert sum("holder_" in n for n in names) == 3
    assert sum("strip_" in n for n in names) == 2
    assert sum("screw_" in n for n in names) == 12
    contacts = {(c["a"].split("/")[-1], c["b"].split("/")[-1]) for c in summary["contacts"]}
    for c in (1, 2, 3):
        assert {(f"holder_{c}", "strip_front"), (f"holder_{c}", "strip_back")} <= contacts
    clashes = summary["interference"]
    assert len(clashes) == 12
    assert all("holder_" in c["a"] and "screw_" in c["b"] for c in clashes)


def test_the_clamp_beam_spans_the_bms_on_two_pillars(tmp_path):
    """1.5 mm thick, two M1.2 countersinks 7.85 mm apart (the pillars' spacing),
    and past the BMS's edges (0.2 mm clear) a 2.15 mm post at each end, as tall
    as the board is thick, with an M1.2 tap hole for a clamp."""
    beam = _summary(build_part(LIBRARY / "brackets/clamp_beam/part.py", tmp_path / "beam"))
    assert beam["bounding_box"]["size"] == pytest.approx([20.0 + 2 * (0.2 + 2.15), 3.4, 1.5 + 1.2])
    assert beam["regions"]["countersinks"]["count"] == 2
    assert beam["regions"]["post_tops"]["count"] == 2
    assert beam["regions"]["post_holes"]["count"] == 2


def test_the_bms_clamp_covers_the_post_and_the_board_edge(tmp_path):
    """1 mm thick, as wide as the beam, one M1.2 countersink over the post's tap
    hole, reaching 0.6 mm over the board's edge."""
    clamp = _summary(build_part(LIBRARY / "brackets/bms_clamp/part.py", tmp_path / "clamp"))
    assert clamp["bounding_box"]["size"] == pytest.approx([1.7 + 2.15 / 2 + 0.2 + 0.6, 3.4, 1.0])
    assert clamp["regions"]["countersink"]["count"] == 1


def test_the_pack_joins_six_holders_with_two_strips(tmp_path):
    """Six holders in two rows of three, a strip and twelve screws at each end,
    two clamping beams screwed onto the front strip's pillars, the BMS on the
    beams, and a clamp screwed onto each of the beams' four posts:
    the only overlaps are the 24 screws forming their threads in the holders."""
    summary = _summary(build_part(LIBRARY / "battery_holders/pack_3x2/assembly.py", tmp_path / "out"))
    names = [c["name"] for c in summary["components"]]
    assert sum("upper_" in n or "lower_" in n for n in names) == 6
    assert sum("strip_" in n for n in names) == 2
    assert sum("screw_" in n for n in names) == 24 + 4 + 4
    assert sum("clamp_" in n and "screw" not in n for n in names) == 4
    assert sum("beam_" in n and "screw" not in n for n in names) == 2
    assert sum("bms" in n for n in names) == 1
    # the 64 mm BMS overhangs the 63 mm pack by 0.5 mm each side
    assert summary["bounding_box"]["size"][1:] == pytest.approx([64.0, 40.0])
    # each beam sits on two of the front strip's pillars, and the BMS on both beams
    contacts = {(c["a"].split("/")[-1], c["b"].split("/")[-1]) for c in summary["contacts"]}
    assert {("strip_front", "beam_1"), ("strip_front", "beam_2"),
            ("beam_1", "bms"), ("beam_2", "bms")} <= contacts
    # each clamp bears on its post and 0.6 mm of the board's edge
    for i in (1, 2):
        for j in (1, 2):
            assert {(f"beam_{i}", f"clamp_{i}_{j}"), (f"clamp_{i}_{j}", "bms")} <= contacts
    clashes = summary["interference"]
    # each screw forming its thread: 24 in the holders, 4 in the front strip's
    # pillars and 4 in the beams' posts
    assert len(clashes) == 32
    assert all("screw_" in c["b"] for c in clashes)
    assert sum("strip_front" in c["a"] and "screw_beam_" in c["b"] for c in clashes) == 4
    assert sum("beam_" in c["a"] and "screw_clamp_" in c["b"] for c in clashes) == 4
