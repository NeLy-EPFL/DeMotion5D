#!/usr/bin/env python3

import sys
from pathlib import Path

from tqdm import tqdm
import npimage

#template_timepoint = 374
template_timepoint = None
planes = slice(1, -1)
metadata = {
    'space dimension': 3,
    'space directions': [[0, 0, 1.5], [0, 1.128, 0], [1.133, 0, 0]],
    'space units': ['microns', 'microns', 'microns']
}

fn = Path(sys.argv[1])
im = npimage.load(fn)
print('im.shape:', im.shape)

target = fn.parent / f'{fn.stem}_demotion'
target_timepoints = target / 'timepoints'
target_timepoints.mkdir(exist_ok=True, parents=True)


def get_vol(t, planes=planes):
    return im[t, planes, ...]


if template_timepoint is not None and not (target / 'template.nrrd').exists():
    template = get_vol(template_timepoint)
    npimage.save(template,
                 target / 'template.nrrd',
                 metadata=metadata)

interval = 1
for t in tqdm(range(0, im.shape[0], interval)):
    npimage.save(get_vol(t),
                 target_timepoints / f't{t:04d}.nrrd',
                 metadata=metadata,
                 overwrite=True)
