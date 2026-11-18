"""Primitives de dessin vectoriel (skia) pour le style « flat cosmic explainer »."""
import math, random
import skia

W, H = 1920, 1080


def C(hexstr, a=255):
    h = hexstr.lstrip('#')
    return skia.ColorSetARGB(int(max(0, min(255, a))), int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def mix(c1, c2, t):
    a = [int(c1.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4)]
    b = [int(c2.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4)]
    return '#%02x%02x%02x' % tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def P(color='#ffffff', a=255, blur=0, stroke=0, shader=None, cap_round=True):
    p = skia.Paint(AntiAlias=True)
    p.setColor(C(color, a))
    if shader is not None:
        p.setShader(shader)
        p.setAlphaf(a / 255.0)
    if blur:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    if stroke:
        p.setStyle(skia.Paint.kStroke_Style)
        p.setStrokeWidth(stroke)
        if cap_round:
            p.setStrokeCap(skia.Paint.kRound_Cap)
            p.setStrokeJoin(skia.Paint.kRound_Join)
    return p


def lin(x0, y0, x1, y1, colors, pos=None):
    return skia.GradientShader.MakeLinear([(x0, y0), (x1, y1)], [C(c) if isinstance(c, str) else c for c in colors], pos)


def rad(x, y, r, colors, pos=None):
    return skia.GradientShader.MakeRadial((x, y), r, [C(c) if isinstance(c, str) else c for c in colors], pos)


def bg_lin(cv, top, bottom, angle_h=False):
    sh = lin(0, 0, (W if angle_h else 0), (0 if angle_h else H), [top, bottom])
    cv.drawRect(skia.Rect.MakeXYWH(-400, -400, W + 800, H + 800), P(shader=sh))


def bg_rad(cv, x, y, r, inner, outer):
    cv.drawRect(skia.Rect.MakeXYWH(-400, -400, W + 800, H + 800), P(outer))
    cv.drawRect(skia.Rect.MakeXYWH(-400, -400, W + 800, H + 800), P(shader=rad(x, y, r, [inner, C(outer, 0) if False else outer])))


def glow(cv, x, y, r, color, a=200):
    cv.drawCircle(x, y, r, P(shader=rad(x, y, r, [C(color, a), C(color, a * 0.35), C(color, 0)], [0, 0.4, 1])))


def circle(cv, x, y, r, color, a=255, **kw):
    cv.drawCircle(x, y, r, P(color, a, **kw))


def oval(cv, x, y, rx, ry, color, a=255, **kw):
    cv.drawOval(skia.Rect.MakeLTRB(x - rx, y - ry, x + rx, y + ry), P(color, a, **kw))


def rrect(cv, x, y, w, h, r, color, a=255, **kw):
    cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), r, r), P(color, a, **kw))


def poly(cv, pts, color, a=255, **kw):
    p = skia.Path()
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    p.close()
    cv.drawPath(p, P(color, a, **kw))


def blob(cv, x, y, r, color, a=255, n=9, seed=0, wob=0.25, t=0.0, **kw):
    """Forme organique (nuage, continent) via courbes lissées."""
    rnd = random.Random(seed)
    radii = [r * (1 - wob + 2 * wob * rnd.random()) for _ in range(n)]
    phs = [rnd.random() * 6.28 for _ in range(n)]
    pts = []
    for i in range(n):
        ang = i / n * 2 * math.pi
        rr = radii[i] * (1 + 0.04 * math.sin(t * 1.3 + phs[i]))
        pts.append((x + math.cos(ang) * rr, y + math.sin(ang) * rr))
    p = skia.Path()
    mids = [((pts[i][0] + pts[(i + 1) % n][0]) / 2, (pts[i][1] + pts[(i + 1) % n][1]) / 2) for i in range(n)]
    p.moveTo(*mids[-1])
    for i in range(n):
        p.quadTo(pts[i][0], pts[i][1], mids[i][0], mids[i][1])
    p.close()
    cv.drawPath(p, P(color, a, **kw))


def cloud(cv, x, y, s, color, a=255, shade=None):
    """Nuage cartoon : grappe de cercles sur une base plate."""
    parts = [(-1.0, 0.15, 0.55), (-0.45, -0.25, 0.75), (0.25, -0.35, 0.85), (0.9, 0.05, 0.6), (0.0, 0.2, 0.7)]
    if shade:
        for dx, dy, r in parts:
            circle(cv, x + dx * s, y + dy * s + s * 0.12, r * s, shade, a)
    for dx, dy, r in parts:
        circle(cv, x + dx * s, y + dy * s, r * s, color, a)


class Stars:
    def __init__(self, n, seed=1, area=(-200, -200, W + 200, H + 200), rmin=1.0, rmax=3.2, colors=('#ffffff',)):
        rnd = random.Random(seed)
        x0, y0, x1, y1 = area
        self.s = [(rnd.uniform(x0, x1), rnd.uniform(y0, y1), rnd.uniform(rmin, rmax) ** 1.0 if rnd.random() > 0.08 else rmax * 1.6,
                   rnd.uniform(0.5, 3.0), rnd.uniform(0, 6.28), rnd.choice(colors)) for _ in range(n)]

    def draw(self, cv, t, a=255, drift=(0, 0)):
        for x, y, r, f, ph, col in self.s:
            k = 0.55 + 0.45 * math.sin(t * f + ph)
            xx, yy = x + drift[0] * t, y + drift[1] * t
            if r > 3.5:
                glow(cv, xx, yy, r * 5, col, 90 * k)
                # étoile à 4 branches
                p = P(col, a * k, stroke=1.6)
                cv.drawLine(xx - r * 3, yy, xx + r * 3, yy, p)
                cv.drawLine(xx, yy - r * 3, xx, yy + r * 3, p)
            circle(cv, xx, yy, r, col, a * k)


def label(cv, x, y, text, size=26, color='#ffffff', a=230, font=None, box=True):
    """Petit libellé encadré façon infographie (comme « ANDROMEDA » dans les vidéos de réf.)."""
    f = skia.Font(font, size)
    f.setEdging(skia.Font.Edging.kAntiAlias)
    w = f.measureText(text)
    pad = size * 0.45
    if box:
        cv.drawRect(skia.Rect.MakeXYWH(x - w / 2 - pad, y - size * 0.95, w + 2 * pad, size * 1.4), P(color, a * 0.9, stroke=2.2, cap_round=False))
    cv.drawString(text, x - w / 2, y, f, P(color, a))


def ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def ease_out(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


# ------------------------------------------------------------------ personnages
SKIN = ['#F2A97E', '#C98058', '#8A5236']


def person_back(cv, x, y, s, shirt='#3C4CC8', pants='#1E1F5C', hair='#2A1A14', skin='#C98058', rim=None):
    """Personnage vu de dos, debout. (x,y) = pieds."""
    if rim:
        sc = 1.0
        cv.save()
        cv.translate(x, y)
        _person_shape(cv, 0, 0, s * 1.04, rim, rim, rim, rim, a=200, blur=6)
        cv.restore()
    _person_shape(cv, x, y, s, shirt, pants, hair, skin)


def _person_shape(cv, x, y, s, shirt, pants, hair, skin, a=255, blur=0):
    kw = dict(blur=blur) if blur else {}
    rrect(cv, x - 0.22 * s, y - 0.95 * s, 0.19 * s, 0.95 * s, 0.09 * s, pants, a, **kw)
    rrect(cv, x + 0.03 * s, y - 0.95 * s, 0.19 * s, 0.95 * s, 0.09 * s, pants, a, **kw)
    rrect(cv, x - 0.33 * s, y - 1.75 * s, 0.66 * s, 0.95 * s, 0.22 * s, shirt, a, **kw)
    rrect(cv, x - 0.46 * s, y - 1.68 * s, 0.17 * s, 0.8 * s, 0.085 * s, shirt, a, **kw)
    rrect(cv, x + 0.29 * s, y - 1.68 * s, 0.17 * s, 0.8 * s, 0.085 * s, shirt, a, **kw)
    circle(cv, x - 0.375 * s, y - 0.86 * s, 0.085 * s, skin, a, **kw)
    circle(cv, x + 0.375 * s, y - 0.86 * s, 0.085 * s, skin, a, **kw)
    rrect(cv, x - 0.08 * s, y - 1.86 * s, 0.16 * s, 0.16 * s, 0.05 * s, skin, a, **kw)
    circle(cv, x, y - 2.08 * s, 0.27 * s, skin, a, **kw)
    circle(cv, x, y - 2.14 * s, 0.27 * s, hair, a, **kw)
    oval(cv, x, y - 2.0 * s, 0.26 * s, 0.16 * s, hair, a, **kw)
