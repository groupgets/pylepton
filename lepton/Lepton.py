#!/usr/bin/env python

import numpy as np
import ctypes
import struct

from ioctl_numbers import _IOR, _IOW
from fcntl import ioctl

SPI_IOC_MAGIC   = ord("k")

SPI_IOC_RD_MODE          = _IOR(SPI_IOC_MAGIC, 1, "=B")
SPI_IOC_WR_MODE          = _IOW(SPI_IOC_MAGIC, 1, "=B")

SPI_IOC_RD_LSB_FIRST     = _IOR(SPI_IOC_MAGIC, 2, "=B")
SPI_IOC_WR_LSB_FIRST     = _IOW(SPI_IOC_MAGIC, 2, "=B")

SPI_IOC_RD_BITS_PER_WORD = _IOR(SPI_IOC_MAGIC, 3, "=B")
SPI_IOC_WR_BITS_PER_WORD = _IOW(SPI_IOC_MAGIC, 3, "=B")

SPI_IOC_RD_MAX_SPEED_HZ  = _IOR(SPI_IOC_MAGIC, 4, "=I")
SPI_IOC_WR_MAX_SPEED_HZ  = _IOW(SPI_IOC_MAGIC, 4, "=I")

class Lepton(object):
  ROWS = 60
  COLS = 80
  VOSPI_FRAME_SIZE = COLS + 2
  VOSPI_FRAME_SIZE_BYTES = VOSPI_FRAME_SIZE * 2
  MODE = 0
  BITS = 8
  SPEED = 18000000

  def __init__(self, spi_dev = "/dev/spidev0.0"):
    self.__spi_dev = spi_dev
    self.__txbuf = np.zeros(Lepton.VOSPI_FRAME_SIZE, dtype=np.uint16)
    self.__rxbuf = np.zeros(Lepton.VOSPI_FRAME_SIZE, dtype='>u2')

    # struct spi_ioc_transfer {
    #   __u64     tx_buf;
    #   __u64     rx_buf;
    #   __u32     len;
    #   __u32     speed_hz;
    #   __u16     delay_usecs;
    #   __u8      bits_per_word;
    #   __u8      cs_change;
    #   __u8      tx_nbits;
    #   __u8      rx_nbits;
    #   __u16     pad;
    # };
    self.__xmit_struct = struct.Struct("=QQIIHBBBBH")
    self.__xmit_buf = ctypes.create_string_buffer(self.__xmit_struct.size)
    self.__msg = _IOW(SPI_IOC_MAGIC, 0, self.__xmit_struct.format)

  def __enter__(self):
    self.__handle = open(self.__spi_dev, "w+")

    ioctl(self.__handle, SPI_IOC_RD_MODE, struct.pack("=B", Lepton.MODE))
    ioctl(self.__handle, SPI_IOC_WR_MODE, struct.pack("=B", Lepton.MODE))

    ioctl(self.__handle, SPI_IOC_RD_BITS_PER_WORD, struct.pack("=B", Lepton.BITS))
    ioctl(self.__handle, SPI_IOC_WR_BITS_PER_WORD, struct.pack("=B", Lepton.BITS))

    ioctl(self.__handle, SPI_IOC_RD_MAX_SPEED_HZ, struct.pack("=I", Lepton.SPEED))
    ioctl(self.__handle, SPI_IOC_WR_MAX_SPEED_HZ, struct.pack("=I", Lepton.SPEED))

    return self

  def __exit__(self, type, value, tb):
    self.__handle.close()

  def capture(self, a = None):
    if a is None:
      a = np.ndarray((Lepton.ROWS, Lepton.VOSPI_FRAME_SIZE, 1), dtype=np.uint16)
    elif a.nbytes < Lepton.ROWS * Lepton.VOSPI_FRAME_SIZE_BYTES:
      raise Exception("Provided input array not large enough")

    rxs = a.ctypes.data
    rxs_end = rxs + Lepton.ROWS * Lepton.VOSPI_FRAME_SIZE_BYTES
    txs = self.__txbuf.ctypes.data
    synced = False
    while rxs < rxs_end:
      self.__xmit_struct.pack_into(self.__xmit_buf, 0, txs, rxs, Lepton.VOSPI_FRAME_SIZE_BYTES, Lepton.SPEED, 0, Lepton.BITS, 0, Lepton.BITS, Lepton.BITS, 0)
      ioctl(self.__handle, self.__msg, self.__xmit_buf)
      if synced or a[0,0] & 0x0f00 != 0x0f00:
        synced = True
        rxs += Lepton.VOSPI_FRAME_SIZE_BYTES

    # TODO: turn on telemetry to get real frame id, sum on this array is fast enough though (< 500us)
    return a, a.sum()
