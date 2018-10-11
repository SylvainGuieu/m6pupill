import os
import numpy as np
from . import io, config

simulatedValues = {
    'derot':0.0, 
    'az':0.0
}

def ccdSetup(buffer):
    #buffer = dict(buffer,**ccdBuffer)
    return None

def  ccdStart():
    return None

def ccdWait():
    return None

def ccdStop():
    return None

def ccdInit():
    return None

def ccdOnline():
    None
    
def takeExposure(file='test.fits'):
    th = config.getTreshold()
    Nx, Ny = (1024,1024)
    pup = 200
        
    rd = np.pi/180
    data = np.random.random((Ny, Nx)) *(th*0.6)
    x,y = np.meshgrid(range(Nx), range(Ny))
    dx = 10*np.cos(getDerotPos()*rd*2) + 2*np.cos(getAzPos()*rd)
    dy = 10*np.sin(getDerotPos()*rd*2) + 2*np.sin(getAzPos()*rd)
    
    test =  ((x-Nx/2-dx)**2 + (y-Ny/2-dx)**2)<= (pup/2)**2
    data[test] = data[test] + th*2
    
    fh = io.fits.HDUList( io.fits.PrimaryHDU(data))
    fh.writeto(os.path.join(io.detdata(), file), overwrite=True)

def getImage():        
    tmpfile = '_tmpimg.fits'
    takeExposure(tmpfile)
    file = os.path.join(io.detdata(), tmpfile)
    fh = io.fits.open(file)
    data = fh[0].data.copy()
    header = fh[0].header.copy()
    fh.close()
    os.remove(file);
    return data, header
    

def moveDerot(angle):
    simulatedValues['derot'] = angle

def moveAz(angle):
    simulatedValues['az'] = angle
    

def getDerotPos():
    return simulatedValues['derot']    

def getAzPos():
    return simulatedValues['az']


