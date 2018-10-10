import numpy as np
from scipy.ndimage.interpolation import shift
from scipy.optimize import curve_fit

def center(mask):
    shape = mask.shape
    X, Y = np.meshgrid(range(shape[1]), range(shape[0]) )
    norm = float(np.sum(mask))
    x = np.sum(mask*X)/norm
    y = np.sum(mask*Y)/norm
    return x,y

def circle(x,  x0,  y0, r ) :
    return np.sqrt( r**2 - (x-x0)**2) + y0
    
def runout(centers):   
    r = max(  (max(centers[:,0]) - min(centers[:,0]))/2.0,  (max(centers[:,1]) - min(centers[:,1]))/2.0 ) 
    params = [np.mean( centers[:,0]), np.mean( centers[:,1]),  r]
    pout, pcov = curve_fit(circle, centers[:,0], centers[:,1], p0=params) 
    return  (pout[0], pout[1]), pout[2]

def circle(x,  x0,  y0, r ) :
    return np.sqrt( r**2 - (x-x0)**2) + y0

