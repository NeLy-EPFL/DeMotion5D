#!/usr/bin/env python3

import sys
import os

from tqdm import tqdm
import numpy as np
import npimage

filenames = sorted(sys.argv[1:])
print(filenames)
im_shape = npimage.load(filenames[0]).shape
result = np.zeros((len(filenames),) + im_shape, dtype=np.float32)
print('result.shape', result.shape)
for t, fn in tqdm(enumerate(filenames)):
    # Check that a 4 digit version of i is in the filename
    assert f'{t:04d}' in fn
    result[t] = npimage.load(fn)

out_fn = 'combined.nrrd'
if os.path.exists(out_fn):
    print(f'{out_fn} already exists, saving to tmp.nrrd instead')
    out_fn = 'tmp.nrrd'

npimage.save(result, out_fn)
npimage.save(result.mean(axis=1), out_fn.replace('.nrrd', '_zmean.nrrd'))
