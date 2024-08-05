#!/bin/bash
# Example usage:
# 2_run_elastix.sh timepoints/*nrrd
# 2_run_elastix.sh /path/to/scan1.nrrd /path/to/scan2.nrrd ...

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

for fn in $@; do
    run_elastix \
        "$fn" \
        -t target.nrrd \
        -ap "$SCRIPT_DIR/elastixParams/elastixParams_affine.txt" \
        -bp "$SCRIPT_DIR/elastixParams/elastixParams_Bspline.txt" \
        -s 48 \
        -w 400 \
        -n
done
