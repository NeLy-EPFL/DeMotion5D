#!/bin/bash
# This script shows the sequence of commands that can be run to register a 4D
# image volume, and optionally apply the registration transforms to a second channel.
#
# This script can be directly run on a data file and there is some chance that the full
# alignment process just works, but this can't be guaranteed. Instead it's often useful
# to run the commands here one at a time and manually inspect the intermediate results.

if [ "$#" -lt 1 ]; then
    echo "Align all timepoints in a 4D NRRD file to a common target, and"
    echo "optionally apply the alignment transformations to a second channel."
    echo "Usage:"
    echo "  dmo_pipeline.sh <nrrd_to_align> [<nrrd_second_channel>]"
    echo "  dmo_pipeline.sh <folder_containing_*red.nrrd_and_*green.nrrd>"
    exit 1
fi

# Check required packages are available
python3 -c "import numpy as np; from tqdm import trange; import npimage; import nrrd; from scipy.ndimage import gaussian_filter"
if [ $? -ne 0 ]; then
    echo "Error: Some required Python packages are not installed. Please \`pip install numpy tqdm numpyimage pynrrd scipy\`"
    exit 1
fi

nrrd_to_align=""
nrrd_second_channel=""
if [ -f "$1" ]; then
    nrrd_to_align="$1"
fi
if [ "$#" -gt 1 ]; then
    nrrd_second_channel="$2"
elif [ -d "$1" ]; then
    red_nrrds=("$1"/*_red.nrrd)
    # Check if there's exactly one red nrrd, if so, use it
    if [ "${#red_nrrds[@]}" -eq 1 ]; then
        nrrd_to_align="${red_nrrds[0]}"

        # Check if there's exactly one green nrrd
        green_nrrds=("$1"/*_green.nrrd)
        if [ "${#green_nrrds[@]}" -eq 1 ]; then
            nrrd_second_channel="${green_nrrds[0]}"
        elif [ "${#green_nrrds[@]}" -gt 1 ]; then
            echo "ERROR: More than one *_green.nrrd found in directory $1"
            exit 1
        fi
    elif [ "${#red_nrrds[@]}" -gt 1 ]; then
        echo "ERROR: More than one *_red.nrrd found in directory $1"
        exit 1
    else
        all_nrrds=("$1"/*.nrrd)
        if [ "${#all_nrrds[@]}" -eq 0 ]; then
            echo "ERROR: No NRRD files found in directory $1"
            exit 1
        fi
        if [ "${#all_nrrds[@]}" -gt 1 ]; then
            echo "ERROR: Multiple nrrd files found in directory $1"
            exit 1
        fi
        nrrd_to_align="${all_nrrds[0]}"
    fi
fi

if [ ! -f "$nrrd_to_align" ]; then
  echo "Error: $nrrd_to_align file not found."
  exit 1
fi
echo "Performing motion correction on $nrrd_to_align"
demotion_dir="${nrrd_to_align/.nrrd/_demotion}"
if [ -n "$nrrd_second_channel" ]; then
    if [ ! -f "$nrrd_second_channel" ]; then
        echo "Error: $nrrd_second_channel file not found."
        exit 1
    fi
    echo "Then applying the corrections computed in the first step to $nrrd_second_channel"
    demotion_dir_2="${nrrd_second_channel/.nrrd/_demotion}"
fi

dmo1_split_timepoints.py "$nrrd_to_align" -o


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
echo "Removing all temporary nrrd files within $(pwd)"
find timepoints/ -type f -name '*.nrrd' -delete

cd "$start_dir"
if [ "$(pwd)" != "$start_dir" ]; then
    echo "Error: Failed to change directory back to $start_dir."
    exit 1
fi
ln -s "$(basename "$demotion_dir")"/"$(basename "$demotion_dir"/combined_*w.nrrd)" "${nrrd_to_align/.nrrd/_demotioned.nrrd}"

# Apply transformations to the second channel, if provided
if [ -n "$nrrd_second_channel" ]; then
    dmo1_split_timepoints.py "$nrrd_second_channel" -t -1 -o
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
    echo "Removing temporary nrrd files $(pwd)/timepoints_transformed/t*.nrrd"
    rm timepoints_transformed/t*.nrrd
    rmdir timepoints_transformed/
    echo "Removing temporary nrrd files $(pwd)/timepoints/t*.nrrd"
    rm timepoints/t*.nrrd
    rmdir timepoints/
    cd "$start_dir"
    if [ "$(pwd)" != "$start_dir" ]; then
        echo "Error: Failed to change directory back to $start_dir."
        exit 1
    fi
    ln -s "$(basename "$demotion_dir_2")"/combined_redreg.nrrd "${nrrd_second_channel/.nrrd/_demotioned.nrrd}"
fi
