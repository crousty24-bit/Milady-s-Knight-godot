"""RUN-021: build the player jump / double-jump cues from Minifantasy Dungeon SFX "12_human_jump" takes
(human request of 8 Oct 2026: the RUN-014 whooshes still read sci-fi; wanted neutral, discreet, slightly modified).
Reuses the tools/prepare_audio.py pipeline (trim -55 dB, 2 ms fade-in, mono 44.1 kHz 16-bit, peak normalization,
max length + 0.15 s fade-out). Light modifications only, both cues keep the human foley character:
- jump: take 3 (lowest spectral centroid, ~1.8 kHz), pitched down 1 semitone, low-pass 5 kHz;
- double jump: take 2, pitched up 1.5 semitones (lighter, airborne), band 200 Hz-6.5 kHz, so the two stay distinct.
Both sit at REPEAT_PEAK_DB (-10 dBFS, the frequent-cue level), under the -8 dBFS default.
The library is read only. Usage: python3 tools/art/run021/prepare_audio_jump.py [LIBRARY_ROOT]
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

MINIFANTASY = "SFX/Minifantasy_Dungeon_SFX"
# target -> (source take, semitones, filter chain, max length in seconds)
CUES = {
	"sfx_player_jump_human": ("12_human_jump_3", -1.0, "lowpass=f=5000", 0.35),
	"sfx_player_double_jump_human": ("12_human_jump_2", 1.5, "highpass=f=200,lowpass=f=6500", 0.3),
}


def main() -> None:
	library = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(pa.DEFAULT_LIBRARY)
	out = ROOT / "assets/sounds/run021"
	out.mkdir(parents=True, exist_ok=True)
	for name, (take, semitones, filters, max_length) in CUES.items():
		target = out / f"{name}.wav"
		ratio = 2.0 ** (semitones / 12.0)
		with tempfile.TemporaryDirectory() as tmp:
			source = Path(tmp) / "shaped.wav"
			# asetrate + aresample: a plain resample pitch shift (duration scales by 1/ratio, a few ms here).
			pa.ffmpeg("-y", "-i", str(library / MINIFANTASY / f"{take}.wav"), "-af",
				f"aformat=channel_layouts=mono,aresample=44100,asetrate={44100 * ratio:.0f},aresample=44100,{filters}",
				"-c:a", "pcm_s16le", str(source))
			pa.build_sfx(source, target, max_length, pa.REPEAT_PEAK_DB)
		dur = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(target)], capture_output=True, text=True).stdout.strip()
		print(f"{target.relative_to(ROOT)}  peak {pa.max_volume(target):.1f} dB  {float(dur):.2f} s")


if __name__ == "__main__":
	main()
