#!/bin/bash
# Rend tous les plans (calés sur la voix Victoria) ; relançable : reprend là où ça s'est arrêté.
cd "$(dirname "$0")"
PLANS="chute:7.7 hotesse:5.25 confusion:2.45 explosion:5.6 cocon:5.1 neige:7.0 hopital:3.3 marche:2.1 guinness:4.7 fin:4.05"
for p in $PLANS; do
  n=${p%%:*}; d=${p##*:}; mkdir -p work/frames/$n
  want=$(python3 -c "print(max(2,int(round($d*30))))"); have=$(find work/frames/$n -name 'f_*.png' -size +1k | wc -l)
  [ "$have" -ge "$want" ] && continue
  find work/frames/$n -name 'f_*.png' -size -1k -delete   # images-témoins d'un rendu interrompu
  echo "== $n ($have/$want)"; SAMPLES=16 blender -b --python shots.py -- $n $d work/frames/$n 1080 1920 2>&1 | grep -E "^Saved|Error|Traceback" | tail -n 2
done
echo FINI
