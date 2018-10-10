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
 




