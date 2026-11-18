"""Covers de « Tu n'aurais jamais dû exister » (réutilise etoiles/cover.py)."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'etoiles'))
os.environ['PROJECT'] = HERE
import render, scenes
import importlib.util
spec = importlib.util.spec_from_file_location('ecover', os.path.join(HERE, '..', 'etoiles', 'cover.py'))
ec = importlib.util.module_from_spec(spec); spec.loader.exec_module(ec)
scene_layer, make = ec.scene_layer, ec.make
img = scene_layer(scenes.Billion, 4.2, 4.7)
lines = ["TU N'AURAIS", "JAMAIS DÛ", "EXISTER"]
make(os.path.join(HERE, 'cover_16x9.png'), 1920, 1080, img, lines, 190, 1050)
make(os.path.join(HERE, 'cover_3x4.png'), 1080, 1440, img, lines, 170, 940)
