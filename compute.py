import numpy as np
from scipy.ndimage.interpolation import shift
from scipy.optimize import curve_fit
from scipy.ndimage.measurements import center_of_mass

def pupillCenter(mask):
    shape = mask.shape
    X, Y = np.meshgrid(range(shape[1]), range(shape[0]) )
    norm = float(np.sum(mask))
    x = np.sum(mask*X)/norm
    y = np.sum(mask*Y)/norm
    return x,y

def spotCenter(img, offset=[0,0]):
    com = center_of_mass(img)
    return com[0]+offset[0], com[1]+offset[1]

def radius(mask):
    return np.sqrt(np.sum(mask)/np.pi)

def circle(x,  x0,  y0, r ) :
    return np.sqrt( r**2 - (x-x0)**2) + y0
    
def runout(centers):   
    r = max(  (max(centers[:,0]) - min(centers[:,0]))/2.0,  (max(centers[:,1]) - min(centers[:,1]))/2.0 ) 
    params = [np.mean( centers[:,0]), np.mean( centers[:,1]),  r]
    pout, pcov = curve_fit(circle, centers[:,0], centers[:,1], p0=params) 
    return  (pout[0], pout[1]), pout[2]

def circle(x,  x0,  y0, r ) :
    return np.sqrt( r**2 - (x-x0)**2) + y0

