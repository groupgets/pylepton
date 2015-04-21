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
  """Communication class for FLIR Lepton module on SPI

  Args:
    spi_dev (str): Location of SPI device node. Default '/dev/spidev0.0'.
  """

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
    self.__capture_buf = np.zeros((60, 82, 1), dtype=np.uint16)

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

  def capture(self, data_buffer = None):
    """Capture a frame of data.

    Captures 80x60 uint16 array of non-normalized (raw 12-bit) data. Returns that frame and a frame_id (which
    is currently just the sum of all pixels). The Lepton will return multiple, identical frames at a rate of up
    to ~27 Hz, with unique frames at only ~9 Hz, so the frame_id can help you from doing additional work
    processing duplicate frames.

    Args:
      data_buffer (numpy.ndarray): Optional. If specified, should be ``(60,80,1)`` with `dtype`=``numpy.uint16``.

    Returns:
      tuple consisting of (data_buffer, frame_id)
    """

    if data_buffer is None:
      data_buffer = np.ndarray((Lepton.ROWS, Lepton.COLS, 1), dtype=np.uint16)
    elif len(data_buffer.shape) < 2 or data_buffer.shape[0] < Lepton.ROWS or data_buffer.shape[1] < Lepton.COLS or data_buffer.elemsize < 2:
      raise Exception("Provided input array not large enough")

    rxs = self.__capture_buf.ctypes.data
    rxs_end = rxs + Lepton.ROWS * Lepton.VOSPI_FRAME_SIZE_BYTES
    txs = self.__txbuf.ctypes.data
    synced = False
    while rxs < rxs_end:
      self.__xmit_struct.pack_into(self.__xmit_buf, 0, txs, rxs, Lepton.VOSPI_FRAME_SIZE_BYTES, Lepton.SPEED, 0, Lepton.BITS, 0, Lepton.BITS, Lepton.BITS, 0)
      ioctl(self.__handle, self.__msg, self.__xmit_buf)
      if synced or data_buffer[0,0] & 0x0f00 != 0x0f00:
        synced = True
        rxs += Lepton.VOSPI_FRAME_SIZE_BYTES

    data_buffer[0:Lepton.ROWS,0:Lepton.COLS] = self.__capture_buf[:2,:]
    data_buffer.byteswap(True)

    # TODO: turn on telemetry to get real frame id, sum on this array is fast enough though (< 500us)
    return data_buffer, data_buffer.sum()
