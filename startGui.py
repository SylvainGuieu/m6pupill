import sys, os
sys.path.append(os.path.join(os.environ["HOME"],"sguieu/python/"))
from runout import gui
if __name__=="__main__":   
    gui.main(files=sys.argv[1:])
