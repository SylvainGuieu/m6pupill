from tkinter import * 
from . import config
import matplotlib
import numpy as np
matplotlib.use('TkAgg')
from . import plot
from .pupill import M6PupillList,  M6Pupill
from . import run, io
from .api import *
from . import cmd


debug = True

PX = 4

def imageChangedGui(lst, current):    
    N = len(lst)
    if N:
        plot.runPlot(lst, current)
        runClock()
        
def tmpImageChangeGui(img):
    if img is None: return
    fig = plot.plt.figure(plot.TMPFIG); fig.clear()
    
    plot.plotPupillCut(img, fig=fig)
    plot.showfig(fig)

def parseBoxCorner(sval):
    vals = [s.strip() for s in sval.split(" ")]
    N = len(vals)
    if not (N==4 or N==3):
        raise ValueError('must be 3 or 4 elements')
        
    fvals = [float(v) for v in vals]
    
    w = fvals[2]
    h = w if len(fvals)==3 else fvals[3]
    if w<=0 or h<=0:
        raise ValueError('width and height must be >0')
    
    x1 = fvals[0]-w/2.0
    y1 = fvals[1]-w/2.0
    x2 = fvals[0]+h/2.0
    y2 = fvals[1]+h/2.0
    return [[x1,y1],[x2,y2]]

def getBoxCorner():
    b = config.getPupLocation()
    w = b[1][0]-b[0][0]
    h = b[1][1]-b[0][1]
    x = (b[0][0]+b[1][0])/2.0
    y = (b[0][1]+b[1][1])/2.0
    return "%.0f %.0f %.0f %.0f"%(x, y, w, h)

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
    
    return svout

clockVars = {}
def addToClock(var, getFunc):        
    clockVars[str(var)] = (var,getFunc)

def runClock():
    for (var,getFunc) in clockVars.values():
        var.set(getFunc())

class PupillConfFrame(Frame):
    def __init__(self,  master, **kwargs):
        Frame.__init__(self, master,  **kwargs)
                                
        def changeParam(f):
            def change(val):
                f(val)
                imageChanged()
            return change
        
        R=0    
        newEntry(self, "Treshold", changeParam(config.setTreshold), config.getTreshold, "", float, R)

        R += 1
        newEntry(self, "Box x0 y0 W H", changeParam(config.setPupLocation), getBoxCorner, "", parseBoxCorner, R)        

        R += 1
        derotVar = newEntry(self, "Derot (degree)", cmd.moveDerot, cmd.getDerotPos, "", float, R, mode="set", default=0.0)
        addToClock(derotVar,cmd.getDerotPos)

        R += 1
        azVar= newEntry(self, "Az (degree)", cmd.moveAz, cmd.getAzPos, "", float, R, mode="set", default=0.0)
        addToClock(azVar, cmd.getAzPos)
        

class RefreshFrame(Frame):
     def __init__(self,  master,  **kwargs):
        Frame.__init__(self, master, **kwargs)

        Label(self, text="Attach").pack(side=LEFT)
        refreshStatVar = BooleanVar(self)
        refreshStatVar.set(getRefreshState())
        refreshStatVar.trace('w', lambda *a,v=refreshStatVar: setRefreshState(v.get()))
        Checkbutton(self, text="Auto Refresh", variable=refreshStatVar).pack(side=LEFT)
        
        addToClock(refreshStatVar, getRefreshState)

        options = ["MANUAL", "LIVE"]
        optionVar = StringVar()
        optionVar.set(options[getRefreshState()])
        #optionVar
        
        
        Button(self, text="Refresh", command=newTmpImage).pack(side=LEFT, padx=PX)        
        runClock()
     
        
        
        
class ImageFrame(Frame):
    def __init__(self,  master,  **kwargs):
        Frame.__init__(self, master, **kwargs)
                
        counterVar = StringVar(self)
        counterVar.set(str(nImage()))

        indexVar = StringVar(self)
        indexVar.set(str(getIndex()+1))
        addToClock(counterVar, lambda self=self:  str(nImage()))
        addToClock(indexVar  , lambda self=self:  str(getIndex()+1))
        
            
        azVar = StringVar(self)
        fc = lambda self=self: getKeyStr(currentImage(), "az")
        azVar.set(fc())
        addToClock(azVar, fc)
        
        derotVar = StringVar(self)
        fc = lambda self=self: getKeyStr(currentImage(), "derot")
        derotVar.set(fc())
        addToClock(derotVar, fc)
        
        centerVar = StringVar(self)                    
        fc = lambda self=self: getCenterStr(currentImage())
        centerVar.set(fc())        
        addToClock(centerVar, fc)
        
        
        f1 = Frame(self)
        Label(f1, text="Counter").pack(side=LEFT)
        Label(f1, textvariable=counterVar).pack(side=LEFT)                        
        Button(f1, text="Measure", width=15, command=newImage).pack(side=LEFT,  padx=PX)
        Button(f1, text="Replace", width=15, command=replaceImage).pack(side=LEFT, padx=PX)

        f2 = Frame(self)
        Label(f2, textvariable=indexVar).pack(side=LEFT) 
        Button(f2, text="Prev", width=10, command=previousImage).pack(side=LEFT)
        Button(f2, text="Next", width=10, command=nextImage).pack(side=LEFT)
        Button(f2, text="Remove", width=10, command=removeImage).pack(side=LEFT)
        
        f3 = Frame(self)
        Label(f3, text="Az: ").pack(side=LEFT)
        Label(f3, textvariable=azVar).pack(side=LEFT)                        
        Label(f3, text="Derot: ").pack(side=LEFT)
        Label(f3, textvariable=derotVar).pack(side=LEFT)      
        Label(f3, text="Center: ").pack(side=LEFT)
        Label(f3, textvariable=centerVar).pack(side=LEFT) 
        
        
        f1.pack(side=TOP)
        f2.pack(side=TOP)
        f3.pack(side=TOP)
        
        imageChanged()
        
        
    def replot(self):
        imageChanged()        


class RunFrame(Frame):
    derotStep = 15
    azStep = 180
    
    def __init__(self,  master, **kwargs):
        Frame.__init__(self, master, **kwargs)
        
        fd = Frame(self)
        Label(fd, text="Derotator Run Out: ").pack(side=LEFT)  
        
        fdp = Frame(fd)     
        newEntry(fdp, "Step", self.setDerotStep, self.getDerotStep,
                      "deg.", float, 0, mode="auto", entryKw={'width':10})
        fdp.pack(side=LEFT)
        
        
        Button(fd, text="RUN", command=self.runDerot).pack(side=LEFT)        
        
        
        
        fa = Frame(self)
        Label(fa, text="Azimuth Run Out: ").pack(side=LEFT)  
        
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
        for angle in angles:
            log("rotating to Derotator %.1f "%angle, end="...")
            cmd.moveDerot(angle)
            log ("ok")
            newImage()
            if config.autoSaveImage:
                log("image saved", io.savePup(currentImage()))
    
    def runAz(self):
        log = print
        current = cmd.getAzPos()
        angles = np.linspace(current, 360+current, int(360/self.azStep)+1)[:-1]
        for angle in angles:
            log("rotating to Azimuth %.1f "%angle, end="...")
            cmd.moveAz(angle)
            log ("ok")
            newImage()
            if config.autoSaveImage:
                log("image saved", io.savePup(currentImage()))
                    
    
    
        
        
class MainFrame(Frame):
    def __init__(self,  master, **kwargs):
        Frame.__init__(self, master, **kwargs)
        PupillConfFrame(self).pack(side=TOP, pady=15)
        RefreshFrame(self).pack(side=TOP, pady=15)
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
    root.after(1000, clock)
    
def main(files=[]):  
    global root, refreshState
    refreshState = False
    addImageChangedTrace(imageChangedGui)
    addTmpImageTrace(tmpImageChangeGui)
    
    lst = M6PupillList([M6Pupill(file=file) for file  in files])
        
    setImageList(lst)
    
    root = Tk()   
    root.protocol("WM_DELETE_WINDOW", _delete_window)
    root.bind("<Destroy>", _destroy) 
    MainFrame(root).pack()
    Button(root, text="Quit", width=10, command=quitGui).pack(side=TOP,  pady=10)
    
    root.geometry("800x480+300+300")
    clock()
    root.mainloop()


if __name__ == '__main__':
    main()

