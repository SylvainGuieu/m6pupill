from . import plot
from . import config
from . import cmd
from . import io
from .pupill import M6PupillList, M6Pupill 
import numpy as np 

log = print

def runCheckFromPrompt(at=0):
    
    p = M6Pupill.fromCcd(header={'at':at})    
    plot.plotPupillCut(p, fig=plot.CUTFIG)
    
    conf = config.atConfLoockup[at]
    
    while input("Ok with threshold (y/n) ?: ").strip() != "y":
        configstr = input(" (1 value)=treshold (4 value)=box corner (5 value)=treshol dan dbox: ").strip()
        configs= [s.strip() for s in configstr.split(" ")]
        if len(configs)==1:
            conf['fluxTreshold'] = float(configs[0])
        elif len(configs)==5:
            conf['fluxTreshold'] = float(configs[0])
            conf['pupLocation'] [ [float(configs[1]), float(configs[2])],
                                  [float(configs[3]), float(configs[4])]]
        elif len(configs)==4:            
            conf['pupLocation'] = [ [float(configs[0]), float(configs[1])],
                                  [float(configs[2]), float(configs[3])]]
            
        p = M6Pupill.fromCcd(header={'at':at})    
        plot.plotPupillCut(p, fig=plot.CUTFIG)
        
    return True

def runFromPrompt(l=None):
    if l is None: l =  M6PupillList([])
    plot.runPlotStart()
    
    runCheckFromPrompt(at=config.getAt())
    
    while l.askNew():
        plot.runPlot(l)
    return l


def runDerot(l=None, angles=None, prefix="", az=None):
    if l is None: l =  M6PupillList([])

    if az is not None:
        log("rotating Azimuth to %.1f "%az, end="...")
        cmd.moveAz(az)
        log ("ok")
    else:
        az = -999.99
    
    angles = np.linspace(0, 360, int(360/15)+1) if angles is None else angles
    plot.runPlotStart()
    runCheckFromPrompt(at=config.getAt())
    for angle in angles:
        log("rotating to Derotator %.1f "%angle, end="...")
        cmd.moveDerot(angle)
        log ("ok")
        l.appendFromCcd(header={'derot':cmd.getDerotPos(), 'az':cmd.getAzPos()})
        if config.autoSaveImage:
            log("image saved", io.savePup(l[-1], prefix=prefix))
        plot.runPlot(l)
    return l

def runAz(l=None, angles=None, prefix="", derot=None):
    if l is None: l =  M6PupillList([])
    
    if derot is not None:
        log("rotating Derotator to %.1f "%derot, end="...")
        cmd.moveDerot(derot)
        log ("ok")
    else:
        derot = -999.99
    
    angles = np.linspace(0, 360, int(360/30)+1)[:-1] if angles is None else angles
    plot.runPlotStart()
    runCheckFromPrompt(at=config.getAt())
    
    for angle in angles:
        log("rotating Az to %.1f "%angle, end="...")
        cmd.moveAz(angle)
        log ("ok")
        if config.autoSaveImage:
            l.appendFromCcd(header={'derot':cmd.getDerotPos(), 'az':cmd.getAzPos()})
        log("image saved", io.savePup(l[-1], prefix=prefix))
        plot.runPlot(l)
    return l



def runAlign(refPupill, pause=1):

    fig = plot.figure(2); fig.clear()
    i = 0
    axes = None
    xlim = None
    while True:
        i += 1
        if axes:
            xlim = axes.get_xlim()
            ylim = axes.get_ylim()
            axes.clear()
        axes = plot.plotDifMask(M6Pupill.fromCcd(), refPupill, fig=2)
        if xlim:
            axes.set_xlim(xlim)
            axes.set_ylim(ylim)
            
        plot.showfig(fig)
        plot.plt.pause(pause)
        log('expo %d'%i)
        
        
    
    
    
