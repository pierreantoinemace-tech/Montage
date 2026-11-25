"""« Le monde va mal… et il va mieux » v3 — abstrait et poétique, voix d'un seul tenant (pas de calage sur le son), perso d'origine au haut plus étroit."""
import math, os, random, sys, json, subprocess, importlib.util
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__))
_s = importlib.util.spec_from_file_location('monde_film', os.path.join(HERE, 'film.py'))
F = importlib.util.module_from_spec(_s); _s.loader.exec_module(F)
RV = F.RV
import haut_etroit
haut_etroit.appliquer(RV.pd)                               # perso d'origine, haut plus étroit
RV.bp = lambda t: 0.0                                       # plus aucune pulsation calée sur le son
F.HERE = os.path.join(HERE, 'naturel'); WORDS = F.load_words(); F.HERE = HERE   # mots sur la voix naturelle
RV.WORDS = WORDS; F.X.WORDS = [(w, s, k) for w, s, e, k in WORDS]
import numpy as np, skia
from lib import P, C, mix, lin, rad, circle, ease, ease_out
W, H, SC, OW_, OH_, PX, PY = RV.W, RV.H, RV.SC, RV.OW_, RV.OH_, RV.PX, RV.PY
CREAM, GOLD, OUT, BIG = RV.CREAM, RV.GOLD, RV.OUT, RV.BIG
clamp, hero, kid, bp, pop, sym, opath, rect = RV.clamp, RV.hero, RV.kid, RV.bp, RV.pop, RV.sym, RV.opath, RV.rect
banded_sky, hill, striped_sun = RV.banded_sky, RV.hill, RV.striped_sun
RED = '#C8505A'; INK = '#14101E'
FPS, DUR = 30, 55.5


# ---------------- vocabulaire abstrait ----------------
def flow(cv, t, n, col, a, seed, k=0.0, area=(-100, -100, W + 100, H + 100), steps=46, w=1.8, speed=1.0):
    rnd = random.Random(seed)
    for _ in range(n):
        x, y = rnd.uniform(area[0], area[2]), rnd.uniform(area[1], area[3]); p = skia.Path(); p.moveTo(x, y)
        for _ in range(steps):
            ang = (math.sin(x * 0.005 + k + t * 0.25 * speed) * 0.9 + math.cos(y * 0.004 - k * 0.7 - t * 0.18 * speed) * 0.8) * math.pi
            x += 10 * math.cos(ang); y += 10 * math.sin(ang); p.lineTo(x, y)
        cv.drawPath(p, P(col, a, stroke=w))


def crack(cv, x, y, prog, seed, col=RED, length=700, w=6):
    if prog <= 0: return
    rnd = random.Random(seed)
    def branch(x, y, ang, L, depth, pr):
        pts = [(x, y)]; n = 9
        for i in range(n):
            ang += rnd.uniform(-0.6, 0.6); x += math.cos(ang) * L / n; y += math.sin(ang) * L / n; pts.append((x, y))
        m = max(2, int(len(pts) * min(1, pr)))
        p = skia.Path(); p.moveTo(*pts[0])
        for q in pts[1:m]: p.lineTo(*q)
        cv.drawPath(p, P(OUT, 255, stroke=w + 6)); cv.drawPath(p, P(col, 255, stroke=w))
        if depth < 2:
            for j in (3, 6):
                if j < m: branch(*pts[j], ang + rnd.choice((-1, 1)) * rnd.uniform(0.5, 1.1), L * 0.5, depth + 1, (pr - j / n) * 2)
    branch(x, y, rnd.uniform(0, 6.28), length, 0, prog)


def shards(cv, x, y, n, u, seed, col=RED, a=255, size=40):
    rnd = random.Random(seed)
    for k in range(n):
        g = rnd.uniform(0, 6.28); d = u * rnd.uniform(80, 520); r = rnd.uniform(0.5, 1.2) * size * (1 - 0.4 * u)
        cx, cy = x + math.cos(g) * d, y + math.sin(g) * d; rot = rnd.uniform(0, 6.28) + u * 3
        pts = [(cx + r * math.cos(rot + j * 2.1 + rnd.uniform(-0.3, 0.3)), cy + r * math.sin(rot + j * 2.1)) for j in range(3)]
        p = skia.Path(); p.moveTo(*pts[0]); p.lineTo(*pts[1]); p.lineTo(*pts[2]); p.close()
        opath(cv, p, col if k % 3 else INK, 4, a)


def rings(cv, x, y, n, t, col=GOLD, a=255, base=24, gap=16):
    for i in range(n):
        r = base + i * gap
        p = skia.Path()
        for j in range(61):
            g = j / 60 * 2 * math.pi; rr = r * (1 + 0.04 * math.sin(g * 5 + i * 0.7))
            (p.moveTo if j == 0 else p.lineTo)(x + rr * math.cos(g), y + rr * 0.92 * math.sin(g))
        p.close(); cv.drawPath(p, P(mix(col, '#6A5A3A', i / max(1, n)), a, stroke=3 if i % 4 else 5))


def vine(cv, x, y, g, t, col=GOLD, scale=1.0):
    """Spirale dorée qui pousse doucement (la « pousse » abstraite)."""
    p = skia.Path(); n = int(10 + 150 * g)
    for i in range(n):
        u = i / 160; ang = -math.pi / 2 + u * 9 + 0.1 * math.sin(t); r = 320 * scale * u ** 0.8
        px, py = x + math.cos(ang) * r * 0.6 + 40 * math.sin(u * 7 + t * 0.5) * u, y - u * 650 * scale + math.sin(ang) * r * 0.25
        (p.moveTo if i == 0 else p.lineTo)(px, py)
    cv.drawPath(p, P(OUT, 255, stroke=13)); cv.drawPath(p, P(col, 255, stroke=6))
    if n > 12:
        pm = skia.PathMeasure(p, False); L = pm.getLength()
        for j in range(1, 6):
            if j / 6 < g:
                pos, tan = pm.getPosTan(L * j / 6)
                RV.sym(cv, 'star4', pos.x(), pos.y(), 12 + 4 * bp(t), 0, CREAM, t)


def orb(cv, x, y, r, lit, t, ink=0.0):
    if lit > 0:
        for j in range(4): cv.drawCircle(x, y, r * (1.2 + j * 0.45) * (1 + 0.08 * bp(t)), P(GOLD, int(40 * lit)))
    cv.drawCircle(x, y, r, P(mix('#3A3550', '#FFE7A0', lit))); cv.drawCircle(x, y, r, P(OUT, 255, stroke=5))
    cv.drawCircle(x, y, r * 0.35, P(mix('#2A2640', '#FFFFFF', lit)))
    if ink > 0:
        rnd = random.Random(int(x))
        for k in range(7):
            g = k * 0.9 + t * 0.6; d = r * (0.9 + 0.5 * math.sin(t + k))
            cv.drawCircle(x + math.cos(g) * d, y + math.sin(g) * d, r * 0.5 * ink, P(INK, int(230 * ink)))


def paper_bird(cv, x, y, s, t, ph, a=255):
    flap = math.sin(t * 6 + ph)
    body = skia.Path(); body.moveTo(x - s, y); body.lineTo(x + s, y - 0.1 * s); body.lineTo(x + 0.1 * s, y + 0.25 * s); body.close()
    w1 = skia.Path(); w1.moveTo(x - 0.3 * s, y - 0.02 * s); w1.lineTo(x + 0.4 * s, y - 0.05 * s); w1.lineTo(x - 0.1 * s, y - 0.9 * s * flap); w1.close()
    opath(cv, body, '#EDE6D8', 4, a); opath(cv, w1, '#D8D0C0', 4, a)


def glyph_line(cv, x, y, w, lit, t, seed):
    rnd = random.Random(seed); xx = x
    while xx < x + w:
        L = rnd.uniform(16, 60)
        cv.drawLine(xx, y, min(x + w, xx + L), y, P(mix('#3A3550', GOLD, lit), 255, stroke=9))
        xx += L + 18
    if lit > 0.5:
        for k in range(3):
            u = (t * 0.4 + k / 3 + seed * 0.1) % 1
            circle(cv, x + w * ((seed * 0.37 + k * 0.3) % 1), y - u * 160, 5 * (1 - u), GOLD, int(255 * (1 - u)))


def sky(cv, t, cols, wav=18):
    banded_sky(cv, cols, -600, 1700, t, wav=wav)


# ---------------- scènes ----------------
def s_infos(cv, t, lt):
    th = ease(clamp((t - 5.3) / 2.5))
    sky(cv, t, [mix(c, '#05040A', 0.35 * th) for c in ['#08070F', '#0E0B18', '#140F22', '#1A132C', '#201634', '#26193C']])
    flow(cv, t, 70 + int(50 * th), '#2E2844', 255, 1, speed=1 + th)
    crack(cv, 820, 120, clamp(t / 0.6), 3, length=620)                    # la 1re image : une fissure frappe le ciel
    for x, y, t0, sd in ((160, 420, 2.71, 11), (900, 640, 3.55, 12), (420, 220, 4.27, 13)):
        crack(cv, x, y, clamp((t - t0) / 0.35), sd)
    if t > 4.27: shards(cv, PX, 300, 14, clamp((t - 4.27) / 4), 7, a=255)
    for j in range(5):                                         # anneaux de pression autour de la tête
        r = 260 + j * 70 - 60 * th * (1 - j / 5) + 6 * math.sin(t * 2 - j)
        cv.drawCircle(PX, PY, r, P(RED if j % 2 else '#4A3A5A', int(150 * th), stroke=3))
    hero(cv, t, PX, PY + 0.55 * 230, 230, 'lidded' if t > 7.9 else 'open', look=(0.0, 0.8), arms='phone')


def s_histoire(cv, t, lt):
    sky(cv, t, ['#08070F', '#0E0B18', '#140F22', '#1A132C', '#201634', '#26193C'])
    op = ease(clamp(lt / 1.4))                                  # le rideau de lignes s'écarte
    for k in range(60):
        x = k * 19 - 30; side = -1 if x < PX else 1
        xx = x + side * op * (380 - abs(x - PX) * 0.3)
        cv.drawLine(xx, -200, xx + 10 * math.sin(t + k), H + 200, P('#1E1A2C', 255, stroke=8))
    th = clamp(lt / 1.0)
    cv.drawLine(PX, -50, PX, -50 + 1300 * th, P(OUT, 255, stroke=12)); cv.drawLine(PX, -50, PX, -50 + 1300 * th, P(GOLD, 255, stroke=5))
    if t > 13.59: shards(cv, 230, 1150, 18, clamp((t - 13.59) / 1.5), 21, size=46)
    if t > 13.59: crack(cv, 230, 1150, clamp((t - 13.59) / 0.3), 22, length=300, w=5)
    vine(cv, 800, 1700, 0.25 + 0.75 * ease(clamp((t - 14.45) / 2.6)), t, scale=1.0)
    hero(cv, t, PX, 1560, 180, 'open', look=(-0.8, 0.0) if t < 14.4 else (0.8, 0.2))


def s_une(cv, t, lt):
    sky(cv, t, ['#07060E', '#0C0A16', '#120E1E', '#181226', '#1E162E', '#241A36'])
    flow(cv, t, 50, '#1E1A2E', 255, 31)
    fx, fy, fw, fh = 110, 900, 420, 560                         # « la une » : un cadre sombre où éclate le rouge
    opath(cv, rect(fx, fy, fw, fh, 8), '#0A0812', 8)
    cv.save(); cv.clipPath(rect(fx, fy, fw, fh, 8), doAntiAlias=True)
    shards(cv, fx + fw / 2, fy + fh / 2, 20, 0.2 + 0.15 * math.sin(t * 3), 41, size=50)
    crack(cv, fx + fw / 2, fy + fh / 2, 1, 42, length=300, w=5)
    cv.restore()
    for k in range(3): cv.drawLine(fx + 20, fy - 40 - k * 26, fx + fw - 20 - k * 80, fy - 40 - k * 26, P(CREAM, 200, stroke=8))
    n = int(32 * ease(clamp((t - 18.0) / 1.6)))                 # 30 ans : des cernes d'arbre qui s'ajoutent lentement
    fade = 1 - 0.75 * clamp((t - 19.65) / 0.5)
    rings(cv, 780, 1180, n, t, a=int(255 * fade), base=14, gap=11)
    if n: circle(cv, 780, 1180, 8, GOLD, int(255 * fade))


def s_planete(cv, t, lt):
    sky(cv, t, ['#03030A', '#070818', '#0B0E24', '#0F1430', '#131A3A', '#172044'], wav=30)
    RV.twinkle(cv, 22, 110, (-50, -50, W + 50, H + 50), t)
    lights = ease(clamp((t - 21.4) / 2.0)); ink = 1 - ease(clamp((t - 21.2) / 2.0))
    x, y, r = PX, 1250, 420 + 5 * bp(t)
    opath(cv, skia.Path().addCircle(x, y, r), '#121A34', 8)
    cv.save(); cv.clipPath(skia.Path().addCircle(x, y, r), doAntiAlias=True)
    for k in range(-6, 7):                                      # latitudes et méridiens fins
        yy = y + k * r / 7; rx = math.sqrt(max(0, r * r - (yy - y) ** 2))
        cv.drawOval(skia.Rect.MakeLTRB(x - rx, yy - 10, x + rx, yy + 10), P('#24345A', 255, stroke=3))
    for k in range(8):
        ph = (k / 8 + t * 0.03) % 1; rx = r * abs(math.cos(ph * math.pi))
        cv.drawOval(skia.Rect.MakeLTRB(x - rx, y - r, x + rx, y + r), P('#24345A', 255, stroke=3))
    flow(cv, t, 40, '#2A3A66', 255, 51, area=(x - r, y - r, x + r, y + r), steps=30, w=2.5)
    rnd = random.Random(5)
    for k in range(300):
        px, py = x + rnd.uniform(-r, r), y + rnd.uniform(-r, r)
        if (px - x) ** 2 + (py - y) ** 2 > (r * 0.96) ** 2: continue
        if rnd.random() < lights: circle(cv, px, py, rnd.uniform(3, 7) * (1 + 0.4 * bp(t) * (k % 3 == 0)), GOLD)
    cv.restore()
    if ink > 0:                                                  # l'encre sombre se défait en particules
        rnd = random.Random(8)
        for k in range(160):
            g = rnd.uniform(0, 6.28); d = r * rnd.uniform(0.7, 1.15) + (1 - ink) * rnd.uniform(100, 600)
            circle(cv, x + math.cos(g) * d, y + math.sin(g) * d, rnd.uniform(8, 26) * ink, INK, int(255 * ink))


ORBS = [(150 + (k % 5) * 195, 1250 + (k // 5) * 300 + 40 * math.sin(k * 1.3)) for k in range(10)]


def s_pauvrete(cv, t, lt):
    sky(cv, t, ['#0A0918', '#100E22', '#16122C', '#1C1636', '#221A40', '#281E48'])
    flow(cv, t, 60, '#24203A', 255, 61)
    for i in range(3):                                         # rubans lents
        y0 = 650 + i * 110
        top = [(x, y0 + 40 * math.sin(x * 0.006 + t * 0.3 + i)) for x in range(-100, W + 140, 30)]
        p = skia.Path(); p.moveTo(*top[0])
        for q in top[1:]: p.lineTo(*q)
        for x, yy in reversed(top): p.lineTo(x, yy + 26 + 10 * math.sin(x * 0.01 + i))
        p.close(); opath(cv, p, ['#2A2244', '#22284A', '#30244C'][i], 4)
    poor = 4 if t < 27.95 else (1 if t > 28.6 else 4 - int(3 * (t - 27.95) / 0.66))
    for k, (x, y) in enumerate(ORBS):
        ink = 1.0 if k < poor else (max(0.0, 1 - (t - 27.95) * 2) if k < 4 else 0)
        lit = 0.0 if k < poor else (clamp((t - 27.95) * 2) if k < 4 else 0.85)
        orb(cv, x, y + 10 * math.sin(t * 1.2 + k), 52, lit, t, ink)


def s_enfants(cv, t, lt):
    sky(cv, t, ['#1A1430', '#241C3E', '#2E224A', '#3A2A56', '#463260', '#523A6A'])
    flow(cv, t, 50, '#3A3058', 255, 71)
    shrink = 1 - 0.58 * ease(clamp((t - 32.8) / 0.9))
    rnd = random.Random(4)
    for k in range(40):                                         # une ombre d'encre qui se réduit de moitié
        g = rnd.uniform(0, 6.28); d = rnd.uniform(0, 330) * shrink
        circle(cv, 540 + math.cos(g) * d, 560 + math.sin(g) * d * 0.7, rnd.uniform(30, 70) * shrink, INK, 240)
    for k in range(3):
        x = 300 + k * 240
        orb(cv, x, 1180 + 20 * math.sin(t * 2 + k), 26, 1.0, t)
    kid(cv, t, 540, 1500, 130, 'open', look=(0.0, -0.7), arms='wave')
    hill(cv, 1830, 25, 0.008, 4.0, '#1E1834', '#26203E', t, n=3)


def s_lire(cv, t, lt):
    sky(cv, t, ['#0C0A1C', '#120F26', '#181430', '#1E183A', '#241C44', '#2A204C'])
    flow(cv, t, 40, '#24203A', 255, 81)
    n = 2 if t < 37.6 else min(9, 2 + int((t - 37.6) * 14))
    for k in range(10):
        glyph_line(cv, 140, 1000 + k * 82, 800 - (k % 3) * 120, 1.0 if k < n else 0.0, t, k)


def s_journaux(cv, t, lt):
    sky(cv, t, ['#1C1632', '#261E40', '#30264C', '#3A2C58', '#443262', '#4E386C'])
    flow(cv, t, 50, '#3A3058', 255, 91)
    gone = ease(clamp((t - 46.03) / 0.8))
    idx = int(max(0, (t - 39.9) / 0.35))
    for k in range(1, 8): opath(cv, rect(340, 1660 - k * 34, 400, 32, 4), '#EDE6D8', 5)   # la pile de journaux
    for k in range(min(1 + idx // 2, 9)):                       # chaque matin, un journal heureux s'envole
        born = 39.9 + k * 0.7; age = t - born
        x = 540 + 380 * math.sin(k * 1.9) * min(1, age * 0.4); y = 1500 - age * 160 - k * 10
        if gone > 0:
            rnd = random.Random(k)
            for j in range(6): circle(cv, x + rnd.uniform(-60, 60) * (1 + gone), y + rnd.uniform(-40, 40) - gone * 120, 5, CREAM, int(255 * (1 - gone)))
        else:
            paper_bird(cv, x, y, 95, t, k)


def s_lumieres(cv, t, lt):
    dawn = ease(clamp((t - 51.2) / 2.5))
    sky(cv, t, [mix(a, b, dawn) for a, b in zip(['#08070F', '#0E0B1A', '#141026', '#1A1432', '#20183C', '#261C46'],
                                                   ['#2A2244', '#3E2E56', '#564068', '#705478', '#8C6886', '#A87E92'])])
    flow(cv, t, 70, mix('#2A2440', '#8C7090', dawn), 255, 101)
    on = ease(clamp((t - 51.2) / 1.4))
    rnd = random.Random(31)
    for k in range(380):                                        # des lucioles qui montent
        x = rnd.uniform(-60, W + 60); sp = rnd.uniform(30, 90)
        y = 1950 - ((t - 47.0) * sp + rnd.uniform(0, 900)) % 1700
        if rnd.random() < 0.12 + 0.88 * on:
            r = rnd.uniform(2.5, 6.5) * (1 + 0.3 * bp(t) * (k % 4 == 0))
            cv.drawLine(x, y, x, y + r * 5, P(GOLD, 120, stroke=r * 0.8)); circle(cv, x, y, r, GOLD)
    hero(cv, t, PX, 1600, 200, 'open', look=(0.0, 0.6) if t < 51.2 else (0.0, -0.4))


SCENES = [(0.0, s_infos, None), (9.85, s_histoire, 'iris'), (16.1, s_une, 'wave'), (20.25, s_planete, 'flash'),
          (23.7, s_pauvrete, 'wave'), (30.65, s_enfants, 'iris'), (34.35, s_lire, 'wave'), (39.7, s_journaux, 'iris'), (47.0, s_lumieres, 'iris')]
RV.SCENES = SCENES


def frame(fi):
    return F.frame(fi)

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--preview':
        from PIL import Image
        for ts in sys.argv[2].split(','):
            arr = np.frombuffer(frame(int(float(ts) * FPS)), np.uint8).reshape(OH_, OW_, 4)
            Image.fromarray(arr[..., :3]).resize((540, 960), Image.LANCZOS).save(os.path.join(sys.argv[3], f'pv_{ts}.png'))
        sys.exit()
    out = os.path.join(HERE, 'monde_v3_4k.mp4'); hd = os.path.join(HERE, 'monde_v3_1080p.mp4')
    n = int(DUR * FPS)
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', f'{OW_}x{OH_}', '-r', str(FPS), '-i', '-',
                           '-i', os.path.join(HERE, 'voice_naturelle.wav'),
                           '-filter_complex', '[0:v]format=yuv420p,split=2[v4][vh];[vh]scale=1080:1920:flags=lanczos[v1]',
                           '-map', '[v4]', '-map', '1:a', '-c:v', 'libx264', '-profile:v', 'high', '-level:v', '5.1', '-preset', 'slow', '-crf', '15',
                           '-maxrate', '25M', '-bufsize', '50M', '-c:a', 'aac', '-b:a', '256k', '-t', str(DUR), '-movflags', '+faststart', out,
                           '-map', '[v1]', '-map', '1:a', '-c:v', 'libx264', '-profile:v', 'high', '-level:v', '4.2', '-preset', 'slow', '-crf', '14',
                           '-maxrate', '20M', '-bufsize', '40M', '-c:a', 'aac', '-b:a', '256k', '-t', str(DUR), '-movflags', '+faststart', hd],
                          stdin=subprocess.PIPE)
    with Pool(3) as pool:
        for i, b in enumerate(pool.imap(frame, range(n), chunksize=2)):
            ff.stdin.write(b)
            if i % 300 == 0: print(i, '/', n, flush=True)
    ff.stdin.close(); ff.wait()
    print('ok')
