import numpy as np
from scipy.ndimage.interpolation import shift
from scipy.optimize import curve_fit
from scipy.ndimage.measurements import center_of_mass
from scipy.ndimage import label

def pupillCenter(mask):
    shape = mask.shape
    X, Y = np.meshgrid(range(shape[1]), range(shape[0]) )
    norm = float(np.sum(mask))
    x = np.sum(mask*X)/norm
    y = np.sum(mask*Y)/norm
    return x,y

def centerOfMass(img):
    mask = img>(np.median(img)+ 1.5*np.std(img))
    img = img*mask
    
    shape = img.shape
    X, Y = np.meshgrid(range(shape[1]), range(shape[0]) )
    norm = float(np.sum(img))
    x = np.sum(img*X)/norm
    y = np.sum(img*Y)/norm
    return x,y
    
def spotCenter(img, offset=[0,0]):        
    #img = img - np.median(img)
    #lb, _ = label(img)
    com = centerOfMass(img)
    print(com)
    return com[0]+offset[0], com[1]+offset[1]

def radius(mask):
    return np.sqrt(np.sum(mask)/np.pi)

def circle(x,  x0,  y0, r ) :
    return np.sqrt( r**2 - (x-x0)**2) + y0



def runout(centers, angles=None):

    N = len(centers)
    if N<2: return (np.nan, np.nan), np.nan
    if N==2:
        if angles is None: return (np.nan, np.nan), np.nan
        if np.abs( angles[0] - angles[1] - 180)<1.0:
            d = np.sqrt( (centers[0,0]-centers[1,0])**2 +\
                         (centers[0,1]-centers[1,1])**2 )
            return (np.mean(centers[:,0]), np.mean(centers[:,1])),  d/2.0
        else:
            return (np.nan, np.nan), np.nan
    
    r = max(  (max(centers[:,0]) - min(centers[:,0]))/2.0,  (max(centers[:,1]) - min(centers[:,1]))/2.0 ) 
    params = [np.mean( centers[:,0]), np.mean( centers[:,1]),  r]
    pout, pcov = curve_fit(circle, centers[:,0], centers[:,1], p0=params) 
    return  (pout[0], pout[1]), pout[2]

def circle(x,  x0,  y0, r ) :
    return np.sqrt( r**2 - (x-x0)**2) + y0





