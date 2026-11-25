# Vidéo « Vesna Vulović » en 3D — état et marche à suivre

## Ce que veut l'utilisateur
- Vidéo TikTok verticale, ~45 s, histoire vraie racontée à la 1re personne (Vesna, voix féminine ElevenLabs).
- Texte : `vesna/script.txt` (136 mots, validé).
- Animation 3D fluide **30 fps** (PAS de rendu « pâte à modeler », PAS de 12 fps stop-motion). Rendu soigné type film d'animation :
  peau douce légèrement translucide (subsurface), matières moins mates, lumière de contour, profondeur de champ, léger flou de mouvement,
  plus d'échantillons (32+). Le temps de rendu n'est pas un problème (~2 h – 2 h 30 OK).
- Plusieurs scènes qui expliquent bien l'histoire, style rêve / fantaisie, DA du compte (perso aux 3 yeux, haut étroit) en plus joyeux.
- Mots à l'écran : même style que les autres vidéos (un mot à la fois, crème, mots clés jaunes, contour sombre épais) — voir `DA_notes.md`.
- Export : 4K (2160x3840, H.264 High niveau 5.1, CRF 15) + Full HD (niveau 4.2, CRF 14), audio AAC 256k. Voix d'un seul tenant, sans coupure.
- La musique est ajoutée par l'utilisateur sur TikTok (ne pas l'inclure).

## Outils
- Blender 4.0 (apt : `apt-get install -y blender`), moteur EEVEE en logiciel (marche en headless malgré les erreurs EGL).
  Cycles : pas de débruiteur dans ce build → éviter.
- `test3d/lib3d.py` : setup(), matériaux, perso `character(...)` (paramètres robe, hat='toque'|'bonnet', beard, hair_cols, nhair, old),
  décors (island, cloud, stars, big_moon, bulb_plant, orb, world, lights, camera), animation (animate_hair, blink, on_frame, key).
- `vesna/shots.py` : 10 plans — chute, hotesse, confusion, explosion, cocon, neige (Bruno), hopital, marche, guinness, fin.
  Aperçu : `blender -b --python vesna/shots.py -- <plan> <durée_s> <sortie.png> 360 640 <t>` ;
  rendu : `... -- <plan> <durée_s> <dossier> <rx> <ry>` (images f_####.png). FPS est à mettre à 30 (actuellement 12 dans le fichier).
- Mesure : ~8,5 s/image en 1080x1920 avec 12 échantillons ; prévoir ~10-12 s avec la qualité supérieure.
- Les commandes en arrière-plan sont coupées au bout de 2 h → lancer un plan (ou un lot de plans) par commande.

## Étapes quand le mp3 arrive
1. Normaliser la voix (loudnorm -14 LUFS), + 0,25 s de silence au début, transcrire avec faster-whisper (script `words.py` : modèle small, int8, fr, initial_prompt = texte).
2. Caler la durée de chaque plan sur les phrases (début de plan = début de phrase).
3. Passer FPS à 30 + réglages qualité, rendre chaque plan, assembler, ajouter les mots (skia, police `etoiles/fonts/Rubik-700.ttf`), exporter.
4. Couvertures 9:16, 3:4, 16:9 ; légendes + hashtags.
