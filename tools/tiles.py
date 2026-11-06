import numpy as np, json, cv2, os, math
M=json.load(open('work/mosaic.json')); mos=np.load('work/mosaic.npy')
PAPER=np.array([241,241,228],np.uint8)
X0,Y0=M['X0'],M['Y0']; n=0; size=0; info={}
for z in range(13,7,-1):
    f=2**(13-z)
    img = mos if f==1 else cv2.resize(mos,(M['W']//f,M['H']//f),interpolation=cv2.INTER_AREA)
    ox,oy=X0/f,Y0/f; h,w=img.shape[:2]
    tx0,ty0=int(ox//1024),int(oy//1024); tx1,ty1=int(math.ceil((ox+w)/1024)),int(math.ceil((oy+h)/1024))
    info[z]=[tx0,ty0,tx1-1,ty1-1]
    for ty in range(ty0,ty1):
        for tx in range(tx0,tx1):
            t=np.empty((1024,1024,3),np.uint8); t[:]=PAPER
            gx0,gy0=tx*1024-ox, ty*1024-oy
            sx0,sy0=int(max(0,gx0)),int(max(0,gy0)); sx1,sy1=int(min(w,gx0+1024)),int(min(h,gy0+1024))
            if sx1<=sx0 or sy1<=sy0: continue
            t[sy0-int(gy0):sy1-int(gy0), sx0-int(gx0):sx1-int(gx0)]=img[sy0:sy1,sx0:sx1]
            d=f'tiles/{z-2}/{tx}'; os.makedirs(d,exist_ok=True)
            p=f'{d}/{ty}.webp'; cv2.imwrite(p,t[:,:,::-1],[cv2.IMWRITE_WEBP_QUALITY,80]); n+=1; size+=os.path.getsize(p)
    print('z',z,'tiles so far',n, round(size/1e6,1),'MB')
json.dump(info,open('work/tileinfo.json','w'))
