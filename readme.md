# pylepton

Quick and dirty pure python library for capturing images from the Lepton over SPI (for example, on a Raspberry PI).

Requires `cv2` and `numpy` modules, if you don't have them already. On a Debian-based system you can probably do this:

    $ sudo apt-get install python-opencv python-numpy

You can run the examples in the working directory, but a distutils setup is included to install into site-packages for distribution:

    $ sudo python setup.py install

## Example usage

    import numpy as np
    import cv2
    from pylepton import Lepton

    with Lepton() as l:
      a,_ = l.capture()
    cv2.normalize(a, a, 0, 65535, cv2.NORM_MINMAX) # extend contrast
    np.right_shift(a, 8, a) # fit data into 8 bits
    cv2.imwrite("output.jpg", np.uint8(a)) # write it!

Image data from `capture()` is 12-bit, non-normalized (raw sensor data). Here we contrast extend it since the bandwidth tends to be narrow.

`capture()` returns a tuple that includes a unique frame ID, as lepton frames can update at ~27 Hz, but only unique ones are returned at ~9 Hz. Currently, this is just a simple sum, but ideally this will turn into a real frame ID from telemetry once this feature is implemented.

Note also that the Lepton contructor can take as an optional argument the SPI device on which to find the Lepton. If in your system that device is `/dev/spidev0.1`, you can instantiate lepton as such:

    ...
    with Lepton("/dev/spidev0.1") as l:
      ...

## Example programs

### pylepton_overlay

Requires `python-picamera`, a Raspberry PI, and compatible camera such as http://www.adafruit.com/products/1367

    $ sudo apt-get install python-picamera

    $ pylepton_overlay --help
    Usage: pylepton_overlay [options]

    Options:
      -h, --help            show this help message and exit
      -f, --flip-vertical   flip the output images vertically
      -a ALPHA, --alpha=ALPHA
                            set lepton overlay opacity

To get a 100% lepton overlay (note camera installation still required):

    $ pylepton_overlay -a 255

### pylepton_capture

Note that this program will output any image format that opencv knows about, just specify the output file format extension (e.g. `output.jpg` or `output.png`)

    $ pylepton_capture --help
    Usage: pylepton_capture [options] output_file[.format]

    Options:
      -h, --help           show this help message and exit
      -f, --flip-vertical  flip the output image vertically

To capture a png file named `output.png`:

    $ pylepton_capture output.png
