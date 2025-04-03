#!/bin/bash
# Example usage:
# dmo2_run_elastix.sh timepoints/*nrrd
# dmo2_run_elastix.sh /path/to/scan1.nrrd /path/to/scan2.nrrd ...
# for i in timepoints/t*nrrd; do if [ ! -e "${i/.nrrd}_elastix/Bspline/48spacing_400bendingweight" ]; then dmo2_run_elastix.sh $i; fi; done
#
# TODO:
# - Add command line arguments for common registration parameters (-s, -w)

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
if [ -f "target_mask.nrrd" ]; then
    mask="-tm target_mask.nrrd"
fi

for fn in $@; do
    run_elastix \
        "$fn" \
        -t target.nrrd \
        $mask \
        -ap "$SCRIPT_DIR/elastixParams/elastixParams_affine.txt" \
        -bp "$SCRIPT_DIR/elastixParams/elastixParams_Bspline.txt" \
        -s 48 \
        -w 400 \
        -n
done

<<comment
        --threads 8
        -a \
        -b \
        -s 64 \
        -w 800 \

comment
