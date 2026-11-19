"""« Pourquoi le temps passe de plus en plus vite » : 15 plans, style TikToks de référence × Midnight Gospel."""
import math, os, random, sys
import skia
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(1, os.path.join(HERE, '..', 'calendrier'))
sys.path.insert(1, HERE)
from lib import *
from kit import *
from mg import *

FONT = None
STYLE = dict(exclusion=True, color='#F0EBBE', size=196, maxw=1760, glitch=True, grain=7, readable=True)
RICH = ('#ffffff', '#ffffff', '#FF5A7A', '#6FA8FF', '#FFB13B', '#B98CFF')
ME = dict(skin='#FF8AB8', top='#2DE2C6', bottom='#8A4BFF', hair='#2A0E3A')


class Scene:
    zoom = (1.0, 1.08)
    pan = (0, 0, 0, 0)
    shake = 0.0

    def static(self, cv):
        pass

    def dyn(self, cv, t, d):
        pass


def psy_sky(cv, seed=1, top='#FF8AD8', mid='#8A4BFF', bottom='#2A0E5A'):
    cv.drawRect(skia.Rect.MakeXYWH(-400, -400, W + 800, H + 800), P(shader=lin(0, -200, 0, H + 200, [top, mid, bottom])))
    rnd = random.Random(seed)
    for i in range(7):
        y = 120 + i * 90
        p = skia.Path(); p.moveTo(-400, y)
        for x in range(-400, W + 440, 120):
            p.lineTo(x, y + 30 * math.sin(x * 0.004 + i))
        cv.drawPath(p, P(rnd.choice(['#FFFFFF', '#FFE6FF', '#FFD0A0']), 30, stroke=24))
    for _ in range(2200):
        circle(cv, rnd.uniform(-200, W + 200), rnd.uniform(-200, H + 200), rnd.uniform(0.8, 2.2), '#FFFFFF', 22)


def mountains(cv, seed, base, cols):
    rnd = random.Random(seed)
    for li, col in enumerate(cols):
        p = skia.Path(); p.moveTo(-400, H + 400); p.lineTo(-400, base + li * 60)
        x = -400
        while x < W + 400:
            x += rnd.uniform(140, 300)
            p.lineTo(x, base + li * 60 - rnd.uniform(80, 260))
            x += rnd.uniform(80, 160)
            p.lineTo(x, base + li * 60 - rnd.uniform(0, 60))
        p.lineTo(W + 400, H + 400); p.close()
        ofill(cv, p, col)


# 1 ─ « Tu as remarqué que chaque année passe plus vite que la précédente ? »
class Pages(Scene):
    zoom = (1.0, 1.1)

    def static(self, cv):
        psy_sky(cv, 1)
        mountains(cv, 2, 860, ['#C04BFF', '#7A2ABF'])
        junk_pile(cv, 3, 930, n=70)

    def dyn(self, cv, t, d):
        cx, cy = 960, 520
        ofill(cv, prr(cx - 190, cy - 120, 380, 420, 26), '#FFF6E0')
        ofill(cv, prr(cx - 190, cy - 120, 380, 110, 26), '#FF4FA8')
        f = skia.Font(FONT, 230); s = str(2020 + min(9, int(t * (1 + t))))
        cv.drawString(s[-2:], cx - f.measureText(s[-2:]) / 2, cy + 230, f, P(OL))
        rate = 1.5 + t * 2.0
        for i in range(14):
            k = ((t * rate * 0.25) + i / 14) % 1.0
            x = cx + (k * 1300) * math.cos(i * 1.3) * 0.8
            y = cy - 60 - k * 700 + 80 * math.sin(i)
            if k < 0.35:
                cv.save(); cv.translate(x, y); cv.rotate(k * 400 + i * 40)
                ofill(cv, prr(-90, -100, 180, 200, 14), '#FFF6E0', a=255)
                cv.restore()
            else:
                wing = 40 * math.sin(t * 14 + i)
                p = skia.Path(); p.moveTo(x - 60, y - wing); p.quadTo(x - 25, y - 20, x, y); p.quadTo(x + 25, y - 20, x + 60, y - wing)
                cv.drawPath(p, P(OL, 255, stroke=16)); cv.drawPath(p, P('#FFF6E0', 255, stroke=8))


# 2 ─ « Ce n'est pas dans ta tête. Enfin, si, justement. »
class HeadClock(Scene):
    zoom = (1.12, 1.0)

    def static(self, cv):
        psy_sky(cv, 4, '#FFB05A', '#FF4FA8', '#5A1A8A')
        junk_pile(cv, 5, 960, n=60)

    def dyn(self, cv, t, d):
        x, y, s = 960, 1160, 220
        lift = ease_out((t - 1.0) / 0.8)
        hx, hy = x, y - 2.2 * s - 1.4 * s
        # intérieur du crâne : horloge qui tourne
        if lift > 0:
            glow(cv, hx, hy - 0.4 * s, s * 1.3 * lift, '#FFE680', 220)
        dude(cv, x, y, s, t, mood='wow' if lift > 0.2 else 'calm', look=(0, -1), **ME)
        if lift > 0:
            cv.save(); cv.clipPath(pcircle(hx, hy, s * 0.98), doAntiAlias=True)
            cv.drawRect(skia.Rect.MakeXYWH(hx - s, hy - s, 2 * s, s * 0.75), P('#2A0E5A'))
            melting_clock(cv, hx, hy - 0.62 * s, s * 0.38 * lift, t * 3, drip=0.4)
            cv.restore()
            # couvercle du crâne qui se soulève
            cv.save(); cv.translate(hx + 0.6 * s * lift, hy - 0.25 * s - 0.9 * s * lift); cv.rotate(25 * lift)
            p = skia.Path(); p.addArc(skia.Rect.MakeLTRB(-s, -0.75 * s, s, 1.25 * s), 180, 180); p.close()
            ofill(cv, p, ME['hair'])
            cv.restore()


# 3 ─ « Quand tu avais cinq ans, une année représentait un cinquième de toute ta vie. »
class PieKid(Scene):
    zoom = (1.0, 1.1)

    def static(self, cv):
        psy_sky(cv, 6, '#9BFF3B', '#2DE2C6', '#1A5A8A')
        junk_pile(cv, 7, 950, n=50)

    def dyn(self, cv, t, d):
        cx, cy, R = 1300, 470, 330
        glow(cv, cx, cy, R * 1.4, '#FFFFFF', 90)
        ofill(cv, pcircle(cx, cy, R), '#8A4BFF')
        k = ease_out(t / 1.0)
        p = skia.Path(); p.moveTo(cx, cy); p.arcTo(skia.Rect.MakeLTRB(cx - R, cy - R, cx + R, cy + R), -90, 72 * k, False); p.close()
        cv.save(); cv.translate(18 * k, -10 * k); ofill(cv, p, '#FFE04A'); cv.restore()
        for i in range(1, 5):
            a = math.radians(-90 + 72 * i)
            cv.drawLine(cx, cy, cx + math.cos(a) * R, cy + math.sin(a) * R, P(OL, 255, stroke=5))
        label(cv, cx + 120, cy - 160, '1 AN', 40, color=OL, font=FONT, box=False)
        dude(cv, 480, 1075, 140, t, kid=True, mood='happy', arms='up', **ME)
        ofill(cv, prr(380, 380, 200, 90, 30), '#FFFFFF')
        label(cv, 480, 440, '5 ANS', 34, color=OL, font=FONT, box=False)


# 4 ─ « À trente ans, ce n'est plus qu'un trentième. Chaque année pèse un peu moins lourd. »
class PieAdult(Scene):
    zoom = (1.08, 1.0)

    def static(self, cv):
        psy_sky(cv, 8, '#2DE2C6', '#2DB8FF', '#2A0E5A')
        junk_pile(cv, 9, 950, n=50)

    def dyn(self, cv, t, d):
        cx, cy, R = 1300, 470, 330
        ofill(cv, pcircle(cx, cy, R), '#8A4BFF')
        k = ease(t / 1.2)
        sweep = 72 * (1 - k) + 12 * k
        p = skia.Path(); p.moveTo(cx, cy); p.arcTo(skia.Rect.MakeLTRB(cx - R, cy - R, cx + R, cy + R), -90, sweep, False); p.close()
        ofill(cv, p, '#FFE04A')
        n = int(5 + 25 * k)
        for i in range(1, n):
            a = math.radians(-90 + 360 * i / n)
            cv.drawLine(cx, cy, cx + math.cos(a) * R, cy + math.sin(a) * R, P(OL, 200, stroke=3))
        g = 1 + 0.5 * k
        dude(cv, 480, 1000, 150 * (0.85 + 0.15 * k), t, kid=k < 0.5, mood='tired' if k > 0.6 else 'calm', look=(1, -0.3), skin='#FF8AB8', top='#2DB8FF', bottom='#2A2A6A', hair='#2A0E3A')
        ofill(cv, prr(370, 240, 220, 90, 30), '#FFFFFF')
        label(cv, 480, 300, f'{int(5 + 25 * k)} ANS', 34, color=OL, font=FONT, box=False)


# 5 ─ « Mais il y a autre chose. »
class Other(Scene):
    zoom = (1.0, 1.2)

    def static(self, cv):
        grain_bg(cv, '#14063A', '#3A0E6A', 10)
        Stars(240, 11, rmax=2.4, colors=RICH).draw(cv, 0)

    def dyn(self, cv, t, d):
        holo_triangle(cv, 960, 420, 300, t)
        for k in range(8):
            a = k / 8 * 6.283 + t * 0.4
            ofill(cv, pcircle(960 + 520 * math.cos(a), 440 + 280 * math.sin(a), 30), PAL[k])
        dude(cv, 960, 1250, 170, t, mood='wow', look=(0, -1), **ME)


# 6 ─ « Ton cerveau ne mesure pas le temps avec une horloge. Il le mesure avec des souvenirs. »
class Jars(Scene):
    zoom = (1.0, 1.1)
    pan = (40, 0, -40, 0)

    def static(self, cv):
        grain_bg(cv, '#5A1A8A', '#2A0E4A', 12)
        for r in range(4):
            ofill(cv, prr(-100, 200 + r * 230, W + 200, 30, 6), '#8A4A2A')

    def dyn(self, cv, t, d):
        rnd = random.Random(13)
        k = ease((t - 1.0) / 2.0)
        for r in range(4):
            for c in range(14):
                x, y = 60 + c * 140 + (r % 2) * 50, 200 + r * 230
                col = rnd.choice(PAL)
                a = min(1, max(0, k * 14 - (c + r * 3) * 0.25))
                if a <= 0:
                    continue
                ofill(cv, prr(x - 40, y - 140, 80, 140, 20), '#BFF6FF', a=200 * a)
                ofill(cv, prr(x - 34, y - 160, 68, 26, 8), '#8A4A2A', a=255 * a)
                glow(cv, x, y - 70, 50, col, 200 * a)
                ofill(cv, pblob(x, y - 70, 18, seed=r * 20 + c, t=t), col, a=255 * a)
        # horloge qui fond au premier plan
        melting_clock(cv, 960, 300, 200 * (1 - 0.5 * k), t, drip=0.6 + 2.5 * k)


# 7 ─ « Quand tu vis quelque chose de nouveau, il enregistre tout : les couleurs, les odeurs, les détails. Le temps paraît long. »
class Rich(Scene):
    zoom = (1.15, 1.0)

    def static(self, cv):
        psy_sky(cv, 14, '#FF8AD8', '#FF8A1F', '#8A2A6A')
        mountains(cv, 15, 760, ['#C04BFF', '#2DE2C6', '#7A2ABF'])

    def dyn(self, cv, t, d):
        k = t / max(d, 0.1)
        rnd = random.Random(16)
        items = [(rnd.uniform(-50, W + 50), rnd.uniform(700, 1060), rnd.uniform(0.7, 1.5), rnd.randrange(8), rnd.choice(PAL), rnd.random()) for _ in range(110)]
        for x, y, s, kind, c, ap in sorted(items, key=lambda q: q[1]):
            a = ease_out((k - ap * 0.8) / 0.12)
            if a > 0:
                junk(cv, kind, x, y + (1 - a) * 80, s * a, c, t)
        for i in range(6):
            p = skia.Path(); x0 = 200 + i * 300; p.moveTo(x0, 900)
            for j in range(1, 12):
                p.lineTo(x0 + 40 * math.sin(j * 0.8 + t * 2 + i), 900 - j * 50)
            cv.drawPath(p, P(PAL[i], 170 * min(1, k * 3), stroke=10))
        for i in range(16):
            a = i * 0.7 + t * 0.5
            sparkle(cv, 960 + 800 * math.cos(a), 300 + 200 * math.sin(a * 1.3), 20, PAL[i % 9])


# 8 ─ « Quand tes journées se ressemblent, il n'enregistre presque rien. »
class Loop(Scene):
    zoom = (1.0, 1.08)

    def static(self, cv):
        grain_bg(cv, '#6A6A8A', '#3A3A5A', 17)

    def dyn(self, cv, t, d):
        g = min(1.0, t / max(d, 0.1) * 1.2)
        m = [0.33, 0.33, 0.33, 0, 0, 0.33, 0.33, 0.33, 0, 0, 0.33, 0.33, 0.33, 0, 0, 0, 0, 0, 1, 0]
        ident = [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0]
        p = skia.Paint(); p.setColorFilter(skia.ColorFilters.Matrix([ident[i] + (m[i] - ident[i]) * g for i in range(20)]))
        cv.saveLayer(None, p)
        cx, cy = 960, 700
        ofill(cv, poval(cx, cy + 60, 760, 260), '#5A5A7A')
        ofill(cv, poval(cx, cy + 60, 560, 160), '#7A7A9A')
        for i, (a, kind) in enumerate([(0.2, 3), (1.8, 5), (3.3, 0), (4.8, 4)]):
            junk(cv, kind, cx + 660 * math.cos(a), cy + 60 + 210 * math.sin(a) + 40, 1.6, PAL[i * 2])
        ang = t * 1.6
        x, y = cx + 660 * math.cos(ang), cy + 60 + 210 * math.sin(ang)
        dude(cv, x, y + 20, 70, t * 3, mood='tired', look=(math.cos(ang + 1.57), 0), **ME)
        cv.restore()
        neon(cv, [(cx + 820 * math.cos(a / 30 * 6.283), cy + 60 + 300 * math.sin(a / 30 * 6.283)) for a in range(0, 28)], '#E8E8F0', w=4, arrow=True, a=150)


# 9 ─ « Métro, boulot, écran, dodo. »
class Routine(Scene):
    zoom = (1.0, 1.06)

    def static(self, cv):
        grain_bg(cv, '#5A5A7A', '#2A2A4A', 18)
        ofill(cv, prr(-100, 820, W + 200, 60, 20), '#3A3A5A')

    def _panel(self, cv, kind, x, y, t):
        ofill(cv, prr(x, y, 380, 360, 30), '#8A8AA8')
        cv.save(); cv.clipPath(prr(x, y, 380, 360, 30), doAntiAlias=True)
        if kind == 0:
            ofill(cv, prr(x + 30, y + 40, 320, 160, 20), '#A8A8C0')
            for k in range(3):
                ofill(cv, prr(x + 50 + k * 100, y + 60, 70, 90, 10), '#C8C8E0')
        elif kind == 1:
            ofill(cv, prr(x + 60, y + 170, 260, 30, 6), '#6A6A8A')
            ofill(cv, prr(x + 140, y + 90, 110, 80, 8), '#C8C8E0')
        elif kind == 2:
            ofill(cv, prr(x + 90, y + 60, 200, 140, 14), '#C8C8E0')
            cv.drawRect(skia.Rect.MakeXYWH(x + 104, y + 74, 172, 112), P('#9AB8C8'))
        else:
            ofill(cv, prr(x + 40, y + 170, 300, 80, 20), '#C8C8E0')
            ofill(cv, poval(x + 110, y + 170, 60, 30), '#E8E8F0')
        dude(cv, x + 190, y + 400, 50, t, mood='tired', skin='#C8B8C8', top='#9A9AB0', bottom='#6A6A8A', hair='#4A4A6A', legs='none')
        cv.restore()
        label(cv, x + 190, y + 330, ['MÉTRO', 'BOULOT', 'ÉCRAN', 'DODO'][kind], 30, color=OL, font=FONT, box=False)

    def dyn(self, cv, t, d):
        off = (t * 260) % 440
        for i in range(7):
            x = -440 + i * 440 + off
            self._panel(cv, i % 4, x, 440, t)


# 10 ─ « Et des mois entiers se compressent en un seul souvenir flou. »
class Compress(Scene):
    zoom = (1.0, 1.15)

    def static(self, cv):
        grain_bg(cv, '#3A2A6A', '#1A0E3A', 19)

    def dyn(self, cv, t, d):
        k = ease(t / max(d * 0.85, 0.1))
        rnd = random.Random(20)
        for i in range(40):
            a = rnd.uniform(0, 6.283); r0 = rnd.uniform(300, 900)
            r = r0 * (1 - k)
            x, y = 960 + math.cos(a) * r, 540 + math.sin(a) * r * 0.6
            ofill(cv, prr(x - 30, y - 50, 60, 100, 16), mix(rnd.choice(PAL), '#8A8AA8', k), a=255 * (1 - k * 0.7))
        R = 80 + 220 * k
        glow(cv, 960, 540, R * 1.4, '#C8C8E0', 120 * k)
        cv.drawCircle(960, 540, R, P('#9A9AB8', 200 * k, blur=20 * k + 1))
        circle(cv, 960, 540, R, '#E8E8F0', 120 * k, stroke=6)


# 11 ─ « C'est pour ça que les étés de ton enfance semblaient durer une éternité. Tout était nouveau. »
class Summer(Scene):
    zoom = (1.12, 1.0)

    def __init__(self):
        rnd = random.Random(21)
        self.drops = [(rnd.uniform(900, 1700), rnd.uniform(500, 800), rnd.uniform(8, 18)) for _ in range(30)]

    def static(self, cv):
        psy_sky(cv, 22, '#FFE04A', '#FF8A1F', '#FF4FA8')
        glow(cv, 1500, 260, 400, '#FFFFFF', 160)
        ofill(cv, pcircle(1500, 260, 150), '#FFF6B0')
        ofill(cv, prr(-100, 820, W + 200, 400, 0), '#2DE2C6')
        for k in range(14):
            cv.drawLine(k * 150, 860 + (k % 3) * 40, k * 150 + 90, 860 + (k % 3) * 40, P('#FFFFFF', 160, stroke=6))
        junk_pile(cv, 23, 820, n=24, rows=1, spread=(-100, 700))

    def dyn(self, cv, t, d):
        hx, hy = dude(cv, 560, 1000, 160, t * 0.3, kid=True, mood='joy', arms='up', skin='#FF8AB8', top='#FFE04A', bottom='#FF4FA8', hair='#2A0E3A')
        # glace qui fond lentement
        ix, iy = 560 + 1.1 * 160, 1000 - 1.6 * 160 - 0.9 * 160
        ofill(cv, ppoly([(ix - 40, iy), (ix + 40, iy), (ix, iy + 120)]), '#E8B86A')
        ofill(cv, pblob(ix, iy - 20, 50, seed=4, t=t * 0.3), '#FF8AD8')
        for x, y, r in self.drops:
            yy = y + 6 * math.sin(t * 0.8 + x)
            ofill(cv, pblob(x, yy, r, n=6, seed=int(x), t=t * 0.2), '#BFF6FF', w=4)
        label(cv, 1300, 160, 'TEMPS × 0,1', 30, color=OL, font=FONT, box=False)


# 12 ─ « Alors si tu veux ralentir le temps, il n'y a pas de secret. »
class Slow(Scene):
    zoom = (1.0, 1.12)

    def static(self, cv):
        psy_sky(cv, 24, '#8A4BFF', '#E83CFF', '#2A0E5A')
        junk_pile(cv, 25, 950, n=60)

    def dyn(self, cv, t, d):
        sp = max(0.05, 1.0 - t / max(d, 0.1))
        melting_clock(cv, 1300, 400, 260, t * sp, drip=0.3, speed=sp * 3)
        dude(cv, 560, 1060, 170, t * 0.5, mood='calm', look=(1, -0.5), arms='out', **ME)


# 13 ─ « Change de chemin. Goûte un truc bizarre. Pars quelque part sans raison. »
class Novelty(Scene):
    zoom = (1.0, 1.08)

    def static(self, cv):
        psy_sky(cv, 26, '#FF8AD8', '#2DE2C6', '#3A0E6A')

    def dyn(self, cv, t, d):
        third = d / 3
        if t < third:
            for i, c in enumerate(['#FF4FA8', '#FF8A1F', '#FFE04A', '#9BFF3B', '#2DB8FF', '#8A4BFF']):
                p = skia.Path(); p.moveTo(960 - 60 + i * 20, H + 40); p.cubicTo(960, 800, 1400, 700, 1500 + i * 30, 300)
                cv.drawPath(p, P(OL, 255, stroke=44)); cv.drawPath(p, P(c, 255, stroke=30))
            p = skia.Path(); p.moveTo(900, H + 40); p.cubicTo(900, 800, 600, 700, 400, 300)
            cv.drawPath(p, P(OL, 255, stroke=110)); cv.drawPath(p, P('#8A8AA8', 255, stroke=96))
            dude(cv, 960, 1040, 110, t * 2, mood='wow', look=(1, -0.5), **ME)
        elif t < 2 * third:
            fx, fy = 960, 600
            ofill(cv, pblob(fx, fy, 260, n=11, seed=7, t=t * 3, wob=0.18), '#9BFF3B')
            for k in range(9):
                a = k / 9 * 6.283
                ofill(cv, pcircle(fx + math.cos(a) * 170, fy + math.sin(a) * 130, 22), '#FF4FA8', w=4)
            for k, dx in enumerate((-80, 80)):
                ofill(cv, pcircle(fx + dx, fy - 40, 50), '#FFFFFF')
                circle(cv, fx + dx + 14 * math.sin(t * 3 + k), fy - 40, 18, OL)
            ofill(cv, prr(fx - 20, fy - 330, 40, 90, 14), '#8A4A2A')
            ofill(cv, poval(fx + 60, fy - 300, 70, 30), '#3FD07A')
        else:
            k = (t - 2 * third) / third
            sx, sy = 960 + 400 * k, 700 - 500 * k
            for side in (-1, 1):
                wing = 30 * math.sin(t * 12)
                ofill(cv, poval(sx + side * 190, sy - 60 - wing * side * 0.3, 140, 60), '#FFFFFF')
            ofill(cv, prr(sx - 150, sy - 110, 300, 220, 30), '#FF8A1F')
            ofill(cv, prr(sx - 50, sy - 160, 100, 60, 20), '#8A4A2A', w=OW)
            for i, c in enumerate(['#2DE2C6', '#FFE04A']):
                ofill(cv, pcircle(sx - 70 + i * 140, sy, 30), c)


# 14 ─ « Fais quelque chose pour la première fois. »
class Door(Scene):
    zoom = (1.0, 1.25)

    def static(self, cv):
        grain_bg(cv, '#3A2A6A', '#1A0E3A', 27)

    def dyn(self, cv, t, d):
        k = ease_out((t - 0.3) / 1.0)
        dx, dy, dw, dh = 760, 160, 400, 760
        cv.save(); cv.clipPath(prr(dx, dy, dw, dh, 200), doAntiAlias=True)
        cv.drawRect(skia.Rect.MakeXYWH(dx, dy, dw, dh), P(shader=lin(0, dy, 0, dy + dh, ['#FFE04A', '#FF4FA8', '#8A4BFF'])))
        for i in range(16):
            cv.save(); cv.translate(960, 540); cv.rotate(i * 22.5 + t * 20)
            ofill(cv, ppoly([(0, 0), (900, -60), (900, 60)]), PAL[i % 9], a=200, w=3); cv.restore()
        holo_triangle(cv, 960, 480, 120, t)
        cv.restore()
        ofill(cv, prr(dx - 30, dy - 30, dw + 60, dh + 30, 220), '#000000', a=0, w=OW * 2)
        cv.save(); cv.translate(dx, dy); cv.scale(max(0.02, 1 - k), 1)
        ofill(cv, prr(0, 0, dw, dh, 200), '#8A4A2A')
        ofill(cv, pcircle(dw - 60, dh / 2, 24), '#FFE04A')
        cv.restore()
        if k > 0.3:
            rnd = random.Random(28)
            for i in range(60):
                a = rnd.uniform(-1.2, 1.2) + math.pi / 2 * 0 + (math.pi if rnd.random() < 0.5 else 0)
                r = 300 + 900 * (k - 0.3) * rnd.uniform(0.4, 1)
                ofill(cv, pcircle(960 + math.cos(a) * r, 540 + math.sin(a) * r * 0.7, rnd.uniform(10, 26)), rnd.choice(PAL), w=4)
        dude(cv, 960, 1250, 150, t, mood='wow', look=(0, -1), **ME)


# 15 ─ « Et tu verras : ta vie va te sembler beaucoup plus longue. »
class Flowers(Scene):
    zoom = (1.12, 1.0)

    def static(self, cv):
        psy_sky(cv, 29, '#FF8AD8', '#FFB05A', '#5A1A8A')
        holo_triangle(cv, 1500, 260, 150, 0)
        p = skia.Path(); p.moveTo(-400, H + 400); p.lineTo(-400, 800); p.quadTo(960, 700, W + 400, 820); p.lineTo(W + 400, H + 400); p.close()
        ofill(cv, p, '#3FD07A')

    def dyn(self, cv, t, d):
        rnd = random.Random(30)
        for i in range(60):
            x, y = rnd.uniform(0, W), rnd.uniform(820, 1080)
            k = ease_out((t - rnd.uniform(0, d * 0.6)) / 0.5)
            if k <= 0:
                continue
            cv.drawLine(x, y, x, y - 40 * k, P(OL, 255, stroke=8)); cv.drawLine(x, y, x, y - 40 * k, P('#2E8A55', 255, stroke=4))
            for j in range(5):
                a = j * 1.256 + t * 0.4
                ofill(cv, pcircle(x + math.cos(a) * 13 * k, y - 40 * k + math.sin(a) * 13 * k, 10 * k), rnd.choice(PAL), w=3)
            ofill(cv, pcircle(x, y - 40 * k, 7 * k), '#FFE04A', w=3)
        # horloge dont les aiguilles deviennent des fleurs
        cx, cy, R = 700, 330, 170
        ofill(cv, pcircle(cx, cy, R), '#FFF6E0')
        for i in range(12):
            a = i / 12 * 6.283
            circle(cv, cx + math.cos(a) * R * 0.75, cy + math.sin(a) * R * 0.75, 7, OL)
        for ang, ln in ((t * 0.05 - 1.2, 0.5), (t * 0.1 + 0.4, 0.8)):
            x2, y2 = cx + math.cos(ang) * R * ln, cy + math.sin(ang) * R * ln
            noodle(cv, [(cx, cy), (x2, y2)], '#3FD07A', w=10)
            for j in range(6):
                a = j * 1.05 + t
                ofill(cv, pcircle(x2 + math.cos(a) * 20, y2 + math.sin(a) * 20, 14), '#FF4FA8', w=3)
            ofill(cv, pcircle(x2, y2, 12), '#FFE04A', w=3)
        # le personnage allongé dans l'herbe, heureux
        cv.save(); cv.translate(1180, 930); cv.rotate(-80)
        dude(cv, 0, 0, 120, t * 0.4, mood='happy', arms='up', **ME)
        cv.restore()


SEGMENTS = [
    (Pages, "Tu as remarqué que chaque année passe plus vite que la précédente ?"),
    (HeadClock, "Ce n'est pas dans ta tête. Enfin, si, justement."),
    (PieKid, "Quand tu avais cinq ans, une année représentait un cinquième de toute ta vie."),
    (PieAdult, "À trente ans, ce n'est plus qu'un trentième. Chaque année pèse un peu moins lourd."),
    (Other, "Mais il y a autre chose."),
    (Jars, "Ton cerveau ne mesure pas le temps avec une horloge. Il le mesure avec des souvenirs."),
    (Rich, "Quand tu vis quelque chose de nouveau, il enregistre tout : les couleurs, les odeurs, les détails. Le temps paraît long."),
    (Loop, "Quand tes journées se ressemblent, il n'enregistre presque rien."),
    (Routine, "Métro, boulot, écran, dodo."),
    (Compress, "Et des mois entiers se compressent en un seul souvenir flou."),
    (Summer, "C'est pour ça que les étés de ton enfance semblaient durer une éternité. Tout était nouveau."),
    (Slow, "Alors si tu veux ralentir le temps, il n'y a pas de secret."),
    (Novelty, "Change de chemin. Goûte un truc bizarre. Pars quelque part sans raison."),
    (Door, "Fais quelque chose pour la première fois."),
    (Flowers, "Et tu verras : ta vie va te sembler beaucoup plus longue."),
]
