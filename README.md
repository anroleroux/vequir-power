# vequir-power

VequIR's battery holders and packs, and the protection boards that guard them, as a parts library for the
[CAD tool](https://github.com/anroleroux/vequir-standard/tree/main/tools/cad): the pack assemblies and the parts they are made of, written as
CadQuery B-rep code from plain-language descriptions and built and checked as
exact solids.

Product page: **[anroleroux.co.za/vequir-power](https://anroleroux.co.za/vequir-power/)**

## The library

| Designation | What |
| --- | --- |
| `battery_holders/single_18650_holder` | assembly: a holder body, its cell and a Keystone 1107-1 clip at each end |
| `battery_holders/single_18650_holder/body` | part: the open plastic frame that cradles one 18650 |
| `battery_holders/end_strip` | part: the strip across one end of six holders, with mounting tabs and four square M1.2 pillars |
| `battery_holders/pack_3x2` | assembly: six single holders, 3 × 2, joined by two end strips and 24 M1.2 screws, with the 3S BMS on the front strip's pillars |
| `protection_boards/bms_3s_20a` | part: DIY Electronics' 3S Li-ion protection module (BMS), 20 A, 64 × 20 × 3.4 mm |

```
library/<category>/category.md                     "# Title", then a blurb
library/<category>/<part>/part.py                  a part (with its description.md)
library/<category>/<assembly>/assembly.md          an assembly
library/<category>/<assembly>/assembly.py          optional: its parts placed together
library/<category>/<assembly>/<part>/part.py       its parts
```

The cell, the clips and the screws are standard parts from
[vequir-standard](https://github.com/anroleroux/vequir-standard), which
`libraries.txt` names (`../vequir-standard/library`): the body takes
`load_library("batteries/cell_18650")` and
`load_library("terminals/keystone_1107_1")` and sizes its cavity and clip
slots from them. [vequir-unit](https://github.com/anroleroux/vequir-unit)'s
PB6 places `battery_holders/pack_3x2`. A change here moves it: rebuild it
before pushing, and push on the same branch name.

Each item's page lists, under "Used in", the scripts that place it in the
other repositories: `used-by.txt` names vequir-unit's site, and the page
reads its `uses.json` (which every site publishes) in the browser. When
another repository starts using this library, add its site there.

## Working on it

Clone the libraries `libraries.txt` names beside this repository, install
the CAD tool (it comes with vequir-standard, under `tools/cad/`),
and run everything from this repository's root:

```bash
git clone https://github.com/anroleroux/vequir-standard ../vequir-standard
python -m venv .venv && source .venv/bin/activate
pip install -e "../vequir-standard/tools/cad[dev]"

python -m pytest -q tests                     # checks of the real parts
cad build library/battery_holders/pack_3x2      # one assembly
cad site --out results --site site      # every part, then the pages
```

`results/` and `site/` are build output and git-ignored. In a Claude Code
session, the `cad-part` skill (`.claude/skills/cad-part/`) takes
a designation plus modelling instructions through the same steps.

## CI and the product page

`.github/workflows/cad.yml` runs on every push to `main` and `claude/**`. It
clones the libraries this repository uses beside the checkout
(the branch of the same name when it exists there, else the default branch),
installs the CAD tool from vequir-standard's clone, runs the tests, builds every part, and deploys the site to GitHub Pages:
**anroleroux.co.za/vequir-power**, the product page. A part that fails to
build fails the job.
Settings → Pages → Source must be GitHub Actions.

Actions → **cad** → *Run workflow*, with `design` set to a part directory
holding a `description.md`, has Claude write its script; it needs the
`ANTHROPIC_API_KEY` repository secret.
