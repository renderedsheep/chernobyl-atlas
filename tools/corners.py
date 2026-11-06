import numpy as np, json, random
from PIL import Image, ImageDraw
SHEETS={"M-35-23":(29.0,51.3333),"M-35-24":(29.5,51.3333),"M-35-35":(29.0,51.0),"M-35-36":(29.5,51.0),
        "M-36-13":(30.0,51.3333),"M-36-14":(30.5,51.3333),"M-36-25":(30.0,51.0),"M-36-26":(30.5,51.0)}
random.seed(1)
def profiles(d, side):
    H,W=d.shape; out=[]
    D=int(.16*W) if side in 'LR' else int(.16*H)
    rng = range(int(.15*H), int(.85*H)-30, 40) if side in 'LR' else range(int(.12*W), int(.88*W)-30, 40)
    for s in rng:
        if side=='L': p=d[s:s+30,0:D].mean(0)
        elif side=='R': p=d[s:s+30,W-D:W].mean(0)[::-1]
        elif side=='T': p=d[0:D,s:s+30].mean(1)
        else: p=d[H-D:H,s:s+30].mean(1)[::-1]
        out.append((s+15,p))
    return out,D
def solve(d,side,kref=None,win=None):
    prs,D=profiles(d,side)
    cands=[]
    for t,p in prs:
        c=[i+ (p[i+1]-p[i-1])/(2*(2*p[i]-p[i-1]-p[i+1])+1e-9) for i in range(2,len(p)-2) if p[i]>60 and p[i]>=p[i-1] and p[i]>p[i+1]]
        if win: c=[x for x in c if win[0]<=x<=win[1]]
        cands.append((t,c))
    pts=[(t,c) for t,cs in cands for c in cs]
    tm=np.mean([t for t,_ in cands]); best={}
    for _ in range(6000):
        (t1,c1),(t2,c2)=random.sample(pts,2)
        if abs(t1-t2)<300: continue
        k=(c2-c1)/(t2-t1)
        if kref is not None and abs(np.degrees(np.arctan(k)-np.arctan(kref)))>0.35: continue
        if abs(np.degrees(np.arctan(k)))>1.5: continue
        b=c1-k*t1
        sup=[(t,c) for t,cs in cands for c in cs if abs(c-(k*t+b))<1.6]
        segs=len(set(t for t,_ in sup))
        if segs<0.8*len(cands): continue
        a=np.array(sup); kk,bb=np.polyfit(a[:,0],a[:,1],1); off=kk*tm+bb
        key=round(off/3)
        if key not in best or segs>best[key][2]: best[key]=(bb,kk,segs,off)
    if not best: return None
    bb,kk,segs,off=max(best.values(),key=lambda v:v[3])   # innermost consistent line
    return bb,kk,segs,len(cands),D,off
res={}
for name,(lon0,lat0) in SHEETS.items():
    g=np.array(Image.open(f'src/{name}.jpg').convert('L')).astype(float); d=255-g; H,W=d.shape
    S={}
    S['L']=solve(d,'L'); S['R']=solve(d,'R',S['L'][1])
    S['T']=solve(d,'T',-S['L'][1]); S['B']=solve(d,'B',S['L'][1], (60,100) if name in ('M-36-13','M-36-14') else None)
    # convert to image-coordinate lines: vertical x = kx*y + cx ; horizontal y = ky*x + cy
    def L_(s):
        bb,kk,_,_,D,_=S[s]
        if s=='L': return (kk,bb)
        if s=='R': return (-kk, W-1-bb)
        if s=='T': return (kk,bb)
        if s=='B': return (-kk, H-1-bb)
    def inter(v,h):
        kv,cv=v; kh,ch=h; y=(kh*cv+ch)/(1-kh*kv); x=kv*y+cv; return [float(x),float(y)]
    c={'NW':inter(L_('L'),L_('T')),'NE':inter(L_('R'),L_('T')),'SW':inter(L_('L'),L_('B')),'SE':inter(L_('R'),L_('B'))}
    res[name]={'corners':c,'size':[W,H],'lon0':lon0,'lat0':lat0}
    print(name,{k:[round(v[0],1),round(v[1],1)] for k,v in c.items()},'support',[(S[s][2],S[s][3],round(S[s][5])) for s in 'LRTB'])
import os; os.makedirs('work',exist_ok=True)
json.dump(res,open('work/corners.json','w'),indent=1)
tiles=[]
for name in SHEETS:
    im=Image.open(f'src/{name}.jpg').convert('RGB'); c=res[name]['corners']
    row=Image.new('RGB',(4*180,200),'white'); dr=ImageDraw.Draw(row)
    for i,k in enumerate(['NW','NE','SW','SE']):
        x,y=c[k]; cr=im.crop((int(x)-45,int(y)-45,int(x)+45,int(y)+45)).resize((180,180),Image.NEAREST)
        dd=ImageDraw.Draw(cr); px=(x-int(x)+45)*2; py=(y-int(y)+45)*2
        dd.line([(px-14,py),(px+14,py)],fill=(255,0,0)); dd.line([(px,py-14),(px,py+14)],fill=(255,0,0))
        row.paste(cr,(i*180,20)); dr.text((i*180+4,4),f'{name} {k}',fill='black')
    tiles.append(row)
out=Image.new('RGB',(720,1600),'white')
for i,t in enumerate(tiles): out.paste(t,(0,i*200))
out.save('work/corners_check.png')
