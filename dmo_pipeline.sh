#!/bin/bash
# This script shows the sequence of commands that can be run to register a 4D
# image volume, and optionally apply the registration transforms to a second channel.
# This script can be directly run and then you pray nothing goes wrong (which is possible
# but far from guaranteed). Instead it's often useful to run the commands here one at
# a time and manually inspect the intermediate results.

nrrd_to_align="$1"
if [ ! -f "$nrrd_to_align" ]; then
  echo "Error: $nrrd_to_align file not found."
  exit 1
fi
demotion_dir="${nrrd_to_align/.nrrd/_demotion}"
dmo1_split_timepoints.py "$nrrd_to_align"

nrrd_second_channel=""
if [ "$#" -gt 1 ]; then
    nrrd_second_channel="$2"
    if [ ! -f "$nrrd_second_channel" ]; then
        echo "Error: $nrrd_second_channel file not found."
        exit 1
    fi
    demotion_dir_2="${nrrd_second_channel/.nrrd/_demotion}"
fi


start_dir=$(pwd)
cd "${demotion_dir}"
if [ "$(pwd)" = "$start_dir" ]; then
    echo "Error: Failed to change directory to $demotion_dir."
    exit 1
fi

# Test one alignment and make sure it produces output
dmo2_run_elastix.sh timepoints/t0000.nrrd
if ! ls timepoints/t0000_elastix/Bspline/result*.nrrd > /dev/null 2>&1; then
    echo "Error: elastix did not produce expected output."
    exit 1
fi
rm -rvf timepoints/t0000_elastix
# Run all alignments
dmo2_run_elastix.sh timepoints/t*.nrrd
# Combine results into a single file
dmo5_combine_timepoints.py timepoints/t*elastix/Bspline/result*.nrrd
cd ..
if [ "$(pwd)" != "$start_dir" ]; then
    echo "Error: Failed to change directory back to $start_dir."
    exit 1
fi
ln -s "$demotion_dir"/combined_*w.nrrd "${nrrd_to_align/.nrrd/_demotioned.nrrd}"

# Apply transformations to the second channel, if provided
if [ -n "$nrrd_second_channel" ]; then
    dmo1_split_timepoints.py "$nrrd_second_channel" -t -1
    dmo4_apply_transforms.sh "$demotion_dir" "$demotion_dir_2"

    wd="$(pwd)"
    cd "${demotion_dir_2}"
    if [ "$(pwd)" = "$wd" ]; then
        echo "Error: Failed to change directory to $demotion_dir_2."
        exit 1
    fi
    rm target.nrrd
    mv timepoints_transformed/transformix_commands.txt ./
    dmo5_combine_timepoints.py timepoints_transformed/t*nrrd
    mv combined.nrrd combined_redreg.nrrd
    mv combined_blur_tmax.nrrd combined_redreg_blur_tmax.nrrd
    echo "Removing intermediate files..."
    rm timepoints_transformed/t*nrrd
    rmdir timepoints_transformed/
    rm timepoints/t*nrrd
    rmdir timepoints/
    cd ..
    if [ "$(pwd)" != "$start_dir" ]; then
        echo "Error: Failed to change directory back to $start_dir."
        exit 1
    fi
    ln -s "$demotion_dir_2"/combined_redreg.nrrd "${nrrd_second_channel/.nrrd/_demotioned.nrrd}"
fi
