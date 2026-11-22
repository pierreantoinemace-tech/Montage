"""« La machine à rêves » : 17 plans, style sombre et onirique (TikToks × Midnight Gospel),
héros = le personnage « troisième œil » de la photo de profil."""
import math, os, random, sys, importlib.util
import skia
HERE = os.path.dirname(os.path.abspath(__file__))
for d in ('../calendrier', '../temps', '../profil'):
    sys.path.insert(1, os.path.join(HERE, d))
from lib import *
from kit import Stars, sparkle, neon
from mg import *
_s = importlib.util.spec_from_file_location('pfp_dark', os.path.join(HERE, '..', 'profil', 'pfp_dark.py'))
pd = importlib.util.module_from_spec(_s); _s.loader.exec_module(pd)
OLD, floating_eye, moon = pd.OLD, pd.floating_eye, pd.moon

FONT = None
STYLE = dict(exclusion=True, color='#F0EBBE', size=196, maxw=1760, glitch=True, grain=7, readable=True, fps=60, trans=0.7, float=True)
HERO = dict(skin='#7AC8D8', hair='#14304A', robe='#3A0E5A')
NIGHT = ('#ffffff', '#BFE6FF', '#FFB0E8', '#B98CFF')


class Scene:
    zoom = (1.0, 1.08)
    pan = (0, 0, 0, 0)
    shake = 0.0

    def static(self, cv):
        pass

    def dyn(self, cv, t, d):
        pass


def night(cv, seed, top='#05020F', mid='#14082E', bottom='#2A0E3A'):
    cv.drawRect(skia.Rect.MakeXYWH(-400, -400, W + 800, H + 800), P(shader=lin(0, 0, 0, H, [top, mid, bottom])))
    rnd = random.Random(seed)
    for _ in range(2600):
        circle(cv, rnd.uniform(-200, W + 200), rnd.uniform(-200, H + 200), rnd.uniform(0.6, 1.8), '#FFFFFF', 16)


def stars(seed, n=180):
    return Stars(n, seed, rmax=2.2, colors=NIGHT)


def hero(cv, t, cx, cy, s, eyes='open', third=True, smile=False, hair_up=True, seed=5, **kw):
    h = dict(HERO); h.update(kw)
    cy += 0.025 * s * math.sin(t * 1.4 + seed)             # respiration / flottement
    cv.save(); cv.translate(cx, cy + s); cv.rotate(1.5 * math.sin(t * 0.7 + seed)); cv.translate(-cx, -cy - s)
    pd.dreamer(cv, cx, cy, s, skin=h['skin'], hair=h['hair'], robe=h['robe'], eyes=eyes, third_eye=third, hair_up=hair_up, seed=seed, t=t + 0.01, arms=h.get('arms'), look=h.get('look'))
    if smile:
        cv.drawRect(skia.Rect.MakeXYWH(cx - 0.18 * s, cy + 0.55 * s, 0.36 * s, 0.12 * s), P(h['skin']))
        p = skia.Path(); p.addArc(skia.Rect.MakeLTRB(cx - 0.16 * s, cy + 0.48 * s, cx + 0.16 * s, cy + 0.68 * s), 20, 140)
        cv.drawPath(p, P(OLD, 255, stroke=5))
    cv.restore()


def eyes_field(cv, t, seed, n=6, area=(80, 80, W - 80, 520)):
    rnd = random.Random(seed)
    for i in range(n):
        x, y, r = rnd.uniform(area[0], area[2]), rnd.uniform(area[1], area[3]), rnd.uniform(24, 46)
        floating_eye(cv, x + 10 * math.sin(t + i), y + 8 * math.cos(t * 0.8 + i), r, (math.sin(t * 0.7 + i), 0.2))


def hooded(cv, x, y, s, t, orb=True):
    """Silhouette encapuchonnée sans visage, main tendue avec un orbe de rêve."""
    p = skia.Path(); p.moveTo(x - 1.4 * s, H + 60); p.cubicTo(x - 1.2 * s, y + 0.5 * s, x - 0.9 * s, y - 1.2 * s, x, y - 1.3 * s)
    p.cubicTo(x + 0.9 * s, y - 1.2 * s, x + 1.2 * s, y + 0.5 * s, x + 1.4 * s, H + 60); p.close()
    glow(cv, x, y - 0.6 * s, 1.6 * s, '#7A3CFF', 110)
    ofill(cv, p, '#3A1A6A', ol=OLD)
    cv.save(); cv.clipPath(p, doAntiAlias=True)
    oval(cv, x + 0.9 * s, y, 0.9 * s, 2.5 * s, '#1A0A2E', 200)
    cv.restore()
    cv.drawPath(p, P('#B98CFF', 160, stroke=4))
    ofill(cv, poval(x, y - 0.55 * s, 0.5 * s, 0.6 * s), '#05020A', ol=OLD)
    for k in (-1, 1):
        glow(cv, x + k * 0.17 * s, y - 0.55 * s, 0.12 * s, '#FFE6B0', 220)
        circle(cv, x + k * 0.17 * s, y - 0.55 * s, 0.035 * s, '#FFF6D0')
    if orb:
        noodle(cv, [(x + 0.7 * s, y + 0.2 * s), (x + 1.2 * s, y + 0.1 * s), (x + 1.6 * s, y - 0.2 * s)], '#3A1A6A', w=0.32 * s, ol=OLD)
        ox, oy = x + 1.75 * s, y - 0.45 * s + 10 * math.sin(t * 2)
        glow(cv, ox, oy, 0.9 * s, '#FFB0E8', 200)
        ofill(cv, pcircle(ox, oy, 0.32 * s), '#FFE6F4', ol=OLD)
        cv.save(); cv.clipPath(pcircle(ox, oy, 0.32 * s), doAntiAlias=True)
        for k in range(4):
            ofill(cv, pblob(ox - 0.2 * s + k * 0.13 * s, oy + 0.1 * s, 0.08 * s, seed=k, t=t), ['#FFE04A', '#FF8AD8', '#2DE2C6', '#B98CFF'][k], w=3)
        cv.restore()


def capsule(cv, x, y, s, t, glow_k=1.0, open_k=0.0):
    """Capsule-cocon organique, câbles-racines qui pulsent."""
    rnd = random.Random(3)
    for i in range(9):
        a = rnd.uniform(-0.2, 3.34)
        x1, y1 = x + math.cos(a) * 1.4 * s, H + 40
        p = [(x + math.cos(a) * 0.6 * s, y + 0.3 * s), (x + math.cos(a) * 1.1 * s, y + 0.5 * s + rnd.uniform(0, 80)), (x1 + rnd.uniform(-200, 200), y1)]
        noodle(cv, p, '#2A1450', w=16, ol=OLD)
        k = (t * 0.8 + i / 9) % 1
        u = k
        px = (1 - u) ** 2 * p[0][0] + 2 * u * (1 - u) * p[1][0] + u ** 2 * p[2][0]
        py = (1 - u) ** 2 * p[0][1] + 2 * u * (1 - u) * p[1][1] + u ** 2 * p[2][1]
        glow(cv, px, py, 30, '#2DE2E6', 220 * glow_k)
    glow(cv, x, y, 1.6 * s, '#B98CFF', 120 * glow_k)
    body = poval(x, y, 1.15 * s, 0.55 * s)
    ofill(cv, body, '#2A1450', ol=OLD)
    cv.save(); cv.clipPath(body, doAntiAlias=True)
    for k in range(7):
        cv.drawLine(x - 1.2 * s + k * 0.4 * s, y - 0.6 * s, x - 1.0 * s + k * 0.35 * s, y + 0.6 * s, P('#3A1A6A', 255, stroke=10))
    cv.restore()
    win = poval(x, y - 0.05 * s, 0.85 * s, 0.33 * s * (1 - 0.0 * open_k))
    cv.drawPath(win, P(shader=lin(x - s, y, x + s, y, ['#2DE2E6', '#B98CFF', '#FF8AD8']), a=150 + 80 * glow_k))
    cv.drawPath(win, P(OLD, 255, stroke=OW))
    return win


# 1 ─ « Une seule question. Et réponds honnêtement. »
class Question(Scene):
    zoom = (1.15, 1.0)

    def __init__(self):
        self.st = stars(801)

    def static(self, cv):
        night(cv, 1)
        for i, c in enumerate(['#2A0E5A', '#3A1470']):
            cv.drawCircle(960, 480, 600 - i * 200, P(c, 80, blur=60))

    def dyn(self, cv, t, d):
        self.st.draw(cv, t)
        eyes_field(cv, t, 2, 5, (120, 120, W - 120, 900))
        hero(cv, t, 960, 790, 220, eyes='open')


# 2 ─ « Si on t'offrait la vie de tes rêves, pour toujours, tu dirais oui ? »
class Offer(Scene):
    zoom = (1.0, 1.12)
    pan = (40, 0, -40, 0)

    def __init__(self):
        self.st = stars(802)

    def static(self, cv):
        night(cv, 2, '#02010A', '#0E0A2A', '#1A0A2A')
        pd.mist(cv, 980, '#B98CFF', 40) if hasattr(pd, 'mist') else None

    def dyn(self, cv, t, d):
        self.st.draw(cv, t)
        hooded(cv, 760, 760, 300, t)


# 3 ─ « Attention. Il y a un piège. »
class Trap(Scene):
    zoom = (1.0, 1.25)
    shake = 0.25

    def static(self, cv):
        night(cv, 3, '#05020A', '#14062A', '#2A0814')

    def dyn(self, cv, t, d):
        ox, oy, R = 960, 520, 320
        glow(cv, ox, oy, R * 2, '#FF4F6B', 90 + 40 * math.sin(t * 6))
        ofill(cv, pcircle(ox, oy, R), '#FFE6F4', ol=OLD)
        cv.save(); cv.clipPath(pcircle(ox, oy, R), doAntiAlias=True)
        for k in range(6):
            ofill(cv, pblob(ox - 200 + k * 80, oy + 60, 70, seed=k, t=t), ['#FFE04A', '#FF8AD8', '#2DE2C6', '#B98CFF', '#FF8A1F', '#9BFF3B'][k], w=4)
        # des câbles noirs envahissent l'orbe
        rnd = random.Random(4)
        k = ease(t / max(d, 0.1))
        for i in range(10):
            a = rnd.uniform(0, 6.283)
            x0, y0 = ox + math.cos(a) * R * 1.2, oy + math.sin(a) * R * 1.2
            x1, y1 = ox + math.cos(a + 0.6) * R * (1 - 0.8 * k), oy + math.sin(a + 0.6) * R * (1 - 0.8 * k)
            noodle(cv, [(x0, y0), (ox + math.cos(a + 0.3) * R * 0.8, oy + math.sin(a + 0.3) * R * 0.8), (x1, y1)], '#1A0A2E', w=18, ol=OLD)
        cv.restore()
        cv.drawPath(pcircle(ox, oy, R), P(OLD, 255, stroke=OW * 1.5))
        floating_eye(cv, ox, oy, 70 + 20 * k, (0, 0))


# 4 ─ « Voilà le marché. Tu t'allonges dans une machine. Tu fermes les yeux. »
class Lie(Scene):
    zoom = (1.0, 1.15)

    def __init__(self):
        self.st = stars(804)

    def static(self, cv):
        night(cv, 4)
        cv.drawRect(skia.Rect.MakeXYWH(-400, 860, W + 800, 600), P('#0E0620'))

    def dyn(self, cv, t, d):
        self.st.draw(cv, t, 200)
        win = capsule(cv, 960, 640, 520, t)
        cv.save(); cv.clipPath(win, doAntiAlias=True)
        cv.translate(960, 620); cv.rotate(-90)
        k = ease((t - d * 0.5) / max(d * 0.4, 0.1))
        hero(cv, t, 0, -80, 150, eyes='closed' if k > 0.5 else 'lidded', hair_up=False, third=k > 0.5)
        cv.restore()


class _Dream(Scene):
    def dream_bg(self, cv):
        cv.drawRect(skia.Rect.MakeXYWH(-400, -400, W + 800, H + 800), P(shader=lin(0, 0, 0, H, ['#3A1A7A', '#FF8AB8', '#FFD08A'])))
        rnd = random.Random(9)
        for _ in range(2000):
            circle(cv, rnd.uniform(-200, W + 200), rnd.uniform(-200, H + 200), rnd.uniform(0.6, 1.8), '#FFFFFF', 20)

    def island(self, cv, x, y, s, t, col='#7A3CFF'):
        yy = y + 14 * math.sin(t * 0.9 + x)
        p = skia.Path(); p.moveTo(x - 1.2 * s, yy); p.quadTo(x, yy - 0.3 * s, x + 1.2 * s, yy); p.quadTo(x + 0.4 * s, yy + 1.4 * s, x, yy + 1.6 * s); p.quadTo(x - 0.4 * s, yy + 1.4 * s, x - 1.2 * s, yy); p.close()
        ofill(cv, p, '#5A2A6A', ol=OLD)
        ofill(cv, poval(x, yy - 0.05 * s, 1.2 * s, 0.22 * s), '#3FD07A', ol=OLD)
        for k in range(3):
            ofill(cv, prr(x - 0.6 * s + k * 0.45 * s, yy - 0.9 * s + (k % 2) * 0.2 * s, 0.32 * s, 0.8 * s - (k % 2) * 0.2 * s, 0.1 * s), ['#FFE04A', '#FFB0E8', '#FFF6D0'][k], ol=OLD)
            poly(cv, [(x - 0.6 * s + k * 0.45 * s, yy - 0.9 * s + (k % 2) * 0.2 * s), (x - 0.44 * s + k * 0.45 * s, yy - 1.2 * s), (x - 0.28 * s + k * 0.45 * s, yy - 0.9 * s + (k % 2) * 0.2 * s)], '#FF4FA8')


# 5 ─ « Et tu vis le rêve parfait, jusqu'à la fin de ta vie. »
class Dream(_Dream):
    zoom = (1.12, 1.0)

    def static(self, cv):
        self.dream_bg(cv)
        glow(cv, 960, 760, 600, '#FFF6D0', 160)

    def dyn(self, cv, t, d):
        for i, (x, y, s) in enumerate([(380, 560, 170), (1500, 480, 200), (980, 760, 140), (240, 260, 90), (1720, 200, 80)]):
            self.island(cv, x, y, s, t)
        # train dans les nuages
        tx = (t * 220) % (W + 900) - 500
        for k in range(4):
            ofill(cv, prr(tx - k * 170, 330, 150, 80, 24), ['#FF4FA8', '#FFE04A', '#2DE2C6', '#B98CFF'][k], ol=OLD)
            for w in (30, 110):
                ofill(cv, pcircle(tx - k * 170 + w, 412, 16), '#2A1450', ol=OLD, w=4)
        for k in range(8):
            cloud(cv, (k * 300 + t * 40) % (W + 400) - 200, 420 + (k % 3) * 40, 50, '#FFFFFF', 200, shade='#FFD0E8')


# 6 ─ « Le succès. L'amour. Les voyages. Tout ce que tu as toujours voulu. »
class Wishes(_Dream):
    zoom = (1.0, 1.08)

    def static(self, cv):
        self.dream_bg(cv)

    def dyn(self, cv, t, d):
        q = min(3, int(t / max(d, 0.1) * 4))
        if q == 0:
            for k in range(30):
                a = k / 30 * 6.283 + t
                circle(cv, 960 + math.cos(a) * 520, 520 + math.sin(a) * 300, 8, '#FFE04A')
            hero(cv, t, 960, 800, 190, eyes='lidded', smile=True)
            ofill(cv, ppoly([(830, 300), (870, 220), (920, 280), (960, 200), (1000, 280), (1050, 220), (1090, 300)]), '#FFE04A', ol=OLD)
        elif q == 1:
            hero(cv, t, 700, 800, 180, eyes='lidded', smile=True)
            hero(cv, t, 1220, 800, 180, eyes='lidded', smile=True, skin='#E07AB8', hair='#2A0E3A', robe='#1E5A6A', seed=9)
            for k in range(6):
                u = (t * 0.6 + k / 6) % 1
                c = '#FF4F81'
                x, y, r = 960 + 60 * math.sin(k * 2 + u * 4), 520 - u * 400, 24
                circle(cv, x - r * 0.5, y, r * 0.55, c, 255 * math.sin(u * math.pi)); circle(cv, x + r * 0.5, y, r * 0.55, c, 255 * math.sin(u * math.pi))
                poly(cv, [(x - r, y + 4), (x + r, y + 4), (x, y + r * 1.2)], c, 255 * math.sin(u * math.pi))
        else:
            bx, by = 960 + 200 * math.sin(t * 0.6), 420
            ofill(cv, pcircle(bx, by, 220), '#FF4FA8', ol=OLD)
            cv.save(); cv.clipPath(pcircle(bx, by, 220), doAntiAlias=True)
            for k in range(6):
                cv.drawRect(skia.Rect.MakeXYWH(bx - 220 + k * 80, by - 220, 40, 440), P('#FFE04A', 230))
            cv.restore()
            cv.drawPath(pcircle(bx, by, 220), P(OLD, 255, stroke=OW))
            for k in (-1, 1):
                cv.drawLine(bx + k * 140, by + 170, bx + k * 60, by + 330, P(OLD, 255, stroke=5))
            ofill(cv, prr(bx - 70, by + 320, 140, 90, 14), '#8A4A2A', ol=OLD)
            self.island(cv, 400, 820, 160, t); self.island(cv, 1560, 860, 140, t)


# 7 ─ « Tout paraît vrai. Tu ne sauras jamais que c'est un rêve. »
class Real(_Dream):
    zoom = (1.15, 1.0)

    def static(self, cv):
        self.dream_bg(cv)

    def dyn(self, cv, t, d):
        hero(cv, t, 960, 790, 220, eyes='lidded', smile=True)
        rnd = random.Random(7)
        for i in range(40):
            a = rnd.uniform(0, 6.283); r = rnd.uniform(300, 800)
            sparkle(cv, 960 + math.cos(a + t * 0.1) * r, 540 + math.sin(a + t * 0.1) * r * 0.6, rnd.uniform(8, 20), '#FFF6D0', 200)
        # fine fissure du rêve, presque invisible
        k = ease(t / max(d, 0.1))
        p = skia.Path(); p.moveTo(1500, 0)
        for j in range(1, 8):
            p.lineTo(1500 - j * 30 + (j % 2) * 40, j * 90 * k)
        cv.drawPath(p, P('#05020A', 160 * k, stroke=4))


# 8 ─ « Pendant ce temps, ton corps reste là, dans le noir, branché à des câbles. »
class Body(Scene):
    zoom = (1.0, 1.2)

    def static(self, cv):
        night(cv, 8, '#000000', '#05020F', '#0E0620')

    def dyn(self, cv, t, d):
        eyes_field(cv, t, 8, 8, (80, 80, W - 80, 500))
        win = capsule(cv, 960, 700, 560, t, glow_k=0.5 + 0.5 * math.sin(t * 2))
        cv.save(); cv.clipPath(win, doAntiAlias=True)
        cv.translate(960, 680); cv.rotate(-90)
        hero(cv, t, 0, -80, 160, eyes='closed', hair_up=False)
        cv.restore()


# 9 ─ « C'est une expérience de pensée du philosophe Robert Nozick. »
class Nozick(Scene):
    zoom = (1.0, 1.1)

    def __init__(self):
        self.st = stars(809)

    def static(self, cv):
        night(cv, 9, '#05020F', '#14082E', '#2A0E3A')

    def dyn(self, cv, t, d):
        self.st.draw(cv, t, 200)
        hero(cv, t, 560, 600, 220, eyes='lidded', third=False, skin='#D8B8A8', hair='#5A5A6A', robe='#3A2A1A', seed=11)
        for k in (-1, 1):
            ofill(cv, pcircle(560 + k * 66, 590, 62), '#000000', a=0, ol=OLD, w=6)
        cv.drawLine(560 - 4, 590, 560 + 4, 590, P(OLD, 255, stroke=6))
        ofill(cv, pblob(560, 760, 110, seed=2, wob=0.15), '#9A9AAA', ol=OLD)
        # tableau holographique de la machine
        cv.drawRect(skia.Rect.MakeXYWH(1000, 220, 760, 520), P('#2DE2E6', 30))
        cv.drawRect(skia.Rect.MakeXYWH(1000, 220, 760, 520), P('#2DE2E6', 200, stroke=4))
        neon(cv, [(1380 + 260 * math.cos(a / 30 * 6.283), 480 + 110 * math.sin(a / 30 * 6.283)) for a in range(31)], '#B98CFF', w=4)
        for k in range(5):
            neon(cv, [(1200 + k * 90, 590), (1180 + k * 100, 700)], '#2DE2E6', w=3, a=180)
        label(cv, 1380, 800, 'ROBERT NOZICK · 1974', 30, color='#2DE2E6', font=FONT)


# 10 ─ « Et la plupart des gens répondent non. »
class No(Scene):
    zoom = (1.12, 1.0)

    def static(self, cv):
        night(cv, 10)
        cv.drawRect(skia.Rect.MakeXYWH(-400, 900, W + 800, 600), P('#0E0620'))

    def dyn(self, cv, t, d):
        for i in range(3):
            capsule(cv, 360 + i * 600, 300, 160, t + i, glow_k=0.6)
        pal = [('#7AC8D8', '#14304A', '#3A0E5A'), ('#E07AB8', '#2A0E3A', '#1E5A6A'), ('#D8B8A8', '#3A2A1A', '#2A1A5A'), ('#B48AE0', '#2A1050', '#5A1A3A'), ('#8AD8A8', '#1A3A2A', '#2A2A6A')]
        for i, (sk, hr, rb) in enumerate(pal):
            x = 220 + i * 370
            sway = 30 * math.sin(t * 6 + i)
            cv.save(); cv.translate(x, 760); cv.rotate(sway * 0.4); cv.translate(-x, -760)
            hero(cv, t, x, 760, 120, eyes='open', third=False, hair_up=False, skin=sk, hair=hr, robe=rb, seed=20 + i)
            cv.restore()


# 11 ─ « Parce qu'au fond, on ne veut pas seulement se sentir heureux. On veut que ce soit vrai. »
class Hearts(Scene):
    zoom = (1.0, 1.12)

    def static(self, cv):
        night(cv, 11, '#05020F', '#1A0A3A', '#3A0E3A')

    def _heart(self, cv, x, y, r, col, a=255, ol=OLD):
        p = skia.Path(); p.moveTo(x, y + r * 0.9)
        p.cubicTo(x - r * 1.4, y - r * 0.1, x - r * 0.7, y - r * 1.2, x, y - r * 0.45)
        p.cubicTo(x + r * 0.7, y - r * 1.2, x + r * 1.4, y - r * 0.1, x, y + r * 0.9); p.close()
        ofill(cv, p, col, a=a, ol=ol)
        return p

    def dyn(self, cv, t, d):
        # cœur de verre, parfait mais froid
        p = self._heart(cv, 560, 520, 220, '#BFE6FF', a=120)
        cv.save(); cv.clipPath(p, doAntiAlias=True)
        for k in range(5):
            cv.drawLine(400 + k * 80, 300, 300 + k * 80, 800, P('#FFFFFF', 120, stroke=6))
        cv.restore()
        label(cv, 560, 900, 'PARFAIT', 30, color='#BFE6FF', font=FONT, box=False)
        # vrai cœur, imparfait, qui bat
        b = 1 + 0.08 * abs(math.sin(t * 3.2))
        glow(cv, 1360, 520, 360 * b, '#FF4F6B', 130)
        self._heart(cv, 1360, 520, 220 * b, '#FF4F6B')
        ofill(cv, prr(1300, 430, 140, 40, 10), '#FFE6D0', ol=OLD, w=4)
        cv.drawLine(1330, 440, 1330, 462, P(OLD, 255, stroke=3)); cv.drawLine(1410, 440, 1410, 462, P(OLD, 255, stroke=3))
        label(cv, 1360, 900, 'VRAI', 30, color='#FF8AA8', font=FONT, box=False)


# 12 ─ « Mais des chercheurs ont retourné la question. »
class Flip(Scene):
    zoom = (1.0, 1.1)
    shake = 0.2

    def static(self, cv):
        night(cv, 12)

    def dyn(self, cv, t, d):
        ang = 180 * ease(t / max(d * 0.9, 0.1))
        cv.save(); cv.translate(960, 540); cv.rotate(ang); cv.translate(-960, -540)
        p = skia.Path(); p.moveTo(-400, H + 400); p.lineTo(-400, 760); p.quadTo(960, 680, W + 400, 760); p.lineTo(W + 400, H + 400); p.close()
        ofill(cv, p, '#1A0A3A', ol=OLD)
        rnd = random.Random(5)
        for i in range(14):
            x = -100 + i * 150; h = rnd.uniform(120, 320)
            ofill(cv, prr(x, 760 - h, 120, h + 20, 8), '#2A1450', ol=OLD)
            for wy in range(int(780 - h), 740, 50):
                if rnd.random() > 0.4:
                    cv.drawRect(skia.Rect.MakeXYWH(x + 40, wy, 30, 24), P('#FFE680', 200))
        moon(cv, 1500, 240, 70, drip=False)
        cv.restore()
        cv.drawCircle(960, 540, 470, P('#B98CFF', 120, stroke=6))
        for k in range(2):
            a = math.radians(ang + k * 180)
            neon(cv, [(960 + 470 * math.cos(a - u * 0.05), 540 + 470 * math.sin(a - u * 0.05)) for u in range(20)], '#B98CFF', w=6, arrow=False)


# 13 ─ « Imagine que tu es déjà branché. Que ta vie, celle-ci, est le rêve. »
class AlreadyIn(Scene):
    zoom = (1.6, 1.0)

    def __init__(self):
        self.st = stars(813, 260)

    def static(self, cv):
        night(cv, 13, '#000000', '#05020F', '#14082E')

    def dyn(self, cv, t, d):
        self.st.draw(cv, t)
        win = capsule(cv, 960, 560, 640, t)
        cv.save(); cv.clipPath(win, doAntiAlias=True)
        cv.drawRect(skia.Rect.MakeXYWH(0, 0, W, H), P(shader=lin(0, 300, 0, 800, ['#FF8AB8', '#FFD08A'])))
        p = skia.Path(); p.moveTo(-400, H); p.lineTo(-400, 600); p.quadTo(960, 520, W + 400, 600); p.lineTo(W + 400, H); p.close()
        ofill(cv, p, '#3FD07A', ol=OLD)
        for i in range(12):
            x = 420 + i * 95
            ofill(cv, prr(x, 600 - 60 - (i % 3) * 30, 70, 80 + (i % 3) * 30, 6), ['#FF4FA8', '#FFE04A', '#2DE2C6', '#B98CFF'][i % 4], ol=OLD, w=4)
        glow(cv, 960, 420, 120, '#FFFFFF', 200)
        cv.restore()


# 14 ─ « On te propose de te réveiller, dans une réalité que tu ne connais pas. »
class WakeDoor(Scene):
    zoom = (1.0, 1.15)

    def static(self, cv):
        night(cv, 14, '#02010A', '#0E1A3A', '#1A0A2A')

    def dyn(self, cv, t, d):
        k = ease_out((t - 0.4) / 1.4)
        dx, dy, dw, dh = 1080, 200, 360, 620
        cv.save(); cv.clipPath(prr(dx, dy, dw, dh, 170), doAntiAlias=True)
        cv.drawRect(skia.Rect.MakeXYWH(dx, dy, dw, dh), P('#F4F8FF'))
        for i in range(3):
            ofill(cv, poval(dx + 90 + i * 100, dy + 420 - (i % 2) * 40, 26, 120), '#C8D0E0', ol='#8A90A8', w=3)
            ofill(cv, pcircle(dx + 90 + i * 100, dy + 280 - (i % 2) * 40, 24), '#C8D0E0', ol='#8A90A8', w=3)
        cv.restore()
        glow(cv, dx + dw / 2, dy + dh / 2, 600 * k, '#FFFFFF', 160 * k)
        cv.save(); cv.translate(dx, dy); cv.scale(max(0.02, 1 - k), 1)
        ofill(cv, prr(0, 0, dw, dh, 170), '#3A1A6A', ol=OLD)
        ofill(cv, pcircle(dw - 50, dh / 2, 20), '#FFE680', ol=OLD, w=4)
        cv.restore()
        cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(dx - 14, dy - 14, dw + 28, dh + 28), 180, 180), P(OLD, 255, stroke=14))
        for j in range(6):
            ofill(cv, prr(dx - 140 - j * 40, dy + dh + 20 + j * 40, 200, 24, 8), '#2A2050', ol=OLD, w=4)
        hero(cv, t, 520, 810, 185, eyes='open')


# 15 ─ « Et là, beaucoup préfèrent rester. »
class Stay(Scene):
    zoom = (1.12, 1.0)

    def static(self, cv):
        night(cv, 15, '#02010A', '#0E1A3A', '#1A0A2A')

    def dyn(self, cv, t, d):
        k = ease((t - 0.3) / max(d * 0.6, 0.1))
        dx, dy, dw, dh = 1080, 200, 360, 620
        cv.save(); cv.clipPath(prr(dx, dy, dw, dh, 170), doAntiAlias=True)
        cv.drawRect(skia.Rect.MakeXYWH(dx, dy, dw, dh), P('#F4F8FF'))
        cv.restore()
        glow(cv, dx + dw / 2, dy + dh / 2, 500 * (1 - k), '#FFFFFF', 140 * (1 - k))
        cv.save(); cv.translate(dx, dy); cv.scale(max(0.02, k), 1)
        ofill(cv, prr(0, 0, dw, dh, 170), '#3A1A6A', ol=OLD)
        cv.restore()
        cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(dx - 14, dy - 14, dw + 28, dh + 28), 180, 180), P(OLD, 255, stroke=14))
        hero(cv, t, 600, 810, 185, eyes='lidded', smile=k > 0.7)


# 16 ─ « Alors peut-être que ce qu'on aime, ce n'est pas la vérité. C'est notre vie. »
class Cozy(Scene):
    zoom = (1.0, 1.1)

    def __init__(self):
        rnd = random.Random(16)
        self.rain = [(rnd.uniform(1100, 1700), rnd.uniform(140, 620), rnd.uniform(300, 600)) for _ in range(60)]

    def static(self, cv):
        night(cv, 16, '#1A0A2A', '#2A1440', '#3A1A3A')
        ofill(cv, prr(1080, 120, 640, 520, 20), '#14082E', ol=OLD)
        glow(cv, 400, 300, 400, '#FFB05A', 120)
        cv.drawRect(skia.Rect.MakeXYWH(-400, 860, W + 800, 600), P('#2A1430'))

    def dyn(self, cv, t, d):
        cv.save(); cv.clipRect(skia.Rect.MakeXYWH(1090, 130, 620, 500))
        for x, y, sp in self.rain:
            yy = 130 + (y - 130 + t * sp) % 500
            cv.drawLine(x, yy, x - 4, yy + 26, P('#7A8BFF', 160, stroke=3))
        cv.restore()
        cv.drawRect(skia.Rect.MakeXYWH(1395, 130, 10, 500), P(OLD)); cv.drawRect(skia.Rect.MakeXYWH(1090, 375, 620, 10), P(OLD))
        hero(cv, t, 640, 800, 200, eyes='lidded', smile=True, hair_up=False)
        mx, my = 1000, 880
        ofill(cv, prr(mx - 70, my - 120, 140, 130, 26), '#FF8A5C', ol=OLD)
        noodle(cv, [(mx + 70, my - 90), (mx + 120, my - 60), (mx + 70, my - 30)], '#FF8A5C', w=14)
        for k in range(3):
            q = (t * 0.5 + k / 3) % 1
            p = skia.Path(); p.moveTo(mx - 30 + k * 30, my - 130)
            p.quadTo(mx - 50 + k * 30 + 30 * math.sin(q * 6), my - 180 - q * 40, mx - 30 + k * 30, my - 240 - q * 60)
            cv.drawPath(p, P('#FFFFFF', 160 * (1 - q), stroke=6))


# 17 ─ « Et toi ? Tu te branches ? Ou tu te réveilles ? »
class Choice(Scene):
    zoom = (1.12, 1.0)

    def __init__(self):
        self.st = stars(817, 220)

    def static(self, cv):
        night(cv, 17)

    def dyn(self, cv, t, d):
        self.st.draw(cv, t)
        capsule(cv, 380, 560, 280, t)
        dx, dy, dw, dh = 1440, 240, 280, 520
        cv.save(); cv.clipPath(prr(dx, dy, dw, dh, 140), doAntiAlias=True)
        cv.drawRect(skia.Rect.MakeXYWH(dx, dy, dw, dh), P('#F4F8FF'))
        cv.restore()
        glow(cv, dx + dw / 2, dy + dh / 2, 340, '#FFFFFF', 120)
        cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(dx - 12, dy - 12, dw + 24, dh + 24), 150, 150), P(OLD, 255, stroke=12))
        hero(cv, t, 960, 800, 200, eyes='open')


SEGMENTS = [
    (Question, "Une seule question. Et réponds honnêtement."),
    (Offer, "Si on t'offrait la vie de tes rêves, pour toujours, tu dirais oui ?"),
    (Trap, "Attention. Il y a un piège."),
    (Lie, "Voilà le marché. Tu t'allonges dans une machine. Tu fermes les yeux."),
    (Dream, "Et tu vis le rêve parfait, jusqu'à la fin de ta vie."),
    (Wishes, "Le succès. L'amour. Les voyages. Tout ce que tu as toujours voulu."),
    (Real, "Tout paraît vrai. Tu ne sauras jamais que c'est un rêve."),
    (Body, "Pendant ce temps, ton corps reste là, dans le noir, branché à des câbles."),
    (Nozick, "C'est une expérience de pensée du philosophe Robert Nozick."),
    (No, "Et la plupart des gens répondent non."),
    (Hearts, "Parce qu'au fond, on ne veut pas seulement se sentir heureux. On veut que ce soit vrai."),
    (Flip, "Mais des chercheurs ont retourné la question."),
    (AlreadyIn, "Imagine que tu es déjà branché. Que ta vie, celle-ci, est le rêve."),
    (WakeDoor, "On te propose de te réveiller, dans une réalité que tu ne connais pas."),
    (Stay, "Et là, beaucoup préfèrent rester."),
    (Cozy, "Alors peut-être que ce qu'on aime, ce n'est pas la vérité. C'est notre vie."),
    (Choice, "Et toi ? Tu te branches ? Ou tu te réveilles ?"),
]
