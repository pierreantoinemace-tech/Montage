# Règles de DA et d'écriture (validées)

## Format
- Vertical 2160x3840 (4K), 30 fps, image très nette : pas de flou, pas de grain, halos à bords nets.
- Moteur : `retard/video.py` (scènes + mots depuis words.json) ; décors dans `vertical/extrait3.py`, perso dans `vertical/extrait2.py`, symboles dans `vertical/symboles.py`.

## Design
- Décors abstraits façon Midnight Gospel, en plus sombre : ciels à bandes, collines striées, plantes-yeux, îles flottantes, soleils rayés.
- Couleurs sombres ou pâles ; on part du sombre et on finit plus pâle sur la fin positive.
- Peu de symboles, intégrés au décor (pas de pluie de symboles).
- Mouvement calme : légère dérive de caméra, pas de coups de zoom. Transitions en cercle ou en vague depuis le troisième œil.
- Perso récurrent aux trois yeux (la mascotte), dont le troisième œil pulse sur les mots clés.
- Texte : un mot à la fois, crème (mots clés en jaune), contour sombre épais et ombre nette, à 40 % de la hauteur.

## Pour chaque nouvelle vidéo
- Hook visuel dès la première image (mouvement ou élément intrigant), premier mot affiché tout de suite, jamais de seconde vide.
- Le perso aux trois yeux revient dans chaque vidéo, SANS nom, et pas de série ni de nom de série.
- Couvertures : même police et même placement du titre.
- La musique et les bruitages sont ajoutés par l'utilisateur dans l'appli TikTok.

## Écriture
- Hook expressif sans trop en faire, puis ton détaché et posé, sans être monotone. Jamais de chuchotement.
- Une idée forte par vidéo, un fait concret surprenant, une phrase finale courte et citable, fin positive.
- Tags ElevenLabs en anglais : [curious], [casual], [thoughtful], [softly], [warmly], [sighs], [short pause].

## Son
- L'utilisateur peut envoyer un son TikTok : on ne garde que l'audio, uniquement pour caler l'animation (transitions, pulsations, gros moments). Le son n'est PAS dans le montage final, il l'ajoute lui-même sur TikTok. La durée de la vidéo n'a pas à égaler celle du son.
- Son actuel analysé : `son/rythme.json`.

## Export
- 4K : H.264 High niveau 5.1 (compatible téléphones), CRF 15. Full HD : H.264 High niveau 4.2, CRF 14. Audio AAC 256k.
- Découpe de la voix : prolonger chaque phrase jusqu à la vraie fin du son (ne pas se fier aux fins de mots de whisper).
