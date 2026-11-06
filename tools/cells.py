import numpy as np, json, cv2
from geo import merc_px, px_merc
from PIL import Image, ImageDraw, ImageFont
M=json.load(open('work/mosaic.json')); mos=np.load('work/mosaic.npy',mmap_mode='r')
S=0.75; CELL=900
# extraction box (WGS)
N_,S_,W_,E_=51.665,51.115,29.33,30.56
x0,y0=merc_px(N_,W_); x1,y1=merc_px(S_,E_)
x0-=M['X0']; x1-=M['X0']; y0-=M['Y0']; y1-=M['Y0']
step=CELL/S
cells={}
try: font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',13)
except: font=None
cols=int(np.ceil((x1-x0)/step)); rows=int(np.ceil((y1-y0)/step))
for r in range(rows):
    for c in range(cols):
        gx,gy=int(x0+c*step),int(y0+r*step)
        sub=np.ascontiguousarray(mos[gy:gy+int(step),gx:gx+int(step)])
        im=Image.fromarray(cv2.resize(sub,(int(sub.shape[1]*S),int(sub.shape[0]*S)),interpolation=cv2.INTER_AREA))
        W,H=im.size; out=Image.new('RGB',(W+60,H+60),'white'); out.paste(im,(30,30)); d=ImageDraw.Draw(out,'RGBA')
        for k in range(0,max(W,H)+1,100):
            if k<=W: d.line([(30+k,30),(30+k,30+H)],fill=(255,0,255,110),width=1); d.text((30+k-10,8),str(k),fill=(200,0,200),font=font); d.text((30+k-10,H+38),str(k),fill=(200,0,200),font=font)
            if k<=H: d.line([(30,30+k),(30+W,30+k)],fill=(255,0,255,110),width=1); d.text((0,30+k-7),str(k),fill=(200,0,200),font=font); d.text((W+32,30+k-7),str(k),fill=(200,0,200),font=font)
        cid=f'r{r}c{c}'; out.save(f'work/cell_{cid}.png'); cells[cid]=[gx,gy]
json.dump({'S':S,'cells':cells},open('work/cells.json','w'))
print(rows,cols,len(cells))
