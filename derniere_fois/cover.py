"""Covers de « Les derniere_fois » (texte crème en exclusion, comme la vidéo)."""
import os, sys, importlib.util
import skia
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'etoiles'))
os.environ['PROJECT'] = HERE
import render, scenes, lib
spec = importlib.util.spec_from_file_location('ecover', os.path.join(HERE, '..', 'etoiles', 'cover.py'))
ec = importlib.util.module_from_spec(spec); spec.loader.exec_module(ec)


def text_lines(cv, lines, cx, cy, size, maxw):
    font = skia.Font(render.TYPE, size)
    sz = min(size, min(size * maxw / font.measureText(l) for l in lines)); font.setSize(sz)
    lh = sz * 0.98; y0 = cy - lh * (len(lines) - 1) / 2 + sz * 0.35
    p = lib.P(scenes.STYLE['color'])
    for i, l in enumerate(lines):
        x = cx - font.measureText(l) / 2
        cv.drawString(l, x, y0 + i * lh + sz * 0.04, font, lib.P('#0A0420', 170, blur=sz * 0.09))
        cv.drawString(l, x, y0 + i * lh + sz * 0.04, font, lib.P('#0A0420', 90, blur=sz * 0.25))
        cv.drawString(l, x, y0 + i * lh, font, p)


ec.text_lines = text_lines

img = ec.scene_layer(scenes.Play, 1.2, 3.9)

lines = ["LA DERNIÈRE", "FOIS"]
ec.make(os.path.join(HERE, 'cover_16x9.png'), 1920, 1080, img, lines, 190, 1100)
ec.make(os.path.join(HERE, 'cover_3x4.png'), 1080, 1440, img, lines, 170, 960)
