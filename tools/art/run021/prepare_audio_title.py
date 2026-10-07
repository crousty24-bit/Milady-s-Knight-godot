"""RUN-021: build the level title-card sting assets/sounds/run021/sfx_level_title.wav from the CC BY 4.0
Helton Yan "Pixel Combat" single files, reusing the tools/prepare_audio.py pipeline
(trim -55 dB, 2 ms fade-in, mono 44.1 kHz 16-bit, peak normalization, max length + 0.15 s fade-out).
Layers (objective choice, see handoff): "Teleport Downer" 005 (falling low resonant tone, 83 % of RMS below
250 Hz, almost no content above 3 kHz, monotone 2.4 s decay) under a "Thud" 003 impact at t=0.
The library is read only. Usage: python3 tools/art/run021/prepare_audio_title.py [LIBRARY_ROOT]
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

IMPACT = "DSGNImpt_EXPLOSION-Thud_HY_PC-003"
TONE = "MAGSpel_CAST-Teleport Downer_HY_PC-005"
MAX_LENGTH = 2.5  # must stay well under the 5 s title (1 s fade-in, ~3 s hold, 1 s fade-out)
PEAK_DB = pa.UI_PEAK_DB  # non-gameplay UI-layer cue, sits under the SFX default (-8 dB)


def main() -> None:
	library = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(pa.DEFAULT_LIBRARY)
	out = ROOT / "assets/sounds/run021"
	out.mkdir(parents=True, exist_ok=True)
	target = out / "sfx_level_title.wav"
	with tempfile.TemporaryDirectory() as tmp:
		source = Path(tmp) / "mix.wav"
		a, b = (library / pa.HELTON / f"{x}.wav" for x in (IMPACT, TONE))
		# Thud at t=0 (-2 dB), tone delayed by 0.08 s so the impact leads, then the tone rings out.
		pa.ffmpeg("-y", "-i", str(a), "-i", str(b), "-filter_complex",
			"[0:a]aformat=channel_layouts=mono,aresample=44100,volume=-2dB[x];[1:a]aformat=channel_layouts=mono,aresample=44100,adelay=80[y];[x][y]amix=inputs=2:normalize=0:duration=longest",
			"-c:a", "pcm_s16le", str(source))
		pa.build_sfx(source, target, MAX_LENGTH, PEAK_DB)
	dur = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(target)], capture_output=True, text=True).stdout.strip()
	print(f"{target.relative_to(ROOT)}  peak {pa.max_volume(target):.1f} dB  {float(dur):.2f} s")


if __name__ == "__main__":
	main()
