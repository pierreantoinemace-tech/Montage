"""Bruitages synthétisés (sans musique) + mixage sous la voix. Réutilisable pour toute la série.
Usage : sfx.mix(voice_wav, events, out_wav)  avec events = [(temps_s, 'type', gain), ...]"""
import numpy as np, wave

SR = 48000
rng = np.random.default_rng(7)


def _t(d): return np.arange(int(d * SR)) / SR


def _env(n, a=0.005, r=None):
    e = np.ones(n); na = max(1, int(a * SR)); e[:na] = np.linspace(0, 1, na)
    if r: nr = min(n, int(r * SR)); e[-nr:] *= np.linspace(1, 0, nr) ** 2
    return e


def _lp(x, cut):
    """Passe-bas à une pôle, coupure variable (scalaire ou tableau)."""
    cut = np.broadcast_to(np.asarray(cut, float), x.shape)
    a = np.exp(-2 * np.pi * cut / SR); y = np.zeros_like(x); s = 0.0
    for i in range(len(x)): s = (1 - a[i]) * x[i] + a[i] * s; y[i] = s
    return y


def _bp(x, lo, hi): return _lp(x, hi) - _lp(x, lo)


def _sweep(f0, f1, d, curve=1.0):
    t = _t(d); u = (t / d) ** curve; f = f0 + (f1 - f0) * u
    return np.sin(2 * np.pi * np.cumsum(f) / SR)


def whoosh(d=0.42, lo=300, hi=3500):
    n = int(d * SR); u = np.linspace(0, 1, n)
    cut = lo + (hi - lo) * np.sin(np.pi * u) ** 1.5
    x = _lp(rng.standard_normal(n), cut) * np.sin(np.pi * u) ** 2
    return x / (np.abs(x).max() + 1e-9) * 0.8


def rise(d=1.0): return whoosh(d, 200, 6000) * np.linspace(0.3, 1, int(d * SR))


def pop(f0=900, f1=280, d=0.09): return _sweep(f0, f1, d, 0.5) * np.exp(-_t(d) * 30) * 0.8


def ding(f=1320, d=1.4):
    t = _t(d); x = sum(a * np.sin(2 * np.pi * f * m * t) * np.exp(-t * k) for a, m, k in ((1, 1, 3), (0.5, 2.76, 6), (0.25, 5.4, 9)))
    return x * _env(len(t), 0.002) * 0.45


def impact(d=0.6):
    t = _t(d); body = _sweep(90, 38, d, 0.4) * np.exp(-t * 7)
    n = _lp(rng.standard_normal(len(t)), 900) * np.exp(-t * 22) * 3
    x = body + n; return x / np.abs(x).max() * 0.95


def beep(f=1500, d=0.07): return np.sin(2 * np.pi * f * _t(d)) * _env(int(d * SR), 0.003, 0.03) * 0.35


def click(d=0.03): return _bp(rng.standard_normal(int(d * SR)), 1500, 6000) * np.exp(-_t(d) * 120) * 4


def blink(): return np.concatenate([whoosh(0.18, 400, 2500) * 0.6, click()])


def scrub(d=0.9):
    n = int(d * SR); t = _t(d)
    x = _bp(rng.standard_normal(n), 1800, 5000) * (0.55 + 0.45 * np.sin(2 * np.pi * 11 * t)) ** 2
    return x / np.abs(x).max() * 0.6 * _env(n, 0.03, 0.15)


def hum(d=2.4):
    t = _t(d); x = sum(np.sin(2 * np.pi * 50 * k * t) / k for k in (1, 2, 3, 5))
    return x / np.abs(x).max() * 0.35 * _env(len(t), 0.1, 1.2)


def sparkle(d=0.9, n=16):
    out = np.zeros(int(d * SR))
    for k in range(n):
        f = rng.uniform(2500, 6500); s = int(rng.uniform(0, d - 0.15) * SR); b = np.sin(2 * np.pi * f * _t(0.15)) * np.exp(-_t(0.15) * 30)
        out[s:s + len(b)] += b * 0.25
    return out


def powerdown(d=0.8): return _sweep(520, 70, d, 0.6) * np.exp(-_t(d) * 3) * 0.45


def heartbeat():
    t = _t(0.18); th = np.sin(2 * np.pi * 55 * t) * np.exp(-t * 25)
    out = np.zeros(int(0.5 * SR)); out[:len(th)] += th; s = int(0.22 * SR); out[s:s + len(th)] += th * 0.7
    return out * 0.9


def flip(): return _bp(rng.standard_normal(int(0.05 * SR)), 800, 5000) * np.exp(-_t(0.05) * 70) * 2.5


def unroll(): return whoosh(0.5, 200, 1800) * 0.7


KINDS = dict(whoosh=whoosh, rise=rise, pop=pop, ding=ding, impact=impact, beep=beep, click=click, blink=blink, scrub=scrub,
             hum=hum, sparkle=sparkle, powerdown=powerdown, heartbeat=heartbeat, flip=flip, unroll=unroll)


def read_wav(p):
    w = wave.open(p); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    if w.getnchannels() == 2: a = a.reshape(-1, 2).mean(1)
    assert w.getframerate() == SR; return a


def mix(voice_wav, events, out_wav, level=0.32):
    v = read_wav(voice_wav); fx = np.zeros(len(v) + SR * 2)
    for t0, kind, g in events:
        x = KINDS[kind]() if isinstance(kind, str) else kind
        s = int(t0 * SR); e = min(len(fx), s + len(x)); fx[s:e] += x[:e - s] * g
    fx = fx[:len(v)]; fx = fx / (np.abs(fx).max() + 1e-9) * level
    out = v + fx; pk = np.abs(out).max()
    if pk > 0.98: out *= 0.98 / pk
    w = wave.open(out_wav, 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((out * 32767).astype(np.int16).tobytes()); w.close()
