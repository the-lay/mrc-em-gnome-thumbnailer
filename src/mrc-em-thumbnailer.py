#!/usr/bin/python3
# -*- coding: utf-8 -*-

import numpy as np
import sys
import mrcfile
import emfile
import argparse
from PIL import Image
import warnings
warnings.simplefilter('ignore')


# Intensity rescaling helpers
# Shamelessly adapted from scikit-image
def rescale(image, in_range) -> np.ndarray:
    imin, imax = in_range
    image = np.clip(image, imin, imax)
    image = (image - imin) / (imax - imin)
    return np.asarray(image * 255., dtype=np.uint8)


# Read mrc file and return central slice
def mrc_central_slice(filename):

    # MrcMemmap reads dtype and shape from header
    # https://github.com/ccpem/mrcfile/blob/master/mrcfile/mrcmemmap.py#L92
    f = mrcfile.mmap(filename, permissive=True)

    # mrcfile can be 2D, should check for that
    ndim = len(f.data.shape)
    if ndim == 2:
        data = f.data
    elif ndim == 3:
        central_slice = f.data.shape[0] // 2
        data = f.data[central_slice]
    else:
        f.close()
        sys.exit(-1)

    f.close()

    return data


# Read em file header and return central slice
def em_central_slice(filename):

    _, f = emfile.read(filename, mmap=True)
    central_slice = f.shape[0] // 2
    data = f[central_slice]

    return data


if __name__ == '__main__':

    # parse arguments
    parser = argparse.ArgumentParser(description='Generate thumbnails for .mrc and .em images')
    parser.add_argument('input',    type=str,   help='Path to input file')
    parser.add_argument('output',   type=str,   help='Path to output png thumbnail')
    parser.add_argument('size',     type=int,   help='Thumbnail image size')
    arguments = parser.parse_args()

    # load data
    if arguments.input.endswith('.mrc'):
        data = mrc_central_slice(arguments.input)
    elif arguments.input.endswith('.em'):
        data = em_central_slice(arguments.input)
    else:
        sys.exit(-1)

    # contrast stretching to 2-98 percentile
    p2, p98 = np.percentile(data, (2, 98))
    data = rescale(data, in_range=(p2, p98))

    # convert to PIL
    img = Image.fromarray(data)

    # resize to thumbnail
    img.thumbnail((arguments.size, arguments.size))

    # save image
    img.save(arguments.output)

    sys.exit(0)
