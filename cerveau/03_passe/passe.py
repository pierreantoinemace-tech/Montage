"""Partie 2 — « Tu vis dans le passé ». Règle : la preuve (test de l'horloge) est À LA FIN ; une barre de progression avec un drapeau
« PREUVE » rappelle tout du long qu'il faut rester."""
import math, os, random, sys
HERE = os.path.dirname(os.path.abspath(__file__))
for d in ('01_nez', '02_tache_aveugle', ''): sys.path.insert(0, os.path.join(HERE, '..', d))
import nez as N
import tache as TA
from nez import (W, H, SC, OW_, OH_, PX, PY, HERO, OTHER, FONT, clamp, back, hero, banded_sky, hill, striped_sun, plant, island, dots, BIG,
                 opath, rect, pop, CREAM, GOLD, sym, OUT, P, C, mix, rad, circle, ease, ease_out, qmark, brain, pov_world, skia, X)
from tache import clock, vignette, BGS, INK
import numpy as np, subprocess
from multiprocessing import Pool

WORK = os.path.join(HERE, '..', 'work', '03')
N.WORK = WORK; N.DUR = DUR = 34.3; FPS = 30
N.KEYS = {'VOIS', 'PASSÉ', 'FIN', 'PROUVE', 'CERVEAU', 'DIXIÈME', 'SECONDE', 'RETARD', 'BALLE', 'LANCE', 'TRICHE', 'DEVINE', 'PRÉDICTION',
          'RÉALITÉ', 'PREUVE', "L'HORLOGE", 'APPARAÎTRE', 'PREMIÈRE', 'LONGTEMPS', 'TROU', 'INVENTANT', 'TEMPS', 'PRÉSENT'}
WORDS = [w for w in N.load_words() if w[0] != 'DEUTS']
for w in WORDS: w[3] = w[0] in N.KEYS
N.WORDS = WORDS
X.WORDS = [(w, s, k) for w, s, e, k, b in WORDS]
N.CHUNKS = N.make_chunks()
PROOF = 19.75                                       # début de la preuve


# ---------------- scènes ----------------
def s_hook(cv, t, lt):
    """Ta vue… en différé : bandeau « DIFFÉRÉ -0,1 s », chrono qui tourne."""
    pov_world(cv, t, 0)
    vignette(cv)
    blink = (t * 2) % 1 < 0.6
    opath(cv, rect(70, 1450, 470, 100, 24), '#1A1426', 6)
    if blink: circle(cv, 120, 1500, 22, '#E8304A')
    f = skia.Font(FONT, 52); cv.drawString('DIFFÉRÉ -0,1 s', 160, 1519, f, P(CREAM))
    f2 = skia.Font(FONT, 44); tc = f'{int(t // 60):02d}:{int(t % 60):02d}:{int((t * 100) % 100):02d}'
    cv.drawString(tc, 760, 1519, f2, P(CREAM, 220))
    for k in range(4):                                           # coins de viseur
        x = 120 if k % 2 == 0 else W - 120; y = 620 if k < 2 else 1640; dx = 1 if k % 2 == 0 else -1; dy = 1 if k < 2 else -1
        cv.drawLine(x, y, x + dx * 90, y, P(CREAM, 255, stroke=8)); cv.drawLine(x, y, x, y + dy * 90, P(CREAM, 255, stroke=8))


def s_promesse(cv, t, lt):
    """« À la fin de cette vidéo, je te le prouve » : le perso montre un coffre fermé, marqué d'une horloge."""
    banded_sky(cv, BGS[3], -600, 1600, t); dots(cv, 31, 110, (-100, -100, W + 100, 1500), '#B8A8D0')
    yy = island(cv, PX, 1500, 760, '#2A3C4C', '#1C1630', '#251E3C', t, 0.4)
    x, y = 700, yy
    opath(cv, rect(x - 170, y - 230, 340, 230, 20), '#8A5A3A', 8); opath(cv, rect(x - 185, y - 300, 370, 90, 30), '#A06A44', 8)
    opath(cv, rect(x - 40, y - 250, 80, 90, 14), GOLD, 6)
    for k in range(3):
        u = (lt * 0.8 + k / 3) % 1; cv.drawCircle(x, y - 200, 120 + 200 * u, P(GOLD, int(160 * (1 - u)), stroke=6))
    clock(cv, x, y - 480, 90, t, False, 0)
    hero(cv, t, 300, yy - 300, 150, 'lidded', look=(0.9, -0.3), arms='reach')


def s_traitement(cv, t, lt):
    """« un dixième de seconde à traiter » : l'image voyage de l'œil au cerveau, chrono 0,00 -> 0,10."""
    cv.drawRect(BIG, P('#120A1C')); dots(cv, 33, 110, (-100, -100, W + 100, H), '#9A8AB8')
    TA.eye_icon(cv, 230, 1250, 150, False, t)
    brain(cv, 790, 1180, 230, t)
    p = skia.Path(); p.moveTo(380, 1250); p.cubicTo(480, 1450, 560, 1450, 640, 1300)
    cv.drawPath(p, P(OUT, 255, stroke=40)); cv.drawPath(p, P('#E0B890', 255, stroke=26))
    pm = skia.PathMeasure(p, False)
    for k in range(4):
        u = (lt * 0.45 + k / 4) % 1; pt = pm.getPosTan(u * pm.getLength())[0]
        opath(cv, rect(pt.x() - 34, pt.y() - 26, 68, 52, 8), '#8FC8C0', 5)
    v = min(0.10, lt * 0.03)
    opath(cv, rect(PX - 230, 1540, 460, 170, 40), '#EFE6D8', 8)
    f = skia.Font(FONT, 120); s = f'{v:0.2f} s'.replace('.', ','); tw = f.measureText(s); cv.drawString(s, PX - tw / 2, 1670, f, P(INK))


def s_retard(cv, t, lt):
    """« Tu vis toujours un peu en retard » : le perso court derrière son propre reflet, toujours un pas devant lui."""
    banded_sky(cv, BGS[1], -600, 1500, t); dots(cv, 35, 120, (-100, -100, W + 100, 1500), '#A8C8D0')
    hill(cv, 1500, 40, 0.006, t * 2, '#12262E', '#183038', t)
    x = PX - 120 + 30 * math.sin(t * 3)
    cv.saveLayerAlpha(None, 110); hero(cv, t + 0.3, x + 260, 1320, 150, 'open', look=(1, 0)); cv.restore()
    hero(cv, t, x, 1320, 150, 'open', look=(1, -0.2), arms='reach')
    f = skia.Font(FONT, 54); cv.drawString('LA RÉALITÉ', x + 140, 1000, f, P(CREAM, 200)); cv.drawString('TOI', x - 60, 1000, f, P(GOLD))


def ball_arc(v): return (100 + 760 * v, 1350 - 750 * math.sin(math.pi * v * 0.85))


def s_balle(cv, t, lt):
    """« comment tu rattrapes une balle qu'on te lance ? »"""
    banded_sky(cv, BGS[2], -600, 1700, t); dots(cv, 37, 110, (-100, -100, W + 100, 1500), '#D8C0E0')
    hill(cv, 1720, 30, 0.007, 1.0, '#2A1A3A', '#32203F', t, n=3)
    u = clamp(lt / 2.2); x, y = ball_arc(u)
    for j in range(1, 6): cv.drawCircle(*ball_arc(max(0, u - j * 0.03)), 50 - j * 6, P('#E88A5A', 60 - j * 10))
    opath(cv, skia.Path().addCircle(x, y, 52), '#E88A5A', 7)
    hero(cv, t, 860, 1560, 150, 'open', look=((x - 860) / 500, (y - 1500) / 600), arms='open')
    if lt > 1.4: qmark(cv, 700, 1100, 160 * min(1, (lt - 1.4) / 0.3), 10, GOLD)


def s_triche(cv, t, lt):
    """« Ton cerveau triche » : le cerveau, un œil malin, sort une carte de sa manche."""
    banded_sky(cv, BGS[0], -600, 2000, t); dots(cv, 39, 120, (-100, -100, W + 100, H), '#B8A8D0')
    brain(cv, PX, 1150, 330, t)
    for k in (-1, 1):
        cx = PX + k * 120
        if k == 1 and (t * 1.5) % 1 < 0.5:
            cv.drawLine(cx - 50, 1100, cx + 50, 1100, P(OUT, 255, stroke=14))
        else:
            opath(cv, skia.Path().addCircle(cx, 1100, 55), '#F4ECFF', 7); circle(cv, cx + 15, 1100, 22, OUT)
    sm = skia.Path(); sm.moveTo(PX - 110, 1240); sm.quadTo(PX + 20, 1330, PX + 140, 1220); cv.drawPath(sm, P(OUT, 255, stroke=14))
    u = pop(lt, 0.3, 0.4)
    if u > 0:
        cv.save(); cv.translate(PX + 380, 1500); cv.rotate(-20 + 10 * math.sin(t * 3)); cv.scale(u, u)
        opath(cv, rect(-80, -115, 160, 230, 16), '#F4EEE2', 7); sym(cv, 'star8', 0, 0, 50, t * 30, '#C0304A', t); cv.restore()


def s_prediction(cv, t, lt):
    """« Il devine où la balle va être… et il te montre sa prédiction » : trajectoire en pointillés, cible, et il l'attrape."""
    banded_sky(cv, BGS[2], -600, 1700, t); dots(cv, 41, 110, (-100, -100, W + 100, 1500), '#D8C0E0')
    hill(cv, 1720, 30, 0.007, 1.0, '#2A1A3A', '#32203F', t, n=3)
    pth = skia.Path(); pth.moveTo(*ball_arc(0))
    for k in range(1, 41): pth.lineTo(*ball_arc(k / 40))
    pa = P(GOLD, 230, stroke=8); pa.setPathEffect(skia.DashPathEffect.Make([24, 20], -lt * 80)); cv.drawPath(pth, pa)
    tx, ty = ball_arc(1)
    for j in range(3): cv.drawCircle(tx, ty, 60 + j * 25 + 6 * math.sin(t * 6), P(GOLD, 200 - j * 60, stroke=6))
    u = clamp(lt / 2.3); x, y = ball_arc(u)
    opath(cv, skia.Path().addCircle(x, y, 52), '#E88A5A', 7)
    hero(cv, t, 860, 1560, 150, 'open' if u < 1 else 'lidded', look=((x - 860) / 500, (y - 1500) / 600), arms='reach' if u > 0.7 else 'open')
    if u >= 1:
        for k in range(8): g = k * math.pi / 4; sym(cv, 'star4', tx + math.cos(g) * 110, ty + math.sin(g) * 110, 24, 0, CREAM, t)


def s_pasreal(cv, t, lt):
    """« Pas la réalité » : la balle que tu vois, et la vraie (fantôme) déjà plus loin."""
    TA.s_passe(cv, t, lt + 1.0)


def s_preuve(cv, t, lt):
    """LA PREUVE (19,75 -> 26,6) : fond calme et fixe ; l'horloge surgit sur le côté, la trotteuse saute une fois par seconde."""
    banded_sky(cv, BGS[0], -600, 2200, 0)
    a = clamp((lt - 0.0) / 0.3)
    f = skia.Font(FONT, 64)
    for i, txt in enumerate(('GARDE LES YEUX ICI', '↓')):
        if i == 1: continue
        tw = f.measureText(txt); cv.drawString(txt, PX - 380 - tw / 2 + 380, 1010, f, P(CREAM, int(200 * a * (1 if lt < 2.4 else max(0, 1 - (lt - 2.4) / 0.3)))))
    if lt < 2.7:
        circle(cv, 270, 1250, 26, GOLD); cv.drawCircle(270, 1250, 50 + 8 * math.sin(t * 6), P(GOLD, 200, stroke=5))
    app = 2.15                                                   # l'horloge apparaît d'un coup sur le côté
    if lt >= app:
        x, y, r = 780, 1420, 230
        opath(cv, skia.Path().addCircle(x, y, r), '#EFE6D8', 10)
        for k in range(60):
            g = k * math.pi / 30 - math.pi / 2; l = 0.14 if k % 5 == 0 else 0.06
            cv.drawLine(x + math.cos(g) * r * (0.92 - l), y + math.sin(g) * r * (0.92 - l), x + math.cos(g) * r * 0.92, y + math.sin(g) * r * 0.92, P(INK, 255, stroke=7 if k % 5 == 0 else 3))
        sec = int(lt - app)                                      # saut net chaque seconde
        g = sec * math.pi / 30 - math.pi / 2 + math.pi / 3
        cv.drawLine(x, y, x + math.cos(g) * r * 0.85, y + math.sin(g) * r * 0.85, P('#C0304A', 255, stroke=8))
        cv.drawLine(x, y, x + math.cos(-math.pi / 2 + 0.9) * r * 0.5, y + math.sin(-math.pi / 2 + 0.9) * r * 0.5, P(INK, 255, stroke=16))
        cv.drawLine(x, y, x + math.cos(-math.pi / 2 + 2.6) * r * 0.7, y + math.sin(-math.pi / 2 + 2.6) * r * 0.7, P(INK, 255, stroke=11))
        circle(cv, x, y, 16, '#C0304A')


def s_bouche(cv, t, lt):
    """« C'est ton cerveau qui bouche le trou… en inventant du temps » : il manque un morceau à l'horloge, le cerveau le repeint."""
    banded_sky(cv, BGS[3], -600, 1500, t); dots(cv, 43, 120, (-100, -100, W + 100, 1500), '#B8A8D0')
    clock(cv, PX, 1150, 320, t, True, ease(clamp((lt - 0.8) / 1.2)))
    brain(cv, 840, 1650, 130, t)
    if 0.8 < lt < 2.0:
        u = (lt - 0.8) / 1.2; bx = PX + 120 + 150 * u; by = 1050 + 80 * math.sin(u * 15)
        cv.save(); cv.translate(bx, by); cv.rotate(-35)
        opath(cv, rect(-12, -150, 24, 140, 10), '#C8946A', 5); opath(cv, rect(-20, -20, 40, 50, 10), GOLD, 5); cv.restore()


def s_present(cv, t, lt):
    """« Tu ne vis pas dans le présent » : une ligne du temps ; le drapeau « PRÉSENT » est devant, le perso juste derrière."""
    banded_sky(cv, BGS[1], -600, 1500, t); dots(cv, 45, 120, (-100, -100, W + 100, 1500), '#A8C8D0')
    y = 1560
    cv.drawLine(-100, y, W + 100, y, P(OUT, 255, stroke=26)); cv.drawLine(-100, y, W + 100, y, P(CREAM, 255, stroke=12))
    for k in range(12): cv.drawLine(k * 100 - (t * 60) % 100, y - 30, k * 100 - (t * 60) % 100, y + 30, P(CREAM, 255, stroke=6))
    fx = 720; cv.drawLine(fx, y, fx, y - 330, P(OUT, 255, stroke=12))
    opath(cv, rect(fx, y - 330, 260, 110, 12), GOLD, 6)
    f = skia.Font(FONT, 48); cv.drawString('PRÉSENT', fx + 20, y - 255, f, P(INK))
    hero(cv, t, 440, y - 330, 130, 'open', look=(1.0, -0.2), arms='reach')


def s_devine(cv, t, lt):
    """« Tu vis dans ce que ton cerveau devine » : le perso, troisième œil brillant, entouré de ses « futurs » possibles."""
    banded_sky(cv, ['#1E1838', '#2A2048', '#3A2A58', '#4C3466', '#5E4072', '#704C7C'], -600, 1600, t)
    dots(cv, 47, 120, (-100, -100, W + 100, 1500), '#D8C8E0'); striped_sun(cv, PX, 700, 220, t, ['#9A6A8A', '#AA7A92', '#BC8C9A'])
    hill(cv, 1700, 40, 0.006, 0.8, '#3A2E58', '#433664', t)
    for k in range(4):
        g = k * math.pi / 2 + t * 0.4
        cv.saveLayerAlpha(None, 70); hero(cv, t + k, PX + math.cos(g) * 330, 1300 + math.sin(g) * 120, 110, 'open', look=(0, -0.3), seed=k + 2); cv.restore()
    hero(cv, t, PX, 1350, 170, 'lidded', look=(0, -0.5))


SCENES = [(0.0, s_hook, None), (2.6, s_promesse, 'pan_r'), (4.95, s_traitement, 'pan_d'), (8.8, s_retard, 'pan_l'), (11.1, s_balle, 'pan_u'),
          (13.8, s_triche, 'pan_r'), (15.15, s_prediction, 'pan_l'), (18.6, s_pasreal, 'pan_d'), (PROOF, s_preuve, 'pan_u'),
          (26.6, s_bouche, 'pan_r'), (29.85, s_present, 'pan_d'), (31.4, s_devine, 'pan_u')]
N.SCENES = SCENES; TW = N.TW

_ds = TA._ds                                      # draw_scene d origine de nez.py
def draw_scene(i, cv, t):
    if SCENES[i][1] is s_preuve:                                 # pendant la preuve : aucune dérive de caméra
        s0, fn, kind = SCENES[i]; fn(cv, t, max(0.0, t - s0)); return
    _ds(i, cv, t)
N.draw_scene = draw_scene


def progress(cv, t):
    """Barre de progression avec le drapeau « PREUVE » : on sait qu'il y a quelque chose à voir à la fin."""
    if t > PROOF + 0.3: return
    y = 1850; x0, x1 = 80, W - 80; fx = x0 + (x1 - x0) * PROOF / DUR
    cv.drawRoundRect(skia.Rect.MakeLTRB(x0, y - 9, x1, y + 9), 9, 9, P('#000000', 120))
    cv.drawRoundRect(skia.Rect.MakeLTRB(x0, y - 9, x0 + (x1 - x0) * t / DUR, y + 9), 9, 9, P(GOLD))
    cv.drawLine(fx, y, fx, y - 90, P(OUT, 255, stroke=10)); cv.drawLine(fx, y, fx, y - 90, P(CREAM, 255, stroke=5))
    opath(cv, rect(fx, y - 92, 190, 58, 10), '#C0304A', 5)
    f = skia.Font(FONT, 36); cv.drawString('PREUVE', fx + 18, y - 50, f, P(CREAM))


def hook_title(cv, t):
    a = 1.0 if t < 2.3 else max(0.0, 1 - (t - 2.3) / 0.3)
    for i, (txt, col, size) in enumerate((('TOUT CE QUE TU VOIS', CREAM, 84), ("S'EST DÉJÀ PASSÉ", GOLD, 104))):
        f = skia.Font(FONT, size); tw = f.measureText(txt)
        y = 230 + i * 120
        o = P(OUT, int(255 * a), stroke=size * 0.18); o.setStrokeJoin(skia.Paint.kRound_Join)
        cv.drawString(txt, W / 2 - tw / 2 + 3, y + 6, f, o); cv.drawString(txt, W / 2 - tw / 2, y, f, o)
        cv.drawString(txt, W / 2 - tw / 2, y, f, P(col, int(255 * a)))


EVENTS = [(0.0, 'impact', 0.6), (0.0, 'beep', 0.6), (0.5, 'beep', 0.5), (1.0, 'beep', 0.5), (1.5, 'beep', 0.5), (2.9, 'ding', 0.6), (3.4, 'sparkle', 0.5)]
for s0, _, kind in SCENES[1:]:
    if kind in N.DIRS: EVENTS.append((s0 - TW + 0.05, 'whoosh', 0.5))
EVENTS += [(s, 'pop', 0.22) for w, s, e, k, b in WORDS if k and not (PROOF < s < 26.6)]
EVENTS += [(5.3 + k * 0.55, 'click', 0.4) for k in range(5)] + [(9.0, 'whoosh', 0.3), (11.2, 'rise', 0.5), (12.6, 'boing', 0.6),
           (14.1, 'ting', 0.6), (15.5, 'rise', 0.5), (17.45, 'impact', 0.5), (17.5, 'sparkle', 0.6), (18.9, 'powerdown', 0.4)]
APP = PROOF + 2.15
EVENTS += [(APP, 'pop', 0.8)] + [(APP + k, 'click', 0.9) for k in range(1, 5)]     # tic de la trotteuse, une fois par seconde
EVENTS += [(27.4, 'scrub', 0.8), (28.6, 'sparkle', 0.6), (30.0, 'click', 0.4), (31.5, 'rise', 0.4), (32.8, 'ding', 0.9)]


def frame(fi):
    t = fi / FPS
    surf = skia.Surface(OW_, OH_); cv = surf.getCanvas(); cv.scale(SC, SC)
    calm = PROOF <= t < 26.4
    cv.save()
    if not calm:
        cv.translate(PX, PY); cv.rotate(0.3 * math.sin(t * 0.35)); cv.scale(1.03, 1.03); cv.translate(-PX + 8 * math.sin(t * 0.4), -PY + 8 * math.cos(t * 0.33))
    N.scene(cv, t); cv.restore()
    cv.drawRect(skia.Rect.MakeWH(W, H), P(shader=rad(W / 2, H / 2, 1250, [C('#000000', 0), C('#000000', 0), C('#000000', 70)], [0, 0.7, 1])))
    if t < 2.6: hook_title(cv, t)
    progress(cv, t)
    N.draw_text(cv, t)
    return surf.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType).tobytes()


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--preview':
        from PIL import Image
        ims = []
        for ts in sys.argv[2].split(','):
            arr = np.frombuffer(frame(int(float(ts) * FPS)), np.uint8).reshape(OH_, OW_, 4)
            ims.append(Image.fromarray(arr[..., :3]).resize((270, 480), Image.LANCZOS))
        m = Image.new('RGB', (270 * min(6, len(ims)), 480 * ((len(ims) + 5) // 6)))
        for k, im in enumerate(ims): m.paste(im, ((k % 6) * 270, (k // 6) * 480))
        m.save(sys.argv[3]); sys.exit()
    import sfx
    sfx.mix(os.path.join(WORK, 'voice.wav'), EVENTS, os.path.join(WORK, 'mix.wav'))
    out = os.path.join(HERE, 'passe_4k.mp4'); hd = os.path.join(HERE, 'passe_1080p.mp4')
    n = int(DUR * FPS)
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', f'{OW_}x{OH_}', '-r', str(FPS), '-i', '-',
                           '-i', os.path.join(WORK, 'mix.wav'),
                           '-filter_complex', '[0:v]format=yuv420p,split=2[v4][vh];[vh]scale=1080:1920:flags=lanczos[v1]',
                           '-map', '[v4]', '-map', '1:a', '-c:v', 'libx264', '-profile:v', 'high', '-level:v', '5.1', '-preset', 'slow', '-crf', '15',
                           '-maxrate', '25M', '-bufsize', '50M', '-c:a', 'aac', '-b:a', '256k', '-t', str(DUR), '-movflags', '+faststart', out,
                           '-map', '[v1]', '-map', '1:a', '-c:v', 'libx264', '-profile:v', 'high', '-level:v', '4.2', '-preset', 'slow', '-crf', '14',
                           '-maxrate', '20M', '-bufsize', '40M', '-c:a', 'aac', '-b:a', '256k', '-t', str(DUR), '-movflags', '+faststart', hd],
                          stdin=subprocess.PIPE)
    with Pool(4) as pool:
        for i, b in enumerate(pool.imap(frame, range(n), chunksize=2)):
            ff.stdin.write(b)
            if i % 300 == 0: print(i, '/', n, flush=True)
    ff.stdin.close(); ff.wait()
    print('ok')
