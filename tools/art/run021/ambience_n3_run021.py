#!/usr/bin/env python3
"""RUN-021: new N3 Black Forrest ambient loop (original, stdlib only, deterministic).

Human request of 8 Oct 2026: the RUN-020 N3 bed is too loud and unpleasant; wanted the spirit of the
N2 Blight Town bed (dark low wind, moaning band, sparse wood creaks) but different and more discreet.
The RUN-020 version is kept untouched; its hissy layers (1.3 kHz rustle, 1.7-1.9 kHz insect chirps)
are not used. Layers: low forest wind (lower cut than N2), a deeper moan sweeping around 150 Hz,
trunk creaks lower than N2's, a soft leaf swell kept under 900 Hz, and one distant owl.
Reuses the DSP primitives and loop construction of tools/art/run020/ambience_run020.py.

Usage: python3 tools/art/run021/ambience_n3_run021.py
Writes the PCM source assets/source/run021/audio/amb_black_forrest_v2.wav and the Vorbis derivative
assets/sounds/run021/amb_black_forrest_v2.ogg.
"""
import importlib.util
import math
import os
import random
import subprocess

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
spec = importlib.util.spec_from_file_location("amb", os.path.join(ROOT, "tools/art/run020/ambience_run020.py"))
amb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(amb)

TARGET_RMS_DB = -33.0  # N2/N3 RUN-020 beds: -28; ~5 dB more discreet at the same node volume
PEAK_LIMIT_DB = -18.0


def normalize(sig):
	m = sum(sig) / len(sig)
	sig = [v - m for v in sig]
	rms = math.sqrt(sum(v * v for v in sig) / len(sig))
	g = 10 ** (TARGET_RMS_DB / 20) / rms
	sig = [v * g for v in sig]
	pk = max(abs(v) for v in sig)
	lim = 10 ** (PEAK_LIMIT_DB / 20)
	if pk > lim:  # gain-only, keeps the loop seamless
		sig = [v * lim / pk for v in sig]
	return sig


def black_forrest_v2():
	rng = random.Random(3021)
	L, XF, DUR, SR, TAU = amb.L, amb.XF, amb.DUR, amb.SR, amb.TAU
	wind = amb.norm_layer(amb.wind(rng, 300, [(2, 0.4), (3, 0.3), (5, 0.12)], 0.9))
	moan = amb.bandpass(amb.noise(rng, L + XF), 0, 6.0, lambda i: 150 + 35 * math.sin(TAU * 2 * (i % L) / L + 1.1))
	menv = amb.periodic_env(rng, 0.5, [(2, 0.45), (3, 0.2)])
	moan = amb.norm_layer(amb.loopify([a * b for a, b in zip(moan, menv)]))
	leaves = amb.lowpass(amb.bandpass(amb.noise(rng, L + XF), 600, 0.7), 900)
	lenv = amb.periodic_env(rng, 0.35, [(3, 0.3), (5, 0.15)])
	leaves = amb.norm_layer(amb.loopify([a * b for a, b in zip(leaves, lenv)]))
	creaks = [0.0] * L
	for s in (0.18, 0.63):
		amb.add_wrapped(creaks, int((s + rng.uniform(-0.03, 0.03)) * L), amb.creak(rng, 50, 110), 1.0)
	owl = [0.0] * L
	amb.add_wrapped(owl, int(0.40 * L), amb.lowpass(amb.owl(rng), 600), 1.0)
	return normalize(amb.mix([(1.0, wind), (0.32, moan), (0.16, leaves), (0.30, amb.norm_layer(creaks)), (0.07, amb.norm_layer(owl))]))


def main():
	source = os.path.join(ROOT, "assets/source/run021/audio/amb_black_forrest_v2.wav")
	target = os.path.join(ROOT, "assets/sounds/run021/amb_black_forrest_v2.ogg")
	os.makedirs(os.path.dirname(source), exist_ok=True)
	os.makedirs(os.path.dirname(target), exist_ok=True)
	amb.write_wav(source, black_forrest_v2())
	print("wrote", os.path.relpath(source, ROOT))
	subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", source, "-c:a", "libvorbis", "-q:a", "4", target], check=True)
	print("encoded", os.path.relpath(target, ROOT))


if __name__ == "__main__":
	main()
