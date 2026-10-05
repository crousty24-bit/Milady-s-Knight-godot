"""Shared Milady's Knight palette (Art Bible: coloured blacks, cold/warm greys,
desaturated browns, very dark blues; saturated colours reserved for gameplay).

Every generator should pick from these ramps (dark -> light) so sprites made by
different scripts sit in the same world. Functional colours follow
docs/06_ART_BIBLE.md: gold = coins, red = danger/HP, violet = shards/corruption,
green = healing (and the Green Slime body), white/pale yellow = neutral VFX.
"""
from pixel import hexc

OUTLINE = hexc("17131b")
STEEL = [hexc(c) for c in ("2b303b", "48505f", "737c8c", "a6aebb", "dde2e8")]
STONE = [hexc(c) for c in ("1c1a21", "2a2830", "39363f", "4b4751", "625d67", "807a82")]
STONE_COOL = [hexc(c) for c in ("191c22", "252a31", "323841", "434a53", "596069", "757c84")]
MOSS = [hexc(c) for c in ("232c20", "34402a", "4b5a35", "687845")]
WOOD = [hexc(c) for c in ("2a1f1a", "3f2e24", "5a4030", "7a5a3c", "9a7a52")]
GOLD = [hexc(c) for c in ("4a3418", "8c6b2e", "c9a24a", "f0d27a", "fff4c4")]
BLOOD = [hexc(c) for c in ("3f0c13", "741620", "a8242c", "d8423a", "f07a5a")]
CORRUPT = [hexc(c) for c in ("21142a", "3c2148", "5e3470", "8a50a0", "c08ad4")]
SLIME_GREEN = [hexc(c) for c in ("1d3318", "35602a", "5e9a36", "98cc58", "d8f49a")]
SKY = [hexc(c) for c in ("0c0f15", "121720", "19202b", "212a37", "2b3646", "3a4759")]
MIST = [hexc(c) for c in ("4b5a6c", "66788c", "8a9cb0")]
EMBER = [hexc(c) for c in ("7a3a1a", "c46a2a", "ff9a3a", "ffd27a")]
