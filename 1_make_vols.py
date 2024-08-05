#!/usr/bin/env python3

import sys
from pathlib import Path

from tqdm import tqdm
import npimage


target_timepoint = 0
if '-t' in sys.argv:
    if sys.argv[-1] == '-t':
        raise ValueError('No target timepoint provided after -t')
    target_timepoint = int(sys.argv[sys.argv.index('-t') + 1])
    sys.argv.remove('-t')
    sys.argv.remove(str(target_timepoint))

# Discard the first and last planes, which typically have some artifacts from
# the galvo returning to the start position during part of the exposure time
# of each of these planes.
planes = slice(1, -1)

fn = Path(sys.argv[1])
im, metadata = npimage.load(fn, return_metadata=True)
if not metadata['space dimension'] == 4:
    raise ValueError('Input image must have 4 dimensions')
del metadata['space dimension']
# Strip the time dimension from the metadata
metadata['space directions'] = metadata['space directions'][1:, 1:]
metadata['space units'] = metadata['space units'][1:]
print('im.shape:', im.shape)

output_root = fn.parent / f'{fn.stem}_demotion'
output_timepoints = output_root / 'timepoints'
output_timepoints.mkdir(exist_ok=True, parents=True)


# Create a 3D volume for each timepoint and save each one to a nrrd file
interval = 1
for t in tqdm(range(0, im.shape[0], interval)):
    npimage.save(im[t, planes, ...],
                 output_timepoints / f't{t:04d}.nrrd',
                 metadata=metadata,
                 overwrite=True)

if not (output_root / 'target.nrrd').exists():
    (output_root / 'target.nrrd').symlink_to(f'timepoints/t{target_timepoint:04d}.nrrd')
