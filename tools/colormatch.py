"""Step 3: match the colour of the two brighter scans (M-36-13, M-36-14) to the other six."""
import numpy as np, json, cv2
from geo import sk42_to_wgs, merc_px
C=json.load(open('work/corners.json')); M=json.load(open('work/mosaic.json')); mos=np.load('work/mosaic.npy')
def sheet_slice(name):
    i=C[name]; lon0,lat0=i['lon0'],i['lat0']
    (a,b),(c,d)=sk42_to_wgs(lat0+1/3,lon0),sk42_to_wgs(lat0,lon0+.5)
    x0,y0=merc_px(a,b); x1,y1=merc_px(c,d)
    return slice(int(y0)-M['Y0']+3,int(y1)-M['Y0']-3), slice(int(x0)-M['X0']+3,int(x1)-M['X0']-3)
stats={}
for n in C:
    sy,sx=sheet_slice(n); lab=cv2.cvtColor(mos[sy,sx][::4,::4],cv2.COLOR_RGB2LAB).reshape(-1,3).astype(np.float32); stats[n]=(lab.mean(0),lab.std(0))
ref=[n for n in C if n not in ('M-36-13','M-36-14')]
tm=np.mean([stats[n][0] for n in ref],0); ts=np.mean([stats[n][1] for n in ref],0)
for n in ('M-36-13','M-36-14'):
    sy,sx=sheet_slice(n); lab=cv2.cvtColor(mos[sy,sx],cv2.COLOR_RGB2LAB).astype(np.float32); m,s=stats[n]
    t=(lab-m)/s*ts+tm; mos[sy,sx]=cv2.cvtColor(np.clip(lab*0.3+t*0.7,0,255).astype(np.uint8),cv2.COLOR_LAB2RGB)
np.save('work/mosaic.npy',mos); print('colour matched')
