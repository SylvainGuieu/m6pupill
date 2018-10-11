from matplotlib.pylab import *
from . import compute

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

def plotPupillCut(p, fig=None):
    fig = getFigure(fig)
    fig.clear()
    fig, axes = plt.subplots(2,2, num=fig.number);
    plotPupill(p, axes=axes[0][0])
    plotCut(p, "y", axes=axes[0][1])
    plotCut(p, "x", axes=axes[1][0])
    plotMask(p, axes=axes[1][1])
    return fig

def plotCut(p,direction, slc=None, axes=None, fig=None):
    axes, fig = getAxes(axes, fig)
    data = p.data
    c = p.getCenter()
    direction = direction.lower()
    if  len(direction)<2:
        direction = direction+direction
    
    if isnan(np.sum(c)):
        c = (data.shape[1]/2., data.shape[0]/2.)
    
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
        axes.axhline(p.fluxTreshold, color='red')
    else:
        axes.plot(data, np.arange(len(data)), 'k-')
        axes.axvline(p.fluxTreshold, color='red')
    return axes
    
    

def plotPupill(p, axes=None, fig=None):
    axes, fig = getAxes(axes, fig)
    axes.imshow(p.data, origin='lower');
    loc = p.pupLocation
    x = [loc[0][0], loc[1][0],  loc[1][0], loc[0][0], loc[0][0]]
    y = [loc[0][1], loc[0][1], loc[1][1], loc[1][1], loc[0][1]]
    axes.plot( x,  y, 'k-')    
    return axes


def plotMask(p, axes=None, fig=None):
    axes, fig = getAxes(axes, fig)
        
    mask = p.getMask()
    axes.imshow(mask, origin='lower');
    axes.set_title("az {h[az]:.0f} derot {h[derot]:.0f}".format(h=p.header))
    xc, yc = p.getCenter();
    axes.plot(xc, yc, 'k+');
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
        axes.text(  c[0],c[1], fmt.format(h=p.header))
    if fit and len(l)>=3:
        (x0,y0), r = compute.runout(centers)
        
        alpha = np.linspace(0,2*np.pi, 100)
        axes.plot(  r*np.cos(alpha)+x0, r*np.sin(alpha)+y0,  'r-')  
        axes.plot( x0, y0,  'r*')
        pupDiam = np.mean( [p.getRadius() for p in l])*2
        runOut = r*2/pupDiam * 100
        axes.set_title('{x0:.2f},  {y0:.2f} runout {d:.2f} / {pupDiam:.0f} pixels => {runOut:.2f}%'.format(x0=x0,y0=y0,r=r,d=r*2, pupDiam=pupDiam, runOut=runOut)) 
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
    

CUTFIG = 1

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
    plotPupillCut(p, fig=fig)
    showfig(fig)
        
    for i,(derot,laz) in enumerate(l.byDerot().items()):
        fnum = (i+1)*10
        fig = plt.figure(fnum); fig.clear()
        fig = plotRunOut(laz,fit=True,fig=fnum).figure
        showfig(fig)
        
    for i,(derot,lderot) in enumerate(l.byAz().items()):
        fnum = (i+1)*100
        fig = plt.figure(fnum); fig.clear()
        fig = plotRunOut(lderot,fit=False,fig=fnum).figure
        showfig(fig)
    plt.pause(0.5)
    
        
    


