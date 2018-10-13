import os
import time

simulate = False

M6MODE = 1
BEACONMODE, M2BEACONMODE, M6MODE = range(3)


atConfLoockup = {# loockup by at
    M6MODE : {
        1: dict(  fluxTreshold = 1550,  box = [(524.5, 537.0), 315] ), 
        2: dict(  fluxTreshold = 1550,  box = [(524.5, 525.0), 315] ),
        3: dict(  fluxTreshold = 2050,  box = [(525.0, 476.5), 315] ),
        4: dict(  fluxTreshold = 2250,  box = [(550.0, 370.5), 315] ),
        0: dict(  fluxTreshold = 1550,  box = [(512,   512.0), 315] )
    },
    M2BEACONMODE : {
        1: dict(  fluxTreshold = 1550,  box = [(524.5, 537.0), 315] ), 
        2: dict(  fluxTreshold = 1550,  box = [(524.5, 525.0), 315] ),
        3: dict(  fluxTreshold = 2050,  box = [(550.0, 488.5), 315] ),
        4: dict(  fluxTreshold = 2250,  box = [(550.0, 370.5), 315] ),
        0: dict(  fluxTreshold = 1550,  box = [(512,   512.0), 315] )
    },
    BEACONMODE : {
        1: dict(  fluxTreshold = 0.0,  box = [(524.5, 537.0), 150] ), 
        2: dict(  fluxTreshold = 0.0,  box = [(524.5, 525.0), 150] ),
        3: dict(  fluxTreshold = 0.0,  box = [(555.0, 392.0), 150] ),
        4: dict(  fluxTreshold = 0.0,  box = [(550.0, 370.5), 150] ),
        0: dict(  fluxTreshold = 0.0,  box = [(512,   512.0), 150] )
    }        
}

centerMode = M6MODE
startupTime = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())


def setTreshold(treshold, at=None, centerMode=None):
    at = getAt() if at is None else at
    centerMode = getCenterMode() if centerMode is None else centerMode
    
    atConfLoockup[centerMode][at]['fluxTreshold'] = treshold

def getTreshold(at=None, centerMode=None):
    at = getAt() if at is None else at
    centerMode = getCenterMode() if centerMode is None else centerMode
    return atConfLoockup[centerMode][at]['fluxTreshold']

def setBox(loc, at=None, centerMode=None):
    at = getAt() if at is None else at
    centerMode = getCenterMode() if centerMode is None else centerMode        
    atConfLoockup[centerMode][at]['box'] = loc

def getBox(at=None, centerMode=None):
    at = getAt() if at is None else at
    centerMode = getCenterMode() if centerMode is None else centerMode
    return atConfLoockup[centerMode][at]['box']

def getCenterMode():
    global centerMode
    return centerMode
    
def setCenterMode(mode):
    global centerMode
    centerMode = mode

defaultAt = 0
def getAt():
    try:
        return int(os.environ['TCSID'])
    except:
        return defaultAt


headerDef = {
    'az':('AZ', float, '[deg]Azimuth position'),
    'derot':('DEROT', float, '[deg] Derotator position'),
    }
keyLoockup = {d[0]:k for k,d in headerDef.items()}

autoSaveImage = True
