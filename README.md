# DeMotion5D

Remove sample movement in 5D microscopy data (xyz plus time plus color)

## Installation
Install [run_elastix](https://github.com/htem/run_elastix) by following the instructions in its README. You can skip the part of the instructions where you're given the option to download a standard template to align to and to set the path to the standard template, because we will just be registering your microscopy data to itself at different time points.

## Prepare your image data
The only required input to this pipeline is a timeseries of 3D image volumes. (Typically you will have multiple of these, one for each color channel in your imaging data.) The first step (see below) converts a single 4D image volume (tzyx for a single color channel) into a series of 3D image volume files, which is the necessary starting point for step 2. If you have already created a timeseries of 3D volumes yourself, you can start with step 2.

Do be mindful of the fact that it's important to have the voxel size specified in your image volumes' metadata! Registration is performed in physical coordinates (e.g. microns), not voxel coordinates, so units must be provided in the metadata so that the physical size of your image volume is known.

## Steps
The whole pipeline is demonstrated in [`dmo_pipeline.sh`](dmo_pipeline.sh). To get started you can try running that script directly and see if the default settings work well for your dataset. If something goes wrong, you'll want to run the steps one by one and inspect the output after each step to see what you need to tweak.

The steps are as follows:
1. [`dmo1_split_timepoints`](dmo1_split_timepoints.py): Make a sequence of nrrd files, one per time point per channel
1. [`dmo2_run_elastix`](dmo2_run_elastix.sh): Run elastix to register each timepoint to a common target
1. (Optional, not run in `dmo_pipeline.sh`) [`dmo3_assess_registrations.py`](dmo3_assess_registrations.py): Check for poor results and troubleshoot/rerun those alignments
1. [`dmo4_apply_transforms`](dmo4_apply_transforms.sh): Apply the transforms to each timepoint in other color channels
1. [`dmo5_combine_timepoints`](dmo5_combine_timepoints.py): Combine all transformed timepoints into a final volume
