from tkinter import *
import os
from . import config
import matplotlib
import numpy as np
matplotlib.use('TkAgg')
from . import plot
from .image import ImageList,  Image
from . import run, io
from .api import *
from . import cmd


debug = True
PX = 4
PY = 4

guiConfig = {
    'expoMode': '1',
    'expoModeList': ['1', 'forever'], 
    'expoRunning': False,
    'busy': False
}

def setExpoMode(mode):
    guiConfig['expoMode'] = mode

def getExpoMode():
    return guiConfig['expoMode']

def startExpo():
    guiConfig['expoRunning'] = True

def stopExpo():
    guiConfig['expoRunning'] = False

    
def measurementChangedGui(lst, current):    
    N = len(lst)
    if N:
        plot.runPlot(lst, current)
        runClock()
        
def tmpImageChangeGui(img):
    if img is None: return
    fig = plot.plt.figure(plot.TMPFIG); fig.clear()    
    plot.plotPupillCut(img, getMeasurementList(), fig=fig)
    plot.showfig(fig)
    if len(getMeasurementList())>1:
        fig = plot.plt.figure(plot.ALIGNFIG); fig.clear() 
        plot.plotAlign(img, getMeasurementList(), fig=fig)
        plot.showfig(fig)
    

def parseBoxCorner(sval):    
    vals = [s.strip() for s in sval.split(" ")]
    N = len(vals)
    if N==3:
        return [(float(vals[0]), float(vals[1])), float(vals[2])]
    if N==4:
        return [(float(vals[0]), float(vals[1])), float(vals[2]), float(vals[3])]
    else:
        raise ValueError('must be 3 or 4 elements')
    
    

def getBoxCorner():
    b = config.getBox()
    if len(b)==2:        
        return "%.0f %.0f %.0f"%(b[0][0], b[0][1], b[1])
    else:
        return "%.0f %.0f %.0f %.0f"%(b[0][0], b[0][1], b[1], b[2])

def getKey(p, key, empty=-99.99):
    if p is None: return empty        
    return p.header[key]

def getKeyStr(p, key, fmt=None):
    if p is None: return ""    
    if fmt:
        return fmt%(p.header[key])
    else:
        return str(p.header[key])

def getCenterStr(p):
    if p is None: return ""
    c = p.getCenter()
    if np.isnan(np.sum(c)): return "Nan"
    return ", ".join("%.2f"%v for v in c)

def getRefreshState():
    global refreshState
    return refreshState

def setRefreshState(val):
    global refreshState
    refreshState = val
    

CL, CE, CV, CU, CB = range(5); 
def newEntry(master, label, setFunc, getFunc,  unit="", dtype=float, row=0, mode="return", default=None, setKw={}, entryKw={}):
    svin  = StringVar(master)
    svout = StringVar(master)
    
    if default is None:
        svin.set(getFunc())
    else:
        svin.set(default)
    svout.set(getFunc())
    
    Label(master, text=label).grid(row=row, column=CL)
    entry = Entry(master, textvariable=svin, **entryKw)
    entry.grid(row=row,column=CE)
    Label(master, textvariable=svout, borderwidth=1).grid(row=row,column=CV)
    
    if unit:
        Label(master, text=unit).grid(row=row, column=CU)
        
    def update(*a, svin=svin, svout=svout, dtype=dtype, config=config, entry=entry):
        try:
            v = dtype(svin.get())
        except Exception as e:
            entry.configure(background="#ff0000")
            if debug: print(e)
        else:         
            entry.configure(background=master['background'])
            setFunc(v)
            svout.set(getFunc())
        
    if mode=="auto":        
        svin.trace('w', update)
    elif mode=="return":
        entry.bind("<Return>", update)
    elif mode=="set":
        kw = dict(setKw)
        kw.setdefault('text', "Set")
        kw.setdefault('width', 10)
        Button(master, command=update, **kw).grid(row=row, column=CB)
    else:
        raise ValueError('unknown mode %s must be "auto", "return", or "set"'%mode)
    
    return svout, svin, entry

clockVars = {}
def addToClock(var, getFunc):        
    clockVars[str(var)] = (var,getFunc)

def runClock():
    for (var,getFunc) in clockVars.values():
        var.set(getFunc())



        
class ComputingFrame(Frame):
    def __init__(self,  master, **kwargs):
        Frame.__init__(self, master,  **kwargs)
        
        def changeParam(f):
            def change(val):
                f(val)
                measurementChanged()
                imageChanged()
            return change
        
        
        f1 = Frame(self)
        
        R=0
        tresholdOutVar, tresholdInVar, _  = newEntry(f1, "Treshold", changeParam(config.setTreshold), config.getTreshold, "", float, R)
        addToClock(tresholdOutVar, config.getTreshold)
        
        R += 1
        boxOutVar, boxInVar, _ = newEntry(f1, "Box x0 y0 W H", changeParam(config.setBox), getBoxCorner, "", parseBoxCorner, R)
        addToClock(boxOutVar, getBoxCorner)
        
        R += 2
        options = ['Image Beacon', 'Pupill Beacon', 'M6 mirror']
        optionVar = StringVar(self)
        
        def setMode(*a, v=optionVar):
            mstr = v.get()
            if mstr[:2]=="M6":
                config.setCenterMode(config.M6MODE)
            elif mstr[:2]=="Pu":
                config.setCenterMode(config.M2BEACONMODE)
            else:
                config.setCenterMode(config.BEACONMODE)                
            measurementChanged()
            imageChanged()
            runClock()            
        
        def getMode(options=options):
            m = config.getCenterMode()
            if m == config.M6MODE:
                return options[2]
            elif m == config.M2BEACONMODE:
                return options[1]            
            else:
                return options[0]
        
        optionVar.set(getMode())        
        optionVar.trace('w', setMode)
        addToClock(optionVar, getMode)
        
        OptionMenu(self,optionVar, *options).pack(side=TOP)
        f1.pack(side=TOP)
        
class SetupFrame(Frame):
    def __init__(self,  master, **kwargs):
        Frame.__init__(self, master,  **kwargs)
        
        f1 = Frame(self)
        R = 0
        
        R += 1
        derotVar,_,_ = newEntry(f1, "Derot (degree)", cmd.moveDerot, cmd.getDerotPos, "", float, R, mode="set", default=0.0)
        addToClock(derotVar,cmd.getDerotPos)

        R += 1
        azVar, _, _= newEntry(f1, "Az (degree)", cmd.moveAz, cmd.getAzPos, "", float, R, mode="set", default=0.0)
        addToClock(azVar, cmd.getAzPos)

        Label(self, text="Setup").pack(side=TOP)
        f1.pack(side=TOP)
        

class ExpoFrame(Frame):
     def __init__(self,  master,  **kwargs):
        Frame.__init__(self, master, **kwargs)
        
        options = guiConfig['expoModeList']
        optionVar = StringVar(self)
        optionVar.set(getExpoMode())
        optionVar.trace('w', lambda *a,v=optionVar: setExpoMode(v.get()))

        Label(self, text="Exposure").pack(side=TOP)
        OptionMenu(self,optionVar, *options).pack(side=LEFT)

        Button(self, text="START", command=startExpo).pack(side=LEFT)
        Button(self, text="STOP",  command=stopExpo).pack(side=LEFT)
        
        #optionVar                
        runClock()
     
        
        
        
class ImageFrame(Frame):
    def __init__(self,  master,  **kwargs):
        Frame.__init__(self, master, **kwargs)
                
        counterVar = StringVar(self)
        counterVar.set(str(nMeasurement()))

        indexVar = StringVar(self)
        indexVar.set(str(getIndex()+1))
        addToClock(counterVar, lambda self=self:  str(nMeasurement()))
        addToClock(indexVar  , lambda self=self:  str(getIndex()+1))
        
            
        azVar = StringVar(self)
        fc = lambda self=self: getKeyStr(currentMeasurement(), "az")
        azVar.set(fc())
        addToClock(azVar, fc)
        
        derotVar = StringVar(self)
        fc = lambda self=self: getKeyStr(currentMeasurement(), "derot")
        derotVar.set(fc())
        addToClock(derotVar, fc)
        
        #centerVar = StringVar(self)                    
        #fc = lambda self=self: getCenterStr(currentMeasurement())
        #centerVar.set(fc())        
        #addToClock(centerVar, fc)

        
            
        
        f0 = Frame(self)
        Label(f0, text="Measurements ").pack(side=LEFT)
        Label(f0, textvariable=counterVar).pack(side=LEFT)    

        
        f1 = Frame(self)                                    
        Button(f1, text="Add", width=10, command=addImageToMeasurement).pack(side=LEFT,  padx=PX)
        Button(f1, text="Replace", width=10, command=replaceTmpImage).pack(side=LEFT, padx=PX)
        
        
        f2 = Frame(self)
        f22 = Frame(self)
        Button(f22, text="Prev", width=10, command=previousMeasurement).pack(side=LEFT, padx=PX)
        Button(f22, text="Next", width=10, command=nextMeasurement).pack(side=LEFT, padx=PX)
        Button(f2, text="Remove", width=10, command=removeMeasurement).pack(side=LEFT, padx=PX)
        Button(f2, text="Save",width=10, command=saveMeasurement).pack(side=LEFT, padx=PX)
        Button(f2, text="Save All",width=10, command=saveAll).pack(side=LEFT, padx=PX)
        
        
        f3 = Frame(self)
        Label(f3, text="#").pack(side=LEFT)
        Label(f3, textvariable=indexVar).pack(side=LEFT) 
        Label(f3, text="Az: ").pack(side=LEFT)
        Label(f3, textvariable=azVar).pack(side=LEFT)                        
        Label(f3, text="Derot: ").pack(side=LEFT)
        Label(f3, textvariable=derotVar).pack(side=LEFT)      
        #Label(f3, text="Center: ").pack(side=LEFT)
        #Label(f3, textvariable=centerVar).pack(side=LEFT) 
        
        f0.pack(side=TOP, pady=PY)        
        f1.pack(side=TOP, pady=PY)
        f2.pack(side=TOP, pady=PY)
        f22.pack(side=TOP, pady=PY)
        f3.pack(side=TOP, pady=PY)
        
        lb = Listbox(self, selectmode=SINGLE, height=5, width=40)
        def updatelb(*a, lb=lb):
            lb.delete(0, lb.size())
            for i,p in enumerate(getMeasurementList(), start=1):
                if p.file:
                    _, file = os.path.split(p.file)
                else:
                    file = ""
                lb.insert(i, "{i:3d} {h[az]:5.1f} {h[derot]:5.1f} {file}".format(i=i, h=p.header, file=file))
            lb.activate(getIndex())
        
        def onSelected(*a, lb=lb):
            selected = lb.get(lb.curselection())
            strnum, _, _ = selected.strip().partition(" ")
            selectMeasurement(int(strnum)-1)
        
        lb.bind('<<ListboxSelect>>', onSelected)
        lb.pack(side=TOP)
        addMeasurementChangedTrace(updatelb)
        measurementChanged()
        
        
    def replot(self):
        measurementChanged()        


class RunFrame(Frame):
    derotStep = 15
    azStep = 180
    
    def __init__(self,  master, **kwargs):
        Frame.__init__(self, master, **kwargs)
        
        Label(self, text="Sequence").pack(side=TOP)  
        fd = Frame(self)
        Label(fd, text="Derotator : ").pack(side=LEFT)  
        
        fdp = Frame(fd)     
        newEntry(fdp, "Step", self.setDerotStep, self.getDerotStep,
                      "deg.", float, 0, mode="auto", entryKw={'width':10})
        fdp.pack(side=LEFT)
        
        
        Button(fd, text="RUN", command=self.runDerot).pack(side=LEFT)        
        
        
        
        fa = Frame(self)
        Label(fa, text="Azimuth : ").pack(side=LEFT)  
        
        fdp = Frame(fa)     
        newEntry(fdp, "Step", self.setAzStep, self.getAzStep,
                      "deg.", float, 0, mode="auto", entryKw={'width':10})
        fdp.pack(side=LEFT)
        
        Button(fa, text="RUN", command=self.runAz).pack(side=LEFT)
        
        
        fd.pack(side=TOP)
        fa.pack(side=TOP)
        
    def setAzStep(self, azStep):
        self.azStep = azStep
    def getAzStep(self):
        return self.azStep
    
    def setDerotStep(self, azStep):
        self.derotStep = derotStep
    
    def getDerotStep(self):
        return self.derotStep
    
    def runDerot(self):
        log = print
        current = cmd.getDerotPos()
        angles = np.linspace(current, 360+current, int(360/self.derotStep)+1)
        stopExpo()
        for angle in angles:
            log("rotating to Derotator %.1f "%angle, end="...")
            cmd.moveDerot(angle)
            log ("ok")            
            grabImage()
            addImageToMeasurement()
            if config.autoSaveImage:
                log("image saved", io.saveImage(currentMeasurement()))
    
    def runAz(self):
        log = print
        current = cmd.getAzPos()
        angles  = np.linspace(current, 360+current, int(360/self.azStep)+1)[:-1]
        stopExpo()
        for angle in angles:
            log("rotating to Azimuth %.1f "%angle, end="...")
            cmd.moveAz(angle)
            log ("ok")
            grabImage()
            addImageToMeasurement()
            if config.autoSaveImage:
                log("image saved", io.saveImage(currentMeasurement()))
                    
    
    
        
        
class MainFrame(Frame):
    def __init__(self,  master, **kwargs):
        Frame.__init__(self, master, **kwargs)
        ComputingFrame(self).pack(side=TOP, pady=15)
        SetupFrame(self).pack(side=TOP, pady=15)
        ExpoFrame(self).pack(side=TOP, pady=15)
        ImageFrame(self).pack(side=TOP, pady=15)
        RunFrame(self).pack(side=TOP, pady=15)     

def quitGui():
    global root
    plot.plt.close('all')
    try:
        root.destroy()
    except:
        pass    
def _delete_window():
    quitGui()    
    
def _destroy(event):
    quitGui()

def clock():
    global root
    runClock()
    if guiConfig['expoRunning']:        
        grabImage()
        if not guiConfig['expoMode']=="forever": guiConfig['expoRunning'] = False
        
    
    root.after(1000, clock)
    
def main(files=[]):  
    global root, refreshState
    refreshState = False
    addMeasurementChangedTrace(measurementChangedGui)
    addNewImageTrace(tmpImageChangeGui)
    
    lst = ImageList([Image(file=file) for file  in files])
        
    setMeasurementList(lst)
    
    root = Tk()   
    root.protocol("WM_DELETE_WINDOW", _delete_window)
    root.bind("<Destroy>", _destroy) 
    MainFrame(root).pack()
    Button(root, text="Quit", width=10, command=quitGui).pack(side=TOP,  pady=10)
    
    root.geometry("715x800+300+300")
    clock()
    root.mainloop()


if __name__ == '__main__':
    main()

