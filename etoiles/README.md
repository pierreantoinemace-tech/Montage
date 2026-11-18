# « Tu es fait d'étoiles mortes » : TikTok style cosmic explainer

Une vidéo dans le style des 3 TikToks de référence :
- **un seul mot à l'écran à la fois**, énorme, centré, police ronde et grasse (Rubik Bold), en **mode de fusion « différence »** : le texte inverse les couleurs du décor, d'où les lettres multicolores ;
- les mots changent en **coupe franche, calés sur la voix** (timings au mot via Whisper) ;
- **illustrations vectorielles plates, très saturées** (violets, oranges, cyans), avec halos lumineux, étoiles qui scintillent, petits libellés encadrés façon infographie ;
- un décor qui change toutes les 2-3 s, avec un zoom lent en continu et des éléments animés (21 scènes originales, toutes dessinées en code) ;
- un ton cosmique et dramatique qui finit sur un message de motivation.

Format : 1920x1080 (16:9 comme les références), 30 fps, environ 64 s, H.264 + AAC.

## Fichiers
- `etoiles_mortes.mp4` : la vidéo finale
- `script.txt` : le texte lu
- `scenes.py` : les 21 scènes illustrées et animées, plus le découpage du texte par scène
- `render.py` : le moteur (alignement des mots, caméra, texte en différence, export ffmpeg)
- `voice.wav` / `words.json` : la voix temporaire (Piper TTS, voix « tom ») et les timings au mot

## Remplacer la voix par une voix ElevenLabs (recommandé)
La voix actuelle est une synthèse locale gratuite, correcte mais assez plate. Pour avoir le rendu « narrateur grave » des références :
1. ElevenLabs, modèle **Eleven v3/v4**, une voix masculine grave et posée (Voice Design : « homme français 35 ans, voix grave et chaude, narrateur de documentaire, ton solennel, débit lent »), stability environ 40 %.
2. Texte avec les audio tags :

```
[serious] Regarde ta main. [pause] Chaque atome de calcium dans tes os… chaque atome de fer dans ton sang… a été fabriqué au cœur d'une étoile.
[slowly] Il y a des milliards d'années, bien avant la Terre, une étoile géante brûlait… seule… dans le noir.
Pendant des millions d'années, elle a écrasé de l'hydrogène pour créer du carbone, de l'oxygène, et du fer.
[whispers] Puis elle est morte.
[intense] Elle a explosé dans une supernova si violente qu'elle a illuminé TOUTE sa galaxie.
Ses cendres ont dérivé dans le vide pendant une éternité. Jusqu'à ce qu'elles forment un nuage, puis un soleil, puis une petite planète bleue.
[pause] Puis toi.
Tu n'es pas juste DANS l'univers. Tu ES l'univers, qui a appris à se regarder.
[emotional] Une étoile est morte pour que tu puisses exister.
[firm] Alors arrête de vivre comme si tu ne comptais pas. Tu as mis treize milliards d'années à arriver ici.
[whispers] Ne gâche pas ça.
```
3. Remplacer `voice.wav`, relancer la transcription (`words.json`), puis `python render.py`. Les coupes se recalent toutes seules sur la nouvelle voix.

Pas de musique dans le fichier : à ajouter dans TikTok (une nappe ambient/cinématique lente, comme dans les références).
