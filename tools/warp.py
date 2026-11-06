import numpy as np, json, cv2, math
from geo import *
import os; os.makedirs('work',exist_ok=True)
C=json.load(open('work/corners.json'))
# output extent (WGS84) padded
S_,N_,W_,E_=50.995,51.672,28.99,31.01
x0,y0=merc_px(N_,W_); x1,y1=merc_px(S_,E_)
X0,Y0=int(math.floor(x0/1024)*1024), int(math.floor(y0/1024)*1024)
X1,Y1=int(math.ceil(x1/1024)*1024), int(math.ceil(y1/1024)*1024)
Wd,Hd=X1-X0,Y1-Y0; print('mosaic',Wd,Hd,'origin',X0,Y0)
PAPER=np.array([241,241,228],np.uint8)
mos=np.empty((Hd,Wd,3),np.uint8); mos[:]=PAPER
cov=np.zeros((Hd,Wd),bool)
for name,info in C.items():
    lon0,lat0=info['lon0'],info['lat0']; lat_top=lat0+1/3
    img=cv2.imread(f'src/{name}.jpg')[:,:,::-1]
    # colour normalise: paper white -> PAPER
    g=img.astype(np.float32)
    ref=np.percentile(g.reshape(-1,3),97,axis=0); g=np.clip(g/ref*np.array([246,244,232]),0,255).astype(np.uint8)
    c=info['corners']; NW,NE,SW,SE=[np.array(c[k]) for k in ('NW','NE','SW','SE')]
    # sheet bounds in mercator px (via WGS)
    bl=[sk42_to_wgs(la,lo) for la,lo in [(lat0,lon0),(lat_top,lon0),(lat0,lon0+.5),(lat_top,lon0+.5)]]
    xs,ys=zip(*[merc_px(a,b) for a,b in bl])
    bx0,bx1=int(min(xs))-X0-2,int(max(xs))-X0+3; by0,by1=int(min(ys))-Y0-2,int(max(ys))-Y0+3
    gx,gy=np.meshgrid(np.arange(bx0,bx1)+X0+0.5, np.arange(by0,by1)+Y0+0.5)
    la,lo=px_merc(gx,gy); la,lo=wgs_to_sk42(la,lo)
    u=(lo-lon0)/0.5; v=(lat_top-la)/(1/3)
    inside=(u>=0)&(u<1)&(v>=0)&(v<1)
    sx=(1-u)*(1-v)*NW[0]+u*(1-v)*NE[0]+(1-u)*v*SW[0]+u*v*SE[0]
    sy=(1-u)*(1-v)*NW[1]+u*(1-v)*NE[1]+(1-u)*v*SW[1]+u*v*SE[1]
    out=cv2.remap(g,sx.astype(np.float32),sy.astype(np.float32),cv2.INTER_CUBIC,borderMode=cv2.BORDER_REPLICATE)
    sub=mos[by0:by1,bx0:bx1]; sub[inside]=out[inside]; cov[by0:by1,bx0:bx1]|=inside
    print(name,'done', inside.sum())
np.save('work/mosaic.npy',mos); json.dump({'X0':X0,'Y0':Y0,'W':Wd,'H':Hd,'Z':13},open('work/mosaic.json','w'))
cv2.imwrite('work/mosaic_preview.jpg',cv2.resize(mos,(Wd//8,Hd//8),interpolation=cv2.INTER_AREA)[:,:,::-1],[cv2.IMWRITE_JPEG_QUALITY,85])
