import ccs
import sys
import os
from . import io 
from . import config
import math
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

ccdServer = "ccdconCI_ccdagfas"
getCcdEnv = lambda : ""

rotServer = "mvdrotServer"
getRotEnv = lambda : "lat%dfsm"%config.getAt()

azServer = "azServer"
getAzEnv =  lambda : "lat%daz"%config.getAt()

azDbParams = {
    'pos':':Appl_data:TCS:LCU:az:altaz:POSLOOP.pos'
}

rotDbControlPoint = '<alias>mvdrot:control:motor:motorD:motor'
rotDbParams = {
    'posUser': rotDbControlPoint+".posUser",
    'state': '<alias>mvdrot.state',
    'substate': '<alias>mvdrot.substate'
    }



def buffer2param(buffer):
    param = []
    for k, v in buffer.items():
        param += [k, str(v)]
    return ' '.join(param)


def ccdSetup(buffer):
    #buffer = dict(buffer,**ccdBuffer)
    return ccs.SendCommand(getCcdEnv(), ccdServer, "SETUP", "-function "+buffer2param(buffer))

def  ccdStart():
    return ccs.SendCommand(getCcdEnv(), ccdServer, "START")

def ccdWait():
    return ccs.SendCommand(getCcdEnv(), ccdServer, "WAIT")

def ccdStop():
    return ccs.SendCommand(getCcdEnv(), ccdServer, "STOP")

def ccdInit():
    ccs.SendCommand(getCcdEnv(), ccdServer, "SETUP", "-expoId -1 -file ccdSetupComplete.det")

def ccdOnline():
    ccs.SendCommand(getCcdEnv(), ccdServer, "ONLINE")
    
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
    return ccs.SendCommand(getRotEnv(), rotServer, "SETDP", "%.4f"%angle)

def moveAz(angle):
    return ccs.SendCommand(getAzEnv(), azServer, "PRESET", "abs,%.4f,600"%angle)

def getDerotPos():
    return ccs.DbRead(rotDbParams['posUser'])

def getAzPos():
    return ccs.DbRead(azDbParams['pos'])*180/math.pi


