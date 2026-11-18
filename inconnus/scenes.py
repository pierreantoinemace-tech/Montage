"""« Les inconnus » : 17 plans, style v2 (même kit que calendrier/)."""
import math, os, random, sys
import skia
sys.path.insert(1, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'calendrier'))
from lib import *
from kit import *

FONT = None
STYLE = dict(exclusion=True, color='#F0EBBE', size=196, maxw=1760, glitch=True, grain=7)

SKINS = ['#F2A97E', '#C98058', '#8A5236', '#FFD0B0', '#A0663E']
HAIRS = ['#2A1A14', '#5A2A14', '#1A1030', '#E0A030', '#B04A1A', '#C8C8D8']
TOPS = ['#FF4F81', '#2DB8FF', '#FFD34A', '#3FC46A', '#7A4BFF', '#FF8A3D', '#2DE2C6', '#E83CFF']
PANTS = ['#1E1F5C', '#2B2A7A', '#3A1E5A', '#1A3A6A']
MOODS = ['smile', 'smile', 'calm', 'happy', 'wow', 'sad']
YOU = dict(top='#FF4F81', hair='#2A1A14', skin='#C98058', pants='#2B2A7A', hairstyle=0)


class Scene:
    zoom = (1.0, 1.08)
    pan = (0, 0, 0, 0)
    shake = 0.0

    def static(self, cv):
        pass

    def dyn(self, cv, t, d):
        pass


def person(rnd):
    return dict(skin=rnd.choice(SKINS), hair=rnd.choice(HAIRS), top=rnd.choice(TOPS), pants=rnd.choice(PANTS),
                hairstyle=rnd.choice([0, 0, 1, 2, 3]), mood=rnd.choice(MOODS))


class Crowd:
    """Foule de personnages de face qui défilent sur plusieurs profondeurs."""
    def __init__(self, n, seed, rows=((780, 34), (880, 44), (1000, 56)), speed=90):
        rnd = random.Random(seed)
        self.p = []
        for i in range(n):
            y, s = rows[i % len(rows)]
            self.p.append((rnd.uniform(-200, W + 200), y, s, rnd.choice([-1, 1]) * rnd.uniform(0.6, 1.3) * speed, rnd.uniform(0, 6), person(rnd)))
        self.p.sort(key=lambda q: q[1])

    def draw(self, cv, t, mood=None, extra=None):
        for x, y, s, v, ph, pr in self.p:
            xx = (x + v * t) % (W + 400) - 200
            kw = dict(pr); m = mood or kw.pop('mood'); kw.pop('mood', None)
            char_front(cv, xx, y, s, t * 1.3 + ph, mood=m, look=(1 if v > 0 else -1, 0), **kw)
            if extra:
                extra(cv, xx, y, s, t, ph, pr)


def grey_layer(cv, k=1.0):
    m = [0.33, 0.33, 0.33, 0, 0, 0.33, 0.33, 0.33, 0, 0, 0.33, 0.33, 0.33, 0, 0, 0, 0, 0, 1, 0]
    ident = [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0]
    mm = [ident[i] + (m[i] - ident[i]) * k for i in range(20)]
    p = skia.Paint(); p.setColorFilter(skia.ColorFilters.Matrix(mm))
    cv.saveLayer(None, p)


def street_bg(cv, sky=('#2A1466', '#FF8AB8'), seed=1, ground='#2A1A5A'):
    bg_lin(cv, *sky)
    rnd = random.Random(seed)
    for layer, (col, base, hmin, hmax) in enumerate([('#5A2A8A', 700, 300, 520), ('#3A1A70', 740, 200, 420)]):
        x = -150
        while x < W + 150:
            w = rnd.uniform(120, 230); h = rnd.uniform(hmin, hmax)
            rrect(cv, x, base - h, w, h + 40, 6, col)
            for wy in range(int(base - h + 24), base - 20, 44):
                for wx in range(int(x + 16), int(x + w - 30), 40):
                    if rnd.random() > 0.45:
                        cv.drawRect(skia.Rect.MakeXYWH(wx, wy, 22, 26), P('#FFD34A' if layer else '#FFB0D0', 170 if layer else 90))
            x += w + rnd.uniform(4, 20)
    cv.drawRect(skia.Rect.MakeXYWH(-400, 740, W + 800, 700), P(ground))
    cv.drawRect(skia.Rect.MakeXYWH(-400, 740, W + 800, 12), P('#7A5BFF', 160))
    for k in range(-3, 30):
        cv.drawLine(k * 110, 760, k * 160 - 900, H + 300, P('#ffffff', 14, stroke=3))


def bubble(cv, x, y, r, icon, t, a=255):
    circle(cv, x - r * 0.5, y + r * 1.05, r * 0.14, '#FFFFFF', a)
    circle(cv, x - r * 0.3, y + r * 0.8, r * 0.2, '#FFFFFF', a)
    glow(cv, x, y, r * 1.6, '#FFFFFF', 60 * a / 255)
    circle(cv, x, y, r, '#FFFFFF', a)
    icon_draw(cv, icon, x, y, r * 0.6, t, a)


def heart(cv, x, y, r, c, a=255):
    circle(cv, x - r * 0.5, y, r * 0.55, c, a); circle(cv, x + r * 0.5, y, r * 0.55, c, a)
    poly(cv, [(x - r * 1.02, y + r * 0.15), (x + r * 1.02, y + r * 0.15), (x, y + r * 1.2)], c, a)


def icon_draw(cv, kind, x, y, r, t, a=255):
    if kind == 'heart':
        heart(cv, x, y - r * 0.3, r * 0.8, '#FF4F81', a)
    elif kind == 'note':
        circle(cv, x - r * 0.35, y + r * 0.45, r * 0.3, '#7A4BFF', a); circle(cv, x + r * 0.45, y + r * 0.3, r * 0.3, '#7A4BFF', a)
        cv.drawLine(x - r * 0.08, y + r * 0.45, x - r * 0.08, y - r * 0.6, P('#7A4BFF', a, stroke=r * 0.14))
        cv.drawLine(x + r * 0.72, y + r * 0.3, x + r * 0.72, y - r * 0.75, P('#7A4BFF', a, stroke=r * 0.14))
        cv.drawLine(x - r * 0.08, y - r * 0.6, x + r * 0.72, y - r * 0.75, P('#7A4BFF', a, stroke=r * 0.22))
    elif kind == 'house':
        poly(cv, [(x - r * 0.8, y), (x, y - r * 0.75), (x + r * 0.8, y)], '#FF8A3D', a)
        rrect(cv, x - r * 0.6, y - r * 0.05, r * 1.2, r * 0.8, 4, '#FFD34A', a)
        rrect(cv, x - r * 0.15, y + r * 0.3, r * 0.3, r * 0.45, 3, '#8A4A1A', a)
    elif kind == 'star':
        sparkle(cv, x, y, r * 0.9, '#FFC23B', a)
    elif kind == 'cloud':
        cloud(cv, x, y, r * 0.45, '#7A8BC8', a)
        for k in range(3):
            cv.drawLine(x - r * 0.4 + k * r * 0.4, y + r * 0.35, x - r * 0.5 + k * r * 0.4, y + r * 0.7, P('#2DB8FF', a, stroke=r * 0.1))
    elif kind == 'baby':
        rrect(cv, x - r * 0.3, y - r * 0.45, r * 0.6, r * 1.1, r * 0.2, '#BFF6FF', a)
        rrect(cv, x - r * 0.18, y - r * 0.8, r * 0.36, r * 0.4, r * 0.15, '#FF8AB8', a)
        for k in range(3):
            cv.drawLine(x - r * 0.3, y - r * 0.1 + k * r * 0.25, x, y - r * 0.1 + k * r * 0.25, P('#2DB8FF', a, stroke=3))
    elif kind == 'key':
        circle(cv, x - r * 0.4, y, r * 0.35, '#FFC23B', a, stroke=r * 0.16)
        cv.drawLine(x - r * 0.05, y, x + r * 0.8, y, P('#FFC23B', a, stroke=r * 0.18))
        cv.drawLine(x + r * 0.55, y, x + r * 0.55, y + r * 0.3, P('#FFC23B', a, stroke=r * 0.16))
    elif kind == 'plane':
        rrect(cv, x - r * 0.8, y - r * 0.12, r * 1.6, r * 0.24, r * 0.12, '#2DB8FF', a)
        poly(cv, [(x - r * 0.1, y), (x + r * 0.2, y), (x - r * 0.1, y + r * 0.7), (x - r * 0.35, y + r * 0.7)], '#2A7ACC', a)
        poly(cv, [(x - r * 0.1, y), (x + r * 0.2, y), (x - r * 0.1, y - r * 0.7), (x - r * 0.35, y - r * 0.7)], '#2A7ACC', a)


# 1 ─ « Aujourd'hui, tu as croisé des dizaines d'inconnus. »
class Street(Scene):
    zoom = (1.0, 1.1)
    pan = (60, 0, -60, 0)

    def __init__(self):
        self.c = Crowd(30, 401)

    def static(self, cv):
        street_bg(cv)
        glow(cv, 1500, 380, 300, '#FFD34A', 150); circle(cv, 1500, 400, 110, '#FFE680')

    def dyn(self, cv, t, d):
        self.c.draw(cv, t)
        n = int(min(1, t / max(d, .1)) * 47) + 3
        label(cv, 1620, 120, f'{n} INCONNUS', 30, font=FONT)

    def fg(self, cv, t, d):
        for x in (-80, 2000):
            rrect(cv, x - 30, 200, 60, 900, 30, '#140A30')
            oval(cv, x, 220, 140, 30, '#140A30')


# 2 ─ « Dans la rue, dans le métro, à la caisse. »
class Places(Scene):
    zoom = (1.0, 1.06)

    def static(self, cv):
        bg_lin(cv, '#1A0A4E', '#4A1270')
        for k in range(0, W, 60):
            cv.drawLine(k, 0, k, H, P('#ffffff', 10, stroke=2))

    def _panel(self, cv, i, x, y, w, h, t):
        cv.save()
        rr = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), 30, 30)
        cv.clipRRect(rr, doAntiAlias=True)
        if i == 0:  # passage piéton
            bg_lin(cv, '#FF8AB8', '#FFD08A')
            cv.drawRect(skia.Rect.MakeXYWH(x, y + h * 0.62, w, h), P('#3A3A5A'))
            for k in range(7):
                cv.drawRect(skia.Rect.MakeXYWH(x + 20 + k * 80, y + h * 0.7, 50, h * 0.3), P('#FFFFFF', 230))
            rnd = random.Random(3)
            for k in range(4):
                pr = person(rnd); m = pr.pop('mood')
                char_front(cv, x + ((80 + k * 140 + t * 70 * (1 if k % 2 else -1)) % (w + 100)) - 50, y + h * 0.95, 30, t + k, mood=m, **pr)
        elif i == 1:  # métro
            bg_lin(cv, '#2DB8FF', '#1A5AAA')
            rrect(cv, x + 30, y + 60, w - 60, h * 0.4, 20, '#0E1A40')
            for k in range(3):
                xx = x + 50 + k * 170 - (t * 300) % 170
                cv.drawRect(skia.Rect.MakeXYWH(xx, y + 80, 120, h * 0.32), P('#5AD7FF', 120))
            cv.drawLine(x, y + 40, x + w, y + 40, P('#C8C8E0', 255, stroke=8))
            for k in range(4):
                cv.drawLine(x + 70 + k * 140, y + 40, x + 70 + k * 140, y + 140, P('#C8C8E0', 255, stroke=5))
                circle(cv, x + 70 + k * 140, y + 155, 18, '#C8C8E0', 255, stroke=5)
            rnd = random.Random(5)
            for k in range(4):
                pr = person(rnd); pr.pop('mood')
                char_front(cv, x + 80 + k * 140, y + h * 1.02, 34, t + k, mood='calm', arms='up' if k == 1 else 'down', **pr)
        else:  # caisse
            bg_lin(cv, '#3FC46A', '#1A7A5A')
            for k in range(4):
                rrect(cv, x + 20, y + 40 + k * 70, w - 40, 14, 4, '#0E3A2A')
                for j in range(8):
                    rrect(cv, x + 30 + j * 70, y + 10 + k * 70, 50, 30, 6, TOPS[(j + k) % 8], 230)
            rrect(cv, x, y + h * 0.66, w, h * 0.4, 10, '#C8C8E0')
            rnd = random.Random(8)
            for k in range(3):
                pr = person(rnd); m = pr.pop('mood')
                char_front(cv, x + 120 + k * 170, y + h * 0.78, 34, t + k, mood=m, **pr)
            label(cv, x + w - 90, y + h * 0.85, '12,40 €', 24, color='#1A1030', font=FONT)
        cv.restore()
        cv.drawRRect(rr, P('#FFFFFF', 255, stroke=10))

    def dyn(self, cv, t, d):
        w, h = 560, 640
        for i in range(3):
            k = ease_out((t - i * d / 3.2) / 0.4)
            if k <= 0:
                continue
            x = 60 + i * 610
            y = 220 + (1 - k) * 700
            cv.save(); cv.translate(x + w / 2, y + h / 2); cv.rotate((i - 1) * 3 * (1 - k * 0.5)); cv.translate(-(x + w / 2), -(y + h / 2))
            self._panel(cv, i, x, y, w, h, t)
            cv.restore()


# 3 ─ « Pour toi, ce sont des figurants. »
class Extras(Scene):
    zoom = (1.12, 1.0)

    def __init__(self):
        self.c = Crowd(24, 403, speed=40)

    def static(self, cv):
        street_bg(cv, sky=('#3A3A5A', '#7A7A9A'), ground='#3A3A4A')

    def dyn(self, cv, t, d):
        grey_layer(cv, 1.0)
        self.c.draw(cv, t, mood='calm', extra=lambda cv, x, y, s, t, ph, pr: label(cv, x, y - 5.7 * s, 'FIGURANT', 26, color='#E8E8F0', font=FONT) if s > 50 and (ph % 2) < 1.2 else None)
        cv.restore()
        # clap de cinéma
        cv.save(); cv.translate(1650, 200); cv.rotate(-8)
        rrect(cv, -120, -10, 240, 160, 10, '#1A1030')
        ang = -20 * abs(math.sin(t * 3))
        cv.save(); cv.translate(-120, -10); cv.rotate(ang)
        rrect(cv, 0, -50, 240, 50, 8, '#FFFFFF')
        for k in range(5):
            poly(cv, [(10 + k * 48, -50), (40 + k * 48, -50), (20 + k * 48, 0), (-10 + k * 48, 0)], '#1A1030')
        cv.restore()
        label(cv, 0, 90, 'PRISE 1', 26, font=FONT, box=False)
        cv.restore()


# 4 ─ « Mais chacun d'eux vit une vie aussi compliquée que la tienne. »
class Complex(Scene):
    zoom = (1.0, 1.1)

    def __init__(self):
        self.c = Crowd(24, 403, speed=40)
        self.icons = ['heart', 'note', 'house', 'star', 'cloud', 'key', 'plane', 'baby']

    def static(self, cv):
        street_bg(cv, seed=4)

    def dyn(self, cv, t, d):
        k = ease(t / 0.9)
        grey_layer(cv, 1 - k)
        def extra(cv, x, y, s, tt, ph, pr):
            if s < 40:
                return
            a = ease_out((t - 0.4 - (ph % 1.5)) / 0.4)
            if a > 0:
                bubble(cv, x + s * 1.3, y - 6.2 * s - 8 * math.sin(tt * 2 + ph), s * 0.85 * a, self.icons[int(ph * 10) % 8], tt, 255)
        self.c.draw(cv, t, extra=extra)
        cv.restore()


# 5 ─ « La femme à l'arrêt de bus vient peut-être d'apprendre qu'elle va être grand-mère. »
class Grandma(Scene):
    zoom = (1.0, 1.12)

    def __init__(self):
        rnd = random.Random(405)
        self.h = [(rnd.uniform(-1, 1), rnd.uniform(0, 1), rnd.uniform(14, 30), rnd.choice(['#FF4F81', '#FF8AB8', '#FFD34A'])) for _ in range(30)]

    def static(self, cv):
        street_bg(cv, sky=('#FF8AB8', '#FFD08A'), seed=5, ground='#5A2A6A')
        # abribus
        rrect(cv, 520, 330, 900, 40, 12, '#2A1A5A')
        for x in (540, 1380):
            rrect(cv, x - 10, 360, 20, 560, 10, '#2A1A5A')
        rrect(cv, 560, 380, 800, 420, 10, '#BFF6FF', 70)
        rrect(cv, 1180, 420, 160, 240, 10, '#FFD34A')
        label(cv, 1260, 470, 'BUS 42', 26, color='#1A1030', font=FONT, box=False)
        rrect(cv, 640, 760, 520, 34, 12, '#7A4BFF')

    def dyn(self, cv, t, d):
        k = ease_out((t - 0.6) / 0.5)
        cx, cy = 900, 980
        char_front(cv, cx, cy, 78, t * (1 + k), skin='#FFD0B0', hair='#E0E0F0', top='#7A4BFF', pants='#3A1E5A', hairstyle=1,
                   mood='laugh' if k > 0.3 else 'wow', arms='up' if k > 0.5 else 'down')
        if k < 0.5:
            rrect(cv, cx + 80, cy - 420, 40, 70, 8, '#1A1030'); rrect(cv, cx + 85, cy - 414, 30, 56, 5, '#9BEFFF')
        for dx, ph, r, c in self.h:
            q = (ph + t * 0.5) % 1
            if k > 0:
                heart(cv, cx + dx * 300 * (0.3 + q), cy - 450 - q * 500, r, c, 255 * math.sin(q * math.pi) * k)
        if k > 0:
            bubble(cv, cx + 330, cy - 640 + 10 * math.sin(t * 2), 90 * k, 'baby', t)

    def fg(self, cv, t, d):
        oval(cv, 1800, 1050, 320, 180, '#3A1A5A', 255, blur=14)


# 6 ─ « Le type qui t'a bousculé sort peut-être de l'hôpital. »
class Bumped(Scene):
    zoom = (1.0, 1.1)
    pan = (0, 0, -60, 0)
    shake = 0.25

    def static(self, cv):
        bg_lin(cv, '#2A6ACC', '#BFE6FF')
        rrect(cv, 950, 180, 880, 640, 14, '#E8F0FF')
        for r in range(4):
            for c in range(7):
                rrect(cv, 990 + c * 118, 260 + r * 120, 80, 80, 8, '#9BC8F0')
        rrect(cv, 1290, 90, 200, 120, 16, '#E8243C')
        cv.drawRect(skia.Rect.MakeXYWH(1370, 110, 40, 80), P('#ffffff')); cv.drawRect(skia.Rect.MakeXYWH(1350, 130, 80, 40), P('#ffffff'))
        label(cv, 1390, 250, 'HÔPITAL', 30, color='#1A1030', font=FONT, box=False)
        cv.drawRect(skia.Rect.MakeXYWH(-400, 820, W + 800, 700), P('#5A5A8A'))
        cv.drawRect(skia.Rect.MakeXYWH(-400, 820, W + 800, 14), P('#ffffff', 140))

    def dyn(self, cv, t, d):
        # ambulance qui s'éloigne
        ax = 1300 + t * 160
        rrect(cv, ax, 680, 300, 150, 20, '#FFFFFF'); rrect(cv, ax + 210, 640, 90, 90, 14, '#FFFFFF')
        cv.drawRect(skia.Rect.MakeXYWH(ax, 730, 300, 20), P('#E8243C'))
        glow(cv, ax + 250, 630, 60, '#2DB8FF' if int(t * 6) % 2 else '#E8243C', 255)
        for k in (60, 240):
            circle(cv, ax + k, 832, 32, '#1A1030')
        # l'homme pressé
        x = 420 + 120 * math.sin(t * 0.8)
        for k in range(5):
            neon(cv, [(x - 260 - k * 30, 600 + k * 50), (x - 140 - k * 30, 600 + k * 50)], '#FFFFFF', w=5, a=160, glow_w=10)
        char_front(cv, x, 1000, 84, t * 2, skin='#C98058', hair='#1A1030', top='#3FC46A', pants='#1E1F5C', mood='sad', hairstyle=0)
        rrect(cv, x + 88, 760, 46, 22, 8, '#FFFFFF')
        label(cv, x + 190, 740, 'BRACELET : SORTIE', 22, font=FONT)


# 7 ─ « Chacun a ses peurs, ses secrets, sa chanson préférée, quelqu'un qu'il aime en silence. »
class Building(Scene):
    zoom = (1.25, 1.0)

    def static(self, cv):
        bg_lin(cv, '#0E0838', '#3A0E5E')
        rrect(cv, 260, 40, 1400, 1100, 20, '#2A1A5A')
        for r in range(3):
            for c in range(4):
                x, y = 320 + c * 340, 90 + r * 320
                rrect(cv, x, y, 300, 270, 14, '#FFE6A0')
                rrect(cv, x, y + 250, 300, 30, 6, '#5A3A8A')

    def dyn(self, cv, t, d):
        scenes_ = ['music', 'fear', 'love', 'secret', 'cat', 'read', 'dance', 'cry', 'plant', 'call', 'cook', 'sleep']
        for i, kind in enumerate(scenes_):
            r, c = divmod(i, 4)
            x, y = 320 + c * 340, 90 + r * 320
            cv.save(); cv.clipRect(skia.Rect.MakeXYWH(x, y, 300, 250))
            rnd = random.Random(i + 20)
            pr = person(rnd); pr.pop('mood')
            cx, fy = x + 150, y + 300
            if kind == 'music':
                char_front(cv, cx, fy, 34, t * 2, mood='happy', arms='up', **pr)
                for k in range(3):
                    q = (t * 0.8 + k / 3) % 1
                    icon_draw(cv, 'note', cx + 70 + k * 10, y + 120 - q * 80, 22, t, 255 * (1 - q))
            elif kind == 'fear':
                char_front(cv, cx, fy, 34, t, mood='scared', **pr)
                blob(cv, x + 50, y + 60, 40, '#1A1030', 200, seed=i, t=t)
            elif kind == 'love':
                char_front(cv, cx - 40, fy, 32, t, mood='happy', **pr)
                heart(cv, cx + 70, y + 70 + 8 * math.sin(t * 4), 28, '#FF4F81')
                icon_draw(cv, 'heart', cx + 70, y + 150, 16, t)
            elif kind == 'secret':
                char_front(cv, cx, fy, 34, t, mood='calm', look=(1, 0), **pr)
                icon_draw(cv, 'key', cx + 80, y + 70, 34, t)
            elif kind == 'cat':
                oval(cv, cx, y + 210, 70, 40, '#FF8A3D'); circle(cv, cx + 60, y + 170, 34, '#FF8A3D')
                poly(cv, [(cx + 36, y + 150), (cx + 46, y + 120), (cx + 60, y + 142)], '#FF8A3D'); poly(cv, [(cx + 66, y + 140), (cx + 82, y + 118), (cx + 86, y + 148)], '#FF8A3D')
                p = skia.Path(); p.moveTo(cx - 60, y + 210); p.quadTo(cx - 120, y + 150 + 20 * math.sin(t * 3), cx - 100, y + 120)
                cv.drawPath(p, P('#FF8A3D', 255, stroke=14))
                for e in (50, 72):
                    circle(cv, cx + e, y + 168, 5, '#1A1030')
            elif kind == 'read':
                char_front(cv, cx, fy, 34, t, mood='calm', look=(0, 1), **pr)
                rrect(cv, cx - 50, y + 150, 100, 60, 6, '#2DB8FF')
            elif kind == 'dance':
                char_front(cv, cx + 30 * math.sin(t * 4), fy, 34, t * 3, mood='laugh', arms='up', **pr)
            elif kind == 'cry':
                char_front(cv, cx, fy, 34, t, mood='sad', **pr)
                q = (t * 1.5) % 1
                oval(cv, cx - 20, y + 170 + q * 40, 5, 8, '#5AD7FF')
            elif kind == 'plant':
                char_front(cv, cx - 50, fy, 32, t, mood='smile', **pr)
                rrect(cv, cx + 50, y + 180, 60, 60, 8, '#C84B7A')
                for k in range(4):
                    blob(cv, cx + 80 + (k - 1.5) * 20, y + 160 - (k % 2) * 30, 26, '#3FC46A', seed=k)
            elif kind == 'call':
                char_front(cv, cx, fy, 34, t, mood='happy', arms='wave', **pr)
            elif kind == 'cook':
                char_front(cv, cx - 30, fy, 32, t, mood='smile', **pr)
                for k in range(3):
                    q = (t * 0.7 + k / 3) % 1
                    circle(cv, cx + 80 + 10 * math.sin(q * 8), y + 160 - q * 100, 12 * (1 - q) + 4, '#FFFFFF', 180 * (1 - q))
                rrect(cv, cx + 40, y + 170, 90, 30, 8, '#1A1030')
            else:
                rrect(cv, x + 30, y + 160, 240, 80, 20, '#7A8BC8')
                circle(cv, x + 80, y + 160, 34, pr['skin'])
                for k in range(3):
                    q = (t * 0.5 + k / 3) % 1
                    label(cv, x + 140 + q * 60, y + 120 - q * 60, 'z', 26, color='#1A1030', a=255 * (1 - q), font=FONT, box=False)
            cv.restore()


# 8 ─ « Quelqu'un a même inventé un mot pour ce vertige : sonder. »
class Sonder(Scene):
    zoom = (1.0, 1.15)

    def __init__(self):
        rnd = random.Random(408)
        self.st = Stars(200, 409, rmax=2)
        self.win = []
        x = -100
        while x < W + 100:
            w = rnd.uniform(110, 200); h = rnd.uniform(260, 640)
            self.win.append((x, w, h))
            x += w + 8
        self.lit = [(rnd.uniform(0, W), rnd.uniform(500, 950)) for _ in range(70)]

    def static(self, cv):
        bg_lin(cv, '#06041C', '#2A0A50')
        for x, w, h in self.win:
            rrect(cv, x, 1000 - h, w, h + 100, 6, '#140A36')

    def dyn(self, cv, t, d):
        self.st.draw(cv, t, 200)
        pts = []
        for i, (x, y) in enumerate(self.lit):
            on = (i * 7 + int(t * 3)) % 11 != 0
            if on:
                cv.drawRect(skia.Rect.MakeXYWH(x - 12, y - 14, 24, 28), P('#FFD34A', 230))
                glow(cv, x, y, 40, '#FFD34A', 90)
                pts.append((x, y))
        k = ease(t / max(d * 0.8, 0.1))
        n = int(len(pts) * k)
        cols = ['#2DE2E6', '#FF4F81', '#B98CFF', '#FFD34A']
        for i in range(n):
            a, b = pts[i], pts[(i * 13 + 5) % len(pts)]
            mx, my = (a[0] + b[0]) / 2, min(a[1], b[1]) - 120 - (i % 4) * 40
            path = [(a[0] + (b[0] - a[0]) * u / 12, (1 - u / 12) ** 2 * a[1] + 2 * (u / 12) * (1 - u / 12) * my + (u / 12) ** 2 * b[1]) for u in range(13)]
            neon(cv, path, cols[i % 4], w=3, a=200, glow_w=10)
        label(cv, 960, 200, 'SONDER (n.) · LA PRISE DE CONSCIENCE QUE CHAQUE PASSANT', 24, font=FONT)
        label(cv, 960, 250, 'VIT UNE VIE AUSSI RICHE QUE LA TIENNE', 24, font=FONT, box=False)


# 9 ─ « Mais retourne la situation. »
class Flip(Scene):
    zoom = (1.0, 1.15)
    shake = 0.2

    def __init__(self):
        rnd = random.Random(410)
        self.ring = [person(rnd) for _ in range(10)]

    def static(self, cv):
        bg_rad(cv, 960, 540, 1100, '#5A1EAA', '#0A0428')

    def dyn(self, cv, t, d):
        yaw = 180 * ease(t / max(d, 0.1)) + 20 * t
        cam = Cam(yaw=yaw, pitch=-20, dist=1700, f=1300, cy=640)
        wire_plane(cv, cam, 300, 1800, 150, '#B98CFF', 110)
        items = []
        for i, pr in enumerate(self.ring):
            a = i / 10 * 6.283
            q = cam.p(700 * math.cos(a), 300, 700 * math.sin(a))
            items.append((q[2], q, pr))
        for z, q, pr in sorted(items, key=lambda it: -it[0]):
            pr = dict(pr); pr.pop('mood')
            char_front(cv, q[0], q[1], 60 * q[3], t, mood='wow', look=(0, 0), **pr)
        glow(cv, 960, 640, 300, '#FFE6A0', 120)
        poly(cv, [(900, -50), (1020, -50), (1150, 660), (770, 660)], '#FFE6A0', 40, blur=20)
        char_front(cv, 960, 660, 60, t, mood='wow', **YOU)


# 10 ─ « Toi aussi, tu es un figurant. Dans des milliers d'histoires. »
class YouExtra(Scene):
    zoom = (1.0, 1.25)

    def static(self, cv):
        bg_lin(cv, '#0A0630', '#2A0B5E')

    def dyn(self, cv, t, d):
        bgs = [('#FF8AB8', '#FFD08A'), ('#2DB8FF', '#1A5AAA'), ('#3FC46A', '#1A7A5A'), ('#FFD34A', '#FF8A3D'), ('#7A4BFF', '#2A0B5E'), ('#2DE2C6', '#1A6A8A')]
        off = (t * 120) % 360
        for r in range(4):
            for c in range(7):
                x = -300 + c * 360 + (off if r % 2 else -off)
                y = 30 + r * 270
                i = (r * 7 + c)
                cv.save()
                rr = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, 320, 230), 16, 16)
                cv.clipRRect(rr, doAntiAlias=True)
                a, b = bgs[i % 6]
                cv.drawRect(skia.Rect.MakeXYWH(x, y, 320, 230), P(shader=lin(x, y, x, y + 230, [a, b])))
                rnd = random.Random(i)
                pr = person(rnd); m = pr.pop('mood')
                char_front(cv, x + 120, y + 300, 34, t + i, mood='happy', **pr)
                char_front(cv, x + 260, y + 270, 18, t + i * 2, mood='smile', **YOU)
                cv.restore()
                cv.drawRRect(rr, P('#FFFFFF', 220, stroke=6))
                for k in range(6):
                    rrect(cv, x + 12 + k * 52, y - 20, 30, 12, 4, '#FFFFFF', 120)
                neon(cv, [(x + 262, y + 140), (x + 262, y + 190)], '#FF4F81', w=4, arrow=True, glow_w=10)


# 11 ─ « Tu es la personne qui a tenu la porte. Celle qui a souri sans raison. »
class Door(Scene):
    zoom = (1.0, 1.1)

    def static(self, cv):
        street_bg(cv, sky=('#FFB0C8', '#FFE0A0'), seed=11, ground='#7A3A6A')
        rrect(cv, 760, 180, 700, 760, 20, '#5A2A8A')
        rrect(cv, 800, 120, 620, 90, 14, '#FF4F81')
        label(cv, 1110, 185, 'BOULANGERIE', 36, font=FONT, box=False)

    def dyn(self, cv, t, d):
        rrect(cv, 820, 260, 300, 680, 10, '#2A1A5A')
        ang = 40 * ease_out(t / 0.6)
        w = 300 * math.cos(math.radians(ang))
        rrect(cv, 1120, 260, -w if False else 4, 680, 2, '#000000', 0)
        poly(cv, [(820, 260), (820 + w, 240), (820 + w, 960), (820, 940)], '#BFF6FF', 200)
        poly(cv, [(820, 260), (820 + w, 240), (820 + w, 960), (820, 940)], '#FFFFFF', 220, stroke=10)
        char_front(cv, 640, 1000, 78, t, mood='happy', arms='out', **YOU)
        k = ease(t / max(d, 0.1))
        sx = 1700 - 700 * k
        char_front(cv, sx, 1000, 74, t * 1.4, mood='happy', skin='#FFD0B0', hair='#B04A1A', top='#2DE2C6', pants='#1E1F5C', hairstyle=2)
        sparkle(cv, sx, 400 + 10 * math.sin(t * 5), 40 * min(1, k * 2), '#FFC23B')
        sparkle(cv, 640, 400 + 10 * math.sin(t * 5 + 1), 34, '#FFFFFF')


# 12 ─ « Celle qu'un inconnu a remarquée un jour, et dont il se souvient encore. »
class Memory(Scene):
    zoom = (1.12, 1.0)

    def static(self, cv):
        bg_lin(cv, '#3A1A6A', '#FF8A5C')
        cv.drawRect(skia.Rect.MakeXYWH(-400, 880, W + 800, 600), P('#2A1450'))
        rrect(cv, 200, 640, 900, 260, 60, '#2DB8FF')
        rrect(cv, 160, 580, 160, 320, 60, '#2A7ACC'); rrect(cv, 980, 580, 160, 320, 60, '#2A7ACC')
        glow(cv, 1500, 700, 260, '#FFD34A', 160)
        rrect(cv, 1480, 600, 40, 300, 10, '#8A4A1A'); poly(cv, [(1400, 600), (1600, 600), (1550, 480), (1450, 480)], '#FFD34A')

    def dyn(self, cv, t, d):
        char_front(cv, 420, 900, 64, t, mood='happy', skin='#FFD0B0', hair='#C8C8D8', top='#2DE2C6', pants='#1E1F5C', hairstyle=2, arms='wave')
        char_front(cv, 760, 900, 40, t + 1, mood='wow', skin='#FFD0B0', hair='#B04A1A', top='#FFD34A', pants='#3C4CC8', hairstyle=1)
        k = ease_out((t - 0.3) / 0.6)
        if k > 0:
            bx, by, R = 1100, 300, 230 * k
            circle(cv, 600, 520, 18 * k, '#FFFFFF'); circle(cv, 700, 450, 28 * k, '#FFFFFF')
            glow(cv, bx, by, R * 1.5, '#FFFFFF', 100)
            cv.save(); clip = skia.Path(); clip.addCircle(bx, by, R); cv.clipPath(clip, doAntiAlias=True)
            cv.drawRect(skia.Rect.MakeXYWH(bx - R, by - R, 2 * R, 2 * R), P(shader=lin(0, by - R, 0, by + R, ['#FFE0A0', '#FFB0C8'])))
            rrect(cv, bx - 40, by - 140, 220, 300, 8, '#5A2A8A')
            char_front(cv, bx - 90, by + 200, 34, t, mood='happy', arms='out', **YOU)
            char_front(cv, bx + 60, by + 200, 32, t, mood='happy', skin='#FFD0B0', hair='#B04A1A', top='#2DE2C6', pants='#1E1F5C', hairstyle=2)
            cv.restore()
            circle(cv, bx, by, R, '#FFFFFF', 255, stroke=10)
            label(cv, bx, by + R + 60, 'IL Y A 20 ANS', 26, font=FONT)


# 13 ─ « Tu ne le sauras jamais. »
class Never(Scene):
    zoom = (1.15, 1.0)

    def __init__(self):
        self.st = Stars(180, 413)

    def static(self, cv):
        bg_lin(cv, '#1A0A4E', '#FF7A5C')
        circle(cv, 960, 760, 260, '#FFD08A', 200)
        p = skia.Path(); p.moveTo(-400, H + 400); p.lineTo(-400, 820); p.quadTo(960, 720, W + 400, 820); p.lineTo(W + 400, H + 400); p.close()
        cv.drawPath(p, P('#2A1450'))

    def dyn(self, cv, t, d):
        self.st.draw(cv, t, 120)
        x = 960 + 60 * t
        rnd = random.Random(2)
        for k in range(9):
            tx, ty = rnd.uniform(100, 1800), rnd.uniform(780, 900)
            s = rnd.uniform(14, 22)
            pr = person(rnd); pr.pop('mood')
            char_front(cv, tx, ty, s, t + k, mood='happy', bob=False, **pr)
            pts = [(x + (tx - x) * u / 10, 700 + (ty - 5 * s - 700) * u / 10 - 120 * math.sin(u / 10 * math.pi)) for u in range(11)]
            neon(cv, pts, ['#FFD34A', '#FF4F81', '#2DE2E6'][k % 3], w=2.5, a=140 + 60 * math.sin(t * 2 + k), glow_w=8)
        char_front(cv, x, 860, 46, t * 1.3, mood='calm', **YOU)


# 14 ─ « Mais quelque part, tu as déjà changé la journée de quelqu'un. »
class Changed(Scene):
    zoom = (1.0, 1.1)

    def static(self, cv):
        street_bg(cv, sky=('#5A6A9A', '#9AB0D0'), seed=14, ground='#3A3A6A')

    def dyn(self, cv, t, d):
        k = ease((t - 0.8) / 1.2)
        sky = P(shader=lin(0, 0, 0, H, [C(mix('#5A6A9A', '#2DB8FF', k), int(200 * k)), C(mix('#9AB0D0', '#FFD08A', k), int(200 * k))]))
        cv.drawRect(skia.Rect.MakeXYWH(-400, -400, W + 800, 1140), sky)
        cx = 960
        if k < 1:
            cloud(cv, cx, 330, 110, '#4A4A6A', 255 * (1 - k), shade='#3A3A5A')
            rnd = random.Random(3)
            for j in range(40):
                yy = (rnd.uniform(0, 500) + t * 700) % 500 + 400
                cv.drawLine(cx - 200 + rnd.uniform(0, 400), yy, cx - 210 + rnd.uniform(0, 400), yy + 30, P('#5AD7FF', 200 * (1 - k), stroke=3))
        if k > 0:
            for i, c in enumerate(['#FF4F81', '#FF8A3D', '#FFD34A', '#3FC46A', '#2DB8FF', '#7A4BFF']):
                p = skia.Path(); p.addArc(skia.Rect.MakeLTRB(cx - 600 + i * 24, 300 + i * 24, cx + 600 - i * 24, 1500 - i * 24), 180, 180 * k)
                cv.drawPath(p, P(c, 220, stroke=24))
            glow(cv, cx + 500, 200, 260 * k, '#FFE680', 220)
            circle(cv, cx + 500, 200, 90 * k, '#FFE680')
        char_front(cv, cx, 1000, 84, t, mood='happy' if k > 0.5 else 'sad', arms='up' if k > 0.7 else 'down', skin='#8A5236', hair='#1A1030', top='#FFD34A', pants='#3C4CC8', hairstyle=1)


# 15 ─ « Alors continue. Souris aux inconnus. Tiens les portes. »
class Continue(Scene):
    zoom = (1.0, 1.1)
    pan = (-60, 0, 60, 0)

    def __init__(self):
        self.c = Crowd(26, 415, speed=70)

    def static(self, cv):
        street_bg(cv, sky=('#FF8AB8', '#FFE0A0'), seed=15, ground='#7A3A6A')

    def dyn(self, cv, t, d):
        def extra(cv, x, y, s, tt, ph, pr):
            if s > 40 and (tt + ph) % 2.0 < 1.0:
                sparkle(cv, x, y - 5.8 * s, s * 0.5, '#FFC23B')
        self.c.draw(cv, t, mood='happy', extra=extra)
        char_front(cv, 960, 1060, 80, t, mood='happy', arms='wave', **YOU)


# 16 ─ « Sois gentil, même quand personne ne regarde. »
class Kind(Scene):
    zoom = (1.0, 1.15)

    def __init__(self):
        rnd = random.Random(416)
        self.rain = [(rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(600, 1000)) for _ in range(160)]

    def static(self, cv):
        street_bg(cv, sky=('#06041C', '#1E1050'), seed=16, ground='#140A30')
        rrect(cv, 1400, 260, 24, 680, 12, '#2A1A5A'); rrect(cv, 1360, 240, 140, 40, 20, '#2A1A5A')
        poly(cv, [(1380, 280), (1480, 280), (1650, 950), (1210, 950)], '#FFD34A', 40, blur=10)
        glow(cv, 1430, 290, 160, '#FFD34A', 160)

    def dyn(self, cv, t, d):
        for x, y, sp in self.rain:
            yy = (y + t * sp) % (H + 100) - 50
            cv.drawLine(x, yy, x - 6, yy + 36, P('#7A8BFF', 110, stroke=3))
        cx = 900
        char_front(cv, cx, 980, 76, t, mood='happy', arms='out', **YOU)
        # parapluie au-dessus du chat
        ux, uy = cx + 240, 610
        cv.drawLine(cx + 120, 800, ux, uy, P('#1A1030', 255, stroke=10))
        p = skia.Path(); p.addArc(skia.Rect.MakeLTRB(ux - 260, uy - 160, ux + 260, uy + 160), 180, 180); p.close()
        cv.drawPath(p, P('#2DE2C6'))
        for k in range(5):
            cv.drawLine(ux, uy - 160, ux - 260 + k * 130, uy, P('#1AA89A', 255, stroke=4))
        # chat
        kx, ky = ux + 40, 960
        oval(cv, kx, ky, 80, 46, '#FF8A3D'); circle(cv, kx + 70, ky - 50, 40, '#FF8A3D')
        poly(cv, [(kx + 42, ky - 76), (kx + 52, ky - 110), (kx + 70, ky - 84)], '#FF8A3D'); poly(cv, [(kx + 78, ky - 86), (kx + 96, ky - 112), (kx + 102, ky - 76)], '#FF8A3D')
        p = skia.Path(); p.moveTo(kx - 70, ky); p.quadTo(kx - 140, ky - 60 + 20 * math.sin(t * 3), kx - 110, ky - 100)
        cv.drawPath(p, P('#FF8A3D', 255, stroke=16))
        for e in (58, 84):
            p = skia.Path(); p.addArc(skia.Rect.MakeLTRB(kx + e - 8, ky - 60, kx + e + 8, ky - 46), 200, 140)
            cv.drawPath(p, P('#1A1030', 255, stroke=4))
        sparkle(cv, kx + 130, ky - 140 + 8 * math.sin(t * 4), 26, '#FFC23B')
        label(cv, 420, 200, 'PERSONNE NE REGARDE', 26, font=FONT)


# 17 ─ « Parce que sans le savoir, tu es le personnage secondaire préféré de quelqu'un. »
class Credits(Scene):
    zoom = (1.0, 1.06)

    def __init__(self):
        self.st = Stars(160, 417, rmax=2)
        self.lines = ["PERSONNAGES SECONDAIRES PRÉFÉRÉS", "", "LA DAME DU BUS 42", "LE TYPE PRESSÉ", "LA FILLE DE LA BOULANGERIE",
                      "LE CHAT DU QUARTIER", "LE VOISIN QUI CHANTE", "LA CAISSIÈRE QUI SOURIT", "TOI", "", "ET DES MILLIERS D'AUTRES"]

    def static(self, cv):
        bg_lin(cv, '#06041C', '#1E0A40')

    def dyn(self, cv, t, d):
        self.st.draw(cv, t, 160)
        y0 = H + 40 - t * 215
        for i, l in enumerate(self.lines):
            y = y0 + i * 90
            if l == 'TOI':
                y = max(y, H / 2 + 260) if t > 3 else y
                glow(cv, 960, y - 14, 300, '#FF4F81', 150)
                label(cv, 960, y, l, 60, color='#FFD34A', font=FONT, box=False)
                for sx in (-1, 1):
                    sparkle(cv, 960 + sx * 110, y - 20, 26 + 6 * math.sin(t * 6), '#FFD34A')
            elif l:
                fade = max(0.0, min(1.0, (abs(y - 20 - H / 2) - 90) / 90))
                label(cv, 960, y, l, 46 if i == 0 else 38, color='#FFFFFF' if i else '#2DE2E6', a=230 * fade, font=FONT, box=False)
        for k in range(2):
            poly(cv, [(300 + k * 1320, -60), (360 + k * 1320, -60), (700 + k * 520, H + 60), (500 + k * 920, H + 60)], '#B98CFF', 30, blur=20)


SEGMENTS = [
    (Street, "Aujourd'hui, tu as croisé des dizaines d'inconnus."),
    (Places, "Dans la rue, dans le métro, à la caisse."),
    (Extras, "Pour toi, ce sont des figurants."),
    (Complex, "Mais chacun d'eux vit une vie aussi compliquée que la tienne."),
    (Grandma, "La femme à l'arrêt de bus vient peut-être d'apprendre qu'elle va être grand-mère."),
    (Bumped, "Le type qui t'a bousculé sort peut-être de l'hôpital."),
    (Building, "Chacun a ses peurs, ses secrets, sa chanson préférée, quelqu'un qu'il aime en silence."),
    (Sonder, "Quelqu'un a même inventé un mot pour ce vertige : sonder."),
    (Flip, "Mais retourne la situation."),
    (YouExtra, "Toi aussi, tu es un figurant. Dans des milliers d'histoires."),
    (Door, "Tu es la personne qui a tenu la porte. Celle qui a souri sans raison."),
    (Memory, "Celle qu'un inconnu a remarquée un jour, et dont il se souvient encore."),
    (Never, "Tu ne le sauras jamais."),
    (Changed, "Mais quelque part, tu as déjà changé la journée de quelqu'un."),
    (Continue, "Alors continue. Souris aux inconnus. Tiens les portes."),
    (Kind, "Sois gentil, même quand personne ne regarde."),
    (Credits, "Parce que sans le savoir, tu es le personnage secondaire préféré de quelqu'un."),
]
