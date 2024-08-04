#!/usr/bin/env python3

import sys
from pathlib import Path

from tqdm import tqdm
import npimage

#template_timepoint = 374
template_timepoint = None
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


def get_vol(t, planes=planes):
    return im[t, planes, ...]


if target_timepoint is not None and not (output_root / 'target.nrrd').exists():
    target = get_vol(target_timepoint)
    npimage.save(target,
                 output_root / 'target.nrrd',
                 metadata=metadata)

interval = 1
for t in tqdm(range(0, im.shape[0], interval)):
    npimage.save(get_vol(t),
                 output_timepoints / f't{t:04d}.nrrd',
                 metadata=metadata,
                 overwrite=True)
