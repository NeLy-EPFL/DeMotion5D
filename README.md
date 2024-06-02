# DeMotion5D

Remove sample movement in 5D microscopy data (xyz plus time plus color)

## Installation
Install [run_elastix](https://github.com/htem/run_elastix)

## Steps
1. Make a sequence of nrrd files, one per time point per channel
1. Run elastix to register each timepoint to a common template
1. Check for poor results and troubleshoot/rerun those alignments
1. Apply the transforms to each timepoint in other color channels
1. Combine all transformed timepoints into a final volume
