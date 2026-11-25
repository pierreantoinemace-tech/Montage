import sys,json,wave,numpy as np
from faster_whisper import WhisperModel
m=WhisperModel("small",device="cpu",compute_type="int8")
w=wave.open(sys.argv[1]);a=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(np.float32)/32768
segs,_=m.transcribe(a,language="fr",word_timestamps=True,initial_prompt=open(sys.argv[3]).read())
out=[]
for s in segs:
    print(s.text)
    for x in s.words: out.append([x.word.strip(),round(x.start,3),round(x.end,3)])
json.dump(out,open(sys.argv[2],"w"),ensure_ascii=False)
