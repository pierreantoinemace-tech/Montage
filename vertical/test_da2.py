"""Tests de DA n°2 : vertical 1080x1920, abstrait / psychique, couleurs sombres ou pâles."""
import math, os, random, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'etoiles'))
import lib
lib.W, lib.H = 1080, 1920
import skia
from lib import P, C, mix, lin, rad, glow, circle
W, H = 1080, 1920
FONT = skia.Typeface.MakeFromFile(os.path.join(HERE, '..', 'etoiles', 'fonts', 'Rubik-700.ttf'))
TY = H * 0.40  # hauteur du mot


def word(cv, text, ink='#F0EBBE', halo='#07050F', size=170):
    f = skia.Font(FONT, size)
    w = f.measureText(text)
    if w > 820:
        f.setSize(size * 820 / w); w = f.measureText(text)
    x, y = (W - w) / 2, TY + f.getSize() * 0.35
    cv.drawString(text, x, y, f, P(halo, 150, blur=f.getSize() * 0.10))
    cv.drawString(text, x, y, f, P(halo, 80, blur=f.getSize() * 0.28))
    cv.drawString(text, x, y, f, P(ink))


def grain(cv, seed, col, a=14, n=9000):
    rnd = random.Random(seed)
    for _ in range(n):
        circle(cv, rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(0.6, 1.6), col, a)


def path_of(pts, close=False):
    p = skia.Path(); p.moveTo(*pts[0])
    for q in pts[1:]: p.lineTo(*q)
    if close: p.close()
    return p


# ---------- 1. SEUL : iris géant, une lueur seule au centre (sombre) ----------
def f_seul(cv):
    cv.drawRect(skia.Rect.MakeWH(W, H), P(shader=lin(0, 0, 0, H, [C('#06060E'), C('#0D0B1E'), C('#160F26')])))
    cx, cy = W / 2, 1180
    for i in range(46):
        r = 40 + i * 13
        wob = [(cx + (r + 6 * math.sin(a * 6 + i * 0.4)) * math.cos(a), cy + (r * 0.92 + 6 * math.sin(a * 6 + i * 0.4)) * math.sin(a))
               for a in [k / 120 * 2 * math.pi for k in range(121)]]
        col = mix('#B9B3D9', '#3E4A7A', i / 46)
        cv.drawPath(path_of(wob, True), P(col, int(150 - i * 2.6), stroke=1.6 if i % 3 else 3))
    for k in range(72):  # fibres de l'iris
        a = k / 72 * 2 * math.pi
        cv.drawLine(cx + 70 * math.cos(a), cy + 64 * math.sin(a), cx + 260 * math.cos(a + 0.12), cy + 240 * math.sin(a + 0.12), P('#8E86C0', 60, stroke=1.4))
    glow(cv, cx, cy, 120, '#E8E3F5', 180)
    circle(cv, cx, cy, 16, '#F4F0FF')
    rnd = random.Random(7)  # les autres, très loin
    for _ in range(14):
        x, y = rnd.uniform(60, W - 60), rnd.uniform(180, 560)
        circle(cv, x, y, rnd.uniform(3, 6), '#6E6A92', 160)
    grain(cv, 1, '#FFFFFF', 12)
    word(cv, 'SEUL')


# ---------- 2. LIENS : deux formes reliées par des fils (pâle) ----------
def blobp(cx, cy, r, seed, n=10, wob=0.18):
    rnd = random.Random(seed); rs = [r * (1 + rnd.uniform(-wob, wob)) for _ in range(n)]
    pts = [(cx + rs[i] * math.cos(i / n * 2 * math.pi), cy + rs[i] * math.sin(i / n * 2 * math.pi)) for i in range(n)]
    p = skia.Path(); m = [((pts[i][0] + pts[(i + 1) % n][0]) / 2, (pts[i][1] + pts[(i + 1) % n][1]) / 2) for i in range(n)]
    p.moveTo(*m[-1])
    for i in range(n): p.quadTo(*pts[i], *m[i])
    p.close(); return p


def f_liens(cv):
    cv.drawRect(skia.Rect.MakeWH(W, H), P(shader=lin(0, 0, 0, H, [C('#EDE7DC'), C('#DCD6DE'), C('#C6C4D4')])))
    for i in range(16):  # lignes de brume
        y = 300 + i * 95
        cv.drawPath(path_of([(x, y + 14 * math.sin(x * 0.008 + i)) for x in range(-20, W + 40, 20)]), P('#B8B0C4', 70, stroke=1.4))
    a, b = (300, 1180), (790, 1420)
    rnd = random.Random(3)
    for k in range(34):
        p = skia.Path(); p.moveTo(*a)
        off = rnd.uniform(-260, 260)
        p.cubicTo(a[0] + 160, a[1] + off, b[0] - 160, b[1] - off * 0.8, *b)
        cv.drawPath(p, P(mix('#6E6488', '#A88AA0', k / 34), 120, stroke=1.3))
    cv.drawPath(blobp(*a, 120, 1), P('#8C7FA6'))
    cv.drawPath(blobp(*a, 120, 1), P('#3A3250', 200, stroke=3))
    cv.drawPath(blobp(*b, 95, 4), P('#B49AAE'))
    cv.drawPath(blobp(*b, 95, 4), P('#3A3250', 200, stroke=3))
    for (x, y), r in ((a, 120), (b, 95)):
        for j in range(1, 4):
            cv.drawPath(blobp(x, y, r + j * 26, 9 + j, wob=0.1), P('#5E5478', 90 - j * 20, stroke=1.4))
    grain(cv, 2, '#3A3250', 10)
    word(cv, 'LIENS', ink='#221C33', halo='#F2EEE6')


# ---------- 3. TEMPS : tunnel de formes qui tournent (sombre) ----------
def f_temps(cv):
    cv.drawRect(skia.Rect.MakeWH(W, H), P(shader=lin(0, 0, 0, H, [C('#050A0E'), C('#0A1418'), C('#101A1E')])))
    cx, cy = W / 2, 1150
    for i in range(30, 0, -1):
        s = 18 * i * 1.12 ** (i * 0.35); rot = i * 7
        cv.save(); cv.translate(cx, cy - i * 4); cv.rotate(rot)
        r = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-s / 2, -s / 2, s, s), s * 0.22, s * 0.22)
        cv.drawRRect(r, P(mix('#0E1C22', '#1C3038', (i % 2)), 255))
        cv.drawRRect(r, P(mix('#9FC8C4', '#4C6E78', i / 30), 200, stroke=2))
        cv.restore()
    glow(cv, cx, cy, 70, '#D8EFEA', 200); circle(cv, cx, cy, 8, '#EFFFFB')
    grain(cv, 3, '#FFFFFF', 10)
    word(cv, 'TEMPS')


# ---------- 4. PENSÉES : profil rempli de courants (crépuscule pâle-sombre) ----------
PROFILE = [(430, 1760), (410, 1500), (340, 1300), (320, 1080), (380, 900), (500, 800), (650, 780), (780, 840), (850, 950),
           (865, 1070), (885, 1120), (935, 1215), (895, 1250), (905, 1300), (885, 1335), (895, 1370), (865, 1430), (800, 1455),
           (760, 1520), (750, 1760)]


def smooth(pts):
    p = skia.Path(); m = [((pts[i][0] + pts[i + 1][0]) / 2, (pts[i][1] + pts[i + 1][1]) / 2) for i in range(len(pts) - 1)]
    p.moveTo(*pts[0]); p.lineTo(*m[0])
    for i in range(1, len(pts) - 1): p.quadTo(*pts[i], *m[i])
    p.lineTo(*pts[-1]); p.close(); return p


def f_pensees(cv):
    cv.drawRect(skia.Rect.MakeWH(W, H), P(shader=lin(0, 0, 0, H, [C('#1A1626'), C('#2A2236'), C('#3A2E40')])))
    def flow(x, y, k): return math.sin(x * 0.006 + k) * 0.9 + math.cos(y * 0.005 - k * 0.7) * 0.7
    rnd = random.Random(5)
    def lines(n, col, a, k):
        for _ in range(n):
            x, y = rnd.uniform(0, W), rnd.uniform(0, H); pts = [(x, y)]
            for _ in range(60):
                ang = flow(x, y, k) * math.pi; x += 9 * math.cos(ang); y += 9 * math.sin(ang); pts.append((x, y))
            cv.drawPath(path_of(pts), P(col, a, stroke=1.5))
    lines(160, '#5A4E6A', 90, 0.0)
    head = smooth(PROFILE)
    cv.drawPath(head, P('#E4DDE6'))
    cv.save(); cv.clipPath(head, doAntiAlias=True)
    lines(420, '#7A6890', 150, 1.7)
    lines(120, '#C49AAE', 170, 2.9)
    glow(cv, 620, 1000, 160, '#FFFFFF', 160)
    cv.restore()
    cv.drawPath(head, P('#1A1626', 230, stroke=4))
    grain(cv, 4, '#FFFFFF', 10)
    word(cv, 'PENSÉES')


if __name__ == '__main__':
    out = os.path.join(HERE, 'tests2'); os.makedirs(out, exist_ok=True)
    names = [('1_seul', f_seul), ('2_liens', f_liens), ('3_temps', f_temps), ('4_pensees', f_pensees)]
    for name, fn in names:
        surf = skia.Surface(W, H); fn(surf.getCanvas())
        surf.makeImageSnapshot().save(os.path.join(out, name + '.png'))
    from PIL import Image
    im = Image.new('RGB', (540 * 4 + 60, 960), '#222')
    for i, (n, _) in enumerate(names):
        im.paste(Image.open(os.path.join(out, n + '.png')).convert('RGB').resize((540, 960)), (i * 560, 0))
    im.save(os.path.join(out, 'planche.jpg'), quality=88)
    print('ok')
