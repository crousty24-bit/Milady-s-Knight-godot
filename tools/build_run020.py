#!/usr/bin/env python3
"""Explicit authoring tool for N2–4 only. Saved scenes remain normally editable.

Run intentionally: python3 tools/build_run020.py. Never regenerates the human N1.
Coordinates are world pixels, floor heights refer to the player's feet.
"""
import base64
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parents[1]
LEVELS = [
    dict(name="BlightTown", file="blight_town", number=2, width=2800, cost=18,
         next="black_forrest", count=24,
         runs=[(0, 576, 144), (640, 960, 144), (960, 1120, 112),
               (1120, 1456, 144), (1456, 1488, 176), (1520, 1568, 176),
               (1568, 1856, 144), (1936, 2240, 144), (2240, 2368, 128),
               (2368, 2800, 144)], trap=1504,
         enemies=[("slime", 352), ("purple", 784), ("red_slime", 1040),
                  ("slime", 1312), ("purple", 1744), ("red_slime", 2080),
                  ("bloated_slime", 2464)],
         spikes=[464, 1648], retract=[864, 2160], plants=[], turrets=[],
         chest=688, potion=2304, shield=None),
    dict(name="BlackForest", file="black_forrest", number=3, width=3200, cost=25,
         next="forbidden_graveyard", count=32,
         runs=[(0, 512, 144), (592, 864, 144), (864, 1024, 128),
               (1024, 1232, 144), (1232, 1264, 176), (1296, 1376, 176),
               (1376, 1664, 144), (1664, 1808, 112), (1808, 2016, 144),
               (2112, 2464, 144), (2464, 2640, 128), (2640, 3200, 144)],
         trap=1280,
         enemies=[("slime", 336), ("purple", 704), ("red_slime", 944),
                  ("skeleton_warrior", 1120), ("skeleton_archer", 1488),
                  ("red_slime", 1744), ("skeleton_warrior", 1920),
                  ("purple", 2224), ("skeleton_archer", 2544),
                  ("skeleton_warrior", 2896)],
         spikes=[432, 2312], retract=[784, 2784], plants=[1584, 2712],
         turrets=[(2384, 130)], chest=640, potion=1856, shield=1408),
    dict(name="ForbiddenGraveyard", file="forbidden_graveyard", number=4,
         width=3600, cost=32, next="", count=40,
         runs=[(0, 896, 144), (976, 1696, 144), (1696, 1728, 176),
               (1760, 1824, 176), (1824, 2096, 144), (2096, 2240, 112),
               (2240, 2432, 144), (2528, 3136, 144), (3136, 3280, 128),
               (3280, 3600, 144)], trap=1744,
         enemies=[("red_slime", 352), ("skeleton_warrior", 816),
                  ("skeleton_archer", 1072), ("red_slime", 1584),
                  ("skeleton_warrior", 1952), ("blight_sorcerer", 2160),
                  ("skeleton_archer", 2352), ("red_slime", 2608),
                  ("skeleton_warrior", 2960), ("skeleton_archer", 3088),
                  ("chud_blob", 3376)],
         spikes=[416, 1888], retract=[1632, 3024], plants=[2288, 3224],
         turrets=[(2048, 130)], chest=1008, potion=2560, shield=1840),
]


def floor_at(level, x):
    for start, end, y in level["runs"]:
        if start <= x < end:
            return y
    if abs(x - level["trap"]) <= 16:
        return 176
    return None


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


def build(level):
    scene = Scene()
    width = level["width"]
    scene.node(level["name"], script=scene.resource("scripts/level.gd", "Script"),
               process_mode=3, world_level=level["number"],
               camera_bounds=f"Rect2(0, -224, {width}, 528)",
               tutorial_rewards_enabled="false", void_y="304.0",
               next_level_scene=f'"res://scenes/{level["next"]}.tscn"' if level["next"] else '""')
    scene.node("Backdrop", ".", script=scene.resource("scripts/campaign_backdrop.gd", "Script"),
               world_level=level["number"])
    scene.node("Decor", ".", script=scene.resource("scripts/campaign_decor.gd", "Script"),
               world_level=level["number"], level_width=float(width))
    cells = {}

    def rectangle(start, end, top, bottom):
        assert all(v % 16 == 0 for v in (start, end, top, bottom))
        for x in range(start // 16, end // 16):
            for y in range(top // 16, bottom // 16):
                cells[x, y] = 0 if y == top // 16 else 1

    for start, end, top in level["runs"]:
        rectangle(start, end, top, 320)
    # The exit gate closes the sole floor aperture; double-jump cannot bypass it.
    rectangle(width - 144, width - 128, -224, 48)
    if level["number"] == 4:
        # Floating branch steps leave the main route below unobstructed.
        # First rise is 48px (within a standard jump), then 32px and 16px.
        for left in (448, 1184):
            rectangle(left, left + 32, 96, 112)
            rectangle(left + 32, left + 64, 64, 80)
            rectangle(left + 64, left + 112, 48, 64)
        # Secret room (32px opening), fully sealed above/below/behind.
        rectangle(560, 784, 48, 64)
        rectangle(560, 784, 0, 16)
        rectangle(768, 784, 16, 48)
        # Coin room: door sits in a 48px-high enclosed branch.
        rectangle(1296, 1520, 48, 64)
        rectangle(1296, 1520, -16, 0)
        rectangle(1504, 1520, 0, 48)
        # Required mechanism: world-height partition + 48px floor aperture.
        rectangle(2800, 2816, -224, 96)
        rectangle(2672, 2912, 80, 96)
    # Godot format 4 stores a uint16 format-version header, then 12-byte cells.
    # Match the existing Godot-saved N1; omitting the header corrupts every cell.
    tile_bytes = struct.pack("<H", 0) + b"".join(
        struct.pack("<hhhhhh", x, y, 0, 8, atlas_y, 0)
        for (x, y), atlas_y in sorted(cells.items()))
    scene.node("Terrain", ".", "TileMapLayer",
               tile_map_data=f'PackedByteArray("{base64.b64encode(tile_bytes).decode()}")',
               tile_set=scene.resource("assets/kingdom_tileset.tres", "TileSet"))
    scene.node("TerrainSkin", ".", script=scene.resource("scripts/campaign_terrain_skin.gd", "Script"),
               world_level=level["number"])
    scene.node("WorldBounds", ".", "StaticBody2D", collision_layer=1, collision_mask=0)
    for i, (x, y, w, h) in enumerate([(-8, 40, 16, 528), (width + 8, 40, 16, 528),
                                     (width / 2, -232, width, 16)]):
        scene.node(f"Shape{i}", "WorldBounds", "CollisionShape2D",
                   position=f"Vector2({x}, {y})", shape=scene.shape(w, h))
    scene.item("Player", "player", 48, 144)
    for group in ("Coins", "Enemies", "Hazards", "Items", "Exploration"):
        scene.node(group, ".", process_mode=1)
    # Walkable coin route: no future ability or branch purchase is required.
    avoid = level["spikes"] + level["retract"] + level["plants"] + [level["trap"]]
    candidates = [x for x in range(128, width - 200, 32)
                  if floor_at(level, x) is not None and floor_at(level, x) <= 144
                  and all(abs(x - hazard) >= 40 for hazard in avoid)]
    indices = [round(i * (len(candidates) - 1) / (level["count"] - 1))
               for i in range(level["count"])]
    assert len(set(indices)) == level["count"]
    for i, index in enumerate(indices):
        x = candidates[index]
        scene.item(f"Coin{i + 1:02}", "coin", x, floor_at(level, x) - 12, "Coins")
    for i, (family, x) in enumerate(level["enemies"]):
        props = dict(patrol_left="-24.0", patrol_right="24.0")
        if family == "purple":
            family = "slime"
            props["variant"] = 1
        scene.item(f"Enemy{i + 1:02}", family, x, floor_at(level, x), "Enemies", **props)
    for family, positions in [("spikes", level["spikes"]),
                              ("retractable_spikes", level["retract"]),
                              ("poison_plant", level["plants"])]:
        for i, x in enumerate(positions):
            scene.item(f"{family.title().replace('_', '')}{i + 1}", family, x,
                       floor_at(level, x), "Hazards")
    scene.item("Trapdoor", "trapdoor", level["trap"], 176, "Hazards")
    for i, (x, y) in enumerate(level["turrets"]):
        scene.item(f"Turret{i + 1}", "turret", x, y, "Hazards", direction="Vector2(-1, 0)")
    scene.item("CommonChest", "reward_chest", level["chest"], floor_at(level, level["chest"]), "Items")
    scene.item("MinorPotion", "minor_potion", level["potion"], floor_at(level, level["potion"]) - 10, "Items")
    if level["shield"]:
        scene.item("MagicShield", "magic_shield", level["shield"], 132, "Items")
    if level["number"] == 4:
        scene.item("SecretWall", "secret_wall", 568, 48, "Exploration", secret_id='"n4_secret_01"')
        scene.item("RareChest", "reward_chest", 720, 48, "Items", kind='"rare"')
        scene.item("MajorPotion", "major_potion", 640, 36, "Items")
        scene.item("CoinDoor", "secondary_door", 1304, 48, "Exploration", coin_cost=4)
        scene.item("HpBonus", "hp_bonus", 1424, 36, "Items", bonus_id='"n4_hp_01"')
        scene.item("MechanismDoor", "secondary_door", 2808, 144, "Exploration", coin_locked="false")
        scene.item("MechanismButton", "mechanism_button", 2640, 144, "Exploration",
                   target_door='NodePath("../MechanismDoor")')
        scene.item("SkullSwarm", "skull_swarm", 2016, 96, "Exploration",
                   zone_size="Vector2(480, 240)")
    scene.item("GoldGate", "gold_gate", width - 144, 144, COST=level["cost"])
    scene.node("ExitArea", ".", "Area2D", collision_layer=0, collision_mask=2)
    scene.node("Shape", "ExitArea", "CollisionShape2D",
               position=f"Vector2({width - 64}, 96)", shape=scene.shape(48, 96))
    scene.node("HUD", ".", instance=scene.resource("scenes/hud.tscn"), process_mode=3)
    scene.node("Music", ".", "AudioStreamPlayer",
               stream=scene.resource("assets/music/music_slice_dreamer.ogg", "AudioStream"),
               volume_db="-24.0", bus='&"Music"')
    scene.node("Ambient", ".", "AudioStreamPlayer",
               stream=scene.resource(f'assets/sounds/run020/amb_{level["file"]}.ogg', "AudioStream"),
               volume_db="-8.0", bus='&"Ambient"')
    optional_cost = 4 if level["number"] == 4 else 0
    assert level["count"] - optional_cost >= level["cost"]
    target = ROOT / "scenes" / (level["file"] + ".tscn")
    target.write_text(scene.text())
    print(f"{target.name}: {len(cells)} terrain cells, {level['count']} coins, "
          f"{len(level['enemies'])} fixed enemies; exit {level['cost']}, optional {optional_cost}")


if __name__ == "__main__":
    for level in LEVELS:
        build(level)
