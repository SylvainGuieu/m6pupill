from .pupill import M6PupillList, M6Pupill
imageList = M6PupillList([])
imageListIndex = -1

imageChangedEvents = []

def addImageChangedTrace(callable):
    global imageChangedEvents
    if not hasattr(callable, "__call__"):
        raise ValueError("expecting a callable")
    imageChangedEvents.append(callable)

def imageChanged():
    global imageChangedEvents
    global imageList, imageListIndex
    for f in imageChangedEvents:
        f(imageList, currentImage())
    
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
    lst = imageList
    imageListIndex = len(imageList)-1    
