"""« Imagine que t'as 85 ans » — vertical 4K 30 fps. Voix d'un seul tenant, animation abstraite et poétique, perso au haut étroit."""
import math, os, random, sys, json, subprocess, importlib.util
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'vertical'))
_s = importlib.util.spec_from_file_location('monde_film3', os.path.join(HERE, '..', 'monde', 'film3.py'))
M = importlib.util.module_from_spec(_s); _s.loader.exec_module(M)
RV, X = M.RV, M.F.X
import numpy as np, skia
from lib import P, C, mix, lin, rad, circle, ease, ease_out
import mg
W, H, SC, OW_, OH_, PX, PY = RV.W, RV.H, RV.SC, RV.OW_, RV.OH_, RV.PX, RV.PY
CREAM, GOLD, OUT, BIG, HERO = RV.CREAM, RV.GOLD, RV.OUT, RV.BIG, RV.HERO
clamp, hero, pop, sym, opath, rect = RV.clamp, RV.hero, RV.pop, RV.sym, RV.opath, RV.rect
flow, crack, shards, rings, vine, orb, paper_bird, glyph_line, sky = M.flow, M.crack, M.shards, M.rings, M.vine, M.orb, M.paper_bird, M.glyph_line, M.sky
INK, RED = M.INK, M.RED
FPS, DUR = 30, 69.7
OLDP = dict(skin='#8EAAB4', hair='#DAD6E6', robe='#3A2E4A')

# ---------------- mots ----------------
KEYS = {'IMAGINE', '85', 'JOURNÉE', "D'AUJOURD'HUI", 'DIT', 'REGRETS', 'MÊMES', 'COURAGE', 'MOI', 'TRAVAILLER', 'HOMMES', 'AMIS',
        'HEUREUX', 'VOITURE', 'MAL', '60', 'CINQUANTAINE', 'JOURNÉES', 'ANNÉES', 'BONHEUR', "L'ARGENT", 'RÉUSSITE', 'LIENS',
        "AUJOURD'HUI", 'PREMIER', "APPELLE-LE"}
FIX = {'BRONY': 'BRONNIE', 'MOTORISER': "M'AUTORISER", 'CONTRAINT': "QU'ON TE REND", '1': 'UN', '2': 'DEUX', '3': 'TROIS',
       'PERSONNE@13': 'PERSONNES', 'LIEN': 'LIENS', 'LEUR': 'LEURS', "T'APPELLERAIT": "T'APPELLERAIS"}


def load_words():
    raw = json.load(open(os.path.join(HERE, 'words.json')))
    toks = []
    for w, s, e in raw:
        if w and w[0] in "'-" and toks: toks[-1][0] += w; toks[-1][2] = e; continue
        if w.strip('?!.,…') == '': continue
        toks.append([w, s, e])
    out = []
    for i, (w, s, e) in enumerate(toks):
        txt = w.strip(',.?!…').upper()
        txt = FIX.get(f'{txt}@{int(s)}', FIX.get(txt, txt))
        nxt = toks[i + 1][1] if i + 1 < len(toks) else e + 1.5
        end = nxt if nxt - e < 0.7 else e + 0.4
        out.append((txt, s, end, txt in KEYS))
    return out


WORDS = load_words()
RV.WORDS = WORDS; X.WORDS = [(w, s, k) for w, s, e, k in WORDS]


# ---------------- perso âgé ----------------
def old_hero(cv, t, cx, cy, s, eyes='lidded', look=(0.0, 0.3), mixv=0.0, arms=None):
    pal = {k: mix(OLDP[k], HERO[k], mixv) for k in OLDP}
    tr = 1.6 * math.sin(t * 31) * (1 - mixv)                    # les mains / la tête tremblent un peu
    hero(cv, t, cx + tr, cy, s, eyes, look=look, pal=pal, arms=arms)
    if mixv < 1:                                                # rides
        a = int(255 * (1 - mixv)); yy = cy + 5 * math.sin(t * 2.1)
        for sx in (-1, 1):
            for j in range(2):
                p = skia.Path(); p.addArc(skia.Rect.MakeLTRB(cx + tr + sx * 0.3 * s - 0.2 * s, yy + 0.12 * s + j * 0.08 * s, cx + tr + sx * 0.3 * s + 0.2 * s, yy + 0.3 * s + j * 0.08 * s), 30, 120)
                cv.drawPath(p, P(mix(OLDP['skin'], '#000000', 0.45), a, stroke=3))
            cv.drawLine(cx + tr + sx * 0.12 * s, yy + 0.45 * s, cx + tr + sx * 0.22 * s, yy + 0.62 * s, P(mix(OLDP['skin'], '#000000', 0.45), a, stroke=3))


def sand(cv, t, n=90, seed=1, col=CREAM, a=200):
    rnd = random.Random(seed)
    for k in range(n):
        x = rnd.uniform(-40, W + 40); sp = rnd.uniform(40, 120)
        y = (rnd.uniform(0, H) + t * sp) % (H + 100) - 50
        circle(cv, x + 10 * math.sin(t * 0.7 + k), y, rnd.uniform(1.5, 3.5), col, a)


# ---------------- scènes ----------------
def s_hook(cv, t, lt):
    sky(cv, t, ['#06050C', '#0B0916', '#100D20', '#15112A', '#1A1432', '#1F173A'])
    flow(cv, t, 60, '#221D34', 255, 201)
    for j in range(6):                                          # les cercles du temps autour de lui
        r = 300 + j * 90 + 8 * math.sin(t * 1.4 - j)
        p = skia.Path(); p.addArc(skia.Rect.MakeLTRB(PX - r, PY - r, PX + r, PY + r), -90 + (t * (12 + j * 4)) % 360, 250)
        cv.drawPath(p, P('#3A3250', 255, stroke=3 if j % 2 else 5))
    sand(cv, t)
    op = ease(clamp((t - 3.3) / 1.2))                           # une porte de lumière s'ouvre : « une seule journée »
    dx, dy, dw, dh = 760, 980, 220, 420
    opath(cv, rect(dx - dw / 2, dy - dh / 2, dw, dh, 110), '#0A0812', 7)
    if op > 0:
        cv.save(); cv.clipPath(rect(dx - dw / 2, dy - dh / 2, dw, dh, 110), doAntiAlias=True)
        cv.drawRect(skia.Rect.MakeXYWH(dx - dw / 2, dy - dh / 2, dw * op, dh), P('#FFE7A0'))
        if t > 4.7: hero(cv, t, dx, dy - 20, 70, 'open', look=(-0.6, 0.0))      # « dans ton corps d'aujourd'hui »
        cv.restore()
        beam = skia.Path(); beam.moveTo(dx - dw / 2, dy - dh / 2 + 60); beam.lineTo(dx - dw / 2 - 500 * op, dy + 700); beam.lineTo(dx - dw / 2 + 40, dy + dh / 2); beam.close()
        cv.drawPath(beam, P('#FFE7A0', int(40 * op)))
    if t > 7.99:                                                # « des gens l'ont déjà dit » : des voix, des lignes
        for k in range(6):
            u = clamp((t - 7.99 - k * 0.12) / 0.5)
            glyph_line(cv, 90 + (k % 2) * 40, 1180 + k * 60, 260 * u, 0.7, t, k + 30)
    old_hero(cv, t, 420, PY + 0.55 * 240 + 40, 240, 'lidded', look=(0.6, 0.0) if t > 3.3 else (0.0, 0.6))


def s_infirmiere(cv, t, lt):
    sky(cv, t, ['#0A0812', '#0F0C1A', '#141022', '#19142A', '#1E1832', '#231C3A'])
    vy = 820
    for k in range(-8, 9):                                      # un long couloir de lignes
        cv.drawLine(PX + k * 30, vy, PX + k * 300, H + 200, P('#1E1A2C', 255, stroke=4))
    for j in range(6):
        y = vy + 60 + j ** 1.7 * 45; w = 120 + j * 110
        opath(cv, rect(PX - w / 2, y, w, 18 + j * 6, 8), mix('#2A2640', '#4A4466', j / 6), 3)
    lx, ly = PX, 1130
    for j in range(5): cv.drawCircle(lx, ly, 70 + j * 45, P('#FFE7A0', 26))
    orb(cv, lx, ly + 6 * math.sin(t * 1.5), 34, 1.0, t)        # la lampe au chevet
    if t > 14.81:                                               # « elle a noté leurs regrets »
        u = clamp((t - 14.81) / 2.2)
        opath(cv, rect(250, 1380, 580, 420, 10), '#EDE6D8', 6)
        for k in range(7):
            ww = 480 * clamp(u * 7 - k)
            if ww > 2: cv.drawLine(300, 1440 + k * 50, 300 + ww, 1440 + k * 50, P('#6A6078', 255, stroke=7))


REG = [(18.05, 'cage'), (23.13, 'clock'), (28.35, 'thread'), (31.17, 'flower')]
POS = [(290, 1130), (790, 1130), (290, 1600), (790, 1600)]


def motif(cv, kind, x, y, t, t0, active):
    a = 255 if active else 150
    lt = t - t0
    if kind == 'cage':
        for k in range(7):
            g = math.pi + k * math.pi / 6
            cv.drawLine(x + 120 * math.cos(g), y - 40 + 120 * math.sin(g), x + 120 * math.cos(g), y + 110, P(CREAM, a, stroke=6))
        cv.drawLine(x - 130, y + 110, x + 130, y + 110, P(CREAM, a, stroke=10))
        u = clamp(lt / 3.0)
        paper_bird(cv, x + 260 * u, y - 20 - 380 * u, 55, t, 1, a)
    elif kind == 'clock':
        mg.melting_clock(cv, x, y - 20, 105, t, face='#B8A27A', drip=0.6 + 0.6 * clamp(lt / 3), speed=0.8)
    elif kind == 'thread':
        e = clamp(lt / 1.2); fray = clamp((lt - 1.0) / 1.2)
        orb(cv, x - 140, y, 30, 0.9, t); orb(cv, x + 140, y, 30, 0.9, t)
        for k in range(5):
            p = skia.Path(); p.moveTo(x - 110, y + (k - 2) * 6)
            mid = 30 * fray * (1 if k % 2 else -1) * (k + 1)
            p.cubicTo(x - 40, y + mid, x + 40, y - mid, x + 110, y + (k - 2) * 6)
            pa = P(GOLD, int(a * (1 - 0.6 * fray)), stroke=3)
            if k >= 3 and fray > 0.5: pa.setPathEffect(skia.DashPathEffect.Make([30, 40 * fray], 0))
            cv.drawPath(p, pa)
    elif kind == 'flower':
        b = ease(clamp(lt / 2.5))
        st = skia.Path(); st.moveTo(x, y + 160); st.quadTo(x - 20, y + 60, x, y)
        cv.drawPath(st, P(OUT, a, stroke=16)); cv.drawPath(st, P('#3E8A68', a, stroke=8))
        for k in range(8):
            g = k * math.pi / 4 + t * 0.15
            pet = skia.Path(); pet.addOval(skia.Rect.MakeXYWH(-20, -25 - 85 * b, 40, 25 + 85 * b))
            cv.save(); cv.translate(x, y); cv.rotate(math.degrees(g)); opath(cv, pet, '#F0B8C8', 4, a); cv.restore()
        opath(cv, skia.Path().addCircle(x, y, 26), '#F0D890', 5, a)


def s_regrets(cv, t, lt):
    sky(cv, t, ['#0A0918', '#100E22', '#16122C', '#1C1636', '#221A40', '#281E48'])
    flow(cv, t, 50, '#24203A', 255, 211)
    cur = max(i for i, (t0, _) in enumerate(REG) if t >= t0 - 0.3) if t >= REG[0][0] - 0.3 else -1
    for i, (t0, kind) in enumerate(REG):
        if t < t0 - 0.3: continue
        x, y = POS[i]; s = 1.35 * pop(t, t0 - 0.3, 0.45)
        cv.save(); cv.translate(x, y); cv.scale(s, s); cv.translate(-x, -y)
        motif(cv, kind, x, y, t, t0, i == cur)
        f = skia.Font(RV.FONT, 46); n = str(i + 1)
        cv.drawString(n, x - 150, y - 150, f, P(OUT, 255, stroke=10)); cv.drawString(n, x - 150, y - 150, f, P(GOLD if i == cur else '#8A80A0'))
        cv.restore()


def s_voiture(cv, t, lt):
    sky(cv, t, ['#100E1E', '#161428', '#1C1832', '#221C3C', '#282046', '#2E2450'])
    flow(cv, t, 40, '#2A2640', 255, 221)
    x, y = PX, 1260 + 10 * math.sin(t * 1.3)
    pp = clamp((t - 36.95) / 0.35)
    if pp < 1:
        sc = 1.5 * (1 + 0.15 * pp)
        cv.save(); cv.translate(x, y); cv.scale(sc, sc)
        body = skia.Path(); body.moveTo(-230, 40); body.lineTo(-210, -30); body.lineTo(-110, -40); body.lineTo(-60, -110); body.lineTo(90, -110)
        body.lineTo(150, -40); body.lineTo(230, -25); body.lineTo(235, 40); body.close()
        opath(cv, body, '#C8505A', 7, int(255 * (1 - pp)))
        opath(cv, rect(-45, -95, 120, 50, 8), '#9FD8F0', 5, int(255 * (1 - pp)))
        for wx in (-130, 140): opath(cv, skia.Path().addCircle(wx, 45, 42), '#2A2238', 6, int(255 * (1 - pp)))
        cv.restore()
    if pp > 0:                                                  # elle éclate en poussière
        rnd = random.Random(3)
        for k in range(70):
            g = rnd.uniform(0, 6.28); d = 40 + pp * rnd.uniform(80, 420) + (t - 37.3) * 60
            circle(cv, x + math.cos(g) * d, y + math.sin(g) * d * 0.6 + (t - 36.95) * 50, rnd.uniform(3, 8), rnd.choice(['#C8505A', CREAM, '#9FD8F0']), int(255 * clamp(1 - (t - 36.95) / 1.4)))


def s_parents(cv, t, lt):
    sky(cv, t, ['#14102A', '#1C1636', '#241C42', '#2E224E', '#38285A', '#422E64'])
    flow(cv, t, 40, '#2E2848', 255, 231)
    RV.hill(cv, 1500, 50, 0.005, 1.0, '#221E38', '#2A2644', t)
    for k, (x, s) in enumerate(((180, 1), (300, 0.95))):        # les parents, au loin sur la colline
        hero(cv, t, x, 1330, 110 * s, 'lidded', look=(0.7, 0.2), pal=OLDP if k == 0 else dict(OLDP, robe='#2A3A4A'), seed=k + 3)
    hero(cv, t, 800, 1560, 180, 'open', look=(-0.8, -0.2))
    p = skia.Path(); p.moveTo(300, 1270); p.cubicTo(450, 1100, 650, 1300, 800, 1460)
    cv.drawPath(p, P(GOLD, 200, stroke=3))
    for k, t0 in enumerate((41.95, 42.25)):                     # « deux fois par an »
        u = clamp((t - t0) / 0.3)
        if u > 0: orb(cv, 470 + k * 140, 1000, 26 * ease_out(u), 1.0, t)


def s_journees(cv, t, lt):
    sky(cv, t, ['#0C0A1A', '#120E24', '#18122E', '#1E1638', '#241A42', '#2A1E4A'])
    shrink = ease(clamp((t - 45.5) / 0.9))                      # « pas des années » : les grands blocs fondent
    if t < 46.6:
        for k in range(3):
            opath(cv, rect(130 + k * 290, 1050 + 400 * shrink, 240, 500 * (1 - shrink) + 10, 10), '#3A3458', 5, int(255 * (1 - shrink)))
    n = int(50 * ease(clamp((t - 43.6) / 1.2)))
    for k in range(n):                                          # cinquante petites journées
        x = 150 + (k % 10) * 87; y = 1080 + (k // 10) * 95
        flick = 1.0 if t < 46.53 else (0.35 if (k * 7) % 11 == 0 and (t - 46.53) > (k % 5) * 0.15 else 1.0)
        opath(cv, rect(x - 32, y - 32, 64, 64, 10), mix('#3A3458', '#FFE7A0', flick), 4)


def s_harvard(cv, t, lt):
    sky(cv, t, ['#08070F', '#0D0B18', '#120F22', '#17132C', '#1C1636', '#211A40'])
    rnd = random.Random(41)
    for k in range(60):                                         # des centaines de vies qui avancent dans le temps
        x0 = rnd.uniform(0, W); ph = rnd.uniform(0, 6)
        p = skia.Path(); p.moveTo(x0, H + 50)
        for j in range(30):
            y = H + 50 - j * 70; p.lineTo(x0 + 40 * math.sin(j * 0.4 + ph + t * 0.3), y)
        pa = P(mix('#3A3458', '#8A7AA8', (k % 5) / 5), 200, stroke=2.5)
        tr_ = clamp((t - 47.3) / 2.5 + (k % 7) * 0.02)
        if tr_ < 0.999: pa.setPathEffect(skia.TrimPathEffect.Make(0, max(0.001, tr_)))
        cv.drawPath(p, pa)
    if 55.6 < t < 57.6:                                         # « pas l'argent »
        u = clamp((t - 55.91) / 1.4)
        for k in range(9): circle(cv, 200 + k * 85, 900 + u * 700 + (k % 3) * 40, 26, '#E8C860', int(255 * (1 - u)))
    if 56.5 < t < 58.2:                                         # « pas la réussite »
        u = clamp((t - 56.71) / 1.2)
        sym(cv, 'star8', PX, 1250 + u * 200, 90 * (1 - u) + 1, t * 40, GOLD, t, int(255 * (1 - u)))
    if t > 57.4:                                                # « la qualité de leurs liens » : un tissage lumineux
        u = ease(clamp((t - 57.45) / 1.4))
        pts = [(PX + 330 * math.cos(k * 2 * math.pi / 9 + 0.3), 1300 + 300 * math.sin(k * 2 * math.pi / 9 + 0.3)) for k in range(9)]
        for i in range(9):
            for j in range(i + 1, 9):
                if (i + j) % 3 == 0 or j == i + 1:
                    a, b = pts[i], pts[j]
                    cv.drawLine(a[0], a[1], a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u, P(GOLD, 220, stroke=3))
        for x, y in pts: orb(cv, x, y, 22, u, t)


def s_aujourdhui(cv, t, lt):
    m = ease(clamp((t - 63.1) / 0.9))                           # « c'est aujourd'hui » : il redevient jeune
    sky(cv, t, [mix(a, b, m) for a, b in zip(['#06050C', '#0B0916', '#100D20', '#15112A', '#1A1432', '#1F173A'],
                                               ['#2A2244', '#3E2E56', '#564068', '#705478', '#8C6886', '#A87E92'])])
    flow(cv, t, 50, mix('#221D34', '#8C7090', m), 255, 241)
    if m > 0: RV.striped_sun(cv, PX, 1500 - 260 * m, 330 * m + 1, t, ['#E8C4A8', '#F0D2B4', '#F6E0C0', '#FAEBD0'])
    sand(cv, t, 60, 2, a=int(200 * (1 - m)))
    old_hero(cv, t, PX, PY + 0.55 * 230, 230, 'lidded' if m < 0.5 else 'open', look=(0.0, 0.3) if m < 0.5 else (0.0, -0.1), mixv=m)
    if 63.1 < t < 63.6:
        u = ease_out((t - 63.1) / 0.5)
        cv.drawCircle(PX, PY, 40 + 1600 * u, P(OUT, int(255 * (1 - u)), stroke=26)); cv.drawCircle(PX, PY, 40 + 1600 * u, P(CREAM, int(255 * (1 - u)), stroke=10))


def s_appel(cv, t, lt):
    sky(cv, t, ['#2A2244', '#3E2E56', '#564068', '#705478', '#8C6886', '#A87E92'])
    flow(cv, t, 50, '#8C7090', 200, 251)
    RV.striped_sun(cv, PX, 1240, 330, t, ['#E8C4A8', '#F0D2B4', '#F6E0C0', '#FAEBD0'])
    RV.hill(cv, 1450, 45, 0.006, 1.0, '#6A5A86', '#746490', t)
    hero(cv, t, PX, PY + 0.55 * 230, 230, 'open', look=(0.0, 0.7), arms='phone')
    c = ease(clamp((t - 67.13) / 0.8))                         # « appelle-le » : le fil part et quelqu'un s'allume au loin
    if c > 0:
        a0 = (PX + 0.32 * 230, PY + 0.55 * 230 + 1.02 * 230); b0 = (880, 330)
        p = skia.Path(); p.moveTo(*a0); p.cubicTo(a0[0] + 300, a0[1] - 300, b0[0] - 200, b0[1] + 400, *b0)
        for pa in (P(OUT, 255, stroke=9), P(GOLD, 255, stroke=4)):
            if c < 0.999: pa.setPathEffect(skia.TrimPathEffect.Make(0, c))
            cv.drawPath(p, pa)
        orb(cv, b0[0], b0[1], 34, c, t)


SCENES = [(0.0, s_hook, None), (9.2, s_infirmiere, 'iris'), (17.75, s_regrets, 'wave'), (34.75, s_voiture, 'iris'), (37.7, s_parents, 'wave'),
          (43.35, s_journees, 'iris'), (47.25, s_harvard, 'wave'), (59.3, s_aujourdhui, 'iris'), (64.2, s_appel, 'wave')]
RV.SCENES = SCENES


def frame(fi):
    return M.F.frame(fi)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--preview':
        from PIL import Image
        for ts in sys.argv[2].split(','):
            arr = np.frombuffer(frame(int(float(ts) * FPS)), np.uint8).reshape(OH_, OW_, 4)
            Image.fromarray(arr[..., :3]).resize((540, 960), Image.LANCZOS).save(os.path.join(sys.argv[3], f'pv_{ts}.png'))
        sys.exit()
    out = os.path.join(HERE, '85ans_4k.mp4'); hd = os.path.join(HERE, '85ans_1080p.mp4')
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
