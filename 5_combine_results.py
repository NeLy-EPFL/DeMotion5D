#!/usr/bin/env python3
"""
Combine multiple image files into a single volume along a new axis.
Typically used to combine multiple 3D volumes each representing a
different timepoint into a single 4D volume.

If a file named 'target.nrrd' exists in the current directory and is
a symlink to a file with a 4 digit number in its name, or if a
timepoint is specified via the -t <number> option, that timepoint
will be replaced by 'target.nrrd' in the combined volume.

Usage:
    5_combine_results.py [-t TARGET_TIMEPOINT] FILE1 [FILE2 ...]
"""

import sys
import os
from pathlib import Path

from tqdm import tqdm
import numpy as np
import npimage

if '-t' in sys.argv:
    if sys.argv[-1] == '-t':
        raise ValueError('-t must be followed by a number')
    target_timepoint = int(sys.argv[sys.argv.index('-t')+1])
#    target = [f for f in sys.argv[1] if f'{target_timepoint:04d}' in f]
#    if len(target) != 1:
#        raise ValueError(f'Could not find target timepoint {target_timepoint}')
#    target = Path(target[0])
elif Path('target.nrrd').exists():
    # Extract the target of the symlink
    #target = Path('target.nrrd').resolve()
    #target_timepoint = int(target.stem.strip('t'))
    target_timepoint = int(Path('target.nrrd').resolve().stem.strip('t'))

filenames = sorted(sys.argv[1:])
if f'{target_timepoint:04d}' not in filenames[target_timepoint]:
    if f'{target_timepoint+1:04d}' in filenames[target_timepoint]:
        filenames.insert(target_timepoint, 'target.nrrd')
    elif f'{target_timepoint+1:04d}' in filenames[target_timepoint+1]:
        filenames[target_timepoint] = 'target.nrrd'

im_shape = npimage.load(filenames[0]).shape
result = np.zeros((len(filenames),) + im_shape, dtype=np.uint16)
print('Combined volume will have shape', result.shape)
for t, fn in tqdm(enumerate(filenames), total=len(filenames)):
    # Check that a 4 digit version of i is in the filename
    if t != target_timepoint:
        assert f'{t:04d}' in fn
    im = np.clip(npimage.load(fn), 0, None)
    result[t] = im.astype(np.uint16)

out_fn = 'combined.nrrd'
if os.path.exists(out_fn):
    print(f'{out_fn} already exists, saving to tmp.nrrd instead')
    out_fn = 'tmp.nrrd'

npimage.save(result, out_fn)
npimage.save(result.mean(axis=1), out_fn.replace('.nrrd', '_zmean.nrrd'))
