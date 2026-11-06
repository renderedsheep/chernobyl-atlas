"""Step 5: trace water (the light-blue fill on the sheets) into polygons -> ../data/water.js"""
import numpy as np, json, cv2
from geo import px_merc
M=json.load(open('work/mosaic.json')); mos=np.load('work/mosaic.npy')
hsv=cv2.cvtColor(mos,cv2.COLOR_RGB2HSV); H,S,V=[hsv[...,i].astype(int) for i in range(3)]
mask=((H>=92)&(H<=112)&(S>=30)&(S<=150)&(V>=150)).astype(np.uint8)
mask=cv2.morphologyEx(mask,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8)); mask=cv2.morphologyEx(mask,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
n,lab,st,_=cv2.connectedComponentsWithStats(mask,8); keep=np.zeros_like(mask)
for i in range(1,n):
    if st[i,cv2.CC_STAT_AREA]>=1500: keep[lab==i]=1
cnts,hier=cv2.findContours(keep,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_SIMPLE); hier=hier[0] if hier is not None else []
def ring(c):
    c=cv2.approxPolyDP(c,1.2,True).reshape(-1,2)
    if len(c)<4: return None
    la,lo=px_merc(c[:,0]+M['X0']+0.5,c[:,1]+M['Y0']+0.5); return [[round(float(b),5),round(float(a),5)] for a,b in zip(la,lo)]
feats=[]
for i,c in enumerate(cnts):
    if hier[i][3]!=-1 or cv2.contourArea(c)<1500: continue
    outer=ring(c)
    if not outer: continue
    holes=[]; j=hier[i][2]
    while j!=-1:
        if cv2.contourArea(cnts[j])>=200:
            h=ring(cnts[j])
            if h: holes.append(h)
        j=hier[j][0]
    feats.append({"type":"Feature","properties":{},"geometry":{"type":"Polygon","coordinates":[outer]+holes}})
open('../data/water.js','w').write("window.ATLAS_WATER="+json.dumps({"type":"FeatureCollection","features":feats},separators=(',',':'))+";\n")
print(len(feats),'water polygons')
