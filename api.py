from .image import ImageList, Image
from . import io
image = None

measurementList = ImageList([])
measurementIndex = -1

measurementChangedEvents = []
imageChangedEvents  = []
def addMeasurementChangedTrace(callable):
    global measurementChangedEvents
    if not hasattr(callable, "__call__"):
        raise ValueError("expecting a callable")
    measurementChangedEvents.append(callable)

def addNewImageTrace(callable):
    global imageChangedEvents
    if not hasattr(callable, "__call__"):
        raise ValueError("expecting a callable")
    imageChangedEvents.append(callable)
    
def measurementChanged():
    global measurementChangedEvents
    global measurementList, measurementIndex
    for f in measurementChangedEvents:
        f(measurementList, currentMeasurement())

def imageChanged():
    global imageChangedEvents
    global image
    for f in imageChangedEvents:
        f(image)

def saveMeasurement():
    img = currentMeasurement()
    if img.file: return 
    img.file = io.saveImage(img)
    measurementChanged()

def saveAll():
    for img in getMeasurementList():
        img.file = io.saveImage(img)
    measurementChanged()
    
def currentMeasurement():
    global measurementList, measurementIndex
    N = len(measurementList)
    if not N: return 
    return measurementList[measurementIndex]

def getIndex():
    global measurementList, measurementIndex
    return measurementIndex

def getMeasurementList():
    global measurementList, measurementIndex
    return measurementList

def nextMeasurement():
    global measurementList, measurementIndex
    N = len(measurementList)
    if measurementIndex>=(N-1): return 
    measurementIndex += 1
    measurementChanged()

def selectMeasurement(index):
    global measurementList, measurementIndex
    N = len(measurementList)
    if index>=0 and index<N:
        measurementIndex = index
        measurementChanged()
    
def previousMeasurement():
    global measurementList, measurementIndex
    N = len(measurementList)
    if measurementIndex<=0 or not N: return 
    measurementIndex -= 1
    measurementChanged()

def removeMeasurement():
    global measurementList, measurementIndex
    N = len(measurementList)
    if not N: return 
    measurementList.lst.remove(currentMeasurement())
    N = len(measurementList)
    if not N: measurementIndex = -1
    else:
        measurementIndex -= 1
    measurementChanged()
    
def nMeasurement():
    global measurementList
    return len(measurementList)

def newMeasurement():
    addMeasurement(Image.fromCcd())
    
def addMeasurement(img):
    global measurementList, measurementIndex
    measurementList.append(img)
    measurementIndex = nMeasurement()-1
    measurementChanged()
    
def replaceMeasurement(img):
    global measurementList, measurementIndex
    measurementIndex = measurementList.replace(img)    
    measurementChanged()

def addImageToMeasurement():
    global measurementList, image
    if image is not None:
        if image not in measurementList.lst:
            addMeasurement(image)

def replaceTmpImage():
    global measurementList, image
    if image is not None:
        if image not in measurementList.lst:
            replaceMeasurement(image)
            
def setMeasurementList(lst, index=None):
    global measurementList, measurementIndex
    measurementList = lst
    measurementIndex = len(measurementList)-1    
    measurementChanged()

def grabImage():
    global image
    image = Image.fromCcd()
    imageChanged()
    
def getImage():
    global image
    return image

def setImage(img):
    global image
    image = img
    imageChanged()
