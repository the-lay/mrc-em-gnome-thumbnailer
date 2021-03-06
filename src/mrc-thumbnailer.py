#!/usr/bin/python3
# -*- coding: utf-8 -*-

import numpy as np
import sys
import mrcfile
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


if __name__ == '__main__':

    # parse arguments
    parser = argparse.ArgumentParser(description='Generate thumbnails for .mrc images')
    parser.add_argument('input',    type=str,   help='Path to input mrc file')
    parser.add_argument('output',   type=str,   help='Path to output png thumbnail')
    parser.add_argument('size',     type=int,   help='Thumbnail image size')
    arguments = parser.parse_args()

    # mmap the input file
    f = mrcfile.mmap(arguments.input, permissive=True)

    # extract central slice
    if len(f.data.shape) == 2:
        data = f.data
    elif len(f.data.shape) == 3:
        data = f.data[f.data.shape[0] // 2]
    else:
        f.close()
        sys.exit(-1)

    f.close()

    # contrast stretching to 2-98 percentile
    p2, p98 = np.percentile(data, (2, 98))
    data = rescale(data, in_range=(p2, p98))

    # rotate 180 deg and flip to be consistent with imagej/fiji
    data = np.rot90(data, 2)
    data = np.fliplr(data)

    # convert to PIL
    img = Image.fromarray(data)

    # resize to thumbnail
    img.thumbnail((arguments.size, arguments.size))

    # save image
    img.save(arguments.output)

    sys.exit(0)
