# DeMotion5D

Remove sample movement in 5D microscopy data (xyz plus time plus color)

## Installation
Install [run_elastix](https://github.com/htem/run_elastix)

## Prepare your image data
The only required input to this pipeline is a timeseries of 3D image volumes. (Typically you will have multiple of these, one for each color channel in your imaging data.) The first step (see below) converts a single 4D image volume (tzyx for a single color channel) into a series of 3D image volume files, which is the necessary starting point for step 2. If you have already created a timeseries of 3D volumes yourself, you can start with step 2.

Do be mindful of the fact that it's important to have the voxel size specified in your image volumes' metadata! Registration is performed in physical coordinates (e.g. microns), not voxel coordinates, so units must be provded in the metadata so that the physical size of your image volume is known.

## Steps
1. Make a sequence of nrrd files, one per time point per channel
1. Run elastix to register each timepoint to a common template
1. Check for poor results and troubleshoot/rerun those alignments
1. Apply the transforms to each timepoint in other color channels
1. Combine all transformed timepoints into a final volume
