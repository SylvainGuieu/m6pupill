import os

simulate = True

atConfLoockup = { # loockup by at 
     1: dict( fluxTreshold = 1550,  pupLocation =  [ [367,404], [682,670]] ), 
     2: dict( fluxTreshold = 1550,  pupLocation = [ [367,350], [682,700]] ), 
     3: dict(  fluxTreshold = 2050,  pupLocation = [ [380,345], [720,632]] ), 
     4: dict(  fluxTreshold = 2250,  pupLocation = [ [400,230], [700,511]] ), 
     0:  dict( fluxTreshold = 1550,  pupLocation =  [ [380,404], [682,670]] ), 
}

def setTreshold(treshold, at=None):
    at = getAt() if at is None else at
    atConfLoockup[at]['fluxTreshold'] = treshold

def getTreshold(at=None):
    at = getAt() if at is None else at
    return atConfLoockup[at]['fluxTreshold']

def setPupLocation(loc, at=None):
    at = getAt() if at is None else at
    atConfLoockup[at]['pupLocation'] = loc

def getPupLocation(at=None):
    at = getAt() if at is None else at
    return atConfLoockup[at]['pupLocation']
    

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
