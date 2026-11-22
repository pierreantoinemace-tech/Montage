"""Extrait test v3 : 4K 30 fps, plus calme, peu de symboles, décors abstraits façon Midnight Gospel en plus sombre."""
import math, os, random, sys, subprocess
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import extrait2 as X                      # perso, mots, timings, symboles, police
from extrait2 import (W, H, SC, OW_, OH_, FPS, DUR, PX, PY, HS, HERO, OTHER, WORDS, T_AB, T_BC, T_CD,
                      clamp, key_pulse, hero, current_word, FONT, TY, pd)
import numpy as np, skia
from lib import P, C, mix, lin, rad, circle, ease, ease_out
from symboles import sym, OUT, eye
import mg

BIG = skia.Rect.MakeLTRB(-600, -600, W + 600, H + 600)


# ---------------- éléments de décor ----------------
def banded_sky(cv, cols, y0, y1, t, wav=12):
    cv.drawRect(BIG, P(cols[-1]))
    n = len(cols); h = (y1 - y0) / n
    for i in range(n - 2, -1, -1):
        yi = y0 + (i + 1) * h
        p = skia.Path(); p.moveTo(-600, -700)
        for x in range(-600, W + 601, 20):
            p.lineTo(x, yi + wav * math.sin(x * 0.004 + i * 1.7 + t * 0.25))
        p.lineTo(W + 600, -700); p.close()
        cv.drawPath(p, P(cols[i]))


def hill(cv, base, amp, freq, ph, col, stripe, t, n=5, gap=30, bottom=H + 600):
    f = lambda x: base - amp * (0.6 * math.sin(x * freq + ph) + 0.4 * math.sin(x * freq * 2.3 + ph * 1.7))
    p = skia.Path(); p.moveTo(-600, bottom)
    for x in range(-600, W + 601, 12): p.lineTo(x, f(x))
    p.lineTo(W + 600, bottom); p.close()
    cv.drawPath(p, P(col))
    cv.save(); cv.clipPath(p, doAntiAlias=True)
    for k in range(1, n + 1):
        q = skia.Path(); q.moveTo(-600, f(-600) + k * gap)
        for x in range(-600, W + 601, 12): q.lineTo(x, f(x) + k * gap + k * 4 * math.sin(x * 0.01 + k))
        cv.drawPath(q, P(stripe, 255, stroke=5))
    cv.restore()
    cv.drawPath(p, P(OUT, 255, stroke=6))


def mesa(cv, x, y, w, h, col, stripe):
    p = skia.Path(); p.moveTo(x - w / 2, y); p.lineTo(x - w * 0.36, y - h * 0.9); p.quadTo(x, y - h * 1.08, x + w * 0.36, y - h * 0.9)
    p.lineTo(x + w / 2, y); p.close()
    cv.drawPath(p, P(col)); cv.save(); cv.clipPath(p, doAntiAlias=True)
    for k in range(1, 6): cv.drawLine(x - w, y - h * k / 6, x + w, y - h * k / 6 - 8, P(stripe, 255, stroke=5))
    cv.restore(); cv.drawPath(p, P(OUT, 255, stroke=5))


def striped_sun(cv, x, y, r, t, cols):
    cv.save(); cv.translate(x, y); cv.rotate(t * 3)
    for k in range(18):
        p = skia.Path(); p.moveTo(0, 0)
        a0, a1 = math.radians(k * 20), math.radians(k * 20 + 9)
        p.lineTo(r * 2.4 * math.cos(a0), r * 2.4 * math.sin(a0)); p.lineTo(r * 2.4 * math.cos(a1), r * 2.4 * math.sin(a1)); p.close()
        cv.drawPath(p, P(cols[0], 40))
    cv.restore()
    for i, c in enumerate(cols):
        rr = r * (1 - i / len(cols)) + 4 * math.sin(t * 1.2 - i)
        cv.drawCircle(x, y, rr, P(c)); cv.drawCircle(x, y, rr, P(OUT, 255, stroke=4))


def plant(cv, x, y, h, col, bulb, t, ph, kind='eye'):
    sway = 18 * math.sin(t * 0.9 + ph)
    tx, ty = x + sway, y - h
    p = skia.Path(); p.moveTo(x, y); p.cubicTo(x - 30, y - h * 0.4, tx + 40, y - h * 0.7, tx, ty)
    cv.drawPath(p, P(OUT, 255, stroke=17)); cv.drawPath(p, P(col, 255, stroke=9))
    for s_ in (-1, 1):                                    # feuilles
        lx, ly = x + s_ * 4, y - h * 0.35
        lf = skia.Path(); lf.moveTo(lx, ly); lf.quadTo(lx + s_ * 60, ly - 50, lx + s_ * 90, ly - 10); lf.quadTo(lx + s_ * 50, ly + 10, lx, ly); lf.close()
        cv.drawPath(lf, P(col)); cv.drawPath(lf, P(OUT, 255, stroke=5))
    r = h * 0.1
    if kind == 'eye':
        cv.drawCircle(tx, ty, r * 1.25, P(bulb)); cv.drawCircle(tx, ty, r * 1.25, P(OUT, 255, stroke=5))
        cv.save(); cv.translate(tx, ty); eye(cv, r * 0.85, '#2DE2C6', t, (math.sin(t * 0.5 + ph), 0.3), 255, ph); cv.restore()
    else:                                                  # fleur
        op = kind if isinstance(kind, float) else 1.0
        for k in range(6):
            a = k * math.pi / 3 + t * 0.2
            pet = skia.Path(); pet.addOval(skia.Rect.MakeXYWH(-r * 0.45, -r * 1.7 * op - r * 0.2, r * 0.9, r * 1.7 * op))
            cv.save(); cv.translate(tx, ty); cv.rotate(math.degrees(a)); cv.drawPath(pet, P(bulb)); cv.drawPath(pet, P(OUT, 255, stroke=4)); cv.restore()
        cv.drawCircle(tx, ty, r * 0.6, P('#F0D890')); cv.drawCircle(tx, ty, r * 0.6, P(OUT, 255, stroke=4))


def island(cv, x, y, w, top, rock, stripe, t, ph=0):
    y += 8 * math.sin(t * 0.8 + ph)
    p = skia.Path(); p.moveTo(x - w / 2, y)
    p.cubicTo(x - w * 0.4, y + w * 0.35, x - w * 0.12, y + w * 0.75, x, y + w * 0.85)
    p.cubicTo(x + w * 0.12, y + w * 0.7, x + w * 0.4, y + w * 0.3, x + w / 2, y); p.close()
    cv.drawPath(p, P(rock)); cv.save(); cv.clipPath(p, doAntiAlias=True)
    for k in range(1, 7): cv.drawLine(x - w, y + k * w * 0.11, x + w, y + k * w * 0.11 + 10, P(stripe, 255, stroke=max(3, w * 0.012)))
    cv.restore(); cv.drawPath(p, P(OUT, 255, stroke=max(3, w * 0.012)))
    tp = skia.Path(); tp.addOval(skia.Rect.MakeLTRB(x - w / 2 - 6, y - w * 0.07, x + w / 2 + 6, y + w * 0.07))
    cv.drawPath(tp, P(top)); cv.drawPath(tp, P(OUT, 255, stroke=max(3, w * 0.012)))
    return y


def figure(cv, x, y, s, col):
    body = skia.Path(); body.moveTo(x - s * 0.45, y); body.quadTo(x, y - s * 1.3, x + s * 0.45, y); body.close()
    cv.drawPath(body, P(col)); cv.drawPath(body, P(OUT, 255, stroke=3))
    cv.drawCircle(x, y - s * 1.05, s * 0.3, P(col)); cv.drawCircle(x, y - s * 1.05, s * 0.3, P(OUT, 255, stroke=3))
    cv.drawCircle(x, y - s * 1.15, s * 0.07, P('#FFE680'))


def floating_ring(cv, x, y, r, t, col, stripe, ph=0):
    y += 12 * math.sin(t * 0.7 + ph)
    ring = skia.Path(); ring.addOval(skia.Rect.MakeLTRB(x - r, y - r * 0.38, x + r, y + r * 0.38))
    cv.drawPath(ring, P(OUT, 255, stroke=r * 0.22 + 10)); cv.drawPath(ring, P(col, 255, stroke=r * 0.22))
    cv.drawPath(ring, P(stripe, 255, stroke=4))


def pyramid(cv, x, y, s, t, col, side, ph=0):
    y += 14 * math.sin(t * 0.6 + ph)
    a = skia.Path(); a.moveTo(x, y - s); a.lineTo(x - s * 0.8, y + s * 0.5); a.lineTo(x + s * 0.1, y + s * 0.65); a.close()
    b = skia.Path(); b.moveTo(x, y - s); b.lineTo(x + s * 0.1, y + s * 0.65); b.lineTo(x + s * 0.8, y + s * 0.45); b.close()
    for q, c in ((a, col), (b, side)): cv.drawPath(q, P(c)); cv.drawPath(q, P(OUT, 255, stroke=5))


def dots(cv, seed, n, area, col, rmax=2.6):
    rnd = random.Random(seed)
    for _ in range(n):
        circle(cv, rnd.uniform(area[0], area[2]), rnd.uniform(area[1], area[3]), rnd.uniform(1.2, rmax), col, 220)


# ---------------- scènes ----------------
def s_temps(cv, t):
    banded_sky(cv, ['#0A0716', '#100A20', '#170E2C', '#1F1238', '#2A1744', '#381D50'], -600, 1300, t)
    dots(cv, 1, 90, (-100, -100, W + 100, 700), '#B8A8D0')
    striped_sun(cv, PX, 900, 400, t, ['#4A2350', '#5A2C5C', '#6C3666', '#7E4270', '#90507A'])
    floating_ring(cv, 170, 330, 110, t, '#3E5A6A', '#5A7A86', 0)
    pyramid(cv, 900, 420, 85, t, '#6A4A7A', '#4A3060', 1)
    mesa(cv, 120, 1330, 260, 260, '#24173A', '#2E1E48'); mesa(cv, 960, 1340, 300, 220, '#24173A', '#2E1E48')
    mg.melting_clock(cv, 120, 1010, 62, t, face='#B8A27A', drip=1.0, speed=0.6)
    hill(cv, 1400, 40, 0.006, 0.3, '#2A1A40', '#33214C', t)
    hill(cv, 1560, 50, 0.005, 2.0, '#1A2438', '#223048', t)
    for x, h, ph, b in ((90, 330, 0, '#C8A8D8'), (230, 220, 1.3, '#8FC8C0'), (870, 280, 2.2, '#D89AAE'), (1000, 200, 3.1, '#E0B890')):
        plant(cv, x, 1700, h, '#2E5A5A', b, t, ph)
    hero(cv, t, PX, PY + 0.55 * HS, HS, 'open', look=(0.2, -0.9))
    hill(cv, 1790, 30, 0.008, 4.0, '#121826', '#1A2232', t, n=3)


ISL = [(160, 520, 150, 0.0), (900, 380, 120, 1.1), (300, 980, 100, 2.3), (870, 860, 170, 3.3)]


def s_seul(cv, t):
    banded_sky(cv, ['#03050C', '#060A16', '#0A0F20', '#0E152A', '#131B34', '#18213C'], -600, 1700, t)
    dots(cv, 2, 160, (-100, -100, W + 100, H), '#9AA8C8')
    cv.drawCircle(860, 200, 95, P('#BDB6CE')); cv.drawCircle(860, 200, 95, P(OUT, 255, stroke=5))
    for cx_, cy_, r_ in ((830, 180, 18), (885, 230, 12), (870, 160, 9)): cv.drawCircle(cx_, cy_, r_, P('#A49CB8'))
    for x, y, w, ph in ISL:
        yy = island(cv, x, y, w, '#2A3C4C', '#1C1630', '#251E3C', t, ph)
        figure(cv, x, yy - 4, w * 0.16, '#4A4466')
    # le perso sur son île
    top = 1660
    old = pd.S; pd.S = top - 40
    hero(cv, t, PX, PY + 0.55 * HS, HS, 'open', look=(0.6, -0.7))
    pd.S = old
    yy = island(cv, PX, top, 820, '#2A3C4C', '#1C1630', '#251E3C', t * 0, 0)
    for x, h, ph, b in ((190, 170, 0.5, '#8FC8C0'), (290, 110, 1.9, '#C8A8D8'), (800, 140, 2.8, '#D89AAE'), (895, 95, 3.6, '#E0B890')):
        plant(cv, x, top + 10, h, '#2E5A5A', b, t, ph)
    for k in range(9):                                     # chute d'eau abstraite
        x = PX - 240 + k * 60
        pp = skia.Path(); pp.moveTo(x, top + 140 + (k % 3) * 40); pp.lineTo(x, H + 100)
        paint = P('#5A7090', 200, stroke=5); paint.setPathEffect(skia.DashPathEffect.Make([40, 30], -t * 120 - k * 13))
        cv.drawPath(pp, paint)


def s_pensees(cv, t, boost=0.0):
    cv.drawRect(BIG, P('#0C0818'))
    cols = ['#1A0E2A', '#22123A', '#2A1746', '#1C1838', '#261A44', '#301E50']
    for i in range(16, 0, -1):                            # tunnel organique
        R = 60 + i * 95
        n = 14; pts = []
        for k in range(n):
            a = k / n * 2 * math.pi + t * 0.06 * (1 if i % 2 else -1)
            rr = R * (1 + 0.07 * math.sin(a * 3 + i + t * 0.8))
            pts.append((PX + rr * math.cos(a), PY + rr * 1.15 * math.sin(a)))
        p = skia.Path(); m = [((pts[j][0] + pts[(j + 1) % n][0]) / 2, (pts[j][1] + pts[(j + 1) % n][1]) / 2) for j in range(n)]
        p.moveTo(*m[-1])
        for j in range(n): p.quadTo(*pts[j], *m[j])
        p.close()
        cv.drawPath(p, P(cols[i % len(cols)])); cv.drawPath(p, P(OUT, 255, stroke=6))
        if i % 3 == 0:
            q = P('#3A2456', 255, stroke=4); q.setPathEffect(skia.DashPathEffect.Make([18, 26], t * 20)); cv.drawPath(p, q)
    pyramid(cv, 170, 520, 90, t, '#5A4A7A', '#3E3060', 0)
    floating_ring(cv, 900, 600, 100, t, '#4A3A6A', '#6A5A8A', 2)
    cv.drawCircle(880, 1580 + 14 * math.sin(t * 0.7), 70, P('#3E5A6A')); cv.drawCircle(880, 1580 + 14 * math.sin(t * 0.7), 70, P(OUT, 255, stroke=5))
    for k in range(3): cv.drawLine(812, 1560 + k * 22 + 14 * math.sin(t * 0.7), 948, 1560 + k * 22 + 14 * math.sin(t * 0.7), P('#2A4250', 255, stroke=6))
    hero(cv, t, PX, PY + 0.55 * HS, HS, 'closed')
    for k, kind in enumerate(['spiral', 'moon', 'star4', 'eye', 'diamond', 'star4']):   # quelques pensées qui montent
        u = (t * 0.18 + k / 6) % 1.0
        x = PX + 160 * math.sin(u * 5 + k) * u
        sym(cv, kind, x, PY - u * 900, 10 + u * 34, k * 20 + t * 10, ['#C8A8D8', '#8FC8C0', '#E0B890', '#D89AAE', '#A8B8E0', '#C8A8D8'][k], t,
            255 * clamp(u * 5) * clamp((1 - u) * 4), seed=k)


def s_liens(cv, t):
    lt = t - T_CD[0]
    banded_sky(cv, ['#3A2E52', '#4E3C66', '#664C78', '#7E5E86', '#967090', '#A98296'], -600, 1350, t)
    striped_sun(cv, PX, 1250, 330, t, ['#C89A98', '#D4A8A0', '#E0B8A8', '#EAC8B0'])
    hill(cv, 1330, 45, 0.006, 1.0, '#5E5078', '#685A84', t)
    hill(cv, 1500, 55, 0.005, 3.0, '#43406A', '#4C4A76', t)
    bloom = ease(clamp((lt - 2.0) / 1.2))
    for x, h, ph, b in ((70, 300, 0, '#E0B8C8'), (200, 200, 1.3, '#B8D8D0'), (900, 260, 2.2, '#E8C8A8'), (1020, 190, 3.1, '#D0B8E0')):
        plant(cv, x, 1720, h, '#3E6A68', b, t, ph, kind=max(0.25, bloom))
    ax, ay, sa = 320, 1230, 175
    pb = ease(clamp((lt - 0.5) / 1.1))
    bx, by, sb = 1350 + (770 - 1350) * pb, 1420, 175
    hero(cv, t, ax, ay, sa, 'open', look=(0.8, 0.5), pal=HERO)
    if pb > 0: hero(cv, t, bx, by, sb, 'open', look=(-0.8, -0.4), pal=OTHER, seed=9)
    hill(cv, 1800, 25, 0.008, 5.0, '#2A2644', '#322E50', t, n=3)
    e1 = (ax, ay - 0.55 * sa + 5 * math.sin(t * 2.1)); e2 = (bx, by - 0.55 * sb + 5 * math.sin(t * 2.1))
    pt = ease(clamp((lt - 1.4) / 1.0))
    if pt > 0:
        rnd = random.Random(3)
        for k in range(12):
            off = rnd.uniform(-200, 200) + 20 * math.sin(t * 1.0 + k)
            p = skia.Path(); p.moveTo(*e1); p.cubicTo(e1[0] + 180, e1[1] + off, e2[0] - 180, e2[1] - off * 0.8, *e2)
            for paint in (P(OUT, 255, stroke=7), P(['#F0EBBE', '#C8B8FF', '#9FE8D8', '#FFB8D0'][k % 4], 255, stroke=3)):
                if pt < 0.999: paint.setPathEffect(skia.TrimPathEffect.Make(0, pt))
                cv.drawPath(p, paint)


# ---------------- composition (calme) ----------------
def iris(cv, t, p, fn, col='#F0EBBE'):
    r = 1900 * ease(p) ** 1.3
    if r < 1: return
    cv.save(); cv.clipPath(skia.Path().addCircle(PX, PY, r), doAntiAlias=True); fn(cv, t); cv.restore()
    cv.drawCircle(PX, PY, r, P(OUT, 255, stroke=16)); cv.drawCircle(PX, PY, r, P(col, 255, stroke=5))


def zoomed(cv, fn, t, z):
    cv.save(); cv.translate(PX, PY); cv.scale(z, z); cv.translate(-PX, -PY); fn(cv, t); cv.restore()


TR = 0.75
def scene(cv, t):
    def ph(T): return (t - (T[1] - TR)) / TR
    if t < T_AB[1] - TR: s_temps(cv, t)
    elif t < T_AB[1]: zoomed(cv, s_temps, t, 1 + 0.6 * ease(ph(T_AB))); iris(cv, t, ph(T_AB), s_seul)
    elif t < T_BC[1] - TR: s_seul(cv, t)
    elif t < T_BC[1]: s_seul(cv, t); iris(cv, t, ph(T_BC), s_pensees, '#C8B8FF')
    elif t < T_CD[1] - TR: s_pensees(cv, t)
    elif t < T_CD[1]: s_pensees(cv, t); iris(cv, t, ph(T_CD), s_liens)
    else: s_liens(cv, t)


def draw_word(cv, t):
    cur, _ = current_word(t)
    if not cur or not cur[0]: return
    w, s, k = cur; age = t - s
    size = 190 if k else 165
    f = skia.Font(FONT, size); tw = f.measureText(w)
    if tw > 820: f.setSize(size * 820 / tw); tw = f.measureText(w)
    sc = 0.9 + 0.1 * ease_out(clamp(age / 0.16))
    cv.save(); cv.translate(W / 2, TY); cv.scale(sc, sc)
    x, y = -tw / 2, f.getSize() * 0.35; fs = f.getSize()
    out = P(OUT, 255, stroke=fs * 0.15); out.setStrokeJoin(skia.Paint.kRound_Join)
    cv.drawString(w, x + fs * 0.03, y + fs * 0.06, f, out); cv.drawString(w, x + fs * 0.03, y + fs * 0.06, f, P(OUT))
    cv.drawString(w, x, y, f, out); cv.drawString(w, x, y, f, P('#F0EBBE'))
    cv.restore()


def frame(fi):
    t = fi / FPS
    surf = skia.Surface(OW_, OH_); cv = surf.getCanvas(); cv.scale(SC, SC)
    z = 1.03 + 0.01 * math.sin(t * 0.5)
    cv.save(); cv.translate(PX, PY); cv.rotate(0.3 * math.sin(t * 0.35)); cv.scale(z, z)
    cv.translate(-PX + 8 * math.sin(t * 0.4), -PY + 8 * math.cos(t * 0.33))
    scene(cv, t); cv.restore()
    cv.drawRect(skia.Rect.MakeWH(W, H), P(shader=rad(W / 2, H / 2, 1250, [C('#000000', 0), C('#000000', 0), C('#000000', 80)], [0, 0.7, 1])))
    draw_word(cv, t)
    return surf.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType).tobytes()


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--preview':
        from PIL import Image
        for ts in sys.argv[2].split(','):
            arr = np.frombuffer(frame(int(float(ts) * FPS)), np.uint8).reshape(OH_, OW_, 4)
            Image.fromarray(arr[..., :3]).resize((540, 960), Image.LANCZOS).save(os.path.join(sys.argv[3], f'pv_{ts}.png'))
        sys.exit()
    out = os.path.join(HERE, 'extrait_test_v3_4k.mp4')
    n = int(DUR * FPS)
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', f'{OW_}x{OH_}', '-r', str(FPS), '-i', '-',
                           '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=stereo', '-t', str(DUR),
                           '-c:v', 'libx264', '-preset', 'slow', '-tune', 'animation', '-crf', '15', '-maxrate', '55M', '-bufsize', '110M',
                           '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-movflags', '+faststart', out], stdin=subprocess.PIPE)
    with Pool(4) as pool:
        for i, b in enumerate(pool.imap(frame, range(n), chunksize=2)):
            ff.stdin.write(b)
    ff.stdin.close(); ff.wait()
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', out, '-vf', 'scale=1080:1920:flags=lanczos', '-c:v', 'libx264', '-profile:v', 'high',
                    '-level', '4.1', '-crf', '18', '-preset', 'slow', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-movflags', '+faststart',
                    os.path.join(HERE, 'extrait_test_v3_apercu_1080p.mp4')])
    print('ok')
