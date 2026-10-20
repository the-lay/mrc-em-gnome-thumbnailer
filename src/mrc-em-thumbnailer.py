#!/usr/bin/python3
# -*- coding: utf-8 -*-

import numpy as np
import sys
import struct
import argparse
from PIL import Image
import warnings
warnings.simplefilter('ignore')

# Supported data types, by MRC2014 mode and EM data type
# https://www.ccpem.ac.uk/mrc_format/mrc2014.php
MRC_DTYPES = {0: 'i1', 1: 'i2', 2: 'f4', 6: 'u2', 12: 'f2'}
EM_DTYPES = {1: 'i1', 2: 'i2', 4: 'i4', 5: 'f4', 9: 'f8'}


# Intensity rescaling helpers
# Shamelessly adapted from scikit-image
def rescale(image, in_range) -> np.ndarray:
    imin, imax = in_range
    image = np.clip(image, imin, imax)
    image = (image - imin) / ((imax - imin) or 1)
    return np.asarray(np.nan_to_num(image) * 255., dtype=np.uint8)


# Read only the central slice of a (nz, ny, nx) array stored after a header
def central_slice(filename, offset, dtype, nx, ny, nz):
    offset += (nz // 2) * nx * ny * dtype.itemsize
    return np.fromfile(filename, dtype=dtype, count=nx * ny, offset=offset).reshape(ny, nx)


# Read mrc file header and return central slice
def mrc_central_slice(filename):

    with open(filename, 'rb') as f:
        header = f.read(1024)

    # machine stamp is 0x11 for big-endian, 0x44 for little-endian
    order = '>' if header[212] == 0x11 else '<'
    nx, ny, nz, mode = struct.unpack(order + '4i', header[:16])
    extended_header_size, = struct.unpack(order + 'i', header[92:96])
    dtype = np.dtype(order + MRC_DTYPES[mode])

    return central_slice(filename, 1024 + extended_header_size, dtype, nx, ny, nz)


# Read em file header and return central slice
def em_central_slice(filename):

    with open(filename, 'rb') as f:
        header = f.read(512)

    nx, ny, nz = struct.unpack('<3i', header[4:16])
    dtype = np.dtype('<' + EM_DTYPES[header[3]])

    return central_slice(filename, 512, dtype, nx, ny, nz)


if __name__ == '__main__':

    # parse arguments
    parser = argparse.ArgumentParser(description='Generate thumbnails for .mrc and .em images')
    parser.add_argument('input',    type=str,   help='Path to input file')
    parser.add_argument('output',   type=str,   help='Path to output png thumbnail')
    parser.add_argument('size',     type=int,   help='Thumbnail image size')
    arguments = parser.parse_args()

    # load data; everything that is not .em is MRC (.mrc, .mrcs, .map, .rec, ...)
    if arguments.input.lower().endswith('.em'):
        data = em_central_slice(arguments.input)
    else:
        data = mrc_central_slice(arguments.input)

    # contrast stretching to 2-98 percentile
    p2, p98 = np.nanpercentile(data, (2, 98))
    data = rescale(data, in_range=(p2, p98))

    # convert to PIL
    img = Image.fromarray(data)

    # resize to thumbnail
    img.thumbnail((arguments.size, arguments.size))

    # save image
    img.save(arguments.output, 'PNG')

    sys.exit(0)
