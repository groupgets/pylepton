#!/usr/bin/env python

import numpy as np
import ctypes
import struct
import time

# relative imports in Python3 must be explicit
from .ioctl_numbers import _IOR, _IOW
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

SPI_CPHA   = 0x01                 # /* clock phase */
SPI_CPOL   = 0x02                 # /* clock polarity */
SPI_MODE_0 = (0|0)                # /* (original MicroWire) */
SPI_MODE_1 = (0|SPI_CPHA)
SPI_MODE_2 = (SPI_CPOL|0)
SPI_MODE_3 = (SPI_CPOL|SPI_CPHA)

class Lepton(object):
  """Communication class for FLIR Lepton module on SPI

  Args:
    spi_dev (str): Location of SPI device node. Default '/dev/spidev0.0'.
  """

  ROWS = 60
  COLS = 80
  VOSPI_FRAME_SIZE = COLS + 2
  VOSPI_FRAME_SIZE_BYTES = VOSPI_FRAME_SIZE * 2
  MODE = SPI_MODE_3
  BITS = 8
  SPEED = 18000000
  SPIDEV_MESSAGE_LIMIT = 24

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
    #   __u32     pad;
    # };
    self.__xmit_struct = struct.Struct("=QQIIHBBI")
    self.__msg_size = self.__xmit_struct.size
    self.__xmit_buf = np.zeros((self.__msg_size * Lepton.ROWS), dtype=np.uint8)
    self.__msg = _IOW(SPI_IOC_MAGIC, 0, self.__xmit_struct.format)
    self.__capture_buf = np.zeros((Lepton.ROWS, Lepton.VOSPI_FRAME_SIZE, 1), dtype=np.uint16)

    for i in range(Lepton.ROWS):
      self.__xmit_struct.pack_into(self.__xmit_buf, i * self.__msg_size,
        self.__txbuf.ctypes.data,                                            #   __u64     tx_buf;
        self.__capture_buf.ctypes.data + Lepton.VOSPI_FRAME_SIZE_BYTES * i,  #   __u64     rx_buf;
        Lepton.VOSPI_FRAME_SIZE_BYTES,                                      #   __u32     len;
        Lepton.SPEED,                                                       #   __u32     speed_hz;
        0,                                                                  #   __u16     delay_usecs;
        Lepton.BITS,                                                        #   __u8      bits_per_word;
        1,                                                                  #   __u8      cs_change;
        0)                                                                  #   __u32     pad;

  def __enter__(self):
    # "In Python 3 the only way to open /dev/tty under Linux appears to be 1) in binary mode and 2) with buffering disabled."
    self.__handle = open(self.__spi_dev, "wb+", buffering=0)

    ioctl(self.__handle, SPI_IOC_RD_MODE, struct.pack("=B", Lepton.MODE))
    ioctl(self.__handle, SPI_IOC_WR_MODE, struct.pack("=B", Lepton.MODE))

    ioctl(self.__handle, SPI_IOC_RD_BITS_PER_WORD, struct.pack("=B", Lepton.BITS))
    ioctl(self.__handle, SPI_IOC_WR_BITS_PER_WORD, struct.pack("=B", Lepton.BITS))

    ioctl(self.__handle, SPI_IOC_RD_MAX_SPEED_HZ, struct.pack("=I", Lepton.SPEED))
    ioctl(self.__handle, SPI_IOC_WR_MAX_SPEED_HZ, struct.pack("=I", Lepton.SPEED))

    return self

  def __exit__(self, type, value, tb):
    self.__handle.close()

  @staticmethod
  def capture_segment(handle, xs_buf, xs_size, capture_buf):
    messages = Lepton.ROWS

    iow = _IOW(SPI_IOC_MAGIC, 0, xs_size)
    ioctl(handle, iow, xs_buf, True)

    while (capture_buf[0] & 0x000f) == 0x000f: # byteswapped 0x0f00
      ioctl(handle, iow, xs_buf, True)

    messages -= 1

    # NB: the default spidev bufsiz is 4096 bytes so that's where the 24 message limit comes from: 4096 / Lepton.VOSPI_FRAME_SIZE_BYTES = 24.97...
    # This 24 message limit works OK, but if you really need to optimize the read speed here, this hack is for you:

    # The limit can be changed when spidev is loaded, but since it is compiled statically into newer raspbian kernels, that means
    # modifying the kernel boot args to pass this option. This works too:
    #   $ sudo chmod 666 /sys/module/spidev/parameters/bufsiz
    #   $ echo 65536 > /sys/module/spidev/parameters/bufsiz
    # Then Lepton.SPIDEV_MESSAGE_LIMIT of 24 can be raised to 59

    while messages > 0:
      if messages > Lepton.SPIDEV_MESSAGE_LIMIT:
        count = Lepton.SPIDEV_MESSAGE_LIMIT
      else:
        count = messages
      iow = _IOW(SPI_IOC_MAGIC, 0, xs_size * count)
      ret = ioctl(handle, iow, xs_buf[xs_size * (60 - messages):], True)
      if ret < 1:
        raise IOError("can't send {0} spi messages ({1})".format(60, ret))
      messages -= count

  def capture(self, data_buffer = None, log_time = False, debug_print = False, retry_reset = True):
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

    start = time.time()

    if data_buffer is None:
      data_buffer = np.ndarray((Lepton.ROWS, Lepton.COLS, 1), dtype=np.uint16)
    elif data_buffer.ndim < 2 or data_buffer.shape[0] < Lepton.ROWS or data_buffer.shape[1] < Lepton.COLS or data_buffer.itemsize < 2:
      raise Exception("Provided input array not large enough")

    while True:
      Lepton.capture_segment(self.__handle, self.__xmit_buf, self.__msg_size, self.__capture_buf[0])
      if retry_reset and (self.__capture_buf[20, 0] & 0xFF0F) != 0x1400: # make sure that this is a well-formed frame, should find line 20 here
        # Leave chip select deasserted for at least 185 ms to reset
        if debug_print:
          print("Garbage frame number reset waiting...")
        time.sleep(0.185)
      else:
        break

    self.__capture_buf.byteswap(True)
    data_buffer[:,:] = self.__capture_buf[:,2:]

    end = time.time()

    if debug_print:
      print("---")
      for i in range(Lepton.ROWS):
        fid = self.__capture_buf[i, 0, 0]
        crc = self.__capture_buf[i, 1, 0]
        fnum = fid & 0xFFF
        print("0x{0:04x} 0x{1:04x} : Row {2:2} : crc={1}".format(fid, crc, fnum))
      print("---")

    if log_time:
      print("frame processed int {0}s, {1}hz".format(end-start, 1.0/(end-start)))

    # TODO: turn on telemetry to get real frame id, sum on this array is fast enough though (< 500us)
    return data_buffer, data_buffer.sum()
