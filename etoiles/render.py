"""Rendu de la vidéo : un mot à la fois en mode « différence », illustrations animées coupées sur la voix.
Usage : python render.py [--preview t1,t2,...] [--out out.mp4]"""
import json, math, os, random, re, subprocess, sys, unicodedata, difflib
from multiprocessing import Pool
import numpy as np
import skia
import lib
from lib import W, H, P

ENGINE = os.path.dirname(os.path.abspath(__file__))
HERE = os.environ.get('PROJECT', ENGINE)
sys.path.insert(0, HERE)
import scenes
FPS = getattr(scenes, 'STYLE', {}).get('fps', 30)
FONT_PATH = os.path.join(ENGINE, 'fonts', 'Rubik-700.ttf')
TYPE = skia.Typeface.MakeFromFile(FONT_PATH)
scenes.FONT = TYPE
SS = 1.5      # sur-échantillonnage du décor statique
M = 160       # marge du décor statique (pour zoom/pan/shake)


def norm(w):
    w = unicodedata.normalize('NFD', w.lower())
    w = ''.join(c for c in w if unicodedata.category(c) != 'Mn')
    return re.sub(r"[^a-z0-9']", '', w)


def build_timeline():
    words = json.load(open(os.path.join(HERE, 'words.json')))
    toks, seg_of = [], []
    for si, (_, text) in enumerate(scenes.SEGMENTS):
        for tk in text.split():
            if not re.search(r'\w', tk):
                continue
            toks.append(tk); seg_of.append(si)
    a = [norm(t) for t in toks]
    b = [norm(w[0]) for w in words]
    times = [None] * len(toks)
    sm = difflib.SequenceMatcher(a=a, b=b, autojunk=False)
    for blk in sm.get_matching_blocks():
        for k in range(blk.size):
            times[blk.a + k] = words[blk.b + k][1]
    # remplissage des trous (mots mal transcrits) par interpolation
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op in ('replace', 'delete'):
            t0 = words[j1 - 1][2] if j1 > 0 else 0.0
            t1 = words[j2][1] if j2 < len(words) else words[-1][2]
            if op == 'replace' and j2 > j1:
                t0, t1 = words[j1][1], words[j2 - 1][2]
            n = i2 - i1
            for k in range(n):
                times[i1 + k] = t0 + (t1 - t0) * k / n
    for i in range(1, len(times)):
        if times[i] < times[i - 1] + 0.06:
            times[i] = times[i - 1] + 0.06
    end = words[-1][2] + 1.4
    disp = [re.sub(r"[,.;:!?]+$", '', t).upper().replace('Œ', 'Œ') for t in toks]
    seg_start = {}
    for i, si in enumerate(seg_of):
        seg_start.setdefault(si, times[i] if i else 0.0)
    seg_start[0] = 0.0
    segs = []
    for si in range(len(scenes.SEGMENTS)):
        t0 = seg_start[si]
        t1 = seg_start.get(si + 1, end)
        segs.append((t0, t1))
    return disp, times, segs, end


DISP, TIMES, SEGS, END = build_timeline()
_cache = {}


def get_scene(si):
    if si not in _cache:
        sc = scenes.SEGMENTS[si][0]()
        surf = skia.Surface(int((W + 2 * M) * SS), int((H + 2 * M) * SS))
        cv = surf.getCanvas()
        cv.scale(SS, SS); cv.translate(M, M)
        sc.static(cv)
        sc._img = surf.makeImageSnapshot()
        if len(_cache) >= 3:
            _cache.pop(next(iter(_cache)))
        _cache[si] = sc
    return _cache[si]


def current_word(t):
    idx = None
    for i, ts in enumerate(TIMES):
        if ts <= t:
            idx = i
        else:
            break
    return idx


STYLE = getattr(scenes, 'STYLE', {})
GRAIN = None
if STYLE.get('grain'):
    _r = np.random.default_rng(0)
    GRAIN = [(_r.normal(0, STYLE['grain'], (H, W, 1))).astype(np.int16) for _ in range(6)]


def draw_word(cv, text, age=1.0, fi=0, surf=None):
    size = STYLE.get('size', 150)
    maxw = STYLE.get('maxw', 1720)
    font = skia.Font(TYPE, size)
    font.setEdging(skia.Font.Edging.kAntiAlias)
    w = font.measureText(text)
    if w > maxw:
        size = size * maxw / w
        font.setSize(size)
        w = font.measureText(text)
    cap = size * 0.70
    x, y = (W - w) / 2, H / 2 + cap / 2
    p = P(STYLE.get('color', '#ffffff'))
    p.setBlendMode(skia.BlendMode.kExclusion if STYLE.get('exclusion') else skia.BlendMode.kDifference)
    if STYLE.get('readable') and surf is not None:
        # luminance moyenne du décor derrière le mot
        x0, y0 = max(0, int(x)), max(0, int(y - cap * 1.1))
        x1, y1 = min(W, int(x + w)), min(H, int(y + cap * 0.3))
        arr = surf.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)[y0:y1:4, x0:x1:4, :3].astype(np.float32) / 255
        lum = arr @ np.array([0.2126, 0.7152, 0.0722], np.float32)
        L = float(lum.mean()); spread = float(lum.std())
        if L < 0.72:
            sh = P('#0A0420', 170, blur=size * 0.09)
            cv.drawString(text, x, y + size * 0.04, font, sh)
            cv.drawString(text, x, y + size * 0.04, font, P('#0A0420', 90, blur=size * 0.25))
        if 0.30 < L < 0.72 or spread > 0.22:
            p = P(STYLE.get('color', '#ffffff'))  # crème plein : toujours lisible
    glitch = STYLE.get('glitch') and age < 0.083
    if not glitch:
        cv.drawString(text, x, y, font, p)
        return
    # glitch d'apparition : tranches horizontales décalées + fantôme coloré
    rnd = random.Random(fi * 7 + len(text))
    top = y - cap * 1.15
    hgt = cap * 1.4
    n = 6
    for k in range(n):
        y0 = top + hgt * k / n
        cv.save()
        cv.clipRect(skia.Rect.MakeLTRB(0, y0, W, y0 + hgt / n + 1))
        dx = rnd.choice([0, 0, rnd.uniform(-38, 38)])
        cv.drawString(text, x + dx, y, font, p)
        cv.restore()
    g = P(rnd.choice(['#2DE2E6', '#FF4F81', '#B6FF3B']), 150)
    g.setBlendMode(skia.BlendMode.kExclusion)
    cv.save()
    y0 = top + hgt * rnd.uniform(0.1, 0.7)
    cv.clipRect(skia.Rect.MakeLTRB(0, y0, W, y0 + hgt * 0.22))
    cv.drawString(text, x + rnd.uniform(-60, 60), y, font, g)
    cv.restore()


def scene_layer(si, t, fi, extra_zoom=0.0):
    """Dessine la scène si au temps global t (sans texte) et renvoie une image."""
    t0, t1 = SEGS[si]
    lt, d = t - t0, t1 - t0
    sc = get_scene(si)
    surf = skia.Surface(W, H)
    cv = surf.getCanvas()
    cv.clear(skia.ColorBLACK)
    u = max(0.0, min(1.0, lt / max(d, 0.1)))
    if STYLE.get('float'):
        u = lib.ease(u)
    z = sc.zoom[0] + (sc.zoom[1] - sc.zoom[0]) * u + extra_zoom
    px = sc.pan[0] + (sc.pan[2] - sc.pan[0]) * u
    py = sc.pan[1] + (sc.pan[3] - sc.pan[1]) * u
    rot = 0.0
    if STYLE.get('float'):
        # caméra « flottante » : lente dérive + léger roulis, comme dans un rêve
        px += 14 * math.sin(t * 0.55 + si) + 6 * math.sin(t * 1.3)
        py += 10 * math.cos(t * 0.45 + si * 0.7)
        rot = 0.7 * math.sin(t * 0.35 + si)
    if sc.shake and 0 <= lt < sc.shake:
        k = 1 - lt / sc.shake
        rnd = random.Random(fi)
        px += rnd.uniform(-28, 28) * k
        py += rnd.uniform(-28, 28) * k
    cv.save()
    cv.translate(W / 2 + px, H / 2 + py)
    cv.scale(z, z)
    cv.rotate(rot)
    cv.translate(-W / 2, -H / 2)
    cv.drawImageRect(sc._img, skia.Rect.MakeXYWH(-M, -M, W + 2 * M, H + 2 * M), skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear))
    sc.dyn(cv, lt, d)
    cv.restore()
    if hasattr(sc, 'fg'):
        cv.save(); cv.translate(W / 2 + px * 1.6, H / 2 + py * 1.6); cv.scale(z * 1.04, z * 1.04); cv.translate(-W / 2, -H / 2)
        sc.fg(cv, lt, d); cv.restore()
    return surf.makeImageSnapshot()


TRANS = ['dissolve', 'ink', 'liquid', 'iris', 'flash', 'dissolve', 'ink', 'liquid']


def trans_mask(kind, p, seed):
    """Masque (chemin) de la scène entrante pour une progression p (0→1)."""
    path = skia.Path()
    if kind == 'iris':
        path.addCircle(W / 2, H / 2, 1150 * p)
    elif kind == 'ink':
        rnd = random.Random(seed)
        cx, cy = rnd.uniform(500, 1400), rnd.uniform(300, 780)
        for k in range(7):
            a = rnd.uniform(0, 6.283); dd = rnd.uniform(0, 380) * p
            c = skia.Path(); c.addCircle(cx + math.cos(a) * dd, cy + math.sin(a) * dd, max(1.0, (200 + 1300 * p) * rnd.uniform(0.55, 1.0) * p))
            path = skia.Op(path, c, skia.PathOp.kUnion_PathOp) if k else c
    elif kind == 'ripple':
        R = 1250 * p
        n = 120
        for i in range(n + 1):
            ang = i / n * 6.2832
            r = max(1.0, R * (1 + 0.06 * math.sin(ang * 14 + p * 18)))
            x, y = W / 2 + math.cos(ang) * r, H / 2 + math.sin(ang) * r
            if i == 0:
                path.moveTo(x, y)
            else:
                path.lineTo(x, y)
        path.close()
    elif kind == 'liquid':
        x = -200 + (W + 400) * p
        path.moveTo(-50, -50); path.lineTo(x, -50)
        for y in range(0, H + 61, 30):
            path.lineTo(x + 90 * math.sin(y * 0.012 + p * 9 + seed) + 40 * math.sin(y * 0.031), y)
        path.lineTo(-50, H + 50); path.close()
    return path


_DREAM = {}


def _dream_assets():
    if not _DREAM:
        rnd = random.Random(77)
        _DREAM['orbs'] = [(rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(6, 34), rnd.uniform(0.15, 0.6), rnd.uniform(0, 6.28),
                           rnd.choice(['#FFB0E8', '#BFE6FF', '#FFE6A0', '#C8A8FF'])) for _ in range(34)]
        _DREAM['dust'] = [(rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(1, 2.6), rnd.uniform(0, 6.28)) for _ in range(140)]
        _DREAM['rows'] = np.arange(H)[:, None]
        _DREAM['cols'] = np.arange(W)[None, :]
    return _DREAM


def dream_pass(surf, cv, t, fi):
    """Couche « rêve » : halo (bloom), flou sur les bords, voile lacté, lumières colorées, brume, orbes, poussières, ondulation."""
    A = _dream_assets()
    img = surf.makeImageSnapshot()
    samp = skia.SamplingOptions(skia.FilterMode.kLinear)
    # image réduite + floutée (sert au halo et au flou des bords)
    small = skia.Surface(W // 4, H // 4)
    sp = skia.Paint(); sp.setImageFilter(skia.ImageFilters.Blur(6, 6))
    small.getCanvas().drawImageRect(img, skia.Rect.MakeWH(W // 4, H // 4), samp, sp)
    blurred = small.makeImageSnapshot()
    # ondulation « sous l'eau » (décalage sinusoïdal des lignes)
    if STYLE.get('wobble', 3) > 0:
        arr = img.toarray(colorType=skia.kRGBA_8888_ColorType)
        amp = STYLE.get('wobble', 3)
        shift = (amp * np.sin(np.arange(H) * 0.018 + t * 1.7)).astype(np.int64)
        arr = arr[A['rows'], (A['cols'] - shift[:, None]) % W]
        img = skia.Image.fromarray(np.ascontiguousarray(arr), colorType=skia.kRGBA_8888_ColorType)
        cv.clear(skia.ColorBLACK)
        cv.drawImage(img, 0, 0)
    # halo : on ajoute la version floutée en mode « screen »
    bp = skia.Paint(); bp.setBlendMode(skia.BlendMode.kScreen); bp.setAlphaf(STYLE.get('bloom', 0.42))
    cv.drawImageRect(blurred, skia.Rect.MakeWH(W, H), samp, bp)
    # flou progressif vers les bords (comme une vision de demi-sommeil)
    if STYLE.get('edge_blur', True):
      cv.saveLayer(None, None)
      cv.drawImageRect(blurred, skia.Rect.MakeWH(W, H), samp, None)
      mk = skia.Paint(); mk.setBlendMode(skia.BlendMode.kDstIn)
      mk.setShader(lib.rad(W / 2, H / 2, 1150, [lib.C('#000000', 0), lib.C('#000000', 0), lib.C('#000000', 255)], [0, 0.45, 1]))
      cv.drawRect(skia.Rect.MakeWH(W, H), mk)
      cv.restore()
    # voile lacté qui remonte les noirs vers le violet
    vp = P('#3A1A6A', STYLE.get('veil', 46)); vp.setBlendMode(skia.BlendMode.kScreen)
    cv.drawRect(skia.Rect.MakeWH(W, H), vp)
    # lumières colorées qui dérivent (light leaks)
    for k, col in enumerate(('#FF6FB8', '#4FD8E8', '#9A6BFF')):
        x = W / 2 + 820 * math.sin(t * 0.13 + k * 2.1)
        y = H / 2 + 420 * math.cos(t * 0.11 + k * 1.7)
        lp = P(shader=lib.rad(x, y, 760, [lib.C(col, STYLE.get('leaks', 70)), lib.C(col, 0)]))
        lp.setBlendMode(skia.BlendMode.kScreen)
        cv.drawRect(skia.Rect.MakeWH(W, H), lp)
    # brume basse qui glisse
    for k in range(4):
        x = (t * (18 + k * 9) + k * 520) % (W + 1200) - 600
        cv.drawOval(skia.Rect.MakeLTRB(x - 600, H - 230 + k * 30, x + 600, H + 140), P('#C8B8FF', 34, blur=60))
    # orbes (bokeh) et poussières qui flottent
    for x, y, r, sp_, ph, col in A['orbs']:
        yy = (y - t * 30 * sp_) % (H + 200) - 100
        xx = x + 40 * math.sin(t * 0.4 + ph)
        a = 0.5 + 0.5 * math.sin(t * 0.9 + ph)
        cv.drawCircle(xx, yy, r * STYLE.get('orb_size', 1.0), P(col, 38 + 40 * a, blur=r * STYLE.get('orb_soft', 0.5) + 0.01))
    for x, y, r, ph in A['dust']:
        yy = (y - t * 14) % H
        cv.drawCircle(x + 20 * math.sin(t * 0.6 + ph), yy, r, P('#FFF6E0', 90 + 80 * math.sin(t * 2 + ph)))


def frame(fi):
    t = fi / FPS
    si = max(i for i, (a, b) in enumerate(SEGS) if a <= t + 1e-6)
    tr = STYLE.get('trans', 0)
    pair = None
    if tr:
        t0, t1 = SEGS[si]
        if si > 0 and t - t0 < tr / 2:
            pair = (si - 1, si, 0.5 + (t - t0) / tr)
        elif si + 1 < len(SEGS) and t1 - t < tr / 2:
            pair = (si, si + 1, 0.5 - (t1 - t) / tr)
    surf = skia.Surface(W, H)
    cv = surf.getCanvas()
    if pair is None:
        cv.drawImage(scene_layer(si, t, fi), 0, 0)
    else:
        a, b, p = pair
        p = lib.ease(max(0.0, min(1.0, p)))
        kinds = STYLE.get('trans_kinds', TRANS)
        kind = kinds[b % len(kinds)]
        ia = scene_layer(a, t, fi, extra_zoom=0.10 * p)
        ib = scene_layer(b, t, fi, extra_zoom=0.10 * (1 - p))
        samp = skia.SamplingOptions(skia.FilterMode.kLinear)
        if kind == 'dream':
            blur = 1 + STYLE.get('dream_blur', 26) * math.sin(p * math.pi)
            pa = skia.Paint(); pa.setImageFilter(skia.ImageFilters.Blur(blur, blur))
            cv.drawImage(ia, 0, 0, samp, pa)
            pb = skia.Paint(); pb.setImageFilter(skia.ImageFilters.Blur(blur, blur)); pb.setAlphaf(p)
            cv.drawImage(ib, 0, 0, samp, pb)
            cv.drawRect(skia.Rect.MakeWH(W, H), P('#F4ECFF', 70 * math.sin(p * math.pi)))
        elif kind == 'dissolve':
            cv.drawImage(ia, 0, 0)
            pb = skia.Paint(); pb.setAlphaf(p)
            cv.drawImage(ib, 0, 0, samp, pb)
        elif kind == 'flash':
            cv.drawImage(ia if p < 0.5 else ib, 0, 0)
            cv.drawRect(skia.Rect.MakeWH(W, H), P('#F4ECFF', 255 * (1 - abs(p - 0.5) * 2) ** 1.5))
        else:
            cv.drawImage(ia, 0, 0)
            m = trans_mask(kind, p, b)
            # liseré lumineux qui suit le bord du masque
            cv.drawPath(m, P('#B98CFF', 200 * math.sin(p * math.pi), stroke=26, blur=12))
            cv.save(); cv.clipPath(m, doAntiAlias=True)
            cv.drawImage(ib, 0, 0)
            cv.restore()
            cv.drawPath(m, P('#F4ECFF', 230 * math.sin(p * math.pi), stroke=5))
    if STYLE.get('dream'):
        dream_pass(surf, cv, t, fi)
    # vignette légère
    cv.drawRect(skia.Rect.MakeWH(W, H), P(shader=lib.rad(W / 2, H / 2, 1250, [lib.C('#000000', 0), lib.C('#000000', 0), lib.C('#000000', 110)], [0, 0.6, 1])))
    wi = current_word(t)
    if wi is not None:
        draw_word(cv, DISP[wi], t - TIMES[wi], fi, surf)
    img = surf.makeImageSnapshot()
    arr = img.toarray(colorType=skia.kRGBA_8888_ColorType)
    if GRAIN is not None:
        rgb = arr[:, :, :3].astype(np.int16) + GRAIN[fi % len(GRAIN)]
        arr[:, :, :3] = np.clip(rgb, 0, 255).astype(np.uint8)
    return arr.tobytes()


def main():
    args = sys.argv[1:]
    out = os.path.join(HERE, os.environ.get('OUTNAME', 'etoiles_mortes.mp4'))
    if '--out' in args:
        out = args[args.index('--out') + 1]
    if '--preview' in args:
        ts = [float(x) for x in args[args.index('--preview') + 1].split(',')]
        odir = args[args.index('--preview') + 2] if len(args) > args.index('--preview') + 2 else '.'
        for tt in ts:
            b = frame(int(tt * FPS))
            arr = np.frombuffer(b, np.uint8).reshape(H, W, 4)
            skia.Image.fromarray(arr.copy(), colorType=skia.kRGBA_8888_ColorType).save(os.path.join(odir, f'prev_{tt:05.1f}.png'))
        return
    n = int(math.ceil(END * FPS))
    print(f'{n} frames, {END:.1f}s, {len(SEGS)} scènes', flush=True)
    ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-i', os.path.join(HERE, 'voice.wav'), '-c:v', 'libx264', '-preset', 'medium', *(['-b:v', '12M', '-maxrate', '14M', '-bufsize', '24M'] if GRAIN is not None else ['-crf', '18']), '-pix_fmt', 'yuv420p',
                           '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', '-t', f'{END:.3f}', out], stdin=subprocess.PIPE)
    with Pool(os.cpu_count()) as pool:
        for i, b in enumerate(pool.imap(frame, range(n), chunksize=6)):
            ff.stdin.write(b)
            if i % 150 == 0:
                print(f'  {i}/{n}', flush=True)
    ff.stdin.close(); ff.wait()
    print('ok ->', out)


if __name__ == '__main__':
    main()
