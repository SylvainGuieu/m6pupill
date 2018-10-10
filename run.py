from . import plot
from . import config
from .pupill import M6PupillList, M6Pupill 


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

def runFromPrompt(l=None, at=0):
    if l is None: l =  M6PupillList([])
    plot.runPlotStart()
    
    runCheckFromPrompt(at=at)
    
    while l.askNew():
        plot.runPlot(l)
        
    
    
