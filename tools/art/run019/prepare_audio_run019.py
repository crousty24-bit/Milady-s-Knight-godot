"""RUN-019: build the threats/exploration SFX in assets/sounds/run019/ from the CC BY 4.0
Helton Yan "Pixel Combat" single files, reusing the RUN-010/014/018 pipeline of tools/prepare_audio.py
(trim -55 dB, 2 ms fade-in, mono 44.1 kHz 16-bit, peak normalization, optional max length + 0.15 s fade-out).
The library is read only. Also writes the AudioStreamRandomizer .tres of the multi-variant cues.
Usage: python3 tools/art/run019/prepare_audio_run019.py [LIBRARY_ROOT] [NAME ...]
"""
from pathlib import Path
import importlib.util
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location("prepare_audio", ROOT / "tools/prepare_audio.py")
pa = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pa)

UI, REPEAT, DEFAULT = pa.UI_PEAK_DB, pa.REPEAT_PEAK_DB, pa.SFX_PEAK_DB


def s(stem: str, n: int) -> str:
	return f"{stem}_HY_PC-{n:03d}"


# name -> (source stem(s) in the Helton pack, max length or None, peak dBFS)
# A tuple of two stems is a layered cue: the second is delayed by 0.12 s and lowered by 4 dB.
SFX = {
	# --- P0: skeletons (bony / rattly) ---
	"sfx_skeleton_warrior_attack_01": (s("DSGNMisc_HIT-Hit Rattle", 2), 0.4, REPEAT),
	"sfx_skeleton_warrior_attack_02": (s("DSGNMisc_HIT-Hit Rattle", 4), 0.4, REPEAT),
	"sfx_skeleton_warrior_death": ((s("DSGNMisc_HIT-Hit Rattle", 1), s("DSGNImpt_EXPLOSION-Crunching", 5)), 0.9, DEFAULT),
	"sfx_skeleton_archer_shot_01": (s("SWSH_MOVEMENT-Bamboo Whip", 1), 0.3, REPEAT),
	"sfx_skeleton_archer_shot_02": (s("SWSH_MOVEMENT-Bamboo Whip", 3), 0.3, REPEAT),
	"sfx_skeleton_archer_death": ((s("DSGNMisc_HIT-Hit Rattle", 6), s("DSGNImpt_EXPLOSION-Cruncher", 5)), 0.9, DEFAULT),
	# --- P0: Blight Sorcerer (dark magic) ---
	"sfx_sorcerer_melee_attack": (s("DSGNTonl_MOVEMENT-Arcane Slap", 1), 0.5, DEFAULT),
	"sfx_sorcerer_spell_cast": (s("DSGNTonl_SKILL RELEASE-Mind Eraser", 5), 0.6, DEFAULT),
	"sfx_sorcerer_ground_warning": (s("MAGSpel_CAST-Energy Riser", 5), 1.0, DEFAULT),
	"sfx_sorcerer_ground_explosion": ((s("DSGNImpt_EXPLOSION-Bass Hit", 3), s("DSGNImpt_EXPLOSION-Magisplosion", 5)), 1.1, DEFAULT),
	"sfx_sorcerer_death": (s("DSGNMisc_SKILL IMPACT-Dramatic Finish", 5), 1.1, DEFAULT),
	# --- P0: Possessed Skulls (spectral) ---
	"sfx_skull_spawn": (s("MAGSpel_CAST-Sharp Summon", 5), 0.8, REPEAT),
	"sfx_skull_death_01": (s("DSGNMisc_SKILL IMPACT-Glassy Sprites", 1), 0.4, REPEAT),
	"sfx_skull_death_02": (s("DSGNMisc_SKILL IMPACT-Glassy Sprites", 2), 0.4, REPEAT),
	"sfx_skull_death_03": (s("DSGNMisc_SKILL IMPACT-Glassy Sprites", 3), 0.4, REPEAT),
	# --- P0: elites (wet / heavy) ---
	"sfx_bloated_slime_attack": (s("DSGNMisc_CAST-Slime Ball", 3), 0.6, DEFAULT),
	"sfx_bloated_slime_death": ((s("DSGNImpt_EXPLOSION-Thud", 4), s("DSGNMisc_SKILL RELEASE-Wet Splash", 5)), 1.1, DEFAULT),
	"sfx_chud_attack_01": (s("FGHTImpt_MELEE-Gut Kick", 3), 0.4, REPEAT),
	"sfx_chud_attack_02": (s("FGHTImpt_MELEE-Gut Kick", 1), 0.4, REPEAT),
	"sfx_chud_death": (s("DSGNMisc_HIT-Mecha Gore Cruncher", 5), 1.0, DEFAULT),
	# --- P0: consumable ---
	"sfx_magic_shield_activate": (s("DSGNSynth_BUFF-Bonus Max Shield", 5), 0.8, DEFAULT),
	# --- P0: traps ---
	"sfx_trapdoor_trigger": (s("DSGNSynth_BUFF-Mecha Lock In", 4), 0.5, DEFAULT),
	"sfx_turret_fire": (s("DSGNMisc_SKILL RELEASE-Flame Ball", 4), 0.5, REPEAT),
	"sfx_turret_projectile_impact": (s("DSGNImpt_EXPLOSION-Small Flare", 1), 0.4, REPEAT),
	"sfx_poison_plant_hit": (s("DSGNMisc_SKILL IMPACT-Bubbly Zaps", 5), 0.6, DEFAULT),
	"sfx_spikes_hit": (s("DSGNMisc_HIT-Mecha Armor Piercer", 6), 0.5, DEFAULT),
	# --- P0: doors, mechanisms, secrets ---
	"sfx_door_coin_payment": (s("DSGNTonl_USABLE-Coin Spend", 4), 0.6, DEFAULT),
	"sfx_door_unlock": ((s("UIMisc_INTERFACE-Lock", 6), s("DSGNSynth_BUFF-Mecha Lock In", 4)), 0.8, DEFAULT),
	"sfx_door_open": (s("DSGNMisc_MOVEMENT-Mecha Large Takeoff", 5), 1.1, DEFAULT),
	"sfx_pressure_plate_activate": ((s("FEETMisc_STEP-Boots on Metal", 3), s("UIClick_INTERFACE-Metallic Click", 1)), 0.4, DEFAULT),
	"sfx_button_activate": (s("UIClick_INTERFACE-Strong Click 1", 3), None, DEFAULT),
	"sfx_secret_reveal": ((s("DSGNImpt_EXPLOSION-Sand Impact", 5), s("MAGSpel_CAST-Skill Ready", 5)), 1.2, DEFAULT),
	# --- P1 ---
	"sfx_magic_shield_end": (s("DSGNSynth_BUFF-Mecha Barrier Fail", 4), 0.7, REPEAT),
	"sfx_player_hp_bonus": (s("DSGNSynth_BUFF-Mecha Level Up", 4), 0.8, DEFAULT),
	"sfx_skull_despawn": (s("DSGNMisc_SKILL IMPACT-Energy Dissipate", 5), 0.6, REPEAT),
	"sfx_skull_attack": (s("DSGNMisc_HIT-Hit Rattle", 3), None, REPEAT),
	"sfx_spikes_extend": (s("DSGNMisc_SKILL RELEASE-Flying Blades", 5), 0.4, DEFAULT),
}

# Randomizer resource -> variant names (same settings as assets/sounds/sfx_slime_death.tres).
RANDOMIZERS = {
	"sfx_skeleton_warrior_attack": ["sfx_skeleton_warrior_attack_01", "sfx_skeleton_warrior_attack_02"],
	"sfx_skeleton_archer_shot": ["sfx_skeleton_archer_shot_01", "sfx_skeleton_archer_shot_02"],
	"sfx_skull_death": ["sfx_skull_death_01", "sfx_skull_death_02", "sfx_skull_death_03"],
	"sfx_chud_attack": ["sfx_chud_attack_01", "sfx_chud_attack_02"],
}


def write_tres(out: Path, name: str, variants: list[str]) -> None:
	lines = ["[gd_resource type=\"AudioStreamRandomizer\" format=3]", ""]
	for i, v in enumerate(variants, 1):
		lines.append(f'[ext_resource type="AudioStream" path="res://assets/sounds/run019/{v}.wav" id="{i}"]')
	lines += ["", "[resource]", "random_pitch = 1.08", "random_volume_offset_db = 1.0", f"streams_count = {len(variants)}"]
	for i in range(len(variants)):
		lines += [f'stream_{i}/stream = ExtResource("{i + 1}")', f"stream_{i}/weight = 1.0"]
	(out / f"{name}.tres").write_text("\n".join(lines) + "\n")


def main() -> None:
	args = sys.argv[1:]
	library = Path(pa.DEFAULT_LIBRARY)
	if args and ("/" in args[0] or "\\" in args[0]):
		library = Path(args.pop(0))
	unknown = set(args) - set(SFX)
	if unknown:
		sys.exit(f"Unknown names: {', '.join(sorted(unknown))}")
	out = ROOT / "assets/sounds/run019"
	out.mkdir(parents=True, exist_ok=True)
	for name, (stems, max_length, peak) in SFX.items():
		if args and name not in args:
			continue
		target = out / f"{name}.wav"
		with tempfile.TemporaryDirectory() as tmp:
			if isinstance(stems, str):
				source = library / pa.HELTON / f"{stems}.wav"
			else:
				a, b = (library / pa.HELTON / f"{x}.wav" for x in stems)
				source = Path(tmp) / "mix.wav"
				pa.ffmpeg("-y", "-i", str(a), "-i", str(b), "-filter_complex",
					"[0:a]aformat=channel_layouts=mono,aresample=44100[x];[1:a]aformat=channel_layouts=mono,aresample=44100,adelay=120,volume=-4dB[y];[x][y]amix=inputs=2:normalize=0:duration=longest",
					"-c:a", "pcm_s16le", str(source))
			pa.build_sfx(source, target, max_length, peak)
		dur = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(target)], capture_output=True, text=True).stdout.strip()
		print(f"{target.relative_to(ROOT)}  peak {pa.max_volume(target):.1f} dB  {float(dur):.2f} s")
	for rname, variants in RANDOMIZERS.items():
		if not args or any(v in args for v in variants):
			write_tres(out, rname, variants)


if __name__ == "__main__":
	main()
