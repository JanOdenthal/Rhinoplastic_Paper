from HyperGuiModules import *
import logging
import os

#logging.basicConfig(level=logging.DEBUG)
xSize=None
ySize=None


def main():
    (window, bp) = init()
    
    # Batch Processing
    BP_frame = frame(bp, BACKGROUND, 0, 0, 16, 16)
    BP_module = BP(BP_frame)
    
    if xSize is not None and ySize is not None:
        window.geometry(str(xSize) + "x" + str(ySize))
    
    window.mainloop()
    

if __name__ == '__main__':
    main()
