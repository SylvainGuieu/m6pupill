#!/diskc/PrivateData/vltipso/python27/anaconda/bin/python
import os
import sys
import glob
import re
from scipy.ndimage.interpolation import shift
from astropy.io import fits
from matplotlib.pylab import plt
from scipy.optimize import curve_fit
import numpy as np 

ext = "png"

confLoockup = { # loockup by at 
     1: dict( fluxTreshold = 1550,  pupLocation =  [ [367,404], [682,670]] ), 
     2: dict( fluxTreshold = 1550,  pupLocation = [ [367,350], [682,700]] ), 
     3: dict(  fluxTreshold = 2050,  pupLocation = [ [380,345], [720,632]] ), 
     4: dict(  fluxTreshold = 2100,  pupLocation = [ [413,250], [682,511]] ), 
     0:  dict( fluxTreshold = 1550,  pupLocation =  [ [380,404], [682,670]] ), 
}

def getConf(at):
    return confLoockup.get(at,0)
        

def renames(files):
    for  file in files:
        directory, filename= os.path.split(file)
        print  file, os.path.join(directory, filename[:3]+"_"+filename[3:])
        os.link(file, os.path.join(directory, filename[:3]+"_"+filename[3:]))

def readFits(file):
    d = {'az':-999.99,'derot':-999.99, 'at':0}
    types = {'az':float, 'derot':float, 'at':int}
    
    directory, fileName  = os.path.split(file);
    fileName, _ = os.path.splitext(fileName)
    infos  = fileName.split("_");
        
    for i in infos:
         m = re.match('([a-zA-Z]+)([0-9.+-]+)$', i)
         if m  is not None:
             key,strval= m.groups()
             key = key.lower()
             #print file, key, strval
             d[key] =types.get(key, float)(strval)
    print file, d
    data = fits.open(file)[0].data.copy()#[pl[0][1]:pl[1][1], pl[0][0]:pl[1][0] ];
    d['data']= data;
    d['file'] = file;
    return d

def runOut(centers):   
    r = max(  (max(centers[:,0]) - min(centers[:,0]))/2.0,  (max(centers[:,1]) - min(centers[:,1]))/2.0 ) 
    params = [np.mean( centers[:,0]), np.mean( centers[:,1]),  r]
    pout, pcov = curve_fit(circle, centers[:,0], centers[:,1], p0=params) 
    return  (pout[0], pout[1]), pout[2]

def circle(x,  x0,  y0, r ):
    return np.sqrt( r**2 - (x-x0)**2) + y0


def makeSynthetic(center, d):
    img = d['data']
    dCenter = getCenter(d)
    mask  = getMask(d)
    dx = center[0]-dCenter[0]
    dy = center[1]-dCenter[1]
    
    print dx,dy
    bckg = getConf(d['at'])['fluxTreshold'] * 0.95

    flatImg =  img.copy()
    flatImg[mask] = np.mean(img[mask])
    flatImg[~mask] = bckg
    
    newData = shift(flatImg,  [dy,dx], mode='constant', cval=bckg)
    
    newd = d.copy()
    newd['data'] = newData
    return newd


def readAllFits(files):
    return [readFits(file) for file in files]

def getMask(d):
    
    fluxTreshold = getConf(d['at'])['fluxTreshold']
    pupLocation = getConf(d['at'])['pupLocation']
    
    shape = d['data'].shape
    X, Y = np.meshgrid(range(shape[1]), range(shape[0]) )
    return (d['data']>fluxTreshold)   *  (X>pupLocation[0][0])  *  (X<pupLocation[1][0])  * (Y>pupLocation[0][1])  *  (Y<pupLocation[1][1])

def getCenter(d):
    mask = getMask(d);
    shape = mask.shape
    X, Y = np.meshgrid(range(shape[1]), range(shape[0]) )
    norm = float(np.sum(mask))
    x = np.sum(mask*X)/norm
    y = np.sum(mask*Y)/norm
    return x,y

def getCenters(allD):
    return np.array([getCenter(d) for d in allD])

def plotMask(d, ax=None):
    if ax is None: 
        ax = plt.gca();
    
    data = d['data']
    mask = getMask(d)
    ax.imshow(mask);
    ax.set_title("az {az:.0f} derot {derot:.0f}".format(**d))
    xc, yc = getCenter(d);
    ax.plot(xc, yc, 'k+');

def plotRunOut(allD, ax=None, leg=None, ttl="",fit=False):
    if ax is None: 
        ax = plt.gca();
    if ttl is None: ttl = title
    
    fmt = {None:"{az:.0f}, {derot:.0f}", "derot":"{derot:.0f}", "az":"{az:.0f}"}[leg]
    
    centers = getCenters(allD)
    
    ax.plot(centers[:,0], centers[:,1], 'k+-')
    ax.set_xlabel('X (pixel)')
    ax.set_ylabel('Y (pixel)')
    for d,c in zip(allD, centers):
        ax.text(  c[0],c[1], fmt.format(**d))
    if fit:
        (x0,y0), r = runOut(centers)
        alpha=np.linspace(0,2*np.pi, 100)
        ax.plot(  r*np.cos(alpha)+x0, r*np.sin(alpha)+y0,  'r-')  
        ax.plot( x0, y0,  'r*')
        ax.set_title('{x0:.2f},  {y0:.2f} runout {d:.2f}'.format(x0=x0,y0=y0,r=r,d=r*2)) 
    
def plotMasks(allD, figNum=None):
    N = len(allD)
    n  = int(N/np.sqrt(N))
    m = int(np.ceil(N/n))
    f, axes = plt.subplots(n,m, num=figNum)
    for d,ax in zip(allD,axes.flat):
        plotMask(d, ax=ax);
    

def increasingAz(allD):
    return sorted(allD, key=lambda x:x['az'] )

def increasingDerot(allD):
    return sorted(allD, key=lambda x:x['derot'] )

def byAt(allD):
    items = {}
    for d in allD:
        items.setdefault(  d['at'], []).append(d)
    return {k:v  for k,v in items.items() if len(v)>0}


def byAz(allD):
    items = {}
    for d in allD:
        items.setdefault(  d['az'], []).append(d)
    return {k:v  for k,v in items.items() if len(v)>1}


def byDerot(allD):
    items = {}
    for d in allD:
        items.setdefault(  d['derot'], []).append(d)
        
    return {k:v  for k,v in items.items() if len(v)>1}

def find(allD, az, derot):
    for d in allD:
        if d['az']==az and d['derot']==derot:
            return d
    return None




if __name__ == "__main__":
    #files = glob.glob(rootDir+"/M6*Az90*.fits")
   if len( sys.argv)<3:
       print """ Usage:  pupillRunOut  title   file1.fits  file2.fits file3.fits ... """
       exit()
   files = sys.argv[1:]
   
   allD =  increasingDerot(readAllFits(files))
   

   for j, (at,allAt) in enumerate( byAt(allD).items()): 
       
       plotMasks(allAt, figNum=j+1);
       
       plt.gcf().set_size_inches(6,9)
       plt.gcf().savefig( "at{at}_pupillMask.{ext}".format(at=at, ext=ext)  )
       

       for i, (az,lst) in enumerate( byAz(allAt).items()): 
           f = plt.figure(10*(j+1)+i);  plotRunOut(lst, leg="derot");
           plt.gca().set_title("AT{at} Az {az:.0f} ".format(az=az, at=at)+plt.gca().title.get_text())
           plt.gcf().savefig( "at{at}_Az{az:03d}.{ext}".format(at=at, ext=ext, az=int(az)) )
       
       for i, (derot,lst) in enumerate( byDerot(allAt).items()):        
           f = plt.figure(100*(j+1)+i);  plotRunOut(lst, leg="az", fit=True);
           plt.gca().set_title("AT{at} Derot {derot:.0f} ".format(at=at, derot=derot)+plt.gca().title.get_text())
           plt.gcf().savefig( "at{at}_Derot{derot:03d}.{ext}".format(at=at, ext=ext, derot=int(derot)) )
           
           
           
           d90  = find(lst, 90, 0)
           if d90:
               runoutCenter, _= runOut( getCenters(lst))
               synt = makeSynthetic(runoutCenter, d90)
               xs,ys =getCenter(synt)
               plt.gca().plot( xs, ys, 'b+')

               f, axes = plt.subplots(2,2)
               axes = axes.flat
               axes[0].imshow(d90['data'] , vmax=np.mean(d90['data'])*1.2  )
               axes[1].imshow(synt['data'])
               im = axes[2].imshow(   getMask(d90)*1.0 - getMask(synt)*1.0)
               plt.colorbar(im)

               fh = fits.HDUList( [fits.PrimaryHDU(synt['data']) ])
               fh.writeto("at{at}_synt_Az90_Derot000.fits".format(at=at), overwrite=True)
               
   plt.show()
