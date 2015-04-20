#!/usr/bin/env python

from distutils.core import setup
from pkgutil import walk_packages

import lepton

def find_packages(path=".", prefix=""):
    yield prefix
    prefix = prefix + "."
    for _, name, ispkg in walk_packages(path, prefix):
        if ispkg:
            yield name

setup(name='lepton',
      version='1.0',
      description='FLIR Lepton interface library for Python',
      author='Kurt Kiefer',
      author_email='kurt@kieferware.com',
      url='https://github.com/kekiefer/python-lepton',
      packages = list(find_packages(lepton.__path__, lepton.__name__)),
      install_depends = ['numpy', 'cv2'],
     )
