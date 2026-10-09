#!/usr/bin/env python3
"""RUN-020 procedural ambient loops (original, stdlib only, deterministic).

Usage: python3 tools/art/run020/ambience_run020.py [--preview]
Writes PCM sources assets/source/run020/amb_{blight_town,black_forrest,forbidden_graveyard}.wav; --ogg also encodes production Vorbis derivatives.
Mono, 22050 Hz, 16-bit PCM, 28 s, with a RIFF 'smpl' forward loop 0..frames-1.
Every layer is periodic over the file length (integer-cycle LFOs, wrapped event
schedules, noise crossfaded end->start), so the loop is seamless.
"""
import math, os, random, struct, sys, wave, subprocess

SR = 22050
DUR = 28
L = SR * DUR
XF = int(1.5 * SR)
TAU = 2 * math.pi
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
OUT = os.path.join(ROOT, "assets", "source", "run020")
TARGET_RMS_DB = -28.0
PEAK_LIMIT_DB = -13.0


def db(x):
    return 20 * math.log10(max(x, 1e-9))


# ---------- DSP primitives ----------
def noise(rng, n):
    return [rng.uniform(-1.0, 1.0) for _ in range(n)]


def lowpass(x, fc):
    a = 1.0 - math.exp(-TAU * fc / SR)
    y = 0.0
    out = []
    for v in x:
        y += a * (v - y)
        out.append(y)
    return out


def highpass(x, fc):
    lp = lowpass(x, fc)
    return [v - l for v, l in zip(x, lp)]


def bandpass(x, fc, q, fc_fn=None, block=32):
    """RBJ constant-0dB-peak bandpass; fc_fn(i)->Hz optional for sweeps."""
    x1 = x2 = y1 = y2 = 0.0
    out = []
    b0 = a1 = a2 = 0.0
    for i, v in enumerate(x):
        if i % block == 0:
            f = fc_fn(i) if fc_fn else fc
            w = TAU * f / SR
            al = math.sin(w) / (2 * q)
            a0 = 1 + al
            b0 = al / a0
            a1 = -2 * math.cos(w) / a0
            a2 = (1 - al) / a0
        y = b0 * v - b0 * x2 - a1 * y1 - a2 * y2
        x2, x1 = x1, v
        y2, y1 = y1, y
        out.append(y)
    return out


def loopify(x):
    """x has length L+XF; equal-power crossfade tail->head -> periodic length L."""
    y = x[:L]
    for i in range(XF):
        p = (i / XF) * math.pi / 2
        y[i] = x[i] * math.sin(p) + x[L + i] * math.cos(p)
    return y


def cycles_for(freq_hz):
    """Snap a frequency to an integer number of cycles over the loop."""
    return max(1, round(freq_hz * DUR)) / DUR


def periodic_env(rng, base, parts):
    """Positive slow envelope, integer cycles over the loop. parts: [(cycles, amp)]"""
    ph = [(c, a, rng.uniform(0, TAU)) for c, a in parts]
    env = []
    for i in range(L + XF):
        t = (i % L) / L
        v = base + sum(a * math.sin(TAU * c * t + p) for c, a, p in ph)
        env.append(max(v, 0.0))
    return env


def add_wrapped(buf, start, sig, gain=1.0):
    for k, v in enumerate(sig):
        buf[(start + k) % L] += v * gain


def smooth_window(n):
    return [0.5 - 0.5 * math.cos(TAU * i / (n - 1)) for i in range(n)]


def mix(layers):
    out = [0.0] * L
    for g, lay in layers:
        for i in range(L):
            out[i] += g * lay[i]
    return out


def norm_layer(x):
    r = math.sqrt(sum(v * v for v in x) / len(x))
    return [v / r for v in x]


# ---------- Event synths ----------
def creak(rng, lo=70, hi=160):
    n = int(rng.uniform(0.9, 1.6) * SR)
    f0 = rng.uniform(lo, hi)
    drift = rng.uniform(-0.35, 0.35)
    ph = 0.0
    sig = []
    win = smooth_window(n)
    for i in range(n):
        t = i / n
        f = f0 * (1 + drift * t) * (1 + 0.04 * math.sin(TAU * 7 * t))
        ph += TAU * f / SR
        stick = 0.6 + 0.4 * math.sin(TAU * 11 * t + 1.3)
        s = math.sin(ph) + 0.5 * math.sin(2 * ph) + 0.3 * math.sin(3 * ph)
        sig.append(s * stick * win[i] * win[i])
    return lowpass(lowpass(sig, 450), 450)


def bubble(rng):
    n = int(rng.uniform(0.05, 0.11) * SR)
    f0 = rng.uniform(110, 260)
    ph = 0.0
    sig = []
    for i in range(n):
        t = i / SR
        ph += TAU * f0 * (1 + 4.0 * t) / SR
        sig.append(math.sin(ph) * min(1.0, t / 0.008) * math.exp(-t / 0.03))
    return lowpass(sig, 500)


def owl(rng):
    out = []
    f1 = rng.uniform(340, 400)
    for k, (f, d) in enumerate(((f1, 0.42), (f1 * 0.84, 0.62))):
        n = int(d * SR)
        ph = 0.0
        w = smooth_window(n)
        for i in range(n):
            t = i / SR
            ph += TAU * f * (1 + 0.012 * math.sin(TAU * 5.5 * t)) / SR
            out.append(math.sin(ph) * w[i] ** 1.5)
        if k == 0:
            out.extend([0.0] * int(0.22 * SR))
    return lowpass(out, 900)


def twig(rng):
    total = int(rng.uniform(0.18, 0.3) * SR)
    sig = [0.0] * total
    for _ in range(rng.randint(3, 6)):
        s = rng.randint(0, total - 400)
        n = rng.randint(80, 260)
        w = smooth_window(n)
        a = rng.uniform(0.4, 1.0)
        for i in range(n):
            sig[s + i] += rng.uniform(-1, 1) * w[i] * a
    return lowpass(bandpass(sig, 1100, 1.2), 1800)


def chirp_burst(rng, f):
    out = []
    for _ in range(rng.randint(3, 4)):
        n = int(0.022 * SR)
        w = smooth_window(n)
        ph = 0.0
        for i in range(n):
            ph += TAU * f / SR
            out.append(math.sin(ph) * w[i])
        out.extend([0.0] * int(0.024 * SR))
    return out


def bell(rng, f):
    n = int(5.5 * SR)
    sig = [0.0] * n
    for r, a, tau in ((1.0, 1.0, 1.4), (2.41, 0.45, 0.9), (3.87, 0.2, 0.5)):
        det = 1 + rng.uniform(-0.002, 0.002)
        ph = rng.uniform(0, TAU)
        for i in range(n):
            t = i / SR
            env = min(1.0, t / 0.35) ** 2 * math.exp(-t / (tau * 1.8))
            sig[i] += a * env * math.sin(ph + TAU * f * r * det * t)
    return lowpass(lowpass(sig, 650), 650)


# ---------- Beds ----------
def wind(rng, lp_fc, gust_parts, base=0.8):
    x = noise(rng, L + XF)
    x = highpass(lowpass(lowpass(x, lp_fc), lp_fc), 45)
    env = periodic_env(rng, base, gust_parts)
    return loopify([a * b for a, b in zip(x, env)])


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


def blight_town():
    rng = random.Random(2002)
    w1 = norm_layer(wind(rng, 380, [(2, 0.45), (3, 0.3), (5, 0.15)], 0.9))
    howl = bandpass(noise(rng, L + XF), 0, 5.0,
                    lambda i: 230 + 60 * math.sin(TAU * 3 * (i % L) / L))
    henv = periodic_env(rng, 0.6, [(2, 0.5), (4, 0.2)])
    howl = norm_layer(loopify([a * b for a, b in zip(howl, henv)]))
    ev = [0.0] * L
    for s in (0.10, 0.42, 0.75):
        add_wrapped(ev, int((s + rng.uniform(-0.04, 0.04)) * L), creak(rng), 1.0)
    bub = [0.0] * L
    t = 0.0
    while t < DUR:
        t += rng.uniform(1.4, 4.0)
        if t < DUR:
            g = rng.uniform(0.5, 1.0)
            add_wrapped(bub, int(t * SR), bubble(rng), g)
            if rng.random() < 0.4:
                add_wrapped(bub, int((t + rng.uniform(0.12, 0.3)) * SR), bubble(rng), g * 0.6)
    return normalize(mix([(1.0, w1), (0.30, howl), (0.35, norm_layer(ev)), (0.20, norm_layer(bub))]))


def black_forrest():
    rng = random.Random(3003)
    rus = lowpass(bandpass(noise(rng, L + XF), 1300, 0.8), 2600)
    swell = periodic_env(rng, 0.45, [(4, 0.35), (7, 0.2), (11, 0.08)])
    rus = norm_layer(loopify([a * b for a, b in zip(rus, swell)]))
    low = norm_layer(wind(rng, 260, [(2, 0.4), (3, 0.3)], 0.9))
    ins = [0.0] * L
    n_groups = 9
    for g in range(n_groups):
        base = (g + rng.uniform(0.1, 0.9)) / n_groups * DUR
        f = rng.uniform(1650, 1900)
        for k in range(rng.randint(2, 4)):
            add_wrapped(ins, int((base + k * 0.22) * SR), chirp_burst(rng, f), rng.uniform(0.6, 1.0))
    owls = [0.0] * L
    for s in (0.22, 0.71):
        add_wrapped(owls, int(s * L), owl(rng), 1.0)
    tw = [0.0] * L
    for s in (0.08, 0.31, 0.55, 0.86):
        add_wrapped(tw, int((s + rng.uniform(-0.02, 0.02)) * L), twig(rng), rng.uniform(0.6, 1.0))
    return normalize(mix([(1.0, rus), (0.55, low), (0.10, norm_layer(ins)),
                          (0.14, norm_layer(owls)), (0.10, norm_layer(tw))]))


def forbidden_graveyard():
    rng = random.Random(4004)
    w = norm_layer(wind(rng, 420, [(2, 0.4), (3, 0.35), (6, 0.1)], 0.9))
    whistle = bandpass(noise(rng, L + XF), 0, 14.0,
                       lambda i: 620 + 220 * math.sin(TAU * 2 * (i % L) / L + 0.7)
                       + 60 * math.sin(TAU * 5 * (i % L) / L))
    wenv = periodic_env(rng, 0.35, [(2, 0.4), (3, 0.25)])
    whistle = norm_layer(loopify([a * b for a, b in zip(whistle, wenv)]))
    drone = [0.0] * L
    for f, a, k in ((55.0, 1.0, 1), (55.0 + 0.11, 0.9, 2), (82.4, 0.5, 3),
                    (82.4 + 0.07, 0.45, 4), (110.0, 0.3, 5), (110.0 + 0.18, 0.25, 6)):
        fs = cycles_for(f)
        ph = rng.uniform(0, TAU)
        for i in range(L):
            drone[i] += a * math.sin(TAU * fs * (i / SR) + ph) * (0.75 + 0.25 * math.sin(TAU * k * i / L + ph))
    bl = [0.0] * L
    for s, f in ((0.30, 196.0), (0.78, 174.6)):
        add_wrapped(bl, int(s * L), bell(rng, f), 1.0)
    br = [0.0] * L
    for s in (0.12, 0.40, 0.62, 0.90):
        n = int(rng.uniform(3.0, 4.5) * SR)
        sig = lowpass(bandpass(noise(rng, n), 700, 1.5), 1800)
        wv = smooth_window(n)
        add_wrapped(br, int(s * L), [a * b for a, b in zip(sig, wv)], 1.0)
    return normalize(mix([(1.0, w), (0.35, whistle), (0.9, norm_layer(drone)),
                          (0.22, norm_layer(bl)), (0.35, norm_layer(br))]))


# ---------- IO ----------
def write_wav(path, sig):
    pcm = [max(-32768, min(32767, int(round(v * 32767)))) for v in sig]
    data = struct.pack("<%dh" % len(pcm), *pcm)
    fmt = struct.pack("<HHIIHH", 1, 1, SR, SR * 2, 2, 16)
    smpl = struct.pack("<IIIIIIIII", 0, 0, int(1e9 / SR), 60, 0, 0, 0, 1, 0)
    smpl += struct.pack("<IIIIII", 0, 0, 0, len(pcm) - 1, 0, 0)
    body = b"WAVE"
    body += b"fmt " + struct.pack("<I", len(fmt)) + fmt
    body += b"data" + struct.pack("<I", len(data)) + data
    body += b"smpl" + struct.pack("<I", len(smpl)) + smpl
    with open(path, "wb") as f:
        f.write(b"RIFF" + struct.pack("<I", len(body)) + body)


def main():
    os.makedirs(OUT, exist_ok=True)
    for name, fn in (("amb_blight_town", blight_town), ("amb_black_forrest", black_forrest),
                     ("amb_forbidden_graveyard", forbidden_graveyard)):
        p = os.path.join(OUT, name + ".wav")
        write_wav(p, fn())
        print("wrote", os.path.relpath(p, ROOT))
        if "--ogg" in sys.argv:
            target = os.path.join(ROOT, "assets", "sounds", "run020", name + ".ogg")
            os.makedirs(os.path.dirname(target), exist_ok=True)
            subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", p,
                            "-c:a", "libvorbis", "-q:a", "4", target], check=True)
            print("encoded", os.path.relpath(target, ROOT))


if __name__ == "__main__":
    main()
