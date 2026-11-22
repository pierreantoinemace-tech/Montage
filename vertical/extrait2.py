"""Extrait test v2 : 4K vertical (2160x3840), 30 fps, net, dynamique, plein de symboles, perso aux trois yeux."""
import math, os, random, sys, subprocess, importlib.util
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__))
for d in ('../etoiles', '../calendrier', '../temps'):
    sys.path.insert(0, os.path.join(HERE, d))
sys.path.insert(0, HERE)
import lib
lib.W, lib.H = 1080, 1920
import numpy as np, skia
from lib import P, C, mix, lin, rad, circle, ease
import symboles as SY
from symboles import sym, PAL, OUT
_s = importlib.util.spec_from_file_location('pfp_dark', os.path.join(HERE, '..', 'profil', 'pfp_dark.py'))
pd = importlib.util.module_from_spec(_s); _s.loader.exec_module(pd)
pd.S = 1990                                  # la robe descend jusqu'en bas du format vertical


def sglow(cv, x, y, r, color, a=200):
    """Halo NET : disques concentriques à bords francs (pas de dégradé flou)."""
    for k in range(4):
        cv.drawCircle(x, y, r * (1 - k * 0.22), P(color, int(a * 0.13)))
pd.glow = sglow

W, H = 1080, 1920            # coordonnées de dessin
SC = 2                       # rendu 4K
OW_, OH_ = W * SC, H * SC
FPS, DUR = 30, 12.0
FONT = skia.Typeface.MakeFromFile(os.path.join(HERE, '..', 'etoiles', 'fonts', 'Rubik-700.ttf'))
PX, PY = W / 2, 1150         # le troisième œil = le fil rouge
HS = 230                     # taille du perso
HERO = dict(skin='#7AC8D8', hair='#14304A', robe='#3A0E5A')
OTHER = dict(skin='#E8B0C8', hair='#4A2050', robe='#1E4A5A')
TY = H * 0.40

WORDS = [('TU', .2, 0), ('CROIS', .5, 0), ('AVOIR', .9, 0), ('LE', 1.25, 0), ('TEMPS', 1.5, 1), ('', 2.6, 0),
         ('MAIS', 3.0, 0), ('TU', 3.3, 0), ('ES', 3.55, 0), ('SEUL', 3.8, 1), ('DANS', 4.6, 0), ('TA', 4.85, 0), ('TÊTE', 5.1, 0), ('', 5.6, 0),
         ('ET', 6.0, 0), ('TES', 6.25, 0), ('PENSÉES', 6.5, 1), ('TOURNENT', 7.25, 0), ('', 7.95, 0),
         ('JUSQU\'À', 8.7, 0), ('CE', 9.1, 0), ('QUE', 9.3, 0), ('QUELQU\'UN', 9.55, 0), ('TE', 10.2, 0), ('RÉPONDE', 10.45, 1), ('', 11.8, 0)]
T_AB, T_BC, T_CD = (2.45, 2.95), (5.45, 5.95), (7.95, 8.6)


def clamp(x): return max(0.0, min(1.0, x))
def back(x):
    x = clamp(x); c = 1.9
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2


def key_pulse(t):
    v = 0
    for w, s, k in WORDS:
        if k and t >= s: v = max(v, math.exp(-(t - s) * 3.0))
    return v


def bg(cv, cols):
    cv.drawRect(skia.Rect.MakeLTRB(-600, -600, W + 600, H + 600), P(shader=lin(0, 0, 0, H, [C(c) for c in cols])))


def hero(cv, t, cx, cy, s, eyes='open', look=None, arms=None, pal=HERO, seed=5):
    cy += 5 * math.sin(t * 2.1)
    pd.dreamer(cv, cx, cy, s, skin=pal['skin'], hair=pal['hair'], robe=pal['robe'], eyes=eyes, third_eye=True,
               seed=seed, t=t, arms=arms, look=look)
    # troisième œil qui pulse sur les mots-clés (anneaux nets)
    k = key_pulse(t); ex, ey = cx, cy - 0.55 * s
    for j in range(3):
        r = s * (0.2 + j * 0.09) * (1 + 0.6 * k) + 4 * math.sin(t * 4 - j)
        cv.drawCircle(ex, ey, r, P('#FFE680', int(200 - j * 60), stroke=3))


# ---------------- A. TEMPS : vol à travers un tunnel de symboles ----------------
RA = random.Random(11)
FLY = [(RA.uniform(0, 2 * math.pi), RA.random(), RA.choice(['clock', 'hourglass', 'spiral', 'star4', 'eye', 'infinity', 'moon', 'star8', 'planet']),
        RA.choice(PAL), RA.uniform(-120, 120)) for _ in range(90)]


def s_temps(cv, t, speed=1.0):
    bg(cv, ['#03080B', '#071318', '#0C1A20'])
    f = (t * 1.4 * speed) % 1.0
    for i in range(38, -1, -1):
        j = i - f
        if j < 0.05: continue
        s = 18 * j * 1.12 ** (j * 0.35); rot = j * 9 + t * 40
        cv.save(); cv.translate(PX, PY - j * 3); cv.rotate(rot)
        r = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-s / 2, -s / 2, s, s), s * 0.22, s * 0.22)
        cv.drawRRect(r, P('#123038' if i % 2 else '#0A1C22'))
        cv.drawRRect(r, P(mix('#9FE8D8', '#3C6E78', min(1, j / 30)), 230, stroke=2.4))
        cv.restore()
    items = []
    for th, ph, kind, col, spin in FLY:
        z = (t * 0.42 * speed + ph) % 1.0
        items.append((z, th, kind, col, spin, ph))
    for z, th, kind, col, spin, ph in sorted(items):
        r = 70 + z ** 2.2 * 1400
        sym(cv, kind, PX + math.cos(th) * r, PY + math.sin(th) * r * 1.25, 6 + z ** 2 * 130, spin * t, col, t, 255 * clamp(z * 5), seed=ph * 10)
    k = key_pulse(t)
    for j in range(8):
        a = j * math.pi / 4 + t * 1.5
        sym(cv, 'star4', PX + math.cos(a) * (120 + 30 * k), PY + math.sin(a) * (120 + 30 * k), 16 + 10 * k, 0, '#FFE680', t)
    sglow(cv, PX, PY, 110 + 60 * k, '#FFE680', 200)
    sym(cv, 'eye', PX, PY, 62 + 30 * k, 0, '#FFD86A', t, seed=3)


# ---------------- B. SEUL : mandala de symboles derrière le perso ----------------
def mandala(cv, t, spread=1.0, a=255):
    for i in range(30):
        r = (60 + i * 26 + 10 * math.sin(t * 3 - i * 0.35)) * spread
        cv.drawCircle(PX, PY, r, P(mix('#C8B8FF', '#3E4A7A', i / 30), int(a * max(0, 0.75 - i * 0.022)), stroke=2.4 if i % 3 else 4))
    rings = [(12, 330, 0.35, 'eye', 34, '#C8B8FF'), (20, 460, -0.25, 'star4', 22, '#F0EBBE'), (8, 580, 0.18, 'moon', 40, '#A8D8FF'),
             (16, 690, -0.12, 'tri_eye', 34, '#FFB8D0'), (24, 820, 0.09, 'diamond', 24, '#9FE8D8'), (10, 950, -0.07, 'planet', 46, '#FFD8A0')]
    for n, R, sp, kind, sz, col in rings:
        for k in range(n):
            g = k * 2 * math.pi / n + t * sp
            puls = 1 + 0.18 * math.sin(t * 4 + k)
            sym(cv, kind, PX + math.cos(g) * R * spread, PY + math.sin(g) * R * spread, sz * puls * spread, math.degrees(g) + 90 if kind in ('moon', 'tri_eye') else t * 30, col, t, a, seed=k)


def s_seul(cv, t, spread=1.0):
    bg(cv, ['#05040D', '#0D0A20', '#170F2A'])
    rnd = random.Random(7)
    for _ in range(14):
        x, y = rnd.uniform(60, W - 60), rnd.uniform(120, 520); ph = rnd.uniform(0, 6)
        sym(cv, 'eye', x + 16 * math.sin(t * 0.6 + ph), y + 10 * math.cos(t * 0.5 + ph), rnd.uniform(8, 13), 0, '#6E6A92', t, 200, seed=ph)
    mandala(cv, t, spread)
    hero(cv, t, PX, PY + 0.55 * HS, HS, 'open', look=(0.5, -0.9))


# ---------------- C. PENSÉES : vortex de symboles qui sort du troisième œil ----------------
RC = random.Random(21)
VORTEX = [(RC.randrange(5), RC.random(), RC.choice(SY.KINDS), RC.choice(PAL), RC.uniform(-200, 200)) for _ in range(110)]


def s_pensees(cv, t, boost=0.0):
    bg(cv, ['#140A22', '#1E0E30', '#2A1238'])
    cv.save(); cv.translate(PX, PY); cv.rotate(t * 25)
    for k in range(24):
        p = skia.Path(); p.moveTo(0, 0)
        a0, a1 = k * 15, k * 15 + 7.5
        p.lineTo(2600 * math.cos(math.radians(a0)), 2600 * math.sin(math.radians(a0)))
        p.lineTo(2600 * math.cos(math.radians(a1)), 2600 * math.sin(math.radians(a1))); p.close()
        cv.drawPath(p, P('#2C1644'))
    cv.restore()
    hero(cv, t, PX, PY + 0.55 * HS, HS, 'closed')
    sp = 1 + 2.5 * boost
    for arm in range(5):                     # bras de spirale nets
        pth = skia.Path()
        for i in range(80):
            u = i / 79; g = arm * 2 * math.pi / 5 + u * 5 + t * 1.2 * sp; r = 30 + u ** 1.3 * 1300
            (pth.moveTo if i == 0 else pth.lineTo)(PX + math.cos(g) * r, PY + math.sin(g) * r)
        cv.drawPath(pth, P(OUT, 255, stroke=11)); cv.drawPath(pth, P(PAL[arm], 255, stroke=5))
    for arm, ph, kind, col, spin in sorted(VORTEX, key=lambda v: (t * 0.5 * sp + v[1]) % 1):
        u = (t * 0.5 * sp + ph) % 1.0
        g = arm * 2 * math.pi / 5 + u * 5 + t * 1.2 * sp + 0.25; r = 30 + u ** 1.3 * 1300
        sym(cv, kind, PX + math.cos(g) * r, PY + math.sin(g) * r, 8 + u * 85, spin * t, col, t, 255 * clamp(u * 6), seed=ph * 7)


# ---------------- D. LIENS : version pâle, quelqu'un répond ----------------
RD = random.Random(31)
DRIFT = [(RD.uniform(0, W), RD.uniform(0, 2300), RD.choice(SY.KINDS), RD.choice(['#8C7FA6', '#B49AAE', '#7FA8B0', '#C8A070', '#9A8CC0']),
          RD.uniform(14, 40), RD.uniform(-60, 60)) for _ in range(46)]


def s_liens(cv, t):
    lt = t - T_CD[0]
    bg(cv, ['#F2ECDF', '#E4DDE6', '#D2CCDE'])
    cv.save(); cv.translate(PX, 1250); cv.rotate(t * 8)
    for k, R in enumerate((420, 270, 150)):          # fleur de vie géante, traits fins
        cv.rotate(15)
        for j in range(7):
            cx, cy = (0, 0) if j == 0 else (R * math.cos(j * math.pi / 3), R * math.sin(j * math.pi / 3))
            cv.drawCircle(cx, cy, R, P(['#CFC3DD', '#D9C6D2', '#C5CFDA'][k], 255, stroke=4))
    cv.restore()
    for x, y0, kind, col, sz, spin in DRIFT:
        y = (y0 - t * 70) % 2300 - 200
        sym(cv, kind, x + 20 * math.sin(t + y0), y, sz, spin * t, col, t, 230, seed=y0)
    ax, ay, sa = 320, 1230, 175
    pb = ease(clamp((lt - 0.5) / 0.9))
    bx, by, sb = 1350 + (770 - 1350) * pb, 1420, 175
    hero(cv, t, ax, ay, sa, 'open', look=(0.8, 0.5), pal=HERO)
    if pb > 0: hero(cv, t, bx, by, sb, 'open', look=(-0.8, -0.4), pal=OTHER, seed=9)
    e1 = (ax, ay - 0.55 * sa + 5 * math.sin(t * 2.1)); e2 = (bx, by - 0.55 * sb + 5 * math.sin(t * 2.1))
    pt = ease(clamp((lt - 1.3) / 0.9))
    if pt > 0:
        rnd = random.Random(3)
        for k in range(36):
            off = rnd.uniform(-320, 320) + 40 * math.sin(t * 1.6 + k)
            p = skia.Path(); p.moveTo(*e1); p.cubicTo(e1[0] + 180, e1[1] + off, e2[0] - 180, e2[1] - off * 0.8, *e2)
            col = PAL[k % 6]
            for paint in (P(OUT, 255, stroke=7), P(col, 255, stroke=3)):
                if pt < 0.999: paint.setPathEffect(skia.TrimPathEffect.Make(0, pt))
                cv.drawPath(p, paint)
            if pt >= 0.999:
                pm = skia.PathMeasure(p, False); pos, _ = pm.getPosTan(((t * 0.4 + k * 0.137) % 1.0) * pm.getLength())
                sym(cv, 'star4', pos.x(), pos.y(), 11, 0, '#FFFFFF', t)
    bl = ease(clamp((lt - 2.2) / 0.8))
    if bl > 0:
        mx, my = (e1[0] + e2[0]) / 2, (e1[1] + e2[1]) / 2 - 40
        sym(cv, 'sun', mx, my, 70 * back(bl), t * 40, '#FFD8A0', t)
        for j in range(10):
            g = j * math.pi / 5 + t * 1.2
            sym(cv, 'star4', mx + math.cos(g) * 150 * bl, my + math.sin(g) * 150 * bl, 16 * bl, 0, PAL[j % 6], t)


# ---------------- composition ----------------
def zoomed(cv, fn, t, z, *a):
    cv.save(); cv.translate(PX, PY); cv.scale(z, z); cv.translate(-PX, -PY); fn(cv, t, *a); cv.restore()


def iris(cv, t, p, fn, col='#FFE680'):
    r = 1900 * ease(p) ** 1.3
    if r < 1: return
    cv.save(); cv.clipPath(skia.Path().addCircle(PX, PY, r), doAntiAlias=True); fn(cv, t); cv.restore()
    cv.drawCircle(PX, PY, r, P(OUT, 255, stroke=22)); cv.drawCircle(PX, PY, r, P(col, 255, stroke=8))
    for k in range(18):
        g = k * 2 * math.pi / 18 + t * 2
        sym(cv, 'star4' if k % 2 else 'eye', PX + math.cos(g) * r, PY + math.sin(g) * r, 26, 0, PAL[k % 6], t, seed=k)


def scene(cv, t):
    if t < T_AB[0]: s_temps(cv, t)
    elif t < T_AB[1]:
        p = (t - T_AB[0]) / (T_AB[1] - T_AB[0])
        zoomed(cv, s_temps, t, 1 + 5 * ease(p) ** 2, 1 + 2 * p); iris(cv, t, p, s_seul)
    elif t < T_BC[0]: s_seul(cv, t)
    elif t < T_BC[1]:
        p = (t - T_BC[0]) / (T_BC[1] - T_BC[0])
        s_seul(cv, t, 1 + 1.2 * ease(p)); iris(cv, t, p, s_pensees, '#C8B8FF')
    elif t < T_CD[0]: s_pensees(cv, t, clamp((t - 7.4) / 0.6))
    elif t < T_CD[1]:
        p = (t - T_CD[0]) / (T_CD[1] - T_CD[0])
        s_pensees(cv, t, 1.0); iris(cv, t, p, s_liens, '#F0EBBE')
    else: s_liens(cv, t)


def current_word(t):
    cur, idx = None, 0
    for i, (w, s, k) in enumerate(WORDS):
        if t >= s: cur, idx = (w, s, k), i
    return cur, idx


def draw_word(cv, t):
    cur, _ = current_word(t)
    if not cur or not cur[0]: return
    w, s, k = cur; age = t - s
    size = 200 if k else 165
    f = skia.Font(FONT, size); tw = f.measureText(w)
    if tw > 820: f.setSize(size * 820 / tw); tw = f.measureText(w)
    sc = 0.5 + 0.5 * back(age / 0.2)
    cv.save(); cv.translate(W / 2, TY); cv.scale(sc, sc); cv.rotate(-3 * math.exp(-age * 10) * (1 if k else 0))
    x, y = -tw / 2, f.getSize() * 0.35
    fs = f.getSize()
    out = P(OUT, 255, stroke=fs * 0.16); out.setStrokeJoin(skia.Paint.kRound_Join)
    cv.drawString(w, x + fs * 0.03, y + fs * 0.07, f, out)           # ombre portée nette
    cv.drawString(w, x + fs * 0.03, y + fs * 0.07, f, P(OUT))
    cv.drawString(w, x, y, f, out)
    cv.drawString(w, x, y, f, P('#FFE680' if k else '#F0EBBE'))
    cv.restore()


def frame(fi):
    t = fi / FPS
    surf = skia.Surface(OW_, OH_); cv = surf.getCanvas(); cv.scale(SC, SC)
    cur, idx = current_word(t)
    punch = math.exp(-(t - cur[1]) * 9) if cur and cur[0] else 0
    z = 1.03 + 0.05 * punch + 0.015 * math.sin(t * 0.9)
    rot = 0.9 * math.sin(t * 0.6) + 1.6 * punch * (1 if idx % 2 else -1)
    cv.save(); cv.translate(PX, PY); cv.rotate(rot); cv.scale(z, z)
    cv.translate(-PX + 12 * math.sin(t * 0.8), -PY + 14 * math.cos(t * 0.65))
    scene(cv, t); cv.restore()
    cv.drawRect(skia.Rect.MakeWH(W, H), P(shader=rad(W / 2, H / 2, 1250, [C('#000000', 0), C('#000000', 0), C('#000000', 70)], [0, 0.7, 1])))
    draw_word(cv, t)
    return surf.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType).tobytes()


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--preview':
        from PIL import Image
        for ts in sys.argv[2].split(','):
            arr = np.frombuffer(frame(int(float(ts) * FPS)), np.uint8).reshape(OH_, OW_, 4)
            Image.fromarray(arr[..., :3]).resize((540, 960), Image.LANCZOS).save(os.path.join(sys.argv[3], f'pv_{ts}.png'))
            if len(sys.argv) > 4: Image.fromarray(arr[..., :3]).save(os.path.join(sys.argv[3], f'full_{ts}.png'))
        sys.exit()
    out = os.path.join(HERE, 'extrait_test_4k.mp4')
    n = int(DUR * FPS)
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', f'{OW_}x{OH_}', '-r', str(FPS), '-i', '-',
                           '-f', 'lavfi', '-i', f'anullsrc=r=44100:cl=stereo', '-t', str(DUR),
                           '-c:v', 'libx264', '-preset', 'slow', '-tune', 'animation', '-crf', '15', '-maxrate', '55M', '-bufsize', '110M',
                           '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-movflags', '+faststart', out], stdin=subprocess.PIPE)
    with Pool(4) as pool:
        for i, b in enumerate(pool.imap(frame, range(n), chunksize=2)):
            ff.stdin.write(b)
            if i % 60 == 0: print(i, '/', n, flush=True)
    ff.stdin.close(); ff.wait(); print('ok', out)
