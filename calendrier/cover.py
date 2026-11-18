"""Covers de « Si l'univers tenait en un an » (texte crème en exclusion, comme la vidéo)."""
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
    p = lib.P(scenes.STYLE['color']); p.setBlendMode(skia.BlendMode.kExclusion)
    for i, l in enumerate(lines):
        cv.drawString(l, cx - font.measureText(l) / 2, y0 + i * lh, font, p)


ec.text_lines = text_lines
img = ec.scene_layer(scenes.Calendar3D, 2.0, 4.0)
lines = ["SI L'UNIVERS", "TENAIT EN", "UN AN"]
ec.make(os.path.join(HERE, 'cover_16x9.png'), 1920, 1080, img, lines, 190, 1100)
ec.make(os.path.join(HERE, 'cover_3x4.png'), 1080, 1440, img, lines, 170, 960)
