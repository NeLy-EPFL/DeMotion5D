#!/usr/bin/env python3

import sys
from pathlib import Path

import numpy as np
from tqdm import trange
import npimage


target_timepoint = None
if '-t' in sys.argv:
    if sys.argv[-1] == '-t':
        raise ValueError('No target timepoint provided after -t')
    target_timepoint = int(sys.argv[sys.argv.index('-t') + 1])
    sys.argv.remove('-t')
    sys.argv.remove(str(target_timepoint))


fn = Path(sys.argv[1])
im, metadata = npimage.load(fn, return_metadata=True)
if not metadata['space dimension'] == 4:
    raise ValueError('Input image must have 4 dimensions (t, scan axis, depth, width')
# Discard the first and last planes, which typically have some artifacts from
# the galvo returning to the start position during part of the exposure time
# of each of these planes.
planes_to_keep = slice(1, -1)
# Discard the first few and last few z (depth) indices, which typically have
# some artifacts from I think a bug in Andor Solis's recording settings.
z_to_keep = slice(2, -2)
im = im[:, planes_to_keep, z_to_keep, :]
print('im.shape after discarding edge planes and z indices:', im.shape)

# Strip the time dimension from the metadata
del metadata['sizes']
del metadata['dimension']
del metadata['space dimension']
metadata['space directions'] = metadata['space directions'][1:, 1:]
metadata['space units'] = metadata['space units'][1:]

output_root = fn.parent / f'{fn.stem}_demotion'
output_timepoints = output_root / 'timepoints'
output_timepoints.mkdir(exist_ok=True, parents=True)

# Find the most stable image – the one that has the highest average
# correlation with its 4 closest neighboring timepoints.
print('Finding the most stable timepoint...')
correlations = []
for t in trange(2, im.shape[0]-2):
    correlations.append(np.mean([np.corrcoef(im[t, ...].ravel(),
                                             im[t+delta, ...].ravel())[0, 1]
                                 for delta in [-2, -1, 1, 2]]))
most_stable_timepoint = np.argmax(correlations) + 2
print('The most stable time point is', most_stable_timepoint)
correlations = []
for t in trange(im.shape[0]):
    correlations.append(np.corrcoef(im[most_stable_timepoint, ...].ravel(),
                                    im[t, ...].ravel())[0, 1])
top_4_correlated_timepoints = np.argsort(correlations)[-4:]
print('The 4 timepoints most correlated with the most stable time point are',
      top_4_correlated_timepoints)
mean_stable_image = np.mean([im[t, ...] for t in top_4_correlated_timepoints],
                            axis=0)
npimage.save(mean_stable_image,
             output_root / 'mean_stable_image.nrrd',
             metadata=metadata)

# Create a 3D volume for each timepoint and save each one to a nrrd file
interval = 1
for t in trange(0, im.shape[0], interval):
    npimage.save(im[t, ...],
                 output_timepoints / f't{t:04d}.nrrd',
                 metadata=metadata,
                 overwrite=True)

if not (output_root / 'target.nrrd').exists():
    if target_timepoint is None:
        (output_root / 'target.nrrd').symlink_to('mean_stable_image.nrrd')
    else:
        (output_root / 'target.nrrd').symlink_to(f'timepoints/t{target_timepoint:04d}.nrrd')
