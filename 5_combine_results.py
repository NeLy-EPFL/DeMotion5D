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
import nrrd
import npimage

if '-t' in sys.argv:
    if sys.argv[-1] == '-t':
        raise ValueError('-t must be followed by a number')
    target_timepoint = int(sys.argv[sys.argv.index('-t')+1])
    # Remove the target timepoint from the list of files
    sys.argv.remove('-t')
    sys.argv.remove(str(target_timepoint))
#    target = [f for f in sys.argv[1] if f'{target_timepoint:04d}' in f]
#    if len(target) != 1:
#        raise ValueError(f'Could not find target timepoint {target_timepoint}')
#    target = Path(target[0])
elif Path('target.nrrd').exists():
    # Extract the target of the symlink
    #target = Path('target.nrrd').resolve()
    #target_timepoint = int(target.stem.strip('t'))
    try:
        target_timepoint = int(Path('target.nrrd').resolve().stem.strip('t'))
    except ValueError:
        print('WARNING: Could not determine target timepoint, so not using one')
        target_timepoint = -1

filenames = sorted(sys.argv[1:])
if target_timepoint >= 0:
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
        assert f'{t:04d}' in fn, f'Filename {fn} does not contain {t:04d}'
    im = np.clip(npimage.load(fn), 0, None)
    result[t] = im.astype(np.uint16)

if 'spacing' in fn and 'bendingweight' in fn:
    # Find the numbers immediately before 'spacing' and 'bendingweight'
    i = -1
    while fn.split('spacing')[0][i].isdigit():
        i -= 1
    spacing = fn.split('spacing')[0][i+1:]
    i = -1
    while fn.split('bendingweight')[0][i].isdigit():
        i -= 1
    bendingweight = fn.split('bendingweight')[0][i+1:]
    out_fn = f'combined_{spacing}s{bendingweight}w.nrrd'
elif 'affine' in fn:
    out_fn = 'combined_affine.nrrd'
else:
    out_fn = 'combined.nrrd'
if os.path.exists(out_fn):
    print(f'{out_fn} already exists, saving to tmp.nrrd instead')
    out_fn = 'tmp.nrrd'
# If the current working directory ends with `_demotion`, pull the metadata
# from the nrrd file with the same name as this directory
metadata = None
if os.getcwd().endswith('_demotion'):
    cwd = os.getcwd()
    unregistered_data_fn = cwd.split('/')[-1][:-len('_demotion')] + '.nrrd'
    unregistered_data_fn = os.path.join(os.path.dirname(os.getcwd()),
                                        unregistered_data_fn)
    if os.path.exists(unregistered_data_fn):
        metadata = nrrd.read_header(unregistered_data_fn)
        npimage.utils.transpose_metadata(metadata, inplace=True)
    else:
        print(f'WARNING: Could not find {unregistered_data_fn} to copy metadata from')

npimage.save(result, out_fn, metadata=metadata)
npimage.save(result.mean(axis=1),
             out_fn.replace('.nrrd', '_zmean.nrrd'),
             metadata=metadata)
