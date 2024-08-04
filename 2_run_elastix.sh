#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

for fn in $@; do
    run_elastix \
        "$fn" \
        -t target.nrrd \
        -ap "$SCRIPT_DIR/elastixParams/elastixParams_affine.txt" \
        -bp "$SCRIPT_DIR/elastixParams/elastixParams_Bspline.txt" \
        -s 64 \
        -w 400 \
        -n
done
