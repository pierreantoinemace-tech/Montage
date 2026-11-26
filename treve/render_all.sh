#!/bin/bash
# Rend tous les plans (calés sur la voix Nicolas) ; relançable.
cd "$(dirname "$0")"
PLANS="poignee:6.75 tranchee:5.65 nuit:8.2 chant:1.7 sortie:3.8 echanges:5.05 foot:2.25 front:2.5 ordre:2.45 fin:3.54"
for p in $PLANS; do
  n=${p%%:*}; d=${p##*:}; mkdir -p work/frames/$n
  want=$(python3 -c "print(max(2,int(round($d*30))))"); have=$(find work/frames/$n -name 'f_*.png' -size +1k | wc -l)
  [ "$have" -ge "$want" ] && continue
  find work/frames/$n -name 'f_*.png' -size -1k -delete
  echo "== $n ($have/$want)"; SAMPLES=16 blender -b --python shots.py -- $n $d work/frames/$n 1080 1920 2>&1 | grep -E "^Saved|Error|Traceback" | tail -n 2
done
echo FINI
