#!/usr/bin/env python
import numpy as np
import cv2
from pylepton import Lepton



#setup the Lepton image buffer
def capture(device = "/dev/spidev0.0"):
    with Lepton() as l:
      a,_ = l.capture()     #grab the buffer
    cv2.normalize(a, a, 0, 65535, cv2.NORM_MINMAX) # extend  contrast
    np.right_shift(a, 8, a) # fit data into 8 bits
    return np.uint8(a)

def applyCustomColorMap(im_gray) :

    lut = np.zeros((256, 1, 3), dtype=np.uint8)
    lut[:, 0, 2] = [0, 253, 251, 249, 247, 245, 243, 241, 239, 237, 235, 233, 231, 229, 227, 225, 223, 221, 219, 217, 215, 213, 211, 209, 207, 205, 203, 201, 199, 197, 195, 193, 191, 189, 187, 185, 183, 181, 179, 177, 175, 173, 171, 169, 167, 165, 163, 161, 159, 157, 155, 153, 151, 149, 147, 145, 143, 141, 139, 137, 135, 133, 131, 129, 126, 124, 122, 120, 118, 116, 114, 112, 110, 108, 106, 104, 102, 100, 98, 96, 94, 92, 90, 88, 86, 84, 82, 80, 78, 76, 74, 72, 70, 68, 66, 64, 62, 60, 58, 56, 54, 52, 50, 48, 46, 44, 42, 40, 38, 36, 34, 32, 30, 28, 26, 24, 22, 20, 18, 16, 14, 12, 10, 8, 6, 4, 2, 0, 0, 2, 4, 6, 8, 10, 12, 14, 17, 19, 21, 23, 25, 27, 29, 31, 36, 41, 46, 51, 56, 61, 66, 71, 76, 81, 86, 91, 96, 101, 106, 111, 116, 121, 125, 130, 135, 139, 144, 149, 153, 158, 163, 167, 172, 177, 181, 186, 189, 191, 194, 196, 198, 200, 203, 205, 207, 209, 212, 214, 216, 218, 221, 223, 224, 225, 226, 227, 228, 229, 230, 231, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 240, 241, 241, 242, 242, 243, 243, 244, 244, 245, 245, 246, 246, 247, 247, 248, 248, 249, 249, 250, 250, 251, 251, 252, 252, 253, 253, 254, 254, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255]
    lut[:, 0, 1] = [0, 253, 251, 249, 247, 245, 243, 241, 239, 237, 235, 233, 231, 229, 227, 225, 223, 221, 219, 217, 215, 213, 211, 209, 207, 205, 203, 201, 199, 197, 195, 193, 191, 189, 187, 185, 183, 181, 179, 177, 175, 173, 171, 169, 167, 165, 163, 161, 159, 157, 155, 153, 151, 149, 147, 145, 143, 141, 139, 137, 135, 133, 131, 129, 126, 124, 122, 120, 118, 116, 114, 112, 110, 108, 106, 104, 102, 100, 98, 96, 94, 92, 90, 88, 86, 84, 82, 80, 78, 76, 74, 72, 70, 68, 66, 64, 62, 60, 58, 56, 54, 52, 50, 48, 46, 44, 42, 40, 38, 36, 34, 32, 30, 28, 26, 24, 22, 20, 18, 16, 14, 12, 10, 8, 6, 4, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 3, 3, 3, 4, 4, 5, 5, 5, 6, 6, 7, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34, 37, 40, 43, 46, 49, 52, 55, 57, 60, 64, 67, 71, 74, 78, 81, 85, 88, 92, 95, 99, 102, 106, 109, 112, 116, 119, 123, 127, 130, 134, 138, 141, 145, 149, 152, 156, 160, 163, 167, 171, 175, 178, 182, 185, 189, 192, 196, 199, 203, 206, 210, 213, 217, 220, 224, 227, 229, 231, 233, 234, 236, 238, 240, 242, 244, 246, 248, 249, 251, 253, 255]
    lut[:, 0, 0] = [0, 253, 251, 249, 247, 245, 243, 241, 239, 237, 235, 233, 231, 229, 227, 225, 223, 221, 219, 217, 215, 213, 211, 209, 207, 205, 203, 201, 199, 197, 195, 193, 191, 189, 187, 185, 183, 181, 179, 177, 175, 173, 171, 169, 167, 165, 163, 161, 159, 157, 155, 153, 151, 149, 147, 145, 143, 141, 139, 137, 135, 133, 131, 129, 126, 124, 122, 120, 118, 116, 114, 112, 110, 108, 106, 104, 102, 100, 98, 96, 94, 92, 90, 88, 86, 84, 82, 80, 78, 76, 74, 72, 70, 68, 66, 64, 62, 60, 58, 56, 54, 52, 50, 48, 46, 44, 42, 40, 38, 36, 34, 32, 30, 28, 26, 24, 22, 20, 18, 16, 14, 12, 10, 8, 6, 4, 2, 0, 9, 16, 24, 31, 38, 45, 53, 60, 67, 74, 82, 89, 96, 103, 111, 118, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 136, 137, 137, 137, 138, 138, 138, 139, 139, 139, 140, 140, 140, 141, 141, 137, 132, 127, 121, 116, 111, 106, 101, 95, 90, 85, 80, 75, 69, 64, 59, 49, 47, 44, 42, 39, 37, 34, 32, 29, 27, 24, 22, 19, 17, 14, 12, 12, 12, 12, 12, 12, 12, 12, 12, 13, 13, 13, 13, 13, 13, 13, 13, 13, 14, 15, 16, 18, 19, 20, 21, 22, 23, 24, 25, 27, 28, 29, 30, 39, 53, 67, 81, 95, 109, 123, 137, 151, 165, 179, 193, 207, 221, 235, 24]
    im_color = cv2.LUT(im_gray, lut)
    return im_color;

#Create a window and give it adjustment sliders
def nothing(x):
    pass
cv2.namedWindow('flir', cv2.WINDOW_AUTOSIZE)
cv2.resizeWindow('flir', 320, 240)
cv2.moveWindow('flir',1,1)
cv2.createTrackbar('thresh','flir',1,255,nothing)
cv2.createTrackbar('erode','flir',1,10,nothing)
cv2.createTrackbar('dilate','flir',1,100,nothing)
cv2.createTrackbar('capture_rate','flir',1,1000,nothing) 

#start a continuous loop    
while True:
        
        #update the image processing variables
        thresh = cv2.getTrackbarPos('thresh','flir')
        erodeSize = cv2.getTrackbarPos('erode','flir')
        dilateSize = cv2.getTrackbarPos('dilate','flir')
        capture_rate = cv2.getTrackbarPos('capture_rate','flir')

        #read the bugger into an object
        frame = capture()
        frame_v = frame
        
        #apply some image processing
        image = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR);
        frame = applyCustomColorMap(image);
        blurredBrightness = cv2.bilateralFilter(frame_v,9,150,255)
        edges = cv2.Canny(blurredBrightness,thresh,thresh*2, L2gradient=True)

        _,mask = cv2.threshold(blurredBrightness,200,1,cv2.THRESH_BINARY)
        if erodeSize <= 1:
            erodeSize = 1
        if dilateSize <= 1:
            dilateSize = 1
        eroded = cv2.erode(mask, np.ones((erodeSize, erodeSize)))
        mask = cv2.dilate(eroded, np.ones((dilateSize, dilateSize)))

        #display the image
        cv2.imshow("flir", cv2.resize(cv2.cvtColor(mask*edges, cv2.COLOR_GRAY2RGB) | frame, (320, 240), interpolation = cv2.INTER_CUBIC))        
        if capture_rate <= 1:
            capture_rate = 1
        cv2.waitKey(capture_rate)

cv2.destroyAllWindows()  



    
