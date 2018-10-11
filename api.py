from .pupill import M6PupillList, M6Pupill

tmpImage = None

imageList = M6PupillList([])
imageListIndex = -1

imageChangedEvents = []
newTmpImageEvents = []
def addImageChangedTrace(callable):
    global imageChangedEvents
    if not hasattr(callable, "__call__"):
        raise ValueError("expecting a callable")
    imageChangedEvents.append(callable)

def addTmpImageTrace(callable):
    global newTmpImageEvents
    if not hasattr(callable, "__call__"):
        raise ValueError("expecting a callable")
    newTmpImageEvents.append(callable)
    
def imageChanged():
    global imageChangedEvents
    global imageList, imageListIndex
    for f in imageChangedEvents:
        f(imageList, currentImage())

def tmpImageChanged():
    global newTmpImageEvents
    global tmpImage
    for f in newTmpImageEvents:
        f(tmpImage)

        
def currentImage():
    global imageList, imageListIndex
    N = len(imageList)
    if not N: return 
    return imageList[imageListIndex]

def getIndex():
    global imageList, imageListIndex
    return imageListIndex

def getImageList():
    global imageList, imageListIndex
    return imageList

def nextImage():
    global imageList, imageListIndex
    N = len(imageList)
    if imageListIndex>=(N-1): return 
    imageListIndex += 1
    imageChanged()
    
def previousImage():
    global imageList, imageListIndex
    N = len(imageList)
    if imageListIndex<=0 or not N: return 
    imageListIndex -= 1
    imageChanged()

def removeImage():
    global imageList, imageListIndex
    N = len(imageList)
    if not N: return 
    imageList.lst.remove(currentImage())
    N = len(imageList)
    if not N: imageListIndex = -1
    else:
        imageListIndex -= 1
    imageChanged()
    
def nImage():
    global imageList
    return len(imageList)

def newImage():
    global imageList, imageListIndex
    imageList.appendFromCcd()
    imageListIndex = nImage()-1
    imageChanged()

def replaceImage():
    global imageList, imageListIndex
    new = M6Pupill.fromCcd()
    imageListIndex = imageList.replace(new)    
    imageChanged()
    
def setImageList(lst, index=None):
    global imageList, imageListIndex
    imageList = lst
    imageListIndex = len(imageList)-1    
    imageChanged()

def newTmpImage():
    global tmpImage
    tmpImage = M6Pupill.fromCcd()
    tmpImageChanged()
    
def getTmpImage():
    global tmpImage
    return  tmpImage

def setTmpImage(img):
    global tmpImage
    tmpImage = img
    tmpImageChanged()
