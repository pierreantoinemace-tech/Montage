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
FPS = 30
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
        _cache.clear()
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


def draw_word(cv, text):
    size = 150
    font = skia.Font(TYPE, size)
    font.setEdging(skia.Font.Edging.kAntiAlias)
    w = font.measureText(text)
    if w > 1720:
        size = size * 1720 / w
        font.setSize(size)
        w = font.measureText(text)
    cap = size * 0.70
    p = P('#ffffff')
    p.setBlendMode(skia.BlendMode.kDifference)
    cv.drawString(text, (W - w) / 2, H / 2 + cap / 2, font, p)


def frame(fi):
    t = fi / FPS
    si = max(i for i, (a, b) in enumerate(SEGS) if a <= t + 1e-6)
    t0, t1 = SEGS[si]
    lt, d = t - t0, t1 - t0
    sc = get_scene(si)
    surf = skia.Surface(W, H)
    cv = surf.getCanvas()
    cv.clear(skia.ColorBLACK)
    u = min(1.0, lt / max(d, 0.1))
    z = sc.zoom[0] + (sc.zoom[1] - sc.zoom[0]) * u
    px = sc.pan[0] + (sc.pan[2] - sc.pan[0]) * u
    py = sc.pan[1] + (sc.pan[3] - sc.pan[1]) * u
    if sc.shake and lt < sc.shake:
        k = 1 - lt / sc.shake
        rnd = random.Random(fi)
        px += rnd.uniform(-28, 28) * k
        py += rnd.uniform(-28, 28) * k
    cv.save()
    cv.translate(W / 2 + px, H / 2 + py)
    cv.scale(z, z)
    cv.translate(-W / 2, -H / 2)
    cv.drawImageRect(sc._img, skia.Rect.MakeXYWH(-M, -M, W + 2 * M, H + 2 * M), skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear))
    sc.dyn(cv, lt, d)
    cv.restore()
    # vignette légère
    cv.drawRect(skia.Rect.MakeWH(W, H), P(shader=lib.rad(W / 2, H / 2, 1250, [lib.C('#000000', 0), lib.C('#000000', 0), lib.C('#000000', 110)], [0, 0.6, 1])))
    wi = current_word(t)
    if wi is not None:
        draw_word(cv, DISP[wi])
    img = surf.makeImageSnapshot()
    return img.toarray(colorType=skia.kRGBA_8888_ColorType).tobytes()


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
                           '-i', os.path.join(HERE, 'voice.wav'), '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p',
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
