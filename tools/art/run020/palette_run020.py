"""Biome accents for N2-N4 (RUN-020), layered on the shared palette (tools/art/palette.py).

Art Bible docs/06: a common dark palette plus 1-2 dominant secondary colours per biome.
- N2 Blight Town: putrid brown / muted olive (proposal, human judgement pending).
- N3 Black Forest: night blue / cold green (docs/06).
- N4 Forbidden Graveyard: desaturated violet / spectral cyan (docs/06). Saturated cyan
  stays reserved for the Magic Shield and saturated violet for shards: the spectral
  ramp below is deliberately greyed and only used dim, in the background or as low-alpha light.
Every ramp runs dark -> light.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from pixel import hexc  # noqa: E402

# N2: rot (olive) and mud (putrid brown).
ROT = [hexc(c) for c in ("1c1b12", "2b2919", "3d3a22", "54502e", "6e683c")]
MUD = [hexc(c) for c in ("1e1814", "2c231c", "3d3026", "524031", "6a533e")]
# N3: night blue and cold green.
NIGHT = [hexc(c) for c in ("0a0e16", "0f1520", "151e2c", "1c283a", "26344a", "334460")]
PINE = [hexc(c) for c in ("111c1c", "182826", "213632", "2c4741", "3c5c54")]
SOIL = [hexc(c) for c in ("17161a", "211f24", "2c2930", "39353c", "4a454c")]
# N4: desaturated violet and greyed spectral cyan.
DUSK_VIOLET = [hexc(c) for c in ("17131d", "201a29", "2b2336", "382e45", "4a3e58", "5f5270")]
SPECTRAL = [hexc(c) for c in ("1f3236", "2c474c", "3f6066", "5a8186", "7ea4a6")]
