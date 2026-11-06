import numpy as np, math
# SK-42 (Krasovsky) -> WGS84, PROJ towgs84 (position vector) 23.92,-141.27,-80.9,0,0.35,0.82,-0.12
KR=(6378245.0,1/298.3); WG=(6378137.0,1/298.257223563)
TW=(23.92,-141.27,-80.9,0.0,0.35,0.82,-0.12)
def to_ecef(lat,lon,ell):
    a,f=ell; e2=f*(2-f); la,lo=np.radians(lat),np.radians(lon); N=a/np.sqrt(1-e2*np.sin(la)**2)
    return N*np.cos(la)*np.cos(lo), N*np.cos(la)*np.sin(lo), N*(1-e2)*np.sin(la)
def from_ecef(x,y,z,ell):
    a,f=ell; e2=f*(2-f); lon=np.arctan2(y,x); p=np.hypot(x,y); lat=np.arctan2(z,p*(1-e2))
    for _ in range(6):
        N=a/np.sqrt(1-e2*np.sin(lat)**2); lat=np.arctan2(z+e2*N*np.sin(lat),p)
    return np.degrees(lat),np.degrees(lon)
def helm(x,y,z,p,inv=False):
    dx,dy,dz,rx,ry,rz,ds=p; s=1+ds*1e-6; r=math.pi/180/3600; rx,ry,rz=rx*r,ry*r,rz*r
    if inv: dx,dy,dz,rx,ry,rz,s=-dx,-dy,-dz,-rx,-ry,-rz,1/s
    return (dx+s*(x - rz*y + ry*z), dy+s*(rz*x + y - rx*z), dz+s*(-ry*x + rx*y + z))
def sk42_to_wgs(lat,lon):
    return from_ecef(*helm(*to_ecef(lat,lon,KR),TW),WG)
def wgs_to_sk42(lat,lon):
    return from_ecef(*helm(*to_ecef(lat,lon,WG),TW,inv=True),KR)
Z=13; WORLD=256*2**Z
def merc_px(lat,lon):
    x=(lon+180)/360*WORLD; s=np.sin(np.radians(lat)); y=(0.5-np.log((1+s)/(1-s))/(4*np.pi))*WORLD; return x,y
def px_merc(x,y):
    lon=x/WORLD*360-180; n=np.pi-2*np.pi*y/WORLD; lat=np.degrees(np.arctan(np.sinh(n))); return lat,lon
if __name__=="__main__":
    la,lo=sk42_to_wgs(51.3894,30.0990); print('shift m: dlat',(la-51.3894)*111200,'dlon',(lo-30.0990)*111200*math.cos(math.radians(51.39)))
