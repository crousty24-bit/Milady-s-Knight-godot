"""RUN-010: build the normalized game audio from the external source library.

The library is read only. Each derivative is trimmed, converted to mono 44.1 kHz
16-bit WAV and peak-normalized; the music is loudness-normalized to Ogg Vorbis.
Usage: python3 tools/prepare_audio.py [LIBRARY_ROOT]
"""
from pathlib import Path
import re
import subprocess
import sys

DEFAULT_LIBRARY = "/mnt/c/Users/allen/OneDrive/Images/assets_ressources/Mildays-knight"
HELTON = "SFX/Helton Yan's Pixel Combat - Single Files"
SFX_PEAK_DB = -3.0
# name -> (source file stem, maximum length in seconds or None)
SFX = {
	"sfx_player_jump": ("DSGNMisc_MOVEMENT-Retro Jump_HY_PC-001", None),
	"sfx_player_double_jump": ("DSGNMisc_MOVEMENT-Jump Sparkle_HY_PC-001", None),
	"sfx_player_wall_jump": ("WHSH_MOVEMENT-Simple Whoosh_HY_PC-001", None),
	"sfx_melee_swing_light_01": ("DSGNMisc_MELEE-Sword Slash_HY_PC-001", None),
	"sfx_melee_swing_light_02": ("DSGNMisc_MELEE-Sword Slash_HY_PC-002", None),
	"sfx_melee_swing_light_03": ("DSGNMisc_MELEE-Sword Slash_HY_PC-003", None),
	"sfx_melee_hit_01": ("DSGNMisc_HIT-Gore Pierce_HY_PC-001", None),
	"sfx_melee_hit_02": ("DSGNMisc_HIT-Gore Pierce_HY_PC-002", None),
	"sfx_melee_hit_03": ("DSGNMisc_HIT-Gore Pierce_HY_PC-003", None),
	"sfx_player_hit_01": ("FGHTImpt_HIT-Strong Smack_HY_PC-001", None),
	"sfx_player_hit_02": ("FGHTImpt_HIT-Strong Smack_HY_PC-002", None),
	"sfx_player_hit_03": ("FGHTImpt_HIT-Strong Smack_HY_PC-003", None),
	"sfx_player_death": ("DSGNImpt_EXPLOSION-Thud_HY_PC-001", None),
	# The coin tail is shortened so rapid pickups do not pile up.
	"sfx_gold_coin_pickup_01": ("DSGNTonl_USABLE-Magic Coin_HY_PC-001", 0.7),
	"sfx_gold_coin_pickup_02": ("DSGNTonl_USABLE-Magic Coin_HY_PC-002", 0.7),
	"sfx_gold_coin_pickup_03": ("DSGNTonl_USABLE-Magic Coin_HY_PC-004", 0.7),
	"sfx_slime_death_01": ("DSGNMisc_SKILL RELEASE-Wet Splash_HY_PC-001", None),
	"sfx_slime_death_02": ("DSGNMisc_SKILL RELEASE-Wet Splash_HY_PC-002", None),
	"sfx_slime_death_03": ("DSGNMisc_SKILL RELEASE-Wet Splash_HY_PC-003", None),
}
MUSIC = {
	"music_slice_dark_fantasy_lofi": "Music/welc0mei0-bgm006-dark-fantasy-lo-fi-retro-game-148338.mp3",
}


def ffmpeg(*args: str) -> str:
	result = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", *args], capture_output=True, text=True, check=True)
	return result.stderr


def max_volume(path: Path) -> float:
	log = ffmpeg("-i", str(path), "-af", "volumedetect", "-f", "null", "-")
	return float(re.search(r"max_volume: (-?[0-9.]+) dB", log).group(1))


def build_sfx(source: Path, target: Path, max_length: float | None) -> None:
	trim = "silenceremove=start_periods=1:start_threshold=-55dB,areverse,silenceremove=start_periods=1:start_threshold=-55dB,areverse"
	if max_length:
		trim += f",atrim=0:{max_length},afade=t=out:st={max_length - 0.15}:d=0.15"
	temp = target.with_suffix(".tmp.wav")
	ffmpeg("-y", "-i", str(source), "-af", trim + ",afade=t=in:d=0.002", "-ac", "1", "-ar", "44100", "-c:a", "pcm_s16le", str(temp))
	gain = SFX_PEAK_DB - max_volume(temp)
	ffmpeg("-y", "-i", str(temp), "-af", f"volume={gain:.2f}dB", "-ac", "1", "-ar", "44100", "-c:a", "pcm_s16le", "-map_metadata", "-1", "-fflags", "+bitexact", "-flags:a", "+bitexact", str(target))
	temp.unlink()


def main() -> None:
	library = Path(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_LIBRARY)
	root = Path(__file__).resolve().parents[1]
	for name, (stem, max_length) in SFX.items():
		target = root / "assets/sounds" / f"{name}.wav"
		build_sfx(library / HELTON / f"{stem}.wav", target, max_length)
		print(f"{target.relative_to(root)}  peak {max_volume(target):.1f} dB")
	for name, relative in MUSIC.items():
		target = root / "assets/music" / f"{name}.ogg"
		ffmpeg("-y", "-i", str(library / relative), "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", "44100", "-c:a", "libvorbis", "-q:a", "5", "-map_metadata", "-1", str(target))
		print(f"{target.relative_to(root)}  peak {max_volume(target):.1f} dB")


if __name__ == "__main__":
	main()
