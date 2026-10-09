"""RUN-018: build the standard-equipment SFX in assets/sounds/run018/ from the CC BY 4.0
Helton Yan "Pixel Combat" single files, reusing the RUN-010/014 pipeline of tools/prepare_audio.py
(trim -55 dB, 2 ms fade-in, mono 44.1 kHz 16-bit, peak normalization, optional max length + 0.15 s fade-out).
The library is read only. Usage: python3 tools/art/run018/prepare_audio_run018.py [LIBRARY_ROOT] [NAME ...]
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
# name -> (source stem(s) in the Helton pack, max length or None, peak dBFS)
# A tuple of two stems is a layered cue: the second is delayed by 0.12 s and lowered by 4 dB.
SFX = {
	# P0
	"sfx_chest_open_rare": (("UIMisc_INTERFACE-Lock_HY_PC-004", "DSGNTonl_USABLE-Magic Item_HY_PC-006"), 0.9, DEFAULT),
	"sfx_chest_reward_refuse": ("DSGNTonl_USABLE-Failed Item_HY_PC-003", None, UI),
	"sfx_weapon_upgrade": ("DSGNTonl_USABLE-Mecha Upgrade Equip_HY_PC-004", None, DEFAULT),
	"sfx_heal_kill": ("MAGAngl_BUFF-Simple Heal_HY_PC-005", 0.32, REPEAT),
	# P1
	"sfx_melee_swing_heavy_01": ("WHSH_MOVEMENT-Wind Sweep Swish_HY_PC-001", 0.6, DEFAULT),
	"sfx_melee_swing_heavy_02": ("WHSH_MOVEMENT-Wind Sweep Swish_HY_PC-003", 0.6, DEFAULT),
	"sfx_melee_swing_heavy_03": ("WHSH_MOVEMENT-Wind Sweep Swish_HY_PC-005", 0.6, DEFAULT),
	"sfx_weapon_knives_throw_01": ("SWSH_MOVEMENT-Reso Swish_HY_PC-001", 0.28, REPEAT),
	"sfx_weapon_knives_throw_02": ("SWSH_MOVEMENT-Reso Swish_HY_PC-002", 0.28, REPEAT),
	"sfx_weapon_knives_throw_03": ("SWSH_MOVEMENT-Reso Swish_HY_PC-004", 0.28, REPEAT),
	"sfx_knife_impact": ("DSGNMisc_HIT-Zap Metal_HY_PC-002", 0.22, REPEAT),
	"sfx_major_potion_pickup": ("DSGNTonl_MOVEMENT-Bubble Babbler_HY_PC-005", 0.8, DEFAULT),
}


def main() -> None:
	args = sys.argv[1:]
	library = Path(pa.DEFAULT_LIBRARY)
	if args and ("/" in args[0] or "\\" in args[0]):
		library = Path(args.pop(0))
	unknown = set(args) - set(SFX)
	if unknown:
		sys.exit(f"Unknown names: {', '.join(sorted(unknown))}")
	out = ROOT / "assets/sounds/run018"
	out.mkdir(parents=True, exist_ok=True)
	for name, (stems, max_length, peak) in SFX.items():
		if args and name not in args:
			continue
		target = out / f"{name}.wav"
		with tempfile.TemporaryDirectory() as tmp:
			if isinstance(stems, str):
				source = library / pa.HELTON / f"{stems}.wav"
			else:
				a, b = (library / pa.HELTON / f"{s}.wav" for s in stems)
				source = Path(tmp) / "mix.wav"
				pa.ffmpeg("-y", "-i", str(a), "-i", str(b), "-filter_complex",
					"[0:a]aformat=channel_layouts=mono,aresample=44100[x];[1:a]aformat=channel_layouts=mono,aresample=44100,adelay=120,volume=-4dB[y];[x][y]amix=inputs=2:normalize=0:duration=longest",
					"-c:a", "pcm_s16le", str(source))
			pa.build_sfx(source, target, max_length, peak)
		dur = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(target)], capture_output=True, text=True).stdout.strip()
		print(f"{target.relative_to(ROOT)}  peak {pa.max_volume(target):.1f} dB  {float(dur):.2f} s")


if __name__ == "__main__":
	main()
