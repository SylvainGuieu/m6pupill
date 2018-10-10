import os
import re
from astropy.io import fits

keyTypes = {'az':float, 'derot':float, 'at':int}

def detdata():
    return os.path.join(os.environ['INS_ROOT'], "SYSTEM", "DETDATA")

def readFitsData(file):
     # read the data and add 
     directory, fileName  = os.path.split(file);
     fileName, _ = os.path.splitext(fileName)
     infos  = fileName.split("_");
     header = {}
     for i in infos:
         m = re.match('([a-zA-Z]+)([0-9.+-]+)$', i)
         if m  is not None:
             key,strval= m.groups()
             key = key.lower()                
             header[key] = keyTypes.get(key, float)(strval)
     fh = fits.open(file)[0];
     header = dict(fh.header, **header)
     data = fh.data.copy()     
     return data, header
 
def saveList(l, prefix=""):
    return [savePup(p,prefix=prefix) for p in l]

def savePup(p, prefix=""):
    h = dict(p.header,prefix=prefix)
    file = os.path.join(detdata(), "{prefix}AT{at:d}_Az{az:03.0f}_Derot{derot:03.0f}.fits".format(**h))
    fh = fits.HDUList([fits.PrimaryHDU(p.data)])
    fh.writeto(file, overwrite=True)
    return file
    



