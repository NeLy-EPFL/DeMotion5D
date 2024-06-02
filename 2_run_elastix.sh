#!/bin/bash

for fn in $@; do
    run_elastix "$fn" -t template.nrrd -s 64 -w 400 -n
done
