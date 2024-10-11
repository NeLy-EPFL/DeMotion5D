#!/usr/bin/env python3

import sys
from pathlib import Path

import numpy as np
from tqdm import trange
import npimage


def vprint(*args, **kwargs):
    if verbose:
        print(*args, **kwargs)


# Argument parsing
z_to_drop = 2
if '-z' in sys.argv:
    if sys.argv[-1] == '-z':
        raise ValueError('No number of z planes to drop provided after -z')
    z_to_drop = int(sys.argv[sys.argv.index('-z') + 1])
    sys.argv.remove('-z')
    sys.argv.remove(str(z_to_drop))
planes_to_drop = 1
if '-p' in sys.argv:
    if sys.argv[-1] == '-p':
        raise ValueError('No number of planes to drop provided after -p')
    planes_to_drop = int(sys.argv[sys.argv.index('-p') + 1])
    sys.argv.remove('-p')
    sys.argv.remove(str(planes_to_drop))
target_timepoint = None
if '-t' in sys.argv:
    if sys.argv[-1] == '-t':
        raise ValueError('No target timepoint provided after -t')
    target_timepoint = int(sys.argv[sys.argv.index('-t') + 1])
    sys.argv.remove('-t')
    sys.argv.remove(str(target_timepoint))
use_n_most_correlated_timepoints = 5
if '-n' in sys.argv:
    if sys.argv[-1] == '-n':
        raise ValueError('No number of most correlated timepoints provided after -n')
    use_n_most_correlated_timepoints = int(sys.argv[sys.argv.index('-n') + 1])
    sys.argv.remove('-n')
    sys.argv.remove(str(use_n_most_correlated_timepoints))
overwrite = False
if '-o' in sys.argv:
    overwrite = True
    sys.argv.remove('-o')
verbose = False
if '-v' in sys.argv:
    verbose = True
    sys.argv.remove('-v')
fn = Path(sys.argv[1])
vprint('Dropping', planes_to_drop, 'first and last planes from each volume')
vprint('Dropping', z_to_drop, 'first and last z indices from each volume')
vprint('Target timepoint:', target_timepoint)
vprint('Using the', use_n_most_correlated_timepoints, 'most correlated timepoints')
vprint('Overwriting:', overwrite)
vprint('Input file:', fn)
# End argument parsing

im, metadata_4d = npimage.load(fn, return_metadata=True)
if not metadata_4d['space dimension'] == 4:
    raise ValueError('Input image must have 4 dimensions (t, scan axis, depth, width')
# Discard the first and last planes, which typically have some artifacts from
# the galvo returning to the start position during part of the exposure time
# of each of these planes.
planes_to_keep = slice(planes_to_drop, -planes_to_drop if planes_to_drop else None)
# Discard the first few and last few z (depth) indices, which typically have
# some artifacts from I think a bug in Andor Solis's recording settings.
z_to_keep = slice(z_to_drop, -z_to_drop if z_to_drop else None)
im = im[:, planes_to_keep, z_to_keep, :]
vprint('im.shape after discarding edge planes and z indices:', im.shape)

# Strip the time dimension from the metadata
del metadata_4d['sizes']
metadata_3d = metadata_4d.copy()
del metadata_3d['dimension']
del metadata_3d['space dimension']
metadata_3d['space directions'] = metadata_3d['space directions'][1:, 1:]
metadata_3d['space units'] = metadata_3d['space units'][1:]

output_root = fn.parent / f'{fn.stem}_demotion'
output_timepoints = output_root / 'timepoints'
output_timepoints.mkdir(exist_ok=True, parents=True)

# Find the most stable image – the one that has the highest average
# correlation with its 4 closest neighboring timepoints.
vprint('Finding the most stable timepoint...')
correlations = []
for t in trange(2, im.shape[0]-2):
    correlations.append(np.mean([np.corrcoef(im[t, ...].ravel(),
                                             im[t+delta, ...].ravel())[0, 1]
                                 for delta in [-2, -1, 1, 2]]))
most_stable_timepoint = np.argmax(correlations) + 2
vprint('The most stable time point is', most_stable_timepoint)
correlations = []
for t in trange(im.shape[0]):
    correlations.append(np.corrcoef(im[most_stable_timepoint, ...].ravel(),
                                    im[t, ...].ravel())[0, 1])
n_most_correlated_timepoints = np.argsort(correlations)[-use_n_most_correlated_timepoints:]
vprint(f'The {use_n_most_correlated_timepoints} timepoints most correlated with'
       f' the most stable time point are {n_most_correlated_timepoints}')
stable_images = [im[t, ...] for t in n_most_correlated_timepoints]
npimage.save(np.stack(stable_images),
             output_root / 'stable_images.nrrd',
             metadata=metadata_4d,
             overwrite=overwrite)
mean_stable_image = np.mean(stable_images, axis=0).astype(im.dtype)
npimage.save(mean_stable_image,
             output_root / 'mean_stable_image.nrrd',
             metadata=metadata_3d,
             overwrite=overwrite)

# Create a 3D volume for each timepoint and save each one to a nrrd file
interval = 1
for t in trange(0, im.shape[0], interval):
    npimage.save(im[t, ...],
                 output_timepoints / f't{t:04d}.nrrd',
                 metadata=metadata_3d,
                 overwrite=overwrite)

if not (output_root / 'target.nrrd').exists():
    if target_timepoint is None:
        (output_root / 'target.nrrd').symlink_to('mean_stable_image.nrrd')
    else:
        (output_root / 'target.nrrd').symlink_to(f'timepoints/t{target_timepoint:04d}.nrrd')
