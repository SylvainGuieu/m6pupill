from matplotlib.pylab import *
from . import compute, config

CUTFIG = 1
TMPFIG = 2
ALIGNFIG = 3

def getAxes(axes, fig):
    if axes is None:
        if fig is None:        
            return gca(), gcf()
        else:
            fig = getFigure(fig)
            return fig.add_subplot(1,1,1), fig
    
    else:        
        if fig is None:            
            return axes, axes.figure
        else:
            return axes, fig

def getFigure(fig):
    if fig is None:
        return gcf()
    if isinstance(fig, int):
        return figure(fig)
    else:
        return fig 

def plotPupillCut(p, l=None, fig=None):
    fig = getFigure(fig)
    fig.clear()
    fig, axes = plt.subplots(2,2, num=fig.number);
    plotPupill(p, axes=axes[0][0])
    plotCut(p, "y", axes=axes[0][1])
    plotCut(p, "x", axes=axes[1][0])
    if p.centerMode==config.M6MODE:
        plotMask(p, axes=axes[1][1])
    else:
        plotSubImage(p, axes=axes[1][1])

    plotCenter(p.getCenter(),axes=axes[1][1])
    if l:
        plotRunOutCenters(l, axes=(axes[0][0],axes[1][1]))       
    return fig

def plotImageAlign(p, roCenter, axesList=None, fig=None):
    if axesList is None:
        fig = getFigure(fig)        
        fig.clear()
        fig, axesList = plt.subplots(1,2, num=fig.number);
    axesList = axesList.flat
    [a.clear() for a in axesList]
    
    plotSubImage(p, axes=axes[0])
    pc = p.getCenter()
    plotCenter(pc, axes=axes[0], color="black")
    
    if roCenter is None or np.isnan(np.mean(roCenter)):
        axes[1].text(0.0, 0.0, "Cannot compute RunOut center")
        return fig
    plotCenter(roCenter, axes=axes[0], color="red")
    
    if p.centerMode == config.M6MODE:        
        sy = p.synthesize(roCenter)
        plotSubDifMask(p, sy, axes=axes[1])
        plotCenter(pc, axes=axes[0], color="red")
        plotCenter(roCenter, axes=axes[0], color="red")
        
    else:
        x = [roCenter[0], pc[0]]
        y = [roCenter[1], pc[1]]
        r = np.sqrt( (x[0]-x[1])**2 + (y[0]-y[1])**2)
        axes[1].plot(x, y, "-+k")
        size = max( r*2, 10)*1.2
        axes.set_xlin( roCenter[0]-size/2.0, roCenter[0]+size/2.0)
        axes.set_ylin( roCenter[1]-size/2.0, roCenter[1]+size/2.0)        
    return axesList
    
def plotAlign(p, l, fig=None, derotTol=0.1):
    
    fig = getFigure(fig)        
    fig.clear()
    fig, axes = plt.subplots(1,2, num=fig.number);
        
    axes = axes.flat
    if l is None or not l:
        axes[0].text(0.0, 0.0, "Not enough measurements")
        return fig
    d = l.byDerot()
    for r, subl in d.items():
        if np.abs(p.derot-r) <= derotTol:
            break
    else:
        axes[0].text(0.0, 0.0, "Cannot find measurements for current Rotator pos")
        return fig    
    roCenter, r = subl.getRunout()
    plotImageAlign(p, roCenter, axesList=axes)
    return fig 
    
    
    
def plotCut(p, direction, slc=None, axes=None, fig=None):
    axes, fig = getAxes(axes, fig)
    data = p.data
    c = p.getCenter()
    direction = direction.lower()
    if  len(direction)<2:
        direction = direction+direction

    (x0,y0),(x1,y1) = p.boxLocation 
    if isnan(np.sum(c)):               
        c = (x0+x1)/2.0, (y0+y1)/2.0
    
    if slc is None:
        slc = slice(0, None)
    if direction[0]=="x":
        data = data[int(round(c[1])),slc]
    elif direction[0]=="y":
        data = data[slc,int(round(c[0]))]
    else:
        raise KeyError('unknown direction%s must be x or y'%direction)
    if direction[1]=='x':
        axes.plot(data,'k-')
        if p.centerMode == config.M6MODE:
            axes.axhline(p.fluxTreshold, color='red')
    else:
        axes.plot(data, np.arange(len(data)), 'k-')
        if p.centerMode == config.M6MODE:               
            axes.axvline(p.fluxTreshold, color='red')
    return axes

def plotSubImage(p, axes=None, fig=None):
    axes, fig = getAxes(axes, fig)
    data, (x0,y0) = p.getSubImage()
    h,w = data.shape
    
    extent = (x0, x0+w, y0, y0+w)
    axes.imshow(data, origin='lower', extent=extent);

def plotSubMask(p, axes=None, fig=None):
    axes, fig = getAxes(axes, fig)
    data, (x0,y0) = p.getSubMask()
    h,w = data.shape
    extent = (x0, x0+w, y0, y0+w)
    axes.imshow(data, origin='lower', extent=extent);
    
    
def plotPupill(p, axes=None, fig=None):
    axes, fig = getAxes(axes, fig)
    axes.imshow(p.data, origin='lower');
    loc = p.boxLocation
    x = [loc[0][0], loc[1][0],  loc[1][0], loc[0][0], loc[0][0]]
    y = [loc[0][1], loc[0][1], loc[1][1], loc[1][1], loc[0][1]]
    axes.plot( x,  y, 'k-')
    plotCenter(p.getCenter(), axes=axes)
    return axes

def plotCenter(center, axes=None, fig=None, size=10, color="black"):
    if center is None: return
    if np.isnan(np.mean(center)): return
    axes, fig = getAxes(axes, fig)
    x,y = center
    axes.plot([x-size/2.0,  x+size/2.0], [y,y], '-', color=color)
    axes.plot([x,x], [y-size/2.0,  y+size/2.0], '-', color=color)
    return axes


def plotRunOutCenters(lst,  axes=None, fig=None, size=10, color="red"):
    #if not isinstance(axes, (list,tuple)):
    if not hasattr(axes, "__iter__"):
        axes, fig = getAxes(axes, fig)
        axes = [axes]
    
    for derot, l in lst.byDerot().items():
        if len(l)<2: continue
        try:
            c,r = l.getRunout()
        except Exception as e:
            print(e)
            return axes[0]
        
        if c is None: continue
        if np.isnan(np.mean(c)): continue
        
        for ax in axes:
            plotCenter(c, axes=ax, size=size, color=color)    
    return axes[-1]

def plotMask(p, axes=None, fig=None):
    axes, fig = getAxes(axes, fig)
        
    mask = p.getMask()
    axes.imshow(mask, origin='lower');
    axes.set_title("az {h[az]:.0f} derot {h[derot]:.0f}".format(h=p.header))
    plotCenter(p.getCenter(), axes=axes)
    
    radius = p.getRadius();
    alpha = np.linspace( 0, 2*pi, 50)
    #axes.plot( radius*np.cos(alpha)+xc, radius*np.sin(alpha)+yc, 'r-') 
    
    return axes

def plotDifMask(p1, p2, axes=None, fig=None):
    axes, fig = getAxes(axes, fig)
    m2 = p2.getMask()
    m1 = p1.getMask()
    dMask = m1*1-m2*1
    norm = np.sum(m2)
    prop = np.abs(np.sum(~dMask[m2])/norm)
    
    
    axes.imshow(dMask, origin='lower');
    axes.set_title("%.4f%%"%(prop*100))
    return axes

def plotSubDifMask(p1, p2, axes=None, fig=None):
    axes, fig = getAxes(axes, fig)

    m2, (x0,y0) = p2.getSubMask()
    m1, _ = p1.getSubMask()

    dMask = m1*1-m2*1
    norm = np.sum(m2)
    prop = np.abs(np.sum(~dMask[m2])/norm)
    
    h,w = dMask.shape
    extent = (x0, x0+w, y0, y0+w)
    axes.imshow(dMask, origin='lower', extent=extent);
    axes.set_title("%.4f%%"%(prop*100))
    return axes

def plotRunOut(l, axes=None, fig=None, leg=None, title="",fit=False):    
    axes, fig = getAxes(axes, fig)
    
    if leg is None:
        if len(set([p.az for p in l]))==1: leg="derot"
        elif len(set([p.derot for p in l]))==1: leg="az"
    
    ttl = "at: "+", ".join(set(["%d"%p.at for p in l]))
    if leg=="derot":
        fmt = "{h[derot]:.0f}"
        ttl  += " Az: "+", ".join(set(["%.0f"%p.az for p in l]))
    elif leg=="az":
        fmt  = "{h[az]:.0f}"
        ttl += " Derot: "+", ".join(set(["%.0f"%p.derot for p in l]))
    else:
        fmt = "{h[az]:.0f}, {h[derot]:.0f}"

    
    centers = l.getCenters()
        
    axes.plot(centers[:,0], centers[:,1], 'k+-')
    axes.set_xlabel('X (pixel)')
    axes.set_ylabel('Y (pixel)')
    axes.set_title(title+" "+ttl)
    
    for p,c in zip(l, centers):
        if not np.isnan(np.sum(c)):
            axes.text(  c[0],c[1], fmt.format(h=p.header))
    
    if fit and len(l)>=2:
        (x0,y0), r = compute.runout(centers, [p.az for p in l])
        
        alpha = np.linspace(0,2*np.pi, 100)
        if not np.isnan(r):
            axes.plot(  r*np.cos(alpha)+x0, r*np.sin(alpha)+y0,  'r-')
        if not np.isnan(x0):
            axes.plot( x0, y0,  'r*')
        if p.centerMode == config.M6MODE:
            pupDiam = np.mean( [p.getRadius() for p in l])*2
            runOut = r*2/pupDiam * 100
            axes.set_title('{x0:.2f},  {y0:.2f} runout {d:.2f} / {pupDiam:.0f} pixels => {runOut:.2f}%'.format(x0=x0,y0=y0,r=r,d=r*2, pupDiam=pupDiam, runOut=runOut))
        else:
           axes.set_title('{x0:.2f},  {y0:.2f} runout {d:.2f} pixels'.format(x0=x0,y0=y0,r=r,d=r*2)) 
    return axes


def plotMasks(l, fig=None):
    fig = getFigure(fig)
    N = len(l)
    n  = int(N/np.sqrt(N))
    m = int(np.ceil(N/n))
    f, axes = plt.subplots(n,m, num=fig.number)
    for d,ax in zip(l,axes.flat):
        plotMask(d, axes=ax)
    return fig
    



shownFigure= set()
def runPlotStart():
    global shownFigure
    plt.figure(CUTFIG).show()
    shownFigure= set([CUTFIG])

def showfig(fig, always=False):
    global shownFigure
    if fig.number not in shownFigure:
        fig.show()
        shownFigure.add(fig.number)
    elif always:
       fig.show()
    fig.canvas.draw()
    
def runPlot(l, p=None):
    if p is None: p = l[-1]
    fig = plt.figure(CUTFIG); fig.clear()
    plotPupillCut(p, l, fig=fig)
    showfig(fig)
    
    for i,(derot,laz) in enumerate(l.byDerot().items()):
        laz = laz.sortedKey('az') 
        fnum = (i+1)*10
        fig = plt.figure(fnum); fig.clear()
        fig = plotRunOut(laz,fit=True,fig=fnum).figure
        showfig(fig)
        
    for i,(derot,lderot) in enumerate(l.byAz().items()):
        lderot = lderot.sortedKey('derot') 
        fnum = (i+1)*100
        fig = plt.figure(fnum); fig.clear()
        fig = plotRunOut(lderot,fit=False,fig=fnum).figure
        showfig(fig)
    plt.pause(0.5)
    
        
    


