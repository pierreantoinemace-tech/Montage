"""Assemble les plans 3D rendus (work/frames/<plan>/f_####.png), fondus courts entre plans, léger étalonnage,
mots à l'écran (DA du compte), voix → export 4K + Full HD. Usage : python3 compose.py [--preview t1,t2,...]"""
import os, sys, json, math, subprocess
from multiprocessing import Pool
import numpy as np, skia
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
FPS = 30
W, H = 1080, 1920                      # repère logique ; sortie 2x (4K)
OW, OH = 2160, 3840
PLANS = [('chute', 7.7), ('hotesse', 5.25), ('confusion', 2.45), ('explosion', 5.6), ('cocon', 5.1),
         ('neige', 7.0), ('hopital', 3.3), ('marche', 2.1), ('guinness', 4.7), ('fin', 4.05)]
XF = 4                                 # demi-largeur du fondu entre plans (images)
FONT = skia.Typeface.MakeFromFile(os.path.join(HERE, '..', 'etoiles', 'fonts', 'Rubik-700.ttf'))
CREAM, GOLD, OUTC = '#F0EBBE', '#FFE680', '#120624'
TY = H * 0.40

# ---------------- plans ----------------
STARTS, acc = [], 0
for n, d in PLANS:
    STARTS.append(acc); acc += int(round(d * FPS))
NTOT = acc


def shot_img(k, i):
    n, d = PLANS[k]; cnt = int(round(d * FPS))
    i = max(0, min(cnt - 1, i))
    return np.asarray(Image.open(os.path.join(HERE, 'work', 'frames', n, f'f_{i + 1:04d}.png')).convert('RGB'), np.float32)


def base(fi):
    k = max(j for j in range(len(PLANS)) if STARTS[j] <= fi)
    a = shot_img(k, fi - STARTS[k])
    nxt = STARTS[k + 1] if k + 1 < len(PLANS) else None
    if nxt is not None and fi >= nxt - XF:                       # fin de plan : fondu vers le suivant
        u = (fi - (nxt - XF) + 0.5) / (2 * XF); u = u * u * (3 - 2 * u)
        a = a * (1 - u) + shot_img(k + 1, 0) * u
    if k > 0 and fi < STARTS[k] + XF:                            # début de plan : fondu depuis le précédent
        u = (fi - (STARTS[k] - XF) + 0.5) / (2 * XF); u = u * u * (3 - 2 * u)
        a = shot_img(k - 1, 10 ** 6) * (1 - u) + a * u
    # étalonnage léger : un peu plus de contraste et de couleur
    x = a / 255.0
    lum = (x * [0.2126, 0.7152, 0.0722]).sum(-1, keepdims=True)
    x = lum + (x - lum) * 1.12
    x = 0.5 + (x - 0.5) * 1.08
    x = np.clip(x, 0, 1) * 255
    im = Image.fromarray(x.astype(np.uint8)).resize((OW, OH), Image.LANCZOS)
    return np.asarray(im.convert('RGBA'))


# ---------------- mots ----------------
FIX = {'TOMBÉ': 'TOMBÉE', 'ENVIE': 'EN VIE', 'CRANE': 'CRÂNE', 'FRACTURÉE': 'FRACTURÉ', 'JAMBE': 'JAMBES', 'MCCARTNEY': 'McCARTNEY'}
KEYS = {'1972', '10 000', 'PARACHUTE', 'VESNA', 'HÔTESSE', 'CONFONDUE', 'EXPLOSE', 'MOI', 'MOI.', 'CHARIOT', 'KILOMÈTRES',
        'NEIGE', 'BRUNO', 'EN VIE', 'CRÂNE', 'PARALYSÉE', 'REMARCHE', 'GUINNESS', 'McCARTNEY', 'IDOLE', 'PENSE'}


def load_words():
    raw = json.load(open(os.path.join(HERE, 'work', 'words.json')))
    toks = []
    for w, s, e in raw:
        if w and w[0] in "'-" and toks:
            toks[-1][0] += w; toks[-1][2] = e; continue
        if w.strip('?!.,…') == '': continue
        if w.startswith('000') and toks and toks[-1][0] == '10':      # « 10 000 »
            toks[-1][0] = '10 000'; toks[-1][2] = e; continue
        toks.append([w, s, e])
    out = []
    for i, (w, s, e) in enumerate(toks):
        txt = w.strip(',.?!…').upper().replace('’', "'")
        txt = FIX.get(txt, txt)
        nxt = toks[i + 1][1] if i + 1 < len(toks) else e + 1.0
        end = nxt if nxt - e < 0.7 else e + 0.35
        out.append((txt, s, end, txt in KEYS))
    return out


WORDS = load_words()


def P(col, a=255, stroke=None):
    p = skia.Paint(AntiAlias=True); c = col.lstrip('#')
    p.setColor(skia.Color(int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16), a))
    if stroke: p.setStyle(skia.Paint.kStroke_Style); p.setStrokeWidth(stroke)
    return p


def draw_word(cv, t):
    for w, s, e, k in WORDS:
        if s <= t < e: break
    else: return
    age = t - s
    size = 185 if k else 160
    f = skia.Font(FONT, size); tw = f.measureText(w)
    if tw > 820: f.setSize(size * 820 / tw); tw = f.measureText(w)
    u = max(0.0, min(1.0, age / 0.16)); sc = 0.9 + 0.1 * (1 - (1 - u) ** 3)
    cv.save(); cv.translate(W / 2, TY); cv.scale(sc, sc)
    fs = f.getSize(); x, y = -tw / 2, fs * 0.35
    o = P(OUTC, 255, stroke=fs * 0.15); o.setStrokeJoin(skia.Paint.kRound_Join)
    cv.drawString(w, x + fs * 0.03, y + fs * 0.06, f, o); cv.drawString(w, x + fs * 0.03, y + fs * 0.06, f, P(OUTC))
    cv.drawString(w, x, y, f, o); cv.drawString(w, x, y, f, P(GOLD if k else CREAM))
    cv.restore()


def frame(fi):
    arr = np.ascontiguousarray(base(fi))
    surf = skia.Surface(arr)                     # dessine directement sur l'image
    cv = surf.getCanvas(); cv.scale(OW / W, OH / H)
    draw_word(cv, fi / FPS)
    surf.flushAndSubmit()
    return arr.tobytes()


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--preview':
        os.makedirs(os.path.join(HERE, 'work', 'prev'), exist_ok=True)
        for ts in sys.argv[2].split(','):
            a = np.frombuffer(frame(int(float(ts) * FPS)), np.uint8).reshape(OH, OW, 4)
            Image.fromarray(a[..., :3]).resize((540, 960), Image.LANCZOS).save(os.path.join(HERE, 'work', 'prev', f'c_{ts}.png'))
        sys.exit()
    out4k = os.path.join(HERE, 'vesna_4k.mp4'); out1080 = os.path.join(HERE, 'vesna_1080p.mp4')
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', f'{OW}x{OH}', '-r', str(FPS), '-i', '-',
                           '-i', os.path.join(HERE, 'work', 'voice.wav'),
                           '-c:v', 'libx264', '-preset', 'slow', '-tune', 'animation', '-profile:v', 'high', '-level', '5.1',
                           '-crf', '15', '-maxrate', '25M', '-bufsize', '50M', '-pix_fmt', 'yuv420p',
                           '-c:a', 'aac', '-b:a', '256k', '-shortest', '-movflags', '+faststart', out4k], stdin=subprocess.PIPE)
    with Pool(3) as pool:
        for i, b in enumerate(pool.imap(frame, range(NTOT), chunksize=2)):
            ff.stdin.write(b)
            if i % 150 == 0: print(i, '/', NTOT, flush=True)
    ff.stdin.close(); ff.wait()
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', out4k, '-vf', 'scale=1080:1920:flags=lanczos', '-c:v', 'libx264', '-profile:v', 'high',
                    '-level', '4.2', '-crf', '14', '-preset', 'slow', '-tune', 'animation', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '256k',
                    '-movflags', '+faststart', out1080])
    print('ok', NTOT)
