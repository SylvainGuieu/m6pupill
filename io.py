import os
import re
from . import config
from astropy.io import fits
import datetime

keyTypes = {'az':float, 'derot':float, 'at':int}

def detdata():
    try:
        return os.path.join(os.environ['INS_ROOT'], "SYSTEM", "DETDATA")
    except KeyError:
        return "/tmp"

def readFitsData(file):
     # read the data and add 
     directory, fileName  = os.path.split(file);
     fileName, _ = os.path.splitext(fileName)
     infos  = fileName.split("_");
     params = {}
     for i in infos:
         m = re.match('([a-zA-Z]+)([0-9.+-]+)$', i)
         if m  is not None:
             key,strval= m.groups()
             key = key.lower()                
             params[key] = keyTypes.get(key, float)(strval)
    
     fh = fits.open(file)[0];
     header = fh.header.copy()
     for k,v in params.items():
         header.setdefault(k,v)
     
     data = fh.data.copy()     
     return data, header
 
def saveList(l, prefix=""):
    return [savePup(p,prefix=prefix) for p in l]

def savePup(p, prefix=""):
    h = p.header
    file = os.path.join(detdata(), "{prefix}AT{h[at]:d}_Az{h[az]:03.0f}_Derot{h[derot]:03.0f}_{day}.fits".format(h=h, prefix=prefix, day=getDayNumber()))
    file = newFile(file)
    fh = fits.HDUList([fits.PrimaryHDU(p.data, dict2fitsHeader(p.header))])
    fh.writeto(file, overwrite=True)
    return file

def newFile(file):
    directory, fileName = os.path.split(file)
    fileCore, ext = os.path.splitext(fileName)
    print(os.path.join(directory, fileCore, ext))
    if not os.path.exists(os.path.join(directory, fileCore+ext)):
        return file
    i =1
    while os.path.exists( os.path.join(directory, fileCore+("_%03d"%i)+ext)):
        i+=1
    return os.path.join(directory, fileCore+("_%03d"%i)+ext)
                          
        
    
    

def dict2fitsHeader(d):    
    hList = []
    headerDef = config.headerDef
    for k,v in d.items():
        try:
            vDef = headerDef[k]
        except KeyError:
            hList.append(fits.Card(k,v))
        else:
            hList.append(fits.Card(vDef[0],vDef[1](v), vDef[2]))
    return fits.Header(hList)


def getDayNumber():
    now = datetime.datetime.now()
    return (datetime.date(now.year, now.month, now.day) - datetime.date(now.year, 1, 1)).days + 1









