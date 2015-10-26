#!/usr/bin/env python

import numpy as np
import ctypes
import struct
import time

from ioctl_numbers import _IOR, _IOW
from fcntl import ioctl

from Lepton import Lepton

SPI_IOC_MAGIC   = ord("k")

SPI_IOC_RD_MODE          = _IOR(SPI_IOC_MAGIC, 1, "=B")
SPI_IOC_WR_MODE          = _IOW(SPI_IOC_MAGIC, 1, "=B")

SPI_IOC_RD_LSB_FIRST     = _IOR(SPI_IOC_MAGIC, 2, "=B")
SPI_IOC_WR_LSB_FIRST     = _IOW(SPI_IOC_MAGIC, 2, "=B")

SPI_IOC_RD_BITS_PER_WORD = _IOR(SPI_IOC_MAGIC, 3, "=B")
SPI_IOC_WR_BITS_PER_WORD = _IOW(SPI_IOC_MAGIC, 3, "=B")

SPI_IOC_RD_MAX_SPEED_HZ  = _IOR(SPI_IOC_MAGIC, 4, "=I")
SPI_IOC_WR_MAX_SPEED_HZ  = _IOW(SPI_IOC_MAGIC, 4, "=I")
 

class Lepton3(Lepton):
  def __init__(self, spi_dev = "/dev/spidev0.0"):
    super(Lepton3, self).__init__(spi_dev)

    self._xmit_buf = np.zeros((self._msg_size * Lepton.ROWS * 4), dtype=np.uint8)
    self._capture_buf = np.zeros((Lepton.ROWS * 4, Lepton.VOSPI_FRAME_SIZE), dtype=np.uint16)

    for i in range(Lepton.ROWS * 4):
      self._xmit_struct.pack_into(self._xmit_buf, i * self._msg_size,
        self._txbuf.ctypes.data,                                            #   __u64     tx_buf;
        self._capture_buf.ctypes.data + Lepton.VOSPI_FRAME_SIZE_BYTES * i,  #   __u64     rx_buf;
        Lepton.VOSPI_FRAME_SIZE_BYTES,                                      #   __u32     len;
        Lepton.SPEED,                                                       #   __u32     speed_hz;
        0,                                                                  #   __u16     delay_usecs;
        Lepton.BITS,                                                        #   __u8      bits_per_word;
        1,                                                                  #   __u8      cs_change;
        0)                                                                  #   __u32     pad;

  def capture(self, data_buffer = None, debug_print = False):

    if data_buffer is None:
      data_buffer = np.zeros((Lepton.ROWS * 2, Lepton.COLS * 2), dtype=np.uint16)
    elif data_buffer.ndim < 2 or data_buffer.shape[0] < Lepton.ROWS * 2 or data_buffer.shape[1] < Lepton.COLS * 2 or data_buffer.itemsize < 2:
      raise Exception("Provided input array not large enough")

    start = time.time()

    Lepton.capture_segment(self._handle, self._xmit_buf[:self._msg_size * Lepton.ROWS], self._msg_size, self._capture_buf[0])

    while (self._capture_buf[20, 0] & 0x00F0) != 0x10: # are we at segment 1 yet?
      # print "Not at start ({0})!".format(self._capture_buf[20, 0] & 0x00F0)
      if (self._capture_buf[20, 0] & 0xFF0F) != 0x1400: # make sure that this is a well-formed frame, should find line 20 here
        print "Garbage frame number resetting..."
        time.sleep(0.185)
      start = time.time()
      Lepton.capture_segment(self._handle, self._xmit_buf[:self._msg_size * Lepton.ROWS], self._msg_size, self._capture_buf[0])

    for i in range(1,4):
      Lepton.capture_segment(self._handle, self._xmit_buf[self._msg_size * Lepton.ROWS * i:self._msg_size * Lepton.ROWS * (i+1)], self._msg_size, self._capture_buf[i*Lepton.ROWS])

    end = time.time()
    self._capture_buf.byteswap(True)

    if debug_print:
      print "---"
      for i in range(240):
        fid = self._capture_buf[i, 0]
        crc = self._capture_buf[i, 1]
        fnum = fid & 0xFFF
        if fnum == 20:
          ttt = (fid & 0xF000) >> 12
        else:
          ttt = " "
        # self._capture_buf[i, 0] = fid & 0x0FFF
        # self._capture_buf[i, 1] = 0
        print "0x{0:04x} 0x{1:04x} : TTT={2} #{3:2} : crc={1}".format(fid, crc, ttt, fnum)
      print "---"

    print "frame processed int {0}s, {1}hz".format(end-start, 1.0/(end-start))

    data_buffer.shape = (240, 80)
    data_buffer[:,:] = self._capture_buf[:,2:]
    data_buffer.shape = (120, 160)

    # TODO: turn on telemetry to get real frame id, sum on this array is fast enough though (< 500us)
    return data_buffer, data_buffer.sum()
  