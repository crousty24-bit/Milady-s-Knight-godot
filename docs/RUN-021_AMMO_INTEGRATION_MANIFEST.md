# RUN-021 ammo — integration manifest (scenes, HUD, placements)

Author: Claude `asset_integrator` contribution (intended Sonnet 5.5 Medium; actual model: `claude-sonnet-5-5`). No Godot execution, no git mutation. Complements `RUN-021_AMMO_ASSET_MANIFEST.md` (assets); native rendering, collision and route checks are owned by the root session.

## Files edited

- `scenes/ammo_crate.tscn`, `scenes/ammo_barrel.tscn`: added child `Art` (AnimatedSprite2D, `ammo_crate_frames.tres` / `ammo_barrel_frames.tres`, `centered = false`, `offset = (-16, -32)`, initial animation `intact_arrows`; `ammo_prop.gd` selects the family animation). Root, script, `Shape` and layer 16 / mask 0 unchanged.
- `scenes/ammo_pickup.tscn`: added `Arrows` and `Knives` (AnimatedSprite2D, `ammo_pickup_frames.tres`, animations `arrows` / `knives`, autoplay, centred, no offset); `Knives` hidden by default, `ammo_pickup.gd` toggles. Area shape/layers unchanged. The `collect` animation exists in the resource but is not wired (no script change).
- `scenes/hud.tscn`: new children of `Equipment` (see below); `Equipment` container grown; nothing else touched.
- `scenes/eidolon_vale.tscn`, `blight_town.tscn`, `black_forrest.tscn`, `forbidden_graveyard.tscn`: additive only — two `ext_resource` lines, `load_steps` +2 where present, and a new root child `AmmoSupplies` (Node2D) appended at the end with the instances below. No existing node, TileMap or property modified. `vertical_slice.tscn` not edited (N1 inherits; `AmmoSupplies` is added in `eidolon_vale.tscn` only).

Baselines: `work/run021/ammo/*-before.tscn` were byte-identical to the live level scenes before editing (checked with `diff`).

## HUD

| Node | Type | Local rect in `Equipment` | Notes |
| --- | --- | --- | --- |
| `AmmoPlate` | NinePatchRect | (0, 34)–(62, 49) | `ui_plate.png`, margins 4 (same as `RangedPlate`), hidden until `set_ammo` |
| `AmmoIcon` | TextureRect | (3, 36)–(15, 48) | AtlasTexture on `ui_ammo_icons.png`, region (0,0,12,12), hidden until `set_ammo` |
| `AmmoCount` | Label | (17, 37)–(60, 47) | existing HUD theme, text `00/00`, hidden until `set_ammo` |
| `AmmoFeedback` | Label | (66, 37)–(200, 47) | hidden, pale-yellow modulate, `hud.gd` sets text/shows/hides |

`Equipment` offsets: right 116 → 208, bottom 76 → 93 (absolute rect (8,44)–(208,93)).

**Adjustment within the approved HUD contribution:** the proposal placed `AmmoPlate` at local (94, 17)–(146, 32), right of `RangedPlate`. `scripts/equipment_slots.gd` `_layout()` widens the melee/ranged plates to fit the exact label (e.g. `  Throwing Knives 3` ≈ 185 px), so the ranged plate would run under that position, and `10/15` (5 chars × 8 px = 40 px) did not fit the 33 px label. The ammo plate was therefore moved *below* the ranged plate (same left edge, 62 px wide, y 34–49), and `AmmoFeedback` sits to its right on the same row (abs. y 81–91; the transient `SaveError` label created by `hud.gd` at (12, 90) may overlap its box by 1 px, glyphs do not collide). Plate, icon and count keep the proposed relative offsets (icon +3/+2, label +17/+3). The root retained this placement after native640×360 inspection of Longbow10/15 and Knives20/20 with pickup feedback; no existing HUD information overlaps. Human artistic validation remains pending.

## Placements (derived from live TileMap cells and existing nodes)

Method: Terrain cells decoded (N1 from the inherited `vertical_slice.tscn`); each origin sits on the top face of a solid cell (origin y = cell row × 16), the 28 px body span is fully supported by solid cells in that row, the two rows above are empty, no existing actor/hazard/chest/potion/coin node within 48 px horizontally on the same level except as noted. Nothing sits on a ledge edge or a floating-platform tile requiring a jump; all are on the main ground or step floors of the route. Static check only — not run in Godot.

| Level | Scene | Node | Type | Family | Position (x, y) |
| --- | --- | --- | --- | --- | --- |
| N1 | `eidolon_vale.tscn` | `AmmoSupplies/AmmoCrate01` | crate | Longbow | (290, 144) |
| N1 | `eidolon_vale.tscn` | `AmmoSupplies/AmmoBarrel01` | barrel | Longbow | (1690, 144) |
| N2 | `blight_town.tscn` | `AmmoSupplies/AmmoCrate01` | crate | Longbow | (144, 144) |
| N2 | `blight_town.tscn` | `AmmoSupplies/AmmoBarrel01` | barrel | Longbow | (560, 112) |
| N2 | `blight_town.tscn` | `AmmoSupplies/AmmoCrate02` | crate | ThrowingKnives | (915, 144) |
| N2 | `blight_town.tscn` | `AmmoSupplies/AmmoBarrel02` | barrel | Longbow | (1632, 144) |
| N2 | `blight_town.tscn` | `AmmoSupplies/AmmoBarrel03` | barrel | ThrowingKnives | (2812, 144) |
| N2 | `blight_town.tscn` | `AmmoSupplies/AmmoCrate03` | crate | Longbow | (3560, 144) |
| N3 | `black_forrest.tscn` | `AmmoSupplies/AmmoCrate01` | crate | Longbow | (150, 144) |
| N3 | `black_forrest.tscn` | `AmmoSupplies/AmmoBarrel01` | barrel | ThrowingKnives | (736, 144) |
| N3 | `black_forrest.tscn` | `AmmoSupplies/AmmoCrate02` | crate | Longbow | (1170, 144) |
| N3 | `black_forrest.tscn` | `AmmoSupplies/AmmoBarrel02` | barrel | ThrowingKnives | (2060, 144) |
| N3 | `black_forrest.tscn` | `AmmoSupplies/AmmoCrate03` | crate | Longbow | (2580, 128) |
| N3 | `black_forrest.tscn` | `AmmoSupplies/AmmoBarrel03` | barrel | ThrowingKnives | (3000, 240) |
| N3 | `black_forrest.tscn` | `AmmoSupplies/AmmoCrate04` | crate | ThrowingKnives | (3392, 240) |
| N3 | `black_forrest.tscn` | `AmmoSupplies/AmmoBarrel04` | barrel | Longbow | (3800, 144) |
| N4 | `forbidden_graveyard.tscn` | `AmmoSupplies/AmmoCrate01` | crate | Longbow | (150, 144) |
| N4 | `forbidden_graveyard.tscn` | `AmmoSupplies/AmmoBarrel01` | barrel | ThrowingKnives | (650, 144) |
| N4 | `forbidden_graveyard.tscn` | `AmmoSupplies/AmmoCrate02` | crate | ThrowingKnives | (930, 144) |
| N4 | `forbidden_graveyard.tscn` | `AmmoSupplies/AmmoBarrel02` | barrel | Longbow | (1320, 240) |
| N4 | `forbidden_graveyard.tscn` | `AmmoSupplies/AmmoCrate03` | crate | ThrowingKnives | (1900, 240) |
| N4 | `forbidden_graveyard.tscn` | `AmmoSupplies/AmmoBarrel03` | barrel | Longbow | (2250, 144) |
| N4 | `forbidden_graveyard.tscn` | `AmmoSupplies/AmmoCrate04` | crate | Longbow | (2720, 144) |
| N4 | `forbidden_graveyard.tscn` | `AmmoSupplies/AmmoBarrel04` | barrel | ThrowingKnives | (3270, 144) |
| N4 | `forbidden_graveyard.tscn` | `AmmoSupplies/AmmoCrate05` | crate | ThrowingKnives | (3600, 144) |
| N4 | `forbidden_graveyard.tscn` | `AmmoSupplies/AmmoBarrel05` | barrel | Longbow | (4560, 144) |

Budgets met: N1 2 (2 Longbow); N2 6 (4 Longbow / 2 Knives); N3 8 (4/4); N4 10 (5/5). Both crates and barrels used in every level with ≥ 2 props (N1: one of each). Distribution along the route: spread roughly evenly over each level length (N1 x 290 / 1690; N2 144 → 3560; N3 150 → 3800; N4 150 → 4560).

Known proximities for the root's route check: N3 `AmmoBarrel01` (736) is 48 px from `Enemy02` (784) and ~32 px from the right edge of `Spikes1` (688, floor); props near patrolling enemies (e.g. N2 `AmmoCrate02`/Enemy17, N4 `AmmoBarrel03`/potion) are non-blocking (layer 16, mask 0) so they cannot trap the player. N4 `AmmoBarrel05` (4560) lies beyond the door and requires the existing mechanism to be solved. Props at y = 240 (N3 `AmmoBarrel03`/`AmmoCrate04`, N4 `AmmoBarrel03`/`AmmoCrate03`) are on the lower route.

## Not done / limits

- Godot was not run: no import check, no scene load, no screenshots, no collision or melee-reachability test. Everything above is file-level verification only.
- Audio, pickup `collect` animation and the pickup VFX are not wired (scripts are not mine).
- A pre-existing `scenes/blight_town.tscn2021995891.tmp` editor temp file was left untouched.
- Artistic fit and perceived scale remain for human validation.
