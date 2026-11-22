"""Extrait test animé (vertical 1080x1920, 60 fps) : TEMPS -> SEUL -> PENSÉES -> LIENS.
Fil rouge : le point de lumière (« toi »), toujours au même endroit. Du sombre vers le pâle."""
import math, os, random, sys, subprocess
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'etoiles'))
import lib
lib.W, lib.H = 1080, 1920
import numpy as np, skia
from lib import P, C, mix, lin, rad, glow, circle, ease
W, H, FPS = 1080, 1920, 60
FONT = skia.Typeface.MakeFromFile(os.path.join(HERE, '..', 'etoiles', 'fonts', 'Rubik-700.ttf'))
PX, PY = W / 2, 1150          # le point « toi »
TY = H * 0.40
DUR = 12.0

# (mot, début, clé)  — '' = rien à l'écran
WORDS = [('TU', .25, 0), ('CROIS', .55, 0), ('AVOIR', .95, 0), ('LE', 1.3, 0), ('TEMPS', 1.55, 1), ('', 2.6, 0),
         ('MAIS', 3.0, 0), ('TU', 3.3, 0), ('ES', 3.55, 0), ('SEUL', 3.8, 1), ('DANS', 4.6, 0), ('TA', 4.85, 0), ('TÊTE', 5.1, 0), ('', 5.6, 0),
         ('ET', 6.0, 0), ('TES', 6.25, 0), ('PENSÉES', 6.5, 1), ('TOURNENT', 7.25, 0), ('', 7.95, 0),
         ('JUSQU\'À', 8.7, 0), ('CE', 9.1, 0), ('QUE', 9.3, 0), ('QUELQU\'UN', 9.55, 0), ('TE', 10.2, 0), ('RÉPONDE', 10.45, 1), ('', 11.7, 0)]
# scènes et transitions : (début transition, fin transition)
T_AB, T_BC, T_CD = (2.4, 3.0), (5.4, 6.0), (7.85, 8.75)


def clamp(x): return max(0.0, min(1.0, x))
def path_of(pts, close=False):
    p = skia.Path(); p.moveTo(*pts[0])
    for q in pts[1:]: p.lineTo(*q)
    if close: p.close()
    return p
def smooth(pts, close=True):
    p = skia.Path(); n = len(pts)
    m = [((pts[i][0] + pts[(i + 1) % n][0]) / 2, (pts[i][1] + pts[(i + 1) % n][1]) / 2) for i in range(n)]
    p.moveTo(*m[-1])
    for i in range(n): p.quadTo(*pts[i], *m[i])
    p.close(); return p


def key_pulse(t):
    """0..1, pic quand un mot-clé apparaît puis décroît."""
    v = 0
    for w, s, k in WORDS:
        if k and t >= s: v = max(v, math.exp(-(t - s) * 3.0))
    return v


def the_point(cv, t, x=PX, y=PY, col='#F4F0FF', halo='#E8E3F5', s=1.0):
    k = key_pulse(t); br = 0.5 + 0.5 * math.sin(t * 2.2)
    glow(cv, x, y, (95 + 25 * br + 120 * k) * s, halo, int(150 + 80 * k))
    circle(cv, x, y, (13 + 3 * br + 8 * k) * s, col)


# ---------------- scènes ----------------
def s_temps(cv, t):
    cv.drawRect(skia.Rect.MakeWH(W, H), P(shader=lin(0, 0, 0, H, [C('#050A0E'), C('#0A1418'), C('#101A1E')])))
    f = (t * 0.9) % 1.0                    # boucle d'aspiration vers le centre
    for i in range(34, -1, -1):
        j = i - f
        if j < 0.05: continue
        s = 18 * j * 1.12 ** (j * 0.35); rot = j * 7 + t * 14
        cv.save(); cv.translate(PX, PY - j * 4); cv.rotate(rot)
        r = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-s / 2, -s / 2, s, s), s * 0.22, s * 0.22)
        cv.drawRRect(r, P('#1C3038' if i % 2 else '#0E1C22'))
        cv.drawRRect(r, P(mix('#9FC8C4', '#4C6E78', min(1, j / 30)), 200, stroke=2))
        cv.restore()
    the_point(cv, t, halo='#D8EFEA', col='#EFFFFB')


def s_seul(cv, t, spread=1.0):
    cv.drawRect(skia.Rect.MakeWH(W, H), P(shader=lin(0, 0, 0, H, [C('#06060E'), C('#0D0B1E'), C('#160F26')])))
    rnd = random.Random(7)
    for _ in range(16):
        x, y = rnd.uniform(60, W - 60), rnd.uniform(160, 560); ph = rnd.uniform(0, 6)
        circle(cv, x + 14 * math.sin(t * 0.4 + ph), y + 8 * math.cos(t * 0.3 + ph), rnd.uniform(3, 6), '#6E6A92', 150)
    for i in range(46):
        r = (40 + i * 13 + 7 * math.sin(t * 2.2 - i * 0.28)) * spread
        pts = []
        for k in range(121):
            a = k / 120 * 2 * math.pi; d = 6 * math.sin(a * 6 + i * 0.4 + t * 0.8)
            pts.append((PX + (r + d) * math.cos(a), PY + (r * 0.92 + d) * math.sin(a)))
        cv.drawPath(path_of(pts, True), P(mix('#B9B3D9', '#3E4A7A', i / 46), int(max(0, 150 - i * 2.6)), stroke=1.6 if i % 3 else 3))
    for k in range(72):
        a = k / 72 * 2 * math.pi + t * 0.05
        cv.drawLine(PX + 70 * math.cos(a) * spread, PY + 64 * math.sin(a) * spread,
                    PX + 260 * math.cos(a + 0.12) * spread, PY + 240 * math.sin(a + 0.12) * spread, P('#8E86C0', 60, stroke=1.4))
    the_point(cv, t)


HEAD = [(430, 1760), (410, 1500), (340, 1300), (320, 1080), (380, 900), (500, 800), (650, 780), (780, 840), (850, 950),
        (865, 1070), (885, 1120), (935, 1215), (895, 1250), (905, 1300), (885, 1335), (895, 1370), (865, 1430), (800, 1455),
        (760, 1520), (750, 1760), (590, 1800)]


def flow_lines(cv, t, n, col, a, k, seed):
    rnd = random.Random(seed)
    for _ in range(n):
        x, y = rnd.uniform(0, W), rnd.uniform(0, H); pts = [(x, y)]
        for _ in range(50):
            ang = (math.sin(x * 0.006 + k + t * 0.35) * 0.9 + math.cos(y * 0.005 - k * 0.7 - t * 0.25) * 0.7) * math.pi
            x += 9 * math.cos(ang); y += 9 * math.sin(ang); pts.append((x, y))
        cv.drawPath(path_of(pts), P(col, a, stroke=1.5))


def s_pensees(cv, t, grow=0.0):
    cv.drawRect(skia.Rect.MakeWH(W, H), P(shader=lin(0, 0, 0, H, [C('#1A1626'), C('#2A2236'), C('#3A2E40')])))
    flow_lines(cv, t, 120, '#5A4E6A', 90, 0.0, 1)
    breath = 1 + 0.012 * math.sin(t * 1.6)
    sc = breath * (1 + 9 * ease(grow) ** 2)
    cv.save(); cv.translate(PX, PY); cv.scale(sc, sc); cv.translate(-PX, -PY)
    head = smooth(HEAD)
    cv.drawPath(head, P(mix('#E4DDE6', '#EDE7DC', grow)))
    cv.save(); cv.clipPath(head, doAntiAlias=True)
    fade = 1 - clamp(grow * 1.6)
    flow_lines(cv, t, 300, '#7A6890', int(150 * fade), 1.7, 2)
    flow_lines(cv, t, 90, '#C49AAE', int(170 * fade), 2.9, 3)
    cv.restore()
    cv.drawPath(head, P('#1A1626', int(230 * fade), stroke=4 / sc))
    cv.restore()
    the_point(cv, t, col=mix('#FFFFFF', '#8C7FA6', grow), halo=mix('#FFFFFF', '#B9A8D0', grow))


def blobp(cx, cy, r, seed, t, n=10, wob=0.16):
    rnd = random.Random(seed)
    rs = [r * (1 + rnd.uniform(-wob, wob) + 0.05 * math.sin(t * 2 + i)) for i in range(n)]
    return smooth([(cx + rs[i] * math.cos(i / n * 2 * math.pi), cy + rs[i] * math.sin(i / n * 2 * math.pi)) for i in range(n)])


def s_liens(cv, t):
    lt = t - T_CD[1]                        # temps local de la scène
    cv.drawRect(skia.Rect.MakeWH(W, H), P(shader=lin(0, 0, 0, H, [C('#EDE7DC'), C('#DCD6DE'), C('#C6C4D4')])))
    for i in range(16):
        y = 300 + i * 95
        cv.drawPath(path_of([(x, y + 14 * math.sin(x * 0.008 + i + t * 0.6)) for x in range(-20, W + 40, 20)]), P('#B8B0C4', 70, stroke=1.4))
    pa = ease(clamp(lt / 1.0))              # « toi » se pose à gauche
    ax, ay = PX + (310 - PX) * pa, PY + (1120 - PY) * pa
    pb = ease(clamp((lt - 0.4) / 1.0))      # quelqu'un arrive d'en haut à droite
    bx, by = 1180 + (790 - 1180) * pb, 520 + (1420 - 520) * pb
    pt = ease(clamp((lt - 1.0) / 1.0))      # les fils se tissent
    ra, rb = 18 + 102 * pa, 95 * pb
    if pt > 0:
        rnd = random.Random(3)
        for k in range(60):
            off = rnd.uniform(-300, 300) + 30 * math.sin(t * 1.3 + k)
            p = skia.Path(); p.moveTo(ax, ay)
            p.cubicTo(ax + 170, ay + off, bx - 170, by - off * 0.8, bx, by)
            paint = P(mix('#6E6488', '#A88AA0', k / 60), 120, stroke=1.3)
            if pt < 0.999: paint.setPathEffect(skia.TrimPathEffect.Make(0, pt))
            cv.drawPath(p, paint)
            if pt >= 1:                       # petites lueurs qui voyagent sur les fils
                pm = skia.PathMeasure(p, False); L = pm.getLength()
                u = ((t * 0.35 + k * 0.137) % 1.0)
                pos, _ = pm.getPosTan(u * L)
                circle(cv, pos.x(), pos.y(), 3, '#FFFFFF', 200)
    for (x, y, r, sd, col) in ((ax, ay, ra, 1, '#8C7FA6'), (bx, by, rb, 4, '#B49AAE')):
        if r < 2: continue
        for j in range(1, 4):
            cv.drawPath(blobp(x, y, r + j * 26 + 6 * math.sin(t * 2 - j), 9 + j, t, wob=0.1), P('#5E5478', 90 - j * 20, stroke=1.4))
        cv.drawPath(blobp(x, y, r, sd, t), P(col))
        cv.drawPath(blobp(x, y, r, sd, t), P('#3A3250', 200, stroke=3))
    the_point(cv, t, ax, ay, col='#FFFFFF', halo='#FFFFFF', s=0.8)


# ---------------- composition ----------------
def zoomed(cv, fn, t, z, *a):
    cv.save(); cv.translate(PX, PY); cv.scale(z, z); cv.translate(-PX, -PY); fn(cv, t, *a); cv.restore()


def iris(cv, p, fn, t, *a):
    r = 1500 * ease(p) ** 1.4
    if r < 1: return
    cv.save(); cv.clipPath(skia.Path().addCircle(PX, PY, r), doAntiAlias=True); fn(cv, t, *a); cv.restore()
    cv.drawCircle(PX, PY, r, P('#E8E3F5', 180, stroke=3))


def scene(cv, t):
    if t < T_AB[0]: s_temps(cv, t)
    elif t < T_AB[1]:
        p = (t - T_AB[0]) / (T_AB[1] - T_AB[0])
        zoomed(cv, s_temps, t, 1 + 3 * ease(p)); iris(cv, p, s_seul, t, 0.3 + 0.7 * ease(p))
    elif t < T_BC[0]: s_seul(cv, t)
    elif t < T_BC[1]:
        p = (t - T_BC[0]) / (T_BC[1] - T_BC[0])
        s_seul(cv, t, 1 + 1.5 * ease(p)); iris(cv, p, s_pensees, t)
    elif t < T_CD[0]: s_pensees(cv, t)
    elif t < T_CD[1]:
        p = (t - T_CD[0]) / (T_CD[1] - T_CD[0])
        s_pensees(cv, t, clamp(p / 0.75))
        if p > 0.65:
            cv.saveLayerAlpha(None, int(255 * clamp((p - 0.65) / 0.35))); s_liens(cv, t); cv.restore()
    else: s_liens(cv, t)


def current_word(t):
    cur = None
    for w, s, k in WORDS:
        if t >= s: cur = (w, s, k)
    return cur


def draw_word(cv, t):
    cur = current_word(t)
    if not cur or not cur[0]: return
    w, s, k = cur; age = t - s
    pale = t >= T_CD[0] + 0.6
    ink, halo = ('#221C33', '#F2EEE6') if pale else ('#F0EBBE', '#07050F')
    size = 190 if k else 165
    f = skia.Font(FONT, size); tw = f.measureText(w)
    if tw > 820: f.setSize(size * 820 / tw); tw = f.measureText(w)
    sc = 0.88 + 0.12 * (1 - math.exp(-age * 18)); a = int(255 * clamp(age / 0.06))
    cv.save(); cv.translate(W / 2, TY); cv.scale(sc, sc)
    x, y = -tw / 2, f.getSize() * 0.35
    cv.drawString(w, x, y, f, P(halo, int(a * 0.6), blur=f.getSize() * 0.10))
    cv.drawString(w, x, y, f, P(halo, int(a * 0.3), blur=f.getSize() * 0.28))
    cv.drawString(w, x, y, f, P(ink, a))
    cv.restore()


GRAIN = None
def grain_img():
    global GRAIN
    if GRAIN is None:
        rng = np.random.default_rng(1)
        a = (rng.random((H + 64, W + 64)) < 0.012).astype(np.uint8) * 30
        arr = np.zeros((H + 64, W + 64, 4), np.uint8); arr[..., :3] = 255; arr[..., 3] = a
        arr[..., :3] = (arr[..., :3].astype(np.uint16) * a[..., None] // 255).astype(np.uint8)  # prémultiplié
        GRAIN = skia.Image.fromarray(arr, colorType=skia.kRGBA_8888_ColorType)
    return GRAIN


def frame(fi):
    t = fi / FPS
    surf = skia.Surface(W, H); cv = surf.getCanvas()
    # légère dérive de caméra (flottement)
    cv.save(); cv.translate(PX, PY); cv.rotate(0.4 * math.sin(t * 0.5)); s = 1.02 + 0.01 * math.sin(t * 0.7)
    cv.scale(s, s); cv.translate(-PX + 6 * math.sin(t * 0.6), -PY + 8 * math.cos(t * 0.45))
    scene(cv, t); cv.restore()
    cv.drawRect(skia.Rect.MakeWH(W, H), P(shader=rad(W / 2, H / 2, 1300, [C('#000000', 0), C('#000000', 0), C('#000000', 90)], [0, 0.6, 1])))
    draw_word(cv, t)
    r = random.Random(fi); cv.drawImage(grain_img(), -r.randint(0, 63), -r.randint(0, 63))
    return surf.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType).tobytes()


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--preview':
        for ts in sys.argv[2].split(','):
            fi = int(float(ts) * FPS)
            arr = np.frombuffer(frame(fi), np.uint8).reshape(H, W, 4)
            from PIL import Image
            Image.fromarray(arr[..., :3]).resize((540, 960)).save(os.path.join(sys.argv[3], f'pv_{ts}.png'))
        sys.exit()
    out = os.path.join(HERE, 'extrait_test.mp4')
    n = int(DUR * FPS)
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-f', 'lavfi', '-i', f'sine=f=110:d={DUR},volume=0.0',
                           '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-preset', 'medium', '-b:v', '12M', '-maxrate', '14M', '-bufsize', '24M',
                           '-c:a', 'aac', '-shortest', out], stdin=subprocess.PIPE)
    with Pool(4) as pool:
        for i, b in enumerate(pool.imap(frame, range(n), chunksize=4)):
            ff.stdin.write(b)
            if i % 120 == 0: print(i, '/', n, flush=True)
    ff.stdin.close(); ff.wait(); print('ok', out)
