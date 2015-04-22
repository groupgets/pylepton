#!/usr/bin/env python

from distutils.core import setup
from pkgutil import walk_packages

import pylepton

def find_packages(path=".", prefix=""):
    yield prefix
    prefix = prefix + "."
    for _, name, ispkg in walk_packages(path, prefix):
        if ispkg:
            yield name

setup(name='pylepton',
      version='0.1.2',
      description='FLIR Lepton interface library for Python',
      author='Kurt Kiefer',
      author_email='kurt@kieferware.com',
      url='https://github.com/kekiefer/pylepton',
      packages = list(find_packages(pylepton.__path__, pylepton.__name__)),
      scripts = ["pylepton_capture", "pylepton_overlay"],
      install_depends = ['numpy', 'cv2'],
     )
