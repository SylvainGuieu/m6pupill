
import re
import os
import numpy as np
import time

from . import compute 
from . import io
from . import config
from . import cmd


from scipy.ndimage.interpolation import shift
import glob


class Image:
    _fluxTreshold = None
    _box  = None
    _centerMode = None
    file = None
    def __init__(self, file=None, data=None, header=None):
        
        header = {} if header is None else header
        
        if file is not None:
            self.data, fitsHeader = io.readFitsData(file)            
            self.file = file            
            fitsHeader.update(header)
            header = fitsHeader
        else:
            self.data = data
        self.header = header
        for k, v in {'az':-999.99,'derot':-999.99, 'at':config.getAt()}.items():
            self.header.setdefault(k,v)
    
    def getHash(self):
        """ In the context of derot return a string representing best the object 
            
            Two objects with the same hash can be considered as equal 
        """
        return "at{d[at]:d}az{h[az]:.1f}derot{h[az]:.1f}"
            
    @classmethod
    def fromCcd(cl, header=None):
        data, h = cmd.getImage()
        header = h if header is None else dict(header, **h)
        if header.get("az", None) is None: header['az'] = cmd.getAzPos()
        if header.get("derot", None) is None: header['derot'] = cmd.getDerotPos()        
        return cl(data=data, header=header)
    
    @property
    def at(self):
        return self.header['at']

    @property
    def az(self):
        return self.header['az']

    @property
    def derot(self):
        return self.header['derot']
        
    @property
    def fluxTreshold(self):
        
        return config.getTreshold(self.at, self.centerMode) if self._fluxTreshold is None else self._fluxTreshold

    @property
    def boxLocation(self):
        return compute.box2location(self.box)
        
    @boxLocation.setter
    def boxLocation(self, loc):
        self.box = compute.location2box(loc)
    
    @property
    def box(self):
        return config.getBox(self.at, self.centerMode) if self._box is None else self._box
    
    @box.setter
    def box(self, loc):
        self._box = loc
    
        
    @fluxTreshold.setter
    def fluxTreshold(self, t):
        self._fluxTreshold = t
    
    @property
    def centerMode(self):
        return config.getCenterMode() if self._centerMode is None else self._centerMode
    
    @centerMode.setter
    def centerMode(self, mode):
        self._centerMode = mode
    
    def getCenter(self):
        if self.centerMode == config.M6MODE:
            return compute.pupillCenter(self.getMask())
        else:
            img, offset = self.getSubImage()
            mask, _ = self.getSubMask()
            return compute.spotCenter(img*mask, offset)
    
    def getSubImage(self):        
        (x0,y0),(x1,y1) = self.boxLocation
        return self.data[y0:y1,x0:x1], (x0,y0)

    def getSubMask(self):        
        (x0,y0),(x1,y1) = self.boxLocation
        m = self.getMask()
        return m[y0:y1,x0:x1], (x0,y0)
    
    def getRadius(self):
        return compute.radius(self.getMask())
        
    def getMask(self):
        
        shape = self.data.shape
        X, Y = np.meshgrid(range(shape[1]), range(shape[0]) )
        
        (x0,y0),(x1,y1) = self.boxLocation
        return (self.data>self.fluxTreshold)   *\
            (X>x0) * (X<x1)  *\
            (Y>y0) * (Y<y1)
    
    def synthesize(self, center, bckg=None, flux=None):
        img = self.data
        dCenter = self.getCenter()
        mask  = self.getMask()
        
        dx = center[0]-dCenter[0]
        dy = center[1]-dCenter[1]
        
        
        bckg = self.fluxTreshold * 0.95 if bckg is None else bckg
        flux = np.mean(img[mask]) if flux is None else flux

        flatImg =  img.copy()
        flatImg[mask]  = flux
        flatImg[~mask] = bckg        
        newData = shift(flatImg,  [dy,dx], mode='constant', cval=bckg)        
        return Image(data=newData, header=dict(self.header))             
    
class ImageList:
    
    def __init__(self, iterable):
        self.lst = list(iterable)
            
    def append(self, p):
        self.lst.append(p)
    
    def appendFromCcd(self, header=None):
        self.append(Image.fromCcd(header=header))
    
    def extend(self, iterable):
        self.lst.extend(iterable)
        
    def replace(self, new):
        N = len(self)
        newHash = new.getHash()
        for i,p in enumerate(self[::-1]):            
            if p.getHash()==newHash:
                self.lst[N-i-1] = new
                return N-i-1
        
        self.append(new)
        return len(self)-1
        
    def sortedKey(self, k):
        return self.__class__(sorted(self, key=lambda p, k=k: p.header[k]))  

    def getRunout(self, rtype="az"):
        return compute.runout(self.getCenters(), [p.header[rtype] for p in self])
    
    def byKey(self, key, nMin=1, ndigits=0):
        items = {}
        for p in self.lst:
            items.setdefault(round(p.header[key],ndigits), self.__class__([])).append(p)
        if nMin>1:
            items = {k:v  for k,v in items.items() if len(v)>=nMin}
        return items
    
    def byAt(self):
        return self.byKey('at',1,0)

    def byAz(self):
        return self.byKey('az',2,0)

    def byDerot(self):
        return self.byKey('derot', 2, 0)

    def increasingKey(self, key):
        return self.__class__(sorted(self.lst, key=lambda x:x.header[key] ))

    def increasingAz(self):
        return self.increasingKey('az')

    def increasingDerot(self):
        return self.increasingKey('derot')

    def find(self, az=0.0, derot=0.0):
        for p in self.lst:
            if p.az==az and p.derot==derot:
                return p
        return None
    
    def getCenters(self):
        return np.array([p.getCenter() for p in self])
    
    def getTable(self):
        header = "#{N:3s} {az:6s} {derot:6s}".format(N="N", az="Az", derot="derot")
        tbl = ["{N:4d} {p.az:6.1f} {p.derot:6.1f}".format(N=i, p=p) for i,p in enumerate(self)]
        return header, tbl
    
    def __iter__(self):
         return self.lst.__iter__()

    def __getitem__(self, item):
         out = self.lst[item]
         if hasattr(out, "__iter__"):
             return self.__class__(out)
         return out

    def __len__(self):
        return len(self.lst)
    
    @classmethod
    def fromGlob(cl, glb, header=None):
        return cl((Image(file, header=header) for file in glob.glob(glb)))
    
        
    
