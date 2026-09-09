# Milady's Knight: Blightfall

![Godot](https://img.shields.io/badge/Godot-4.5.1-478CBF?logo=godot-engine&logoColor=white)
![Language](https://img.shields.io/badge/Language-GDScript-478CBF)
![Status](https://img.shields.io/badge/Status-Playable%20Prototype-f0ad4e)
![Tests](https://img.shields.io/badge/Tests-150%20passing-brightgreen)

**Milady's Knight: Blightfall** is a compact 2D action-platformer prototype and a first game-development experiment built with Godot and Astra GPT-6. Play as a knight crossing a ruined kingdom, master aerial movement, fight corrupted slimes, collect enough gold to break the gate's seal, and follow the trail left by the missing princess.

The Godot project identifier is `miladys_knight`. The repository currently contains a playable vertical slice rather than a production-ready or standalone release.

## Project origin

This project is a continuation and substantial reworking of an earlier Godot test project created from the YouTube tutorial [The ultimate introduction to Godot 4](https://youtu.be/LOhfqjmasi0?si=tdgg3XWfNvRXQkSV). The current version expands that foundation with redesigned movement, combat, level routes, progression, persistence, automated tests, and original prototype-level world dressing.

## Current features

- Pixel-art 2D action-platforming at a 320 × 180 internal resolution.
- Responsive movement with acceleration, variable jump height, coyote time, and input buffering.
- Double jump, wall slide, repeatable wall jump, and moving-platform traversal.
- Ground and aerial sword combat with per-swing hit protection and wall occlusion.
- Two slime variants: five Green slimes with 3 HP and three Purple slimes with 4 HP.
- Player health, contact damage, hazards, knockback, temporary invulnerability, death, and full level restart.
- A branching level with upper mobility challenges and a combat-oriented lower route; both routes support backtracking.
- 18 authored coins: 8 shared, 5 on the upper route, and 5 on the lower route.
- A gold-gate objective requiring 12 seal coins, plus a separate bonus economy.
- Persistent banked bonuses stored in `user://progress.json` after a completed run.
- Keyboard controls, pause handling, contextual HUD feedback, music, and sound effects.
- Automated engine-level coverage for movement, physics, mobility, combat, platforms, boundaries, controls, integration, bonuses, routes, and backtracking.

## Gameplay

Explore the abandoned village, choose either branch through the ruins, and reach the corrupted gate. Collect at least **12 of the 18 coins**, offer them at the gate, then cross the exit to complete the level.

Coins collected beyond the 12 required for the seal become pending bonuses. Defeating a slime also awards one pending bonus. Pending bonuses are added to the persistent reserve only after the level is completed; dying, restarting, or closing the game before completion discards only the current attempt's pending rewards.

The upper route emphasizes double jumping, wall jumping, and a moving ferry. The lower route features more combat. One route is enough to open the seal, while exploring both yields additional rewards.

### Controls

The current keyboard layout targets an AZERTY keyboard.

| Action | Key |
| --- | --- |
| Move left / right | `Q` / `D` |
| Jump / double jump | `Space` |
| Wall jump | `Space` while touching a grippable wall |
| Attack | `F` |
| Interact / pay the gate | `E` |
| Restart the current attempt | `R` |
| Pause / resume | `Escape` |

`Z` and `S` are reserved as up/down inputs for future systems. Controller support and in-level checkpoints are not implemented.

## Requirements

- [Godot Engine 4.5.1](https://godotengine.org/download/archive/4.5.1-stable/) or a compatible Godot 4.5 release.
- Windows, Linux, or WSL for the provided helper scripts.
- No third-party Godot add-ons are required.

## Installation and launch

1. Clone the repository once an `origin` remote is available:

   ```bash
   git clone <repository-url> milady-s-knight-godot
   cd milady-s-knight-godot
   ```

2. Import `project.godot` from the Godot Project Manager.
3. Press `F5` to start through `scenes/game.tscn`, or `F6` from `scenes/vertical_slice.tscn` while developing the level.

On Linux or WSL, the helper launcher accepts all standard Godot arguments:

```bash
./tools/run.sh
```

On Windows, double-click `Lancer-Windows.cmd`. If Godot is installed elsewhere, define `GODOT_EXE` with the full path to the executable before running the launcher. The first launch may take longer while Godot imports the assets.

No standalone game export is currently included.

## Development commands

Run the project:

```bash
./tools/run.sh
```

Run the complete headless test suite:

```bash
./tools/test.sh
```

Use a specific Godot executable when necessary:

```bash
GODOT_BIN=/path/to/godot ./tools/test.sh
```

Replay the two complete routes with a visible game window:

```bash
./tools/run.sh --script res://tests/routes.gd
```

Test output is written to the ignored `work/test-results/` directory. The suite fails on a failed assertion, script error, engine error, or detected leaked object.

## Project structure

```text
.
├── assets/                  # Fonts, music, sound effects, sprites, and TileSet data
├── docs/                    # Implementation, validation, improvement, and progression notes
├── scenes/                  # Game bootstrap, level, actors, hazards, gate, platform, and HUD
├── scripts/                 # Gameplay, presentation, level, and persistence logic
├── tests/                   # Godot engine-level and route test scripts
│   └── fixtures/            # Test-only scenes
├── tools/                   # Launch, test, and authoring utilities
├── Lancer-Windows.cmd       # Windows launcher
└── project.godot            # Godot project configuration
```

The authoring utilities in `tools/` can overwrite generated scene files. They are not required to run or test the game and should not be executed after manual scene edits without first preserving those changes.

## Planned development

- Additional handcrafted levels and environment variety.
- More enemy types, combat interactions, and encounter patterns.
- A stable level catalog and richer progression beyond the current bonus reserve.
- Menus, save profiles, configurable controls, and controller support.
- Checkpoints and broader accessibility options.
- Improved art direction, animation, audio mixing, and narrative presentation.
- Export presets and packaged desktop builds.
- External playtesting and balancing for route readability, wall-jump comfort, difficulty, and completion time.

## Known limitations

- The prototype contains one playable level; the next-level scene under `tests/fixtures/` exists only for automated validation.
- The current French in-game text has not yet been localized.
- There is no controller support, checkpoint system, settings menu, or packaged build.
- Original asset license information was not included with the source test project and must be documented before public distribution.

## Documentation

- [`docs/IMPLEMENTATION.md`](docs/IMPLEMENTATION.md) — current architecture and gameplay rules.
- [`docs/VALIDATION.md`](docs/VALIDATION.md) — test evidence and known validation limits.
- [`docs/IMPROVEMENTS.md`](docs/IMPROVEMENTS.md) — movement, collision, and encounter improvements.
- [`docs/BONUS_AND_LEVELS.md`](docs/BONUS_AND_LEVELS.md) — bonus persistence and future-level contract.

## Acknowledgements

- Original learning reference: [Godot 4 tutorial on YouTube](https://youtu.be/LOhfqjmasi0?si=tdgg3XWfNvRXQkSV).
- Built as a first Godot game-development experiment with Astra GPT-6.
- Godot is available under the [MIT license](https://godotengine.org/license/).
