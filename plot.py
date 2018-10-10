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
    
def plotMask(p, axes=None, fig=None):
    axes, fig = getAxes(axes, fig)
    
    
    mask = p.getMask()
    axes.imshow(mask);
    axes.set_title("az {az:.0f} derot {derot:.0f}".format(**p.header))
    xc, yc = p.getCenter();
    axes.plot(xc, yc, 'k+');        
    return axes


def plotRunOut(l, axes=None, fig=None, leg=None, title="",fit=False):    
    axes, fig = getAxes(axes, fig)
    
    if leg is None:
        if len(set([p.az for p in l]))==1: leg="derot"
        elif len(set([p.derot for p in l]))==1: leg="az"
    
    ttl = "at: "+", ".join(set(["%d"%p.at for p in l]))
    if leg=="derot":
        fmt = "{derot:.0f}"
        ttl  += " Az: "+", ".join(set(["%.0f"%p.az for p in l]))
    elif leg=="az":
        fmt  = "{az:.0f}"
        ttl += " Derot: "+", ".join(set(["%.0f"%p.derot for p in l]))
    else:
        fmt = "{az:.0f}, {derot:.0f}"

    
    centers = l.getCenters()
    
    axes.plot(centers[:,0], centers[:,1], 'k+-')
    axes.set_xlabel('X (pixel)')
    axes.set_ylabel('Y (pixel)')
    axes.set_title(title+" "+ttl)
    
    for p,c in zip(l, centers):
        axes.text(  c[0],c[1], fmt.format(**p.header))
    if fit:
        (x0,y0), r = compute.runout(centers)
        
        alpha = np.linspace(0,2*np.pi, 100)
        axes.plot(  r*np.cos(alpha)+x0, r*np.sin(alpha)+y0,  'r-')  
        axes.plot( x0, y0,  'r*')
        axes.set_title('{x0:.2f},  {y0:.2f} runout {d:.2f}'.format(x0=x0,y0=y0,r=r,d=r*2)) 
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
    




