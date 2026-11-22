"""Tests de DA en format vertical 1080x1920 (TikTok). Génère des images fixes à valider."""
import math, os, random, sys, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
for d in ('../etoiles', '../calendrier', '../temps', '../profil'):
    sys.path.insert(0, os.path.join(HERE, d))
import lib
lib.W, lib.H = 1080, 1920          # format vertical, à définir AVANT d'importer le reste
import skia
from lib import *
from kit import Stars, sparkle, neon
from mg import *
_s = importlib.util.spec_from_file_location('pfp_dark', os.path.join(HERE, '..', 'profil', 'pfp_dark.py'))
pd = importlib.util.module_from_spec(_s); _s.loader.exec_module(pd)
OLD = pd.OLD
W, H = 1080, 1920
FONT = skia.Typeface.MakeFromFile(os.path.join(HERE, '..', 'etoiles', 'fonts', 'Rubik-700.ttf'))
HERO = dict(skin='#7AC8D8', hair='#14304A', robe='#3A0E5A')


def night(cv, seed, top='#05020F', mid='#14082E', bottom='#2A0E3A'):
    cv.drawRect(skia.Rect.MakeWH(W, H), P(shader=lin(0, 0, 0, H, [top, mid, bottom])))
    rnd = random.Random(seed)
    for _ in range(3500):
        circle(cv, rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(0.6, 1.8), '#FFFFFF', 16)
    Stars(220, seed, area=(0, 0, W, H), rmax=2.4, colors=('#ffffff', '#BFE6FF', '#FFB0E8', '#B98CFF')).draw(cv, 0.7, 230)


def ribbons(cv, seed, y0, n=4, spread=140):
    rnd = random.Random(seed)
    cols = ['#5A0E5A', '#1E3A6A', '#3A0E6A', '#0E4A5A']
    for i in range(n):
        y = y0 + i * spread; ph = rnd.uniform(0, 6)
        top, bot = [], []
        for x in range(-100, W + 140, 30):
            yy = y + 50 * math.sin(x * 0.006 + ph); ww = 60 * (0.6 + 0.4 * math.sin(x * 0.01 + ph))
            top.append((x, yy - ww / 2)); bot.append((x, yy + ww / 2))
        p = skia.Path(); p.moveTo(*top[0])
        for q in top[1:]: p.lineTo(*q)
        for q in reversed(bot): p.lineTo(*q)
        p.close()
        cv.drawPath(p, P(shader=lin(0, y, W, y, [cols[i % 4], cols[(i + 2) % 4]]), a=140))
        cv.drawPath(p, P(OLD, 140, stroke=4))


def word(cv, text, y=None, size=170):
    """Gros mot central (crème + halo sombre), placé un peu au-dessus du centre."""
    y = y or H * 0.40
    f = skia.Font(FONT, size)
    w = f.measureText(text)
    if w > 820:
        f.setSize(size * 820 / w); w = f.measureText(text); size = size * 900 / w * w / 900
    x = (W - w) / 2
    cap = f.getSize() * 0.7
    cv.drawString(text, x, y + cap / 2 + f.getSize() * 0.04, f, P('#0A0420', 170, blur=f.getSize() * 0.09))
    cv.drawString(text, x, y + cap / 2 + f.getSize() * 0.04, f, P('#0A0420', 90, blur=f.getSize() * 0.25))
    cv.drawString(text, x, y + cap / 2, f, P('#F0EBBE'))


def lantern(cv, x, y, r, col):
    glow(cv, x, y, r * 2.6, col, 150)
    ofill(cv, pcircle(x, y, r), mix(col, '#FFFFFF', 0.4), ol=OLD, w=4)
    circle(cv, x, y - r * 0.15, r * 0.3, OLD); oval(cv, x, y + r * 0.45, r * 0.45, r * 0.3, OLD)


def ui_overlay(cv):
    """Gabarit de l'interface TikTok (zones masquées), pour vérifier les zones de sécurité."""
    cv.drawRect(skia.Rect.MakeXYWH(0, 0, W, 150), P('#FF3B5C', 40))
    cv.drawRect(skia.Rect.MakeXYWH(0, H - 420, W, 420), P('#FF3B5C', 40))
    cv.drawRect(skia.Rect.MakeXYWH(W - 150, 700, 150, 800), P('#FF3B5C', 40))
    for i, y in enumerate((800, 960, 1110, 1260, 1410)):
        cv.drawCircle(W - 75, y, 40, P('#FFFFFF', 150))
    label(cv, 300, H - 300, '@ton_compte', 34, color='#FFFFFF', font=FONT, box=False)
    label(cv, 380, H - 240, 'légende de la vidéo… #hopecore', 28, color='#FFFFFF', a=200, font=FONT, box=False)
    label(cv, W / 2, 95, 'Abonnements   Pour toi', 32, color='#FFFFFF', a=220, font=FONT, box=False)


def frame_portrait(cv):
    night(cv, 1)
    ribbons(cv, 2, 220)
    for i, (a, r, c) in enumerate([(-2.5, 380, '#FFB0E8'), (-1.9, 420, '#BFE6FF'), (-1.1, 400, '#FFE6A0'), (-0.5, 360, '#C8A8FF')]):
        lantern(cv, W / 2 + math.cos(a) * r, 700 + math.sin(a) * r, 34, c)
    pd.dreamer(cv, W / 2, 1180, 300, skin=HERO['skin'], hair=HERO['hair'], robe=HERO['robe'], eyes='open', third_eye=True,
               seed=5, t=1.2, arms='heart', look=(0.6, -0.8))
    word(cv, 'AMIS')


def frame_city(cv):
    night(cv, 3, '#02010A', '#0E0A2A', '#24082E')
    rnd = random.Random(4)
    wins = []
    x = -40
    while x < W + 40:
        w = rnd.uniform(140, 240); h = rnd.uniform(500, 1100)
        ofill(cv, prr(x, H - h, w, h + 40, 8), '#140A2E', ol=OLD, w=4)
        for wy in range(int(H - h + 40), H - 60, 80):
            for wx in range(int(x + 24), int(x + w - 40), 60):
                if rnd.random() < 0.4:
                    wins.append((wx, wy))
                    cv.drawRect(skia.Rect.MakeXYWH(wx, wy, 34, 44), P('#FFE680', 220))
        x += w + rnd.uniform(8, 20)
    (x0, y0), (x1, y1) = wins[10], wins[-25]
    neon(cv, [(x0 + 17 + (x1 - x0) * j / 24, y0 + 22 + (y1 - y0) * j / 24 - 260 * math.sin(j / 24 * math.pi)) for j in range(25)], '#FFE680', w=5, glow_w=18)
    glow(cv, x1 + 17, y1 + 22, 120, '#FFE680', 255)
    word(cv, 'RÉPONDE')


def frame_phone(cv):
    night(cv, 5, '#000000', '#05020F', '#140A2A')
    pd.dreamer(cv, W / 2, 1020, 280, skin=HERO['skin'], hair=HERO['hair'], robe=HERO['robe'], eyes='open', third_eye=False,
               seed=5, t=1.0, arms='scroll', look=(0.3, 0.9))
    glow(cv, W / 2, 1300, 400, '#5AD7FF', 80)
    for i, (n, y) in enumerate([('Léa', 260), ('Karim', 330), ('Inès', 400)]):
        ofill(cv, prr(120, y - 40, 360, 56, 28), '#2A3A6A', a=180, ol=OLD, w=3)
        label(cv, 300, y - 2, n, 26, color='#BFE6FF', font=FONT, box=False)
    word(cv, 'CONTACTS', y=H * 0.40)


if __name__ == '__main__':
    out = os.path.join(HERE, 'tests')
    os.makedirs(out, exist_ok=True)
    for name, fn in (('1_portrait', frame_portrait), ('2_ville', frame_city), ('3_telephone', frame_phone)):
        for ui in (False, True):
            surf = skia.Surface(W, H); cv = surf.getCanvas()
            fn(cv)
            cv.drawRect(skia.Rect.MakeWH(W, H), P(shader=rad(W / 2, H / 2, 1300, [C('#000000', 0), C('#000000', 0), C('#000000', 110)], [0, 0.6, 1])))
            if ui:
                ui_overlay(cv)
            surf.makeImageSnapshot().save(os.path.join(out, f'{name}{"_gabarit" if ui else ""}.png'))
    print('ok')
