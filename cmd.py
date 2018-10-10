import ccs
import sys
import os
from . import io 
ccs.CcsInit()
ccdDefaultBuffer = {
    'DET.FRAM.FITSUNC':  "img.fits",
    #0 = 'none'    (image is not saved on disk)
    #1 = 'compressed'
    #2 = 'uncompressed'
    #3 = 'both'
    'DET.FRAM.FITSMTD': 2,
    
    'DET.EXP.TYPE': 'Normal',
    'DET.EXP.NREP': 1,
    'DET.WIN1.BINX': 1,
    'DET.WIN1.BINY': 1,
    'DET.FRAM.TYPE': 'Normal'
    
}

ccdBuffer = dict()

ccdEnv = "ccdconCI_ccdagfas"
rotEnv = "mvdrotServer"


def buffer2param(buffer):
    param = []
    for k, v in buffer.items():
        param += [k, str(v)]
    return ' '.join(param)


def ccdSetup(buffer):
    #buffer = dict(buffer,**ccdBuffer)
    return ccs.SendCommand("", ccdEnv, "SETUP", "-function "+buffer2param(buffer))

def  ccdStart():
    return ccs.SendCommand("", ccdEnv, "START")

def ccdWait():
    return ccs.SendCommand("", ccdEnv, "WAIT")

def ccdStop():
    return ccs.SendCommand("", ccdEnv, "STOP")

def ccdInit():
    ccs.SendCommand("", ccdEnv, "SETUP", "-expoId -1 -file ccdSetupComplete.det")

def ccdOnline():
    ccs.SendCommand("", ccdEnv, "ONLINE")
    
def takeExposure(file='test.fits'):
    if file:
        ccdSetup({'DET.FRAM.FITSUNC':file,  'DET.FRAM.FITSMTD': 2})
    ccdStart();
    ccdWait();    
    return os.path.join(io.detdata(), file)

def getImage():    
    ccdSetup({'DET.FRAM.FITSUNC':'_tmpimg.fits',  'DET.FRAM.FITSMTD': 2})
    ccdStart();
    ccdWait();
    file = os.path.join(io.detdata(), '_tmpimg.fits')
    fh = io.fits.open(file)
    data = fh[0].data.copy()
    header = fh[0].header.copy()
    fh.close()
    os.remove(file);
    return data, header


def moveDerot(angle):
    return ccs.SendCommand("", rotEnv, "SETDP", "%.0f"%angle)

