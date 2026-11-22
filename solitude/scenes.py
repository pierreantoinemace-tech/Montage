"""« La solitude de l'âge adulte » : 14 plans, style sombre et onirique + couche « rêve »."""
import math, os, random, sys, importlib.util
import skia
HERE = os.path.dirname(os.path.abspath(__file__))
for d in ('../calendrier', '../temps', '../profil'):
    sys.path.insert(1, os.path.join(HERE, d))
from lib import *
from kit import Stars, sparkle, neon
from mg import *
_s = importlib.util.spec_from_file_location('wow_scenes', os.path.join(HERE, '..', 'wow', 'scenes.py'))
ws = importlib.util.module_from_spec(_s); _s.loader.exec_module(ws)
night, stars, hero, OLD, ribbons = ws.night, ws.stars, ws.hero, ws.OLD, ws.ribbons

FONT = None
STYLE = dict(exclusion=True, color='#F0EBBE', size=196, maxw=1760, glitch=True, grain=7, readable=True,
             fps=60, trans=1.0, float=True, dream=True, bloom=0.42, wobble=3,
             trans_kinds=['dream', 'ink', 'dream', 'liquid', 'dream', 'ripple', 'dream', 'iris'])


class Scene:
    zoom = (1.0, 1.08)
    pan = (0, 0, 0, 0)
    shake = 0.0

    def static(self, cv):
        pass

    def dyn(self, cv, t, d):
        pass


FRIENDS = [('#E07AB8', '#2A0E3A', '#1E5A6A'), ('#D8B8A8', '#3A2A1A', '#2A1A5A'), ('#8AD8A8', '#1A3A2A', '#2A2A6A'),
           ('#B48AE0', '#2A1050', '#5A1A3A'), ('#FFB08A', '#5A2A14', '#1E3A5A')]


def lantern(cv, x, y, r, col, a=255):
    glow(cv, x, y, r * 2.6, col, 150 * a / 255)
    ofill(cv, pcircle(x, y, r), mix(col, '#FFFFFF', 0.4), a=a, ol=OLD, w=4)
    circle(cv, x, y - r * 0.15, r * 0.3, OLD, a)
    oval(cv, x, y + r * 0.45, r * 0.45, r * 0.3, OLD, a)


def bird(cv, x, y, s, t, a=255):
    w = 0.6 * s * math.sin(t * 12)
    glow(cv, x, y, s * 2.4, '#FFE680', 200 * a / 255)
    for side in (-1, 1):
        p = skia.Path(); p.moveTo(x, y); p.quadTo(x + side * s * 0.8, y - s * 0.4 - w, x + side * s * 1.5, y - w * 0.6)
        p.quadTo(x + side * s * 0.8, y + s * 0.1, x, y + s * 0.15); p.close()
        ofill(cv, p, '#FFF0B0', a=a, ol=OLD, w=4)
    ofill(cv, poval(x, y + s * 0.05, s * 0.35, s * 0.22), '#FFE680', a=a, ol=OLD, w=4)


def city(cv, seed, base=1080, lit=0.5):
    rnd = random.Random(seed)
    wins = []
    x = -80
    while x < W + 80:
        w = rnd.uniform(110, 200); h = rnd.uniform(220, 560)
        ofill(cv, prr(x, base - h, w, h + 40, 6), '#140A2E', ol=OLD, w=4)
        for wy in range(int(base - h + 30), base - 40, 70):
            for wx in range(int(x + 20), int(x + w - 40), 55):
                if rnd.random() < lit:
                    wins.append((wx, wy))
        x += w + rnd.uniform(6, 20)
    return wins


# 1 ─ « Personne ne t'a prévenu qu'en grandissant, tu perdrais tes amis. Sans même t'en rendre compte. »
class Drift(Scene):
    zoom = (1.12, 1.0)

    def __init__(self):
        self.st = stars(1101, 260)

    def static(self, cv):
        night(cv, 1, '#05020F', '#14082E', '#2A0E3A')

    def dyn(self, cv, t, d):
        self.st.draw(cv, t)
        ribbons(cv, t, 2, 3, 140, 140, 70)
        k = ease(t / max(d, 0.1))
        for i, col in enumerate(['#FFB0E8', '#BFE6FF', '#FFE6A0', '#C8A8FF', '#8AD8C8']):
            a = i / 5 * 6.283 + 0.6
            r = 260 + 700 * k
            lantern(cv, 960 + math.cos(a) * r, 520 + math.sin(a) * r * 0.5 - 60 * k, 38 - 10 * k, col, 255 * (1 - 0.5 * k))
        hero(cv, t, 960, 790, 190, eyes='lidded')


# 2 ─ « Enfant, c'était facile. Un ballon, une cour de récré, et tu avais un meilleur ami pour la vie. »
class Childhood(Scene):
    zoom = (1.0, 1.1)

    def static(self, cv):
        cv.drawRect(skia.Rect.MakeXYWH(-400, -400, W + 800, H + 800), P(shader=lin(0, 0, 0, H, ['#5A2A6A', '#FF8A5C', '#FFD08A'])))
        glow(cv, 960, 700, 600, '#FFE6A0', 200)
        ofill(cv, pcircle(960, 720, 160), '#FFF0C0', ol=None, w=0)
        cv.drawRect(skia.Rect.MakeXYWH(-400, 860, W + 800, 600), P('#A85A4A'))
        for k in range(12):
            cv.drawLine(k * 180 - 100, 900, k * 180 + 60, 900, P('#FFE6A0', 120, stroke=5))
        for x in (160, 1760):
            ofill(cv, prr(x - 12, 560, 24, 300, 10), '#5A2A3A', ol=OLD)
            ofill(cv, prr(x - 60, 520, 120, 70, 14), '#7A3A4A', ol=OLD)

    def dyn(self, cv, t, d):
        bx = 960 + 380 * math.sin(t * 1.5)
        by = 960 - abs(math.sin(t * 4)) * 200
        for i, sk in enumerate(['#FF8AB8', '#FFB08A']):
            x = 960 + 460 * math.sin(t * 1.5 - 0.6 - i * 0.9)
            dude(cv, x, 1000, 70, t * 3 + i, kid=True, mood='joy', arms='up' if i else 'out', skin=sk,
                 top=['#2DE2C6', '#FFE04A'][i], bottom=['#8A4BFF', '#FF4FA8'][i], hair=OLD)
        ofill(cv, pcircle(bx, by, 34), '#FFFFFF', ol=OLD)
        cv.drawLine(bx - 34, by, bx + 34, by, P('#FF4FA8', 255, stroke=5))


# 3 ─ « Puis il y a eu les études. Le travail. Les déménagements. »
class Conveyor(Scene):
    zoom = (1.0, 1.08)
    pan = (60, 0, -60, 0)

    def static(self, cv):
        night(cv, 3, '#05020F', '#1A0A2A', '#2A0E2A')

    def dyn(self, cv, t, d):
        ofill(cv, prr(560, 900, 1500, 50, 25), '#3A2A5A', ol=OLD)
        for k in range(14):
            x = 560 + ((k * 110 - t * 160) % 1500)
            circle(cv, x, 925, 14, '#2A1A4A')
        for i in range(8):
            x = 600 + ((i * 220 + t * 160) % 1600)
            kind = i % 3
            if kind == 0:
                ofill(cv, prr(x - 60, 800, 120, 100, 6), '#C8946A', ol=OLD, w=4)
                cv.drawLine(x - 60, 830, x + 60, 830, P('#8A5A3A', 255, stroke=6))
            elif kind == 1:
                ofill(cv, prr(x - 70, 840, 140, 60, 8), '#F4EEDC', ol=OLD, w=4)
                ofill(cv, pcircle(x + 40, 880, 14), '#D81E2E', ol=OLD, w=3)
            else:
                ofill(cv, prr(x - 55, 790, 110, 110, 16), '#5A7ABF', ol=OLD, w=4)
                ofill(cv, prr(x - 20, 770, 40, 26, 8), '#5A7ABF', ol=OLD, w=4)
        hero(cv, t, 1180, 760, 150, eyes='lidded')
        k = ease(t / max(d, 0.1))
        ofill(cv, prr(-100, 900, 560 - 300 * k, 50, 20), '#2A1A3A', ol=OLD)
        for i, (sk, hr, rb) in enumerate(FRIENDS[:3]):
            cv.save(); cv.clipRect(skia.Rect.MakeXYWH(-100, 0, 560, 900))
            cv.saveLayerAlpha(None, int(255 * (1 - 0.6 * k)))
            hero(cv, t, 120 + i * 140 - 200 * k, 780, 80, eyes='open', third=False, hair_up=False, skin=sk, hair=hr, robe=rb, seed=70 + i)
            cv.restore(); cv.restore()


# 4 ─ « Les “on se fait un truc bientôt” qui ne se font jamais. »
class Bubbles(Scene):
    zoom = (1.0, 1.1)

    def static(self, cv):
        night(cv, 4, '#05020F', '#14082E', '#24082E')

    def dyn(self, cv, t, d):
        rnd = random.Random(4)
        msgs = ['on se voit bientôt ?', 'grave, ce week-end !', 'on se fait un truc', 'je te redis', 'trop hâte']
        for i in range(10):
            ph = rnd.uniform(0, 1); x0 = rnd.uniform(200, 1700)
            q = (t * 0.25 + ph) % 1
            y = 1100 - q * 1250
            x = x0 + 50 * math.sin(q * 6 + i)
            if q > 0.85:
                kk = (q - 0.85) / 0.15
                for j in range(8):
                    a = j / 8 * 6.283
                    circle(cv, x + math.cos(a) * 80 * kk, y + math.sin(a) * 50 * kk, 6, '#BFE6FF', 255 * (1 - kk))
                continue
            w = 330
            ofill(cv, prr(x - w / 2, y - 45, w, 90, 45), '#2A3A8A' if i % 2 else '#5A2A8A', a=230, ol=OLD, w=4)
            label(cv, x, y + 10, msgs[i % 5], 26, color='#E8E4FF', font=FONT, box=False)


# 5 ─ « Et un samedi soir, tu fais défiler tes contacts, et tu ne sais plus qui appeler. »
class Contacts(Scene):
    zoom = (1.0, 1.12)

    def static(self, cv):
        night(cv, 5, '#000000', '#05020F', '#0E0620')

    def dyn(self, cv, t, d):
        px, py, pw, ph = 1120, 120, 420, 840
        glow(cv, px + pw / 2, py + ph / 2, 600, '#5AD7FF', 90)
        ofill(cv, prr(px, py, pw, ph, 50), '#0E0E1E', ol=OLD)
        cv.save(); cv.clipPath(prr(px + 20, py + 60, pw - 40, ph - 120, 30), doAntiAlias=True)
        cv.drawRect(skia.Rect.MakeXYWH(px, py, pw, ph), P('#1A2A4A'))
        names = ['Léa', 'Karim', 'Maxime', 'Inès', 'Thomas', 'Sarah', 'Hugo', 'Camille', 'Yanis', 'Jade', 'Lucas', 'Nora']
        off = (t * 90) % 100
        for i in range(16):
            y = py + 100 + i * 100 - off
            a = max(0, 1 - abs(y - (py + ph / 2)) / 450)
            ofill(cv, pcircle(px + 80, y, 30), '#3A4A7A', a=255 * a, ol=None, w=0)
            label(cv, px + 230, y + 10, names[(i + int(t * 0.9)) % len(names)], 28, color='#BFE6FF', a=200 * a * (1 - 0.5 * ease(t / max(d, 0.1))), font=FONT, box=False)
        cv.restore()
        hero(cv, t, 620, 800, 190, eyes='lidded', third=False)
        glow(cv, 620, 760, 260, '#5AD7FF', 80)


# 6 ─ « Ce n'est pas qu'une impression. »
class NotJust(Scene):
    zoom = (1.15, 1.0)

    def __init__(self):
        self.st = stars(1106, 200)

    def static(self, cv):
        night(cv, 6, '#05020F', '#1A0A3A', '#2A0E3A')

    def dyn(self, cv, t, d):
        self.st.draw(cv, t)
        for i in range(6):
            q = (t * 0.6 + i / 6) % 1
            cv.drawCircle(960, 690, 100 + q * 900, P('#B98CFF', 120 * (1 - q), stroke=4))
        hero(cv, t, 960, 800, 200, eyes='open')
        glow(cv, 960, 800 - 0.55 * 200, 110 + 30 * math.sin(t * 4), '#FFE680', 230)


# 7 ─ « Des chercheurs ont montré que notre nombre d'amis atteint son maximum vers vingt-cinq ans, puis diminue. »
class Curve(Scene):
    zoom = (1.0, 1.1)

    def __init__(self):
        self.st = stars(1107, 220)

    def static(self, cv):
        night(cv, 7, '#05020F', '#14082E', '#3A0E3A')

    def curve_y(self, u):
        return 920 - 520 * math.exp(-((u - 0.32) ** 2) / 0.05) - 80 * (1 - u)

    def dyn(self, cv, t, d):
        self.st.draw(cv, t, 200)
        k = ease(t / max(d * 0.8, 0.1))
        pts = [(160 + u / 100 * 1600, self.curve_y(u / 100)) for u in range(0, int(100 * k) + 1)]
        p = skia.Path(); p.moveTo(160, H + 50)
        for q in pts:
            p.lineTo(*q)
        if pts:
            p.lineTo(pts[-1][0], H + 50)
        p.close()
        cv.drawPath(p, P('#2A1450', 220))
        if len(pts) > 1:
            neon(cv, pts, '#FF8AD8', w=6, glow_w=20)
            x, y = pts[-1]
            cv.save(); cv.clipRect(skia.Rect.MakeXYWH(x - 110, y - 220, 220, 222))
            hero(cv, t * 2, x, y - 110, 45, eyes='lidded', hair_up=False, robe='#3A0E5A')
            cv.restore()
        px = 160 + 0.32 * 1600
        if k > 0.35:
            cv.drawLine(px, self.curve_y(0.32), px, 960, P('#FFE680', 160, stroke=3))
            label(cv, px, 1010, '25 ANS', 30, color='#FFE680', font=FONT)
        for i, u in enumerate((0.1, 0.2, 0.32, 0.45, 0.6)):
            if k > u:
                x = 160 + u * 1600; y = self.curve_y(u)
                lantern(cv, x + 40 * math.sin(t + i), y - 150 - 20 * math.sin(t * 1.3 + i), 22, ['#FFB0E8', '#BFE6FF', '#FFE6A0', '#C8A8FF', '#8AD8C8'][i], 220 * (1 - max(0, u - 0.35) * 1.5))


# 8 ─ « Et il faut environ deux cents heures passées ensemble pour devenir vraiment proches. »
class Hours(Scene):
    zoom = (1.0, 1.12)

    def static(self, cv):
        night(cv, 8, '#05020F', '#1A0A2A', '#2A0E3A')

    def icon(self, cv, kind, x, y, s, a=255):
        if kind == 0:   # tasse
            ofill(cv, prr(x - s, y - s, 2 * s, 1.8 * s, s * 0.4), '#FF8A5C', a=a, ol=OLD, w=3)
        elif kind == 1:  # cœur
            circle(cv, x - s * 0.5, y, s * 0.55, '#FF4F81', a); circle(cv, x + s * 0.5, y, s * 0.55, '#FF4F81', a)
            poly(cv, [(x - s, y + s * 0.15), (x + s, y + s * 0.15), (x, y + s * 1.2)], '#FF4F81', a)
        elif kind == 2:  # note
            circle(cv, x, y + s * 0.6, s * 0.45, '#B98CFF', a); cv.drawLine(x + s * 0.4, y + s * 0.6, x + s * 0.4, y - s, P('#B98CFF', a, stroke=s * 0.25))
        else:            # étoile
            sparkle(cv, x, y, s * 1.2, '#FFE680', a)

    def dyn(self, cv, t, d):
        cx, cy = 960, 520
        ofill(cv, ppoly([(cx - 300, cy - 400), (cx + 300, cy - 400), (cx + 24, cy), (cx - 24, cy)]), '#BFE6FF', a=50, ol=OLD)
        ofill(cv, ppoly([(cx - 24, cy), (cx + 24, cy), (cx + 300, cy + 400), (cx - 300, cy + 400)]), '#BFE6FF', a=50, ol=OLD)
        rnd = random.Random(8)
        for i in range(40):
            ph = rnd.uniform(0, 1); dx = rnd.uniform(-1, 1); kind = i % 4
            q = (ph + t * 0.25) % 1
            if q < 0.45:
                x = cx + dx * 220 * (1 - q / 0.45); y = cy - 340 + q / 0.45 * 330
            else:
                x = cx + dx * 220 * (q - 0.45) * 1.8; y = cy + 20 + (q - 0.45) / 0.55 * 340
            self.icon(cv, kind, x, y, 16)
        label(cv, 1500, 520, '200 H', 52, color='#FFE680', font=FONT, box=False)


# 9 ─ « Deux cents heures. Exactement ce qu'on n'a plus le temps de donner. »
class Frozen(Scene):
    zoom = (1.0, 1.1)

    def __init__(self):
        rnd = random.Random(9)
        self.c = [(rnd.uniform(100, W - 100), rnd.uniform(100, H - 100), rnd.uniform(40, 90), rnd.uniform(0, 6)) for _ in range(12)]

    def static(self, cv):
        night(cv, 9, '#05020F', '#120830', '#24082E')

    def dyn(self, cv, t, d):
        for x, y, r, ph in self.c:
            yy = y + 20 * math.sin(t * 0.6 + ph)
            ofill(cv, pcircle(x, yy, r), '#E8E4FF', a=140, ol=OLD, w=4)
            for sp, ln in ((0.3, 0.5), (2.0, 0.8)):
                a = t * sp * 0.2 + ph - 1.57
                cv.drawLine(x, yy, x + math.cos(a) * r * ln, yy + math.sin(a) * r * ln, P(OLD, 200, stroke=4))
        for k in range(5):
            cv.drawOval(skia.Rect.MakeLTRB(-200 + k * 380, 700 + 20 * math.sin(t + k), 500 + k * 380, 1100), P('#C8B8FF', 40, blur=50))


# 10 ─ « Mais voilà ce que personne ne dit. »
class Secret(Scene):
    zoom = (1.15, 1.0)

    def __init__(self):
        self.st = stars(1110, 260)

    def static(self, cv):
        night(cv, 10, '#05020F', '#1A0A3A', '#3A0E4A')

    def dyn(self, cv, t, d):
        self.st.draw(cv, t)
        k = ease(t / max(d, 0.1))
        for side in (-1, 1):
            x = 960 + side * (300 + 700 * k)
            cv.drawOval(skia.Rect.MakeLTRB(x - 600, 200, x + 600, 1100), P('#B98CFF', 70, blur=60))
        hero(cv, t, 960, 800, 190, eyes='open')
        glow(cv, 960, 800 - 0.55 * 190, 160 * k + 40, '#FFE680', 230)


# 11 ─ « Ceux que tu as perdus de vue ressentent exactement la même chose. »
class Windows(Scene):
    zoom = (1.12, 1.0)

    def __init__(self):
        self.st = stars(1111, 200)
        self.wins = None

    def static(self, cv):
        night(cv, 11, '#02010A', '#0E0A2A', '#1A0A2A')
        self.wins = city(cv, 12, 1080, 0.35)

    def dyn(self, cv, t, d):
        self.st.draw(cv, t, 180)
        for i, (x, y) in enumerate(self.wins):
            on = (i * 7 + int(t * 2)) % 13 != 0
            cv.drawRect(skia.Rect.MakeXYWH(x, y, 32, 40), P('#FFE680' if on else '#5A4A2A', 220))
            if i % 3 == 0:
                circle(cv, x + 16, y + 26, 8, OLD)
                glow(cv, x + 16, y + 30, 18, '#5AD7FF', 160)


# 12 ─ « Ils attendent, eux aussi, que quelqu'un fasse le premier pas. »
class Threads(Windows):
    zoom = (1.0, 1.1)

    def dyn(self, cv, t, d):
        super().dyn(cv, t, d)
        rnd = random.Random(5)
        pts = rnd.sample(self.wins, 12)
        for i in range(0, 12, 2):
            (x0, y0), (x1, y1) = pts[i], pts[i + 1]
            u = 0.3 + 0.25 * math.sin(t * 1.3 + i)
            mx, my = (x0 + x1) / 2, min(y0, y1) - 160
            path = []
            for j in range(13):
                v = j / 12 * u
                path.append(((1 - v) ** 2 * x0 + 2 * v * (1 - v) * mx + v ** 2 * x1, (1 - v) ** 2 * y0 + 2 * v * (1 - v) * my + v ** 2 * y1))
            neon(cv, path, '#FFB0E8', w=3, a=200, glow_w=10)


# 13 ─ « Alors si tu te sens seul ce soir, envoie ce message. »
class Send(Scene):
    zoom = (1.0, 1.1)

    def __init__(self):
        self.st = stars(1113, 220)

    def static(self, cv):
        night(cv, 13, '#05020F', '#14082E', '#2A0E3A')

    def dyn(self, cv, t, d):
        self.st.draw(cv, t)
        hero(cv, t, 560, 800, 180, eyes='open', smile=True)
        px, py = 900, 720
        ofill(cv, prr(px, py, 200, 340, 30), '#0E0E1E', ol=OLD)
        cv.drawRect(skia.Rect.MakeXYWH(px + 14, py + 40, 172, 260), P('#2A3A6A'))
        k = ease_out((t - d * 0.4) / max(d * 0.5, 0.1))
        ofill(cv, prr(px + 30, py + 220, 140, 50, 25), '#5AD7FF' if k <= 0 else '#3FD07A', ol=OLD, w=3)
        if k > 0:
            bird(cv, px + 100 + 800 * k, py + 160 - 500 * k + 40 * math.sin(t * 3), 40, t)


# 14 ─ « Le pire qui puisse arriver, c'est qu'il te réponde. »
class Reply(Windows):
    zoom = (1.12, 1.0)

    def dyn(self, cv, t, d):
        super().dyn(cv, t, d)
        k = ease(t / max(d * 0.5, 0.1))
        sx, sy = 260, 180
        tx, ty = self.wins[len(self.wins) // 2]
        bx, by = sx + (tx - sx) * k, sy + (ty - 60 - sy) * k + 60 * math.sin(k * math.pi) * -1
        if k < 1:
            bird(cv, bx, by, 36, t)
        else:
            k2 = ease((t - d * 0.5) / max(d * 0.4, 0.1))
            glow(cv, tx + 16, ty + 20, 200 * k2 + 30, '#FFE680', 255)
            ox, oy = self.wins[len(self.wins) // 4]
            path = [(ox + 16 + (tx - ox) * j / 20, oy + 20 + (ty - oy) * j / 20 - 160 * math.sin(j / 20 * math.pi)) for j in range(int(20 * k2) + 1)]
            if len(path) > 1:
                neon(cv, path, '#FFE680', w=5, glow_w=18)
            glow(cv, ox + 16, oy + 20, 120 * k2, '#FFE680', 220)


SEGMENTS = [
    (Drift, "Personne ne t'a prévenu qu'en grandissant, tu perdrais tes amis. Sans même t'en rendre compte."),
    (Childhood, "Enfant, c'était facile. Un ballon, une cour de récré, et tu avais un meilleur ami pour la vie."),
    (Conveyor, "Puis il y a eu les études. Le travail. Les déménagements."),
    (Bubbles, "Les « on se fait un truc bientôt » qui ne se font jamais."),
    (Contacts, "Et un samedi soir, tu fais défiler tes contacts, et tu ne sais plus qui appeler."),
    (NotJust, "Ce n'est pas qu'une impression."),
    (Curve, "Des chercheurs ont montré que notre nombre d'amis atteint son maximum vers vingt-cinq ans, puis diminue."),
    (Hours, "Et il faut environ deux cents heures passées ensemble pour devenir vraiment proches."),
    (Frozen, "Deux cents heures. Exactement ce qu'on n'a plus le temps de donner."),
    (Secret, "Mais voilà ce que personne ne dit."),
    (Windows, "Ceux que tu as perdus de vue ressentent exactement la même chose."),
    (Threads, "Ils attendent, eux aussi, que quelqu'un fasse le premier pas."),
    (Send, "Alors si tu te sens seul ce soir, envoie ce message."),
    (Reply, "Le pire qui puisse arriver, c'est qu'il te réponde."),
]
