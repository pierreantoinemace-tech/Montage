# « Si l'univers tenait en un an »

Style v2, plus fidèle aux références :
- texte crème `#F0EBBE` en mode **exclusion** (crème sur fond sombre, vert pâle sur violet, bleu sur jaune), glitch de 2 frames à chaque mot ;
- 18 plans longs (1 par phrase), denses, toujours en mouvement : calendrier 3D en fil de fer, grilles en perspective, traînées néon, personnages de face expressifs (`kit.py`) ;
- grain léger, encodage plafonné à 12 Mb/s.

Rendu :
```
PROJECT=$PWD/calendrier OUTNAME=univers_en_un_an.mp4 python3 etoiles/render.py
python3 calendrier/cover.py
```
