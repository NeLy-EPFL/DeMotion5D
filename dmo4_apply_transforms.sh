#!/bin/bash

show_help () {
    >&2 echo "Usage: ./4_apply_transforms.sh source_folder target_folder [target_folder2 ...]"
    >&2 echo "                               [-v] [-f] [-c num_cores]"
    >&2 echo "Apply the transforms from the source_folder to the target_folder(s)."
    >&2 echo ""
    >&2 echo "Positional arguments:"
    >&2 echo "  source_folder       The folder containing the elastix output from the source timepoints."
    >&2 echo "  target_folder       The folder(s) containing the timepoints to be transformed."
    >&2 echo ""
    >&2 echo "Optional arguments:"
    >&2 echo "  -v, --verbose       Run in verbose mode."
    >&2 echo "  -f, --fake          Run in fake mode (don't execute commands)."
    >&2 echo "  -c, --cores         The number of cores to use for transformix (default: 28)."
}

if [ "$#" -eq 0 ] || [ "$1" = "--help" ]; then
    show_help
    exit 1
fi

#DEFAULTS FOR ARGUMENT-MODIFIABLE VARIABLES GO HERE
verbose=false
fake=false
num_cores=28
alignment_settings='Bspline/*'

positionalArgs=()
unknownOptions=()
while [ "$#" -gt 0 ]; do
    case "$1" in
        -v|--verbose)
            verbose=true
            >&2 echo "Running verbose"
            shift
        ;;
        -f|--fake)
            fake=true
            >&2 echo "Running fake"
            shift
        ;;
        -s|--settings)
            alignment_settings="$2"
            shift; shift
        ;;
        -c|--cores)
            num_cores="$2"
            shift; shift
        ;;
        *)  # Catch all other arguments
            if [ " ${1:0:1}" = " -" ]; then  # Ignore arguments starting with - that aren't explicitly listed above
                unknownOptions+=("$1")
                >&2 echo "WARNING: Unknown option $1, ignoring"
            else
                if [ -z "${1/* */}" ]; then
                    >&2 echo "Spaces not allowed inside positional args: $1"
                    exit 1
                fi
                positionalArgs+=("$1")  # Store arguments (other than ones recognized above) in order
            fi
            shift
        ;;
    esac
done
set -- "${positionalArgs[@]}"  # Set the positional arguments, now without any of the options/flags arguments
if [ "$#" -eq 0 ]; then
    show_help
    exit 1
fi

#FAKEABLE COMMANDS GO HERE.
fakeableCommands="rm mv transformix"
#For the commands listed here, you can use "$command" instead of "command" anywhere in your code that you want the command to echo instead of execute when running in fake mode. For instance, write the line "$mv file1 file2" instead of "mv file1 file2" if you want that line's mv command to not execute when the -f flag is given. If you write "mv file1 file2", then your mv command will happen normally regardless of if -f is given.

if $fake; then
    for cmd in $fakeableCommands; do
        eval $cmd=\"echo \$cmd\"
    done
else
    for cmd in $fakeableCommands; do
        eval $cmd=\"\$cmd\"
    done
fi


source_folder="$1"
for target_folder in "${@:2}"; do
    mkdir "$target_folder"/timepoints_transformed 2> /dev/null
    if ! ls "$target_folder"/timepoints/t*.nrrd 1> /dev/null 2>&1; then
        >&2 echo "ERROR: No nrrd files found in $target_folder/timepoints"
        exit 1
    fi
    for target_file in "$target_folder"/timepoints/t*.nrrd; do
        echo ""
        echo "Processing $target_file"
        t=$(basename "$target_file" | sed 's/t\([0-9]*\).nrrd/\1/')
        transform_pattern="$source_folder"/timepoints/t"$t"_elastix/${alignment_settings}/TransformParameters.0.txt
        matched_files=($transform_pattern)
        if [ ${#matched_files[@]} -gt 1 ]; then
            >&2 echo "ERROR: Multiple transforms found for timepoint $t:"
            for f in "${matched_files[@]}"; do
                >&2 echo "$f"
            done
            echo "Use the -s flag to specify a more specific pattern."
            exit 1
        fi
        transform_file="${matched_files[0]}"
        if [ ! -f "$transform_file" ]; then
            >&2 echo "ERROR: No transform found for timepoint $t"
            exit 1
        fi
        $transformix -in "$target_file" -out "$target_folder"/timepoints_transformed -tp "$transform_file" -threads $num_cores
        echo transformix -in "$target_file" -out "$target_folder"/timepoints_transformed -tp "$transform_file" -threads $num_cores >> "$target_folder"/timepoints_transformed/transformix_commands.txt
        $mv "$target_folder"/timepoints_transformed/result.nrrd "$target_folder"/timepoints_transformed/t"$t".nrrd
    done
    $rm "$target_folder"/timepoints_transformed/transformix.log
done
