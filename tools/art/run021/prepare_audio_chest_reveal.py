"""RUN-021: build the paid-chest reveal cues assets/sounds/run021/sfx_chest_reveal_rise.wav (crescendo,
~2.9 s) and sfx_chest_reveal_burst.wav (climax, <= 1.2 s) from the CC BY 4.0 Helton Yan "Pixel Combat"
single files, reusing the tools/prepare_audio.py pipeline (trim -55 dB, 2 ms fade-in, mono 44.1 kHz 16-bit,
peak normalization, max length + fade-out).
Rise: "Aura Up" 002 (first 2.4 s, the part before its decay, time-stretched x1.22 so the pitch and brightness
keep rising over 2.9 s) + "Growing Strength" 004 reversed (warm swell ending on its own peak, -5 dB).
A dB-linear volume ramp (-34 dB at t=0 -> 0 dB at 2.9 s) enforces the crescendo; 30 ms fade-out at the tail
because the burst cuts it.
Burst: "Glistening Shimmers" 004 (bright sustained shimmer) + "Magic Sparkles" 002 (-3 dB, glitter), both at t=0.
The library is read only. Usage: python3 tools/art/run021/prepare_audio_chest_reveal.py [LIBRARY_ROOT]
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

RISE_TONE = "MAGSpel_CAST-Aura Up_HY_PC-002"
RISE_BODY = "MAGSpel_CAST-Growing Strength_HY_PC-004"
BURST_SHIMMER = "DSGNTonl_SKILL IMPACT-Glistening Shimmers_HY_PC-004"
BURST_SPARKLE = "DSGNTonl_SKILL IMPACT-Magic Sparkles_HY_PC-002"
RISE_LENGTH = 2.9  # chest animation reaches the white flash at ~2.9 s
RISE_START_DB = -34.0
RISE_PEAK_DB = -10.0
BURST_LENGTH = 1.2
BURST_PEAK_DB = -9.0
MONO = "aformat=channel_layouts=mono,aresample=44100"


def duration(path: Path) -> float:
	out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)], capture_output=True, text=True).stdout
	return float(out.strip())


def main() -> None:
	library = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(pa.DEFAULT_LIBRARY)
	out = ROOT / "assets/sounds/run021"
	out.mkdir(parents=True, exist_ok=True)

	def src(stem: str) -> str:
		return str(library / pa.HELTON / f"{stem}.wav")

	with tempfile.TemporaryDirectory() as tmp:
		raw = Path(tmp) / "rise_raw.wav"
		pa.ffmpeg("-y", "-i", src(RISE_TONE), "-i", src(RISE_BODY), "-filter_complex",
			f"[0:a]{MONO},atrim=0:2.4,atempo=0.82,asetpts=PTS-STARTPTS,atrim=0:{RISE_LENGTH}[a];"
			f"[1:a]{MONO},atrim=0:2.8,asetpts=PTS-STARTPTS,areverse,volume=-5dB[b];"
			f"[a][b]amix=inputs=2:normalize=0:duration=longest,atrim=0:{RISE_LENGTH},"
			f"volume='pow(10,({RISE_START_DB}*(1-pow(t/{RISE_LENGTH},1.0)))/20)':eval=frame,"
			f"afade=t=out:st={RISE_LENGTH - 0.03}:d=0.03",
			"-c:a", "pcm_s16le", str(raw))
		# The head sits ~34 dB under the peak: bring the mix near full scale first so the -55 dB trim keeps it.
		loud = Path(tmp) / "rise_loud.wav"
		pa.ffmpeg("-y", "-i", str(raw), "-af", f"volume={-1.0 - pa.max_volume(raw):.2f}dB", "-c:a", "pcm_s16le", str(loud))
		pa.build_sfx(loud, out / "sfx_chest_reveal_rise.wav", None, RISE_PEAK_DB)

		burst = Path(tmp) / "burst_mix.wav"
		pa.ffmpeg("-y", "-i", src(BURST_SHIMMER), "-i", src(BURST_SPARKLE), "-filter_complex",
			f"[0:a]{MONO}[x];[1:a]{MONO},volume=-3dB[y];[x][y]amix=inputs=2:normalize=0:duration=longest",
			"-c:a", "pcm_s16le", str(burst))
		pa.build_sfx(burst, out / "sfx_chest_reveal_burst.wav", BURST_LENGTH, BURST_PEAK_DB)

	for name in ("sfx_chest_reveal_rise.wav", "sfx_chest_reveal_burst.wav"):
		target = out / name
		print(f"{target.relative_to(ROOT)}  peak {pa.max_volume(target):.1f} dB  {duration(target):.2f} s")


if __name__ == "__main__":
	main()
