#!/usr/bin/env python

import time
import picamera
import numpy as np
import cv2
import traceback
from pylepton import Lepton

def main(flip_v = False, alpha = 128, device = "/dev/spidev0.0"):
  # Create an array representing a 1280x720 image of
  # a cross through the center of the display. The shape of
  # the array must be of the form (height, width, color)
  a = np.zeros((240, 320, 3), dtype=np.uint8)
  lepton_buf = np.zeros((60, 80, 1), dtype=np.uint16)

  with picamera.PiCamera() as camera:
    camera.resolution = (640, 480)
    camera.framerate = 24
    camera.vflip = flip_v
    camera.start_preview()
    camera.zoom = (0.0, 0.0, 1.0, 1.0)
    # Add the overlay directly into layer 3 with transparency;
    # we can omit the size parameter of add_overlay as the
    # size is the same as the camera's resolution
    o = camera.add_overlay(np.getbuffer(a), size=(320,240), layer=3, alpha=int(alpha), crop=(0,0,80,60), vflip=flip_v)
    try:
      time.sleep(0.2) # give the overlay buffers a chance to initialize
      with Lepton(device) as l:
        last_nr = 0
        while True:
          _,nr = l.capture(lepton_buf)
          if nr == last_nr:
            # no need to redo this frame
            continue
          last_nr = nr
          cv2.normalize(lepton_buf, lepton_buf, 0, 65535, cv2.NORM_MINMAX)
          np.right_shift(lepton_buf, 8, lepton_buf)
          a[:lepton_buf.shape[0], :lepton_buf.shape[1], :] = lepton_buf
          o.update(np.getbuffer(a))
    except Exception:
      traceback.print_exc()
    finally:
      camera.remove_overlay(o)

if __name__ == '__main__':
  from optparse import OptionParser

  usage = "usage: %prog [options] output_file[.format]"
  parser = OptionParser(usage=usage)

  parser.add_option("-f", "--flip-vertical",
                    action="store_true", dest="flip_v", default=False,
                    help="flip the output images vertically")

  parser.add_option("-a", "--alpha",
                    dest="alpha", default=128,
                    help="set lepton overlay opacity")

  parser.add_option("-d", "--device",
                    dest="device", default="/dev/spidev0.0",
                    help="specify the spi device node (might be /dev/spidev0.1 on a newer device)")

  (options, args) = parser.parse_args()

  main(flip_v = options.flip_v, alpha = options.alpha, device = options.device)
