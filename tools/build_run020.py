#!/usr/bin/env python3
"""Explicit authoring tool for N2–4 only. Saved scenes remain normally editable.

Run intentionally: python3 tools/build_run020.py. Never regenerates the human N1.
Coordinates are world pixels; a floor/feet height is the top of the surface the player
stands on. RUN-020 reprise (Claude): every terrain block, coin, actor, hazard and item is
authored explicitly per level; see docs/RUN-020_ASSET_MANIFEST_02.md for the dimensioned
plans, routes and budgets. Player reference for the gaps below: jump apex ~42 px, double
jump ~75 px, 105 px/s; authored rises stay <= 32 px (single) or <= 64 px (double), flat
gaps <= 48 px (single) or <= 96 px (double).
"""
import base64
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parents[1]
BOTTOM = 320  # Terrain fill limit; the void line is void_y = 304.


class Plan:
	"""One level: terrain operations then gameplay placements, in authoring order."""

	def __init__(self, name, file, number, width, cost, next_file, top=-224):
		self.name, self.file, self.number = name, file, number
		self.width, self.cost, self.next, self.top = width, cost, next_file, top
		self.ops = []  # ("fill"|"carve", x0, x1, y0, y1)
		self.coins = []  # (x, centre_y, route)
		self.enemies = []  # (family, x, feet_y, left, right)
		self.hazards = []  # (family, x, y, props)
		self.items = []  # (name, scene, x, y, parent, props)
		self.optional_cost = 0
		self.routes = {}  # route -> description, for the manifest and the checker

	# --- terrain (multiples of 16)
	def ground(self, x0, x1, y):
		"""Solid column from the walkable surface y down to the bottom of the world."""
		self.ops.append(("fill", x0, x1, y, BOTTOM))

	def block(self, x0, x1, y0, y1):
		self.ops.append(("fill", x0, x1, y0, y1))

	def slab(self, x0, x1, y, h=16):
		"""Floating ledge whose walkable surface is y."""
		self.ops.append(("fill", x0, x1, y, y + h))

	def carve(self, x0, x1, y0, y1):
		self.ops.append(("carve", x0, x1, y0, y1))

	# --- placements
	def coin(self, x, feet, route="main", lift=0):
		"""Coin resting 12 px above a surface, or `lift` px higher on a jump arc."""
		self.coins.append((x, feet - 12 - lift, route))

	def enemy(self, family, x, feet, left=-24, right=24):
		self.enemies.append((family, x, feet, left, right))

	def hazard(self, family, x, y, **props):
		self.hazards.append((family, x, y, props))

	def item(self, name, scene, x, y, parent="Items", **props):
		self.items.append((name, scene, x, y, parent, props))

	def cells(self):
		cells = set()
		for op, x0, x1, y0, y1 in self.ops:
			assert all(v % 16 == 0 for v in (x0, x1, y0, y1)), (self.name, x0, x1, y0, y1)
			assert 0 <= x0 < x1 <= self.width and y0 < y1, (self.name, x0, x1, y0, y1)
			for x in range(x0 // 16, x1 // 16):
				for y in range(y0 // 16, y1 // 16):
					if op == "fill":
						cells.add((x, y))
					else:
						cells.discard((x, y))
		return cells


def exit_frame(p):
	"""Shared end of every level: gate on the 144 floor, closed above, exit area behind."""
	w = p.width
	p.ground(w - 208, w, 144)
	# The exit gate closes the sole floor aperture; double-jump cannot bypass it.
	p.block(w - 144, w - 128, -224, 48)


# ============================================================================ N2
def blight_town():
	p = Plan("BlightTown", "blight_town", 2, 3840, 18, "black_forrest")
	p.routes = {
		"main": "street, mandatory",
		"f1_up": "F1 ramparts over the canal breach (coins, jumps, Purple)",
		"f1_down": "F1 towpath and vault (common chest, Red pack, canal gap, timed spikes)",
		"f2_up": "F2 church causeway (one coin, gap and fixed spikes, safer)",
		"f2_down": "F2 plague lane under the causeway (minor potion, trapdoor pit, Reds)",
	}
	# S1 Outskirts 0-1008: crate, first spikes, raised yard, timed spikes.
	p.ground(0, 480, 144)
	p.block(176, 224, 112, 144)
	p.ground(480, 704, 112)
	p.ground(704, 1008, 144)
	p.coin(112, 144)
	p.coin(200, 112)
	p.coin(352, 144, lift=24)
	p.coin(432, 144, lift=34)  # over the first spikes
	p.coin(592, 112)
	p.coin(784, 144)
	p.coin(944, 144)
	p.enemy("slime", 320, 144, -56, 56)
	p.enemy("purple", 624, 112, -48, 48)
	p.hazard("spikes", 432, 144)
	p.hazard("retractable_spikes", 864, 144, initial_phase=0.0)
	# F1 Canal breach 1008-1600: one tower, two crossings that rejoin on the east quay.
	p.ground(1008, 1056, 112)  # tower top: the fork is visible from here
	# Up: broken ramparts (falling lands on the towpath, never in the void).
	p.slab(1088, 1136, 80)
	p.slab(1168, 1264, 48)
	p.slab(1312, 1376, 48)
	p.slab(1424, 1520, 64)
	p.slab(1552, 1600, 96)
	p.coin(1032, 112)
	p.coin(1344, 48, "f1_up", lift=20)
	p.coin(1584, 96, "f1_up")
	p.enemy("purple", 1472, 64, -24, 24)
	# Down: towpath, vault with the chest, canal gap, east steps.
	p.ground(1056, 1104, 192)
	p.ground(1104, 1312, 240)
	p.block(1136, 1296, 176, 192)  # vault ceiling
	p.ground(1360, 1504, 240)
	p.ground(1504, 1552, 208)
	p.ground(1552, 1600, 176)
	p.item("CommonChest", "reward_chest", 1232, 240)
	p.enemy("red_slime", 1184, 240, -32, 32)
	p.enemy("red_slime", 1280, 240, -16, 16)
	p.hazard("retractable_spikes", 1440, 240, initial_phase=0.8)
	p.coin(1392, 240, "f1_down", lift=16)
	p.coin(1488, 240, "f1_down")
	# S2 Market 1600-2400: first trapdoor (spiked pit), well, crates, then the market hall
	# roof is the only way on (a mandatory climb of 80 px), dropping back to the street.
	p.ground(1600, 1712, 144)
	p.ground(1712, 1744, 208)  # trapdoor pit floor (escape by double jump)
	p.ground(1744, 2400, 144)
	p.hazard("trapdoor", 1728, 144)
	p.hazard("spikes", 1728, 208)
	p.block(1792, 1840, 112, 144)  # well
	p.block(1904, 1952, 112, 144)  # crates
	p.block(1984, 2304, 64, 144)  # market hall, roof at 64
	p.coin(1664, 144)
	p.coin(1728, 144, lift=28)
	p.coin(1816, 112)
	p.coin(2048, 64)
	p.coin(2240, 64)
	p.enemy("slime", 2144, 64, -56, 56)
	p.enemy("red_slime", 2352, 144, -32, 32)
	# F2 Church hill 2400-3168: causeway above (potion, fixed spikes, gap), plague lane
	# below (more coins, timed spikes in a sunk stretch, trapdoor pit, Red); both reach
	# the square. Falling from the causeway lands in the lane, never in the void.
	p.ground(2400, 3168, 144)  # lane floor
	p.ground(2448, 2496, 112)  # first terrace (shared)
	p.slab(2528, 2576, 80)
	p.slab(2576, 2752, 48, 32)  # causeway west
	p.slab(2800, 3104, 48, 32)  # causeway east, 48 px gap above the lane
	p.carve(2640, 2768, 144, 176)  # sunk stretch of the lane
	p.carve(2928, 2960, 144, 208)  # trapdoor pit
	p.coin(2472, 112)
	p.coin(2672, 48, "f2_up")
	p.hazard("spikes", 2896, 48)
	p.item("MinorPotion", "minor_potion", 2976, 38)
	p.enemy("purple", 3040, 48, -40, 40)
	p.hazard("retractable_spikes", 2672, 176, initial_phase=0.0)
	p.hazard("retractable_spikes", 2736, 176, initial_phase=1.2)
	p.hazard("trapdoor", 2944, 144)
	p.hazard("spikes", 2944, 208)
	p.coin(2816, 144, "f2_down")
	p.coin(3056, 144, "f2_down")
	p.enemy("red_slime", 2864, 144, -32, 40)
	# S3 Plague square 3168-3632 and exit: Bloated arena with a firing ledge.
	p.ground(3168, 3632, 144)
	p.slab(3312, 3392, 80)
	p.coin(3216, 144)
	p.coin(3352, 80)
	p.coin(3600, 144)
	p.enemy("bloated_slime", 3456, 144, -72, 72)
	exit_frame(p)
	return p


# ============================================================================ N3
def black_forest():
	p = Plan("BlackForest", "black_forrest", 3, 4320, 25, "forbidden_graveyard")
	p.routes = {
		"main": "forest floor and ravine, mandatory",
		"f1_up": "F1 canopy branches (coins, Archer and Purple, falling lands below)",
		"f1_down": "F1 bramble undergrowth (common chest between plants, Red, Warrior)",
		"f2_up": "F2 high oak crowns up to y -48 (minor potion, Archer, Green)",
		"f2_down": "F2 root gully at y 240 (trapdoor over a plant pit, timed spikes, Red, Warrior)",
	}
	# S1 Forest edge 0-1200: log, plant hollow, fixed spikes, first void gap, timed spikes.
	p.ground(0, 400, 144)
	p.block(224, 288, 128, 144)  # fallen log
	p.ground(400, 560, 176)  # hollow
	p.ground(560, 832, 144)
	p.ground(880, 1200, 144)  # 48 px void gap before it
	p.hazard("poison_plant", 480, 176)
	p.hazard("spikes", 688, 144)
	p.hazard("retractable_spikes", 1120, 144, initial_phase=0.4)
	for x, feet, lift in ((128, 144, 0), (256, 128, 0), (480, 176, 40), (640, 144, 0), (688, 144, 34),
						  (856, 144, 30), (976, 144, 0), (1088, 144, 0), (1168, 144, 0)):
		p.coin(x, feet, lift=lift)
	p.enemy("slime", 320, 144, -48, 48)
	p.enemy("purple", 784, 144, -48, 32)
	p.enemy("red_slime", 1024, 144, -48, 48)
	# F1 1200-2048: from the trunk, canopy branches or the undergrowth below them.
	p.ground(1200, 1248, 112)  # trunk, fork point
	p.coin(1224, 112)
	for x0, x1, y in ((1280, 1344, 80), (1376, 1472, 48), (1520, 1584, 16), (1616, 1760, 16),
					  (1808, 1872, 48), (1920, 2000, 80)):
		p.slab(x0, x1, y)
	p.coin(1440, 48, "f1_up")
	p.coin(1552, 16, "f1_up")
	p.coin(1840, 48, "f1_up")
	p.enemy("purple", 1408, 48, -24, 24)
	p.enemy("skeleton_archer", 1704, 16, 0, 0)
	p.ground(1248, 1440, 144)
	p.ground(1440, 1632, 176)  # bramble hollow
	p.ground(1632, 2048, 144)
	p.block(1664, 1760, 96, 144)  # fallen giant log
	p.hazard("poison_plant", 1488, 176)
	p.hazard("poison_plant", 1584, 176)
	p.item("CommonChest", "reward_chest", 1536, 176)
	p.coin(1344, 144, "f1_down")
	p.coin(1792, 144, "f1_down")
	p.coin(1984, 144, "f1_down")
	p.enemy("red_slime", 1712, 96, -24, 24)
	p.enemy("skeleton_warrior", 1888, 144, -48, 48)
	# S2 Ravine 2048-2800: Shield, void ravine on three stumps under turret fire.
	p.ground(2048, 2224, 144)
	p.item("MagicShield", "magic_shield", 2176, 132)
	p.ground(2272, 2304, 128)
	p.ground(2352, 2384, 96)
	p.ground(2432, 2464, 112)
	p.ground(2512, 2688, 128)
	p.ground(2688, 2800, 96)  # east bluff
	p.hazard("turret", 2678, 112, direction="Vector2(-1, 0)")
	p.coin(2096, 144)
	p.coin(2248, 144, lift=30)
	p.coin(2368, 96)
	p.coin(2448, 112)
	p.coin(2600, 128)
	p.coin(2744, 96)
	# F2 2800-3760: oak crowns climbing to y -48, or the root gully at y 240.
	for x0, x1, y in ((2848, 2912, 48), (2960, 3024, 16), (3056, 3168, -16), (3216, 3280, -48),
					  (3328, 3424, -16), (3472, 3536, 16), (3584, 3648, 48)):
		p.slab(x0, x1, y)
	p.item("MinorPotion", "minor_potion", 3248, -58)
	p.coin(2992, 16, "f2_up")
	p.coin(3504, 16, "f2_up")
	p.enemy("skeleton_archer", 3112, -16, 0, 0)
	p.enemy("slime", 3376, -16, -24, 24)
	p.ground(2800, 2848, 176)
	p.ground(2848, 3664, 240)  # root gully
	p.carve(3072, 3104, 240, 288)  # plant pit under the trapdoor
	p.ground(3664, 3712, 192)
	p.ground(3712, 3760, 160)
	p.hazard("retractable_spikes", 2944, 240, initial_phase=0.0)
	p.hazard("trapdoor", 3088, 240)
	p.hazard("poison_plant", 3088, 288)
	p.hazard("retractable_spikes", 3328, 240, initial_phase=0.9)
	p.coin(3008, 240, "f2_down")
	p.coin(3536, 240, "f2_down")
	p.enemy("red_slime", 3200, 240, -48, 48)
	p.enemy("skeleton_warrior", 3456, 240, -48, 48)
	# S3 Clearing 3760-4176: mound with an Archer, plant, Warrior before the gate.
	p.ground(3760, 4112, 144)
	p.block(3856, 3936, 112, 144)
	p.hazard("poison_plant", 4000, 144)
	p.enemy("skeleton_archer", 3896, 112, 0, 0)
	p.enemy("skeleton_warrior", 4064, 144, -32, 32)
	for x, feet, lift in ((3792, 144, 0), (3880, 112, 0), (4000, 144, 38), (3960, 144, 0), (4056, 144, 0), (4144, 144, 0)):
		p.coin(x, feet, lift=lift)
	exit_frame(p)
	return p


# ============================================================================ N4
def forbidden_graveyard():
	p = Plan("ForbiddenGraveyard", "forbidden_graveyard", 4, 4800, 32, "")
	p.optional_cost = 4
	p.routes = {
		"main": "graveyard, skull field, bell tower and mechanism, Chud arena, mandatory",
		"f1_up": "F1 ruined chapel (Sorcerer; optional 4-coin door and HP bonus room)",
		"f1_down": "F1 sunken crypt yard at y 240 (common chest, trapdoor pit, Red, Warrior)",
		"f2_up": "F2 graveyard surface (minor potion, plants, turret, Archer on the mausoleum)",
		"f2_down": "F2 catacomb tunnel at y 240 (trapdoor pit, timed spikes, two Warriors)",
	}
	# S1 Cemetery gate 0-1040: graves, an arched mausoleum whose roof leads to the secret
	# wall (n4_secret_01); the room above the path holds the rare chest and major potion.
	p.ground(0, 1040, 144)
	p.block(208, 240, 128, 144)  # grave
	p.block(352, 400, 112, 144)  # step
	p.block(400, 544, 64, 144)  # mausoleum, roof at 64
	p.carve(400, 544, 96, 144)  # arch: the path passes under it
	p.slab(544, 768, 64)  # secret room floor
	p.block(544, 768, 16, 32)  # secret room ceiling
	p.block(752, 768, 32, 64)  # back wall
	p.block(976, 1024, 112, 144)  # tall grave
	p.item("SecretWall", "secret_wall", 568, 64, "Exploration", secret_id="n4_secret_01")
	p.item("MajorPotion", "major_potion", 640, 52)
	p.item("RareChest", "reward_chest", 704, 64, kind="rare")
	p.hazard("spikes", 816, 144)
	for x, feet, lift in ((128, 144, 0), (224, 128, 0), (304, 144, 0), (376, 112, 0), (472, 64, 0),
						  (608, 144, 0), (704, 144, 0), (816, 144, 34), (928, 144, 0), (1000, 112, 0)):
		p.coin(x, feet, lift=lift)
	p.enemy("red_slime", 288, 144, -48, 48)
	p.enemy("skeleton_warrior", 880, 144, -40, 40)
	p.enemy("skeleton_archer", 1000, 112, 0, 0)
	# F1 1040-2000: ruined chapel above (HP room behind the paid door, crossed by its
	# roof) or the sunken crypt yard below; falling from the chapel lands in the yard.
	p.slab(1088, 1152, 96)
	p.slab(1200, 1296, 64)
	p.slab(1344, 1696, 48, 32)  # chapel floor
	p.block(1536, 1696, -16, 0)  # HP room ceiling, its top is the way on
	p.block(1680, 1696, 0, 48)  # HP room back wall
	p.item("CoinDoor", "secondary_door", 1544, 48, "Exploration", coin_cost=4)
	p.item("HpBonus", "hp_bonus", 1640, 36, bonus_id="n4_hp_01")
	p.slab(1744, 1808, 16)
	p.slab(1856, 1936, 48)
	p.coin(1248, 64, "f1_up")
	p.coin(1776, 16, "f1_up")
	p.enemy("blight_sorcerer", 1456, 48, -40, 40)
	p.ground(1040, 1088, 176)
	p.ground(1088, 1952, 240)  # crypt yard
	p.carve(1680, 1712, 240, 288)
	p.ground(1952, 2000, 192)
	p.hazard("trapdoor", 1696, 240)
	p.hazard("spikes", 1696, 288)
	p.item("CommonChest", "reward_chest", 1824, 240)
	p.coin(1376, 240, "f1_down")
	p.coin(1904, 240, "f1_down")
	p.enemy("red_slime", 1264, 240, -48, 48)
	p.enemy("skeleton_warrior", 1536, 240, -48, 48)
	# S2 Skull field 2000-2720: Shield, tombs and a raised crypt with a Sorcerer under
	# the autonomous swarm zone (480x240, four slots per attempt).
	p.ground(2000, 2720, 144)
	p.block(2160, 2192, 128, 144)
	p.block(2304, 2432, 96, 144)
	p.block(2528, 2560, 112, 144)
	p.item("MagicShield", "magic_shield", 2048, 132)
	p.item("SkullSwarm", "skull_swarm", 2368, 48, "Exploration", zone_size="Vector2(480, 240)")
	p.enemy("blight_sorcerer", 2384, 96, -32, 32)
	for x, feet, lift in ((2096, 144, 0), (2176, 128, 0), (2240, 144, 0), (2280, 144, 30), (2336, 96, 0),
						  (2416, 96, 0), (2480, 144, 0), (2544, 112, 0), (2624, 144, 0), (2688, 144, 0), (2144, 144, 0)):
		p.coin(x, feet, lift=lift)
	# F2 2720-3600: graveyard surface (exposed) or the catacomb tunnel beneath it.
	p.ground(2720, 3680, 144)
	p.carve(2784, 2832, 144, 240)  # entry shaft (jumped over on the surface)
	p.carve(2832, 3488, 176, 240)  # catacomb, 64 px high
	p.carve(3488, 3536, 144, 240)  # exit shaft with a ledge
	p.block(3504, 3536, 192, 208)
	p.block(2944, 3008, 112, 144)  # grave
	p.block(3392, 3440, 80, 144)  # mausoleum
	p.hazard("poison_plant", 3120, 144)
	p.hazard("poison_plant", 3328, 144)
	p.hazard("turret", 3382, 112, direction="Vector2(-1, 0)", initial_phase=0.6)
	p.item("MinorPotion", "minor_potion", 3200, 134)
	p.coin(2976, 112, "f2_up")
	p.coin(3264, 144, "f2_up")
	p.enemy("skeleton_archer", 3416, 80, 0, 0)
	p.coin(3600, 144)  # shared again after both F2 routes
	p.carve(3040, 3072, 240, 288)
	p.hazard("trapdoor", 3056, 240)
	p.hazard("spikes", 3056, 288)
	p.hazard("retractable_spikes", 3232, 240, initial_phase=0.5)
	p.coin(2896, 240, "f2_down")
	p.coin(3440, 240, "f2_down")
	p.enemy("skeleton_warrior", 3152, 240, -48, 48)
	p.enemy("skeleton_warrior", 3376, 240, -40, 40)
	# S3 3680-4656: bell tower climb to the button (required, no payment), back down
	# through the mechanism door, then the Chud arena with a firing ledge before the gate.
	p.ground(3680, 4800, 144)
	p.block(3776, 3840, 96, 144)
	p.slab(3888, 3952, 48)
	p.slab(4000, 4096, 0)
	p.item("MechanismButton", "mechanism_button", 4048, 0, "Exploration",
		   target_door='NodePath("../MechanismDoor")')
	p.block(4160, 4176, -224, 96)  # partition: the door closes the only aperture
	p.item("MechanismDoor", "secondary_door", 4168, 144, "Exploration", coin_locked=False)
	p.slab(4320, 4400, 80)
	p.hazard("retractable_spikes", 4224, 144, initial_phase=0.2)
	for x, feet, lift in ((3744, 144, 0), (3808, 96, 0), (3856, 144, 0), (3920, 48, 0), (4072, 0, 0), (4096, 144, 0),
						  (4272, 144, 0), (4360, 80, 0), (4560, 144, 0), (4624, 144, 0)):
		p.coin(x, feet, lift=lift)
	p.enemy("red_slime", 3712, 144, -24, 48)
	p.enemy("skeleton_warrior", 3968, 144, -48, 64)
	p.enemy("skeleton_archer", 3920, 48, 0, 0)
	p.enemy("chud_blob", 4480, 144, -64, 64)
	exit_frame(p)
	return p


LEVELS = [blight_town, black_forest, forbidden_graveyard]
SCENES = {"slime": "slime", "purple": "slime"}


class Scene:
	def __init__(self):
		self.resources = {}
		self.shapes = []
		self.nodes = []

	def resource(self, path, kind="PackedScene"):
		key = (kind, path)
		if key not in self.resources:
			self.resources[key] = str(len(self.resources) + 1)
		return f'ExtResource("{self.resources[key]}")'

	def shape(self, width, height):
		key = f"shape{len(self.shapes)}"
		self.shapes.append(f'[sub_resource type="RectangleShape2D" id="{key}"]\nsize = Vector2({width}, {height})')
		return f'SubResource("{key}")'

	def node(self, name, parent=None, node_type="Node2D", instance=None, **props):
		attrs = [f'name="{name}"']
		if instance:
			attrs.append(f"instance={instance}")
		else:
			attrs.append(f'type="{node_type}"')
		if parent is not None:
			attrs.append(f'parent="{parent}"')
		self.nodes.append("[node " + " ".join(attrs) + "]\n" +
						  "\n".join(f"{k} = {v}" for k, v in props.items()))

	def item(self, name, file, x, y, parent=".", **props):
		self.node(name, parent, instance=self.resource(f"scenes/{file}.tscn"),
				  position=f"Vector2({x}, {y})", **props)

	def text(self):
		refs = [f'[ext_resource type="{kind}" path="res://{path}" id="{key}"]'
				for (kind, path), key in self.resources.items()]
		return "\n\n".join([f'[gd_scene load_steps={1 + len(refs) + len(self.shapes)} format=4]',
							  *refs, *self.shapes, *self.nodes]) + "\n"


def value(v):
	if isinstance(v, bool):
		return "true" if v else "false"
	if isinstance(v, float):
		return repr(v)
	if isinstance(v, str) and not v.startswith(("Vector2", "NodePath", '"')):
		return f'"{v}"'
	return str(v)


def hazard_names(p):
	counts, names = {}, []
	for family, *_ in p.hazards:
		counts[family] = counts.get(family, 0) + 1
		base = {"trapdoor": "Trapdoor", "turret": "Turret"}.get(family, family.title().replace("_", ""))
		# Historical names: the first trapdoor is "Trapdoor", the rest are numbered.
		if family == "trapdoor":
			names.append(base if counts[family] == 1 else f"{base}{counts[family]}")
		else:
			names.append(f"{base}{counts[family]}")
	return names


def build(p, out_dir=None):
	scene = Scene()
	width = p.width
	scene.node(p.name, script=scene.resource("scripts/level.gd", "Script"),
			   process_mode=3, world_level=p.number,
			   camera_bounds=f"Rect2(0, {p.top}, {width}, {BOTTOM - 16 - p.top})",
			   tutorial_rewards_enabled="false", void_y="304.0",
			   next_level_scene=f'"res://scenes/{p.next}.tscn"' if p.next else '""')
	scene.node("Backdrop", ".", script=scene.resource("scripts/campaign_backdrop.gd", "Script"),
			   world_level=p.number)
	scene.node("Decor", ".", script=scene.resource("scripts/campaign_decor.gd", "Script"),
			   world_level=p.number, level_width=float(width))
	cells = p.cells()
	# Godot format 4 stores a uint16 format-version header, then 12-byte cells.
	# Match the existing Godot-saved N1; omitting the header corrupts every cell.
	# Atlas row 0 marks an exposed top, row 1 the body (as the first RUN-020 pass).
	tile_bytes = struct.pack("<H", 0) + b"".join(
		struct.pack("<hhhhhh", x, y, 0, 8, 1 if (x, y - 1) in cells else 0, 0)
		for (x, y) in sorted(cells))
	scene.node("Terrain", ".", "TileMapLayer",
			   tile_map_data=f'PackedByteArray("{base64.b64encode(tile_bytes).decode()}")',
			   tile_set=scene.resource("assets/kingdom_tileset.tres", "TileSet"))
	scene.node("TerrainSkin", ".", script=scene.resource("scripts/campaign_terrain_skin.gd", "Script"),
			   world_level=p.number)
	scene.node("WorldBounds", ".", "StaticBody2D", collision_layer=1, collision_mask=0)
	height = BOTTOM - 16 - p.top  # 528 for the default top: walls span top..void line
	middle = (p.top + BOTTOM - 16) // 2
	for i, (x, y, w, h) in enumerate([(-8, middle, 16, height), (width + 8, middle, 16, height),
									  (width / 2, p.top - 8, width, 16)]):
		scene.node(f"Shape{i}", "WorldBounds", "CollisionShape2D",
				   position=f"Vector2({x}, {y})", shape=scene.shape(w, h))
	scene.item("Player", "player", 48, 144)
	for group in ("Coins", "Enemies", "Hazards", "Items", "Exploration"):
		scene.node(group, ".", process_mode=1)
	for i, (x, y, _route) in enumerate(p.coins):
		scene.item(f"Coin{i + 1:02}", "coin", x, y, "Coins")
	for i, (family, x, y, left, right) in enumerate(p.enemies):
		props = dict(patrol_left=f"{float(left)!r}", patrol_right=f"{float(right)!r}")
		if family == "purple":
			props["variant"] = 1
		scene.item(f"Enemy{i + 1:02}", SCENES.get(family, family), x, y, "Enemies", **props)
	for name, (family, x, y, props) in zip(hazard_names(p), p.hazards):
		scene.item(name, family, x, y, "Hazards", **{k: value(v) for k, v in props.items()})
	for name, file, x, y, parent, props in p.items:
		scene.item(name, file, x, y, parent, **{k: value(v) for k, v in props.items()})
	scene.item("GoldGate", "gold_gate", width - 144, 144, COST=p.cost)
	scene.node("ExitArea", ".", "Area2D", collision_layer=0, collision_mask=2)
	scene.node("Shape", "ExitArea", "CollisionShape2D",
			   position=f"Vector2({width - 64}, 96)", shape=scene.shape(48, 96))
	scene.node("HUD", ".", instance=scene.resource("scenes/hud.tscn"), process_mode=3)
	scene.node("Music", ".", "AudioStreamPlayer",
			   stream=scene.resource("assets/music/music_slice_dreamer.ogg", "AudioStream"),
			   volume_db="-24.0", bus='&"Music"')
	scene.node("Ambient", ".", "AudioStreamPlayer",
			   stream=scene.resource(f'assets/sounds/run020/amb_{p.file}.ogg', "AudioStream"),
			   volume_db="-8.0", bus='&"Ambient"')
	assert len(p.coins) - p.optional_cost >= p.cost
	target = Path(out_dir or ROOT / "scenes") / (p.file + ".tscn")
	target.write_text(scene.text())
	print(f"{target.name}: {len(cells)} terrain cells, {len(p.coins)} coins, "
		  f"{len(p.enemies)} fixed enemies, {len(p.hazards)} hazards; exit {p.cost}, optional {p.optional_cost}")


if __name__ == "__main__":
	import sys
	out = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else None
	for level in LEVELS:
		build(level(), out)
