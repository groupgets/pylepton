#!/usr/bin/env python

import sys
import numpy as np
import cv2
from pylepton.Lepton3 import Lepton3

def capture(flip_v = False, device = "/dev/spidev0.0"):
  with Lepton3(device) as l:
    a,_ = l.capture()
  if flip_v:
    cv2.flip(a,0,a)
  cv2.normalize(a, a, 0, 65535, cv2.NORM_MINMAX)
  np.right_shift(a, 8, a)
  return np.uint8(a)

if __name__ == '__main__':
  from optparse import OptionParser

  usage = "usage: %prog [options] output_file[.format]"
  parser = OptionParser(usage=usage)

  parser.add_option("-f", "--flip-vertical",
                    action="store_true", dest="flip_v", default=False,
                    help="flip the output image vertically")

  parser.add_option("-d", "--device",
                    dest="device", default="/dev/spidev0.0",
                    help="specify the spi device node (might be /dev/spidev0.1 on a newer device)")

  (options, args) = parser.parse_args()

  if len(args) < 1:
    print("You must specify an output filename")
    sys.exit(1)

  image = capture(flip_v = options.flip_v, device = options.device)
  cv2.imwrite(args[0], image)
