#!/usr/bin/env python
import numpy as np
import cv2
import imutils
from pylepton import Lepton

#define the capture function for the Lepton
def capture(device = "/dev/spidev0.0"):
  with Lepton(device) as l:
    a,_ = l.capture()
  cv2.normalize(a, a, 0, 65535, cv2.NORM_MINMAX)
  np.right_shift(a, 8, a)
  return np.uint8(a)

#grab the buffer from the Lepton
image = capture()

#add a color map 
#image_color = cv2.applyColorMap(image, cv2.COLORMAP_HOT)
image_color = image

#scale up a bit
image_color = imutils.resize(image_color, width=min(400, image.shape[1]))

#Save the image in the "images" folder
cv2.imwrite("images/snap.jpg", image_color) 

#create a new window
cv2.namedWindow('Pylepton Snapshot', cv2.WINDOW_NORMAL)
cv2.resizeWindow('Pylepton Snapshot', 640, 480) #native size is 80x60
cv2.moveWindow('Pylepton Snapshot',1,1)

#display the snapshot in the window
cv2.imshow('Pylepton Snapshot',image_color )
cv2.waitKey()


  
