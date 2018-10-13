from . import plot
from . import config
try:
    from . import cmd
except:
    print('CSS in Simu')
    from . import cmdSimu as cmd

from . import io
from .image import ImageList, Image 
import numpy as np 

log = print
    
def runDerot(l=None, angles=None, prefix="", az=None, closure=1, callback=None):
    
    if l is None: l =  ImageList([])
    
    if az is not None:
        log("rotating Azimuth to %.1f "%az, end="...")
        cmd.moveAz(az)
        log ("ok")
    else:
        az = cmd.getAzPos()
    
    if angles is None:
        angles = np.linspace(0,360,360/15+1)
    
    plot.runPlotStart()
    #runCheckFromPrompt(at=config.getAt())
    for angle in angles:
        log("rotating to Derotator %.1f "%angle, end="...")
        cmd.moveDerot(angle)
        log ("ok")
        l.appendFromCcd(header={'derot':cmd.getDerotPos(), 'az':cmd.getAzPos()})
        if config.autoSaveImage:
            log("image saved", io.saveImage(l[-1], prefix=prefix))
        plot.runPlot(l)
        if callback: callback()
    return l

def runAz(l=None, angles=None, prefix="", derot=None, closure=False, callback=None):
    if l is None: l =  ImageList([])
    
    if derot is not None:
        log("rotating Derotator to %.1f "%derot, end="...")
        cmd.moveDerot(derot)
        log ("ok")
    else:
        derot = -999.99
    
    if angles is None:
        angles = np.linspace(0,360,360/30+1)[:-1]
        
    
    plot.runPlotStart()
    #runCheckFromPrompt(at=config.getAt())
    
    for angle in angles:
        log("rotating Az to %.1f "%angle, end="...")
        cmd.moveAz(angle)
        log ("ok")
        if config.autoSaveImage:
            l.appendFromCcd(header={'derot':cmd.getDerotPos(), 'az':cmd.getAzPos()})
        log("image saved", io.saveImage(l[-1], prefix=prefix))
        plot.runPlot(l)
        if callback: callback()
    return l

def runAlign(roCenter, pause=1, callback=None):    
    fig = plot.figure(plot.ALIGNFIG); fig.clear()
    fig, axesList = plt.subplots(1,2, num=fig.number)    
    i = 0    
    while True:
        i += 1
        plot.plotAlignImage(Image.fromCcd(), roCenter, axesList=axesList)                    
        plot.showfig(fig)
        plot.plt.pause(pause)
        log('expo %d'%i)
        
        
    
    
    
