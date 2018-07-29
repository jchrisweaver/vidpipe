import numpy as np
import cv2

img = cv2.imread('/Users/chris/code/bounder/vidpipe/images/VidPipe.png',0)
cv2.imshow('image',img)
k = cv2.waitKey(1) & 0xFF

if k == 27:         # wait for ESC key to exit
    cv2.destroyAllWindows()
elif k == ord('s'): # wait for 's' key to save and exit
    cv2.destroyAllWindows()

