---
name: using-demotion5d
description: Remove sample motion from 5D (xyz + time + color) microscopy data via 3D image volume alignment. Load when user mentions DeMotion5D, demotion, dmo, dmo_pipeline, motion correction, demotioned data, sample movement, registering/aligning 3D volumes, or cleaning up leftover timepoints/ temp files eating disk space.
---

## What DeMotion5D is

DeMotion5D removes sample movement from 5D microscopy data (xyz plus time plus
color) by registering each timepoint volume to a common target with elastix.
For SCAPE data, the whole pipeline is driven by the `dmo_pipeline.sh` script
(repo: `NeLy-EPFL/DeMotion5D`), which chains the `dmo1..dmo5` steps.
`dmo_pipeline.sh` is assumed to be on `PATH`.

Much of the logic in DeMotion5D is general and can be borrowed in any other
application where there's a need to register 3D image volumes together.

To install DeMotion5D or troubleshoot an installation, load
`installation.md` in this skill directory.

## Running demotion


```bash
# Run on a single dataset
dmo_pipeline.sh j2_run3

# Example of running on all scans in a folder
for scan in *_run*; do dmo_pipeline.sh "$scan"; done
```

Important notes:
- NEVER run demotion on `*_HR` folders. `_HR` = high resolution = single
  timepoint, so motion correction is meaningless (there are no other timepoints
  to register to). Filter these out unconditionally, even if a `_HR` scan is
  explicitly listed — point this out and confirm before proceeding.
- Run sequentially, not in parallel – `dmo_pipeline.sh` uses many cores.
- Registration happens in physical coordinates (microns), so each input
  volume's metadata **must** carry the correct voxel size, or the results will
  be wrong.

## Outputs and done check

For a scan, demotion produces per-channel demotioned volumes:

- `<scan>/<scan>_red_demotioned.nrrd`
- `<scan>/<scan>_green_demotioned.nrrd`

**Done check** (per scan): treat demotion as already done — and skip it —
if `<scan>/<scan>_demotioned.nrrd` exists.

## What is valuable vs disposable inside a `*_demotion` folder

Each aligned channel gets a `<scan>/<scan>_<channel>_demotion/` folder:

```
<scan>_red_demotion/
├── combined_<params>.nrrd            final aligned volume    KEEP
├── combined_<params>_blur_tmax.nrrd  projection              KEEP
├── target.nrrd, target_mask.nrrd     links to the inputs     KEEP
├── stable_images.nrrd                                        KEEP
└── timepoints/
    ├── t0000.nrrd                    split input volume      DISPOSABLE
    └── t0000_elastix/
        ├── affine/
        │   ├── TransformParameters.0.txt                     KEEP
        │   ├── elastix.log, IterationInfo.*.txt              diagnostics
        │   └── result.0.nrrd         aligned timepoint       DISPOSABLE
        └── Bspline/
            ├── result.<params>.nrrd  -> <params>/result.0.nrrd  DISPOSABLE
            └── <params>/             same contents as affine/ above
```

**Under `timepoints/`, every `.nrrd` is regenerable and every `.txt` is not.**

- `TransformParameters.0.txt` costs hours of elastix compute per scan.
  `dmo4_apply_transforms.sh` reads it from the *source* folder to register a
  second channel, so discarding it forces a full re-registration.
- `t*.nrrd` regenerate with `dmo1_split_timepoints.py` from the raw
  `<scan>_<channel>.nrrd`, which demotion never modifies.
- `result.0.nrrd` regenerate from the retained transforms with transformix,
  far cheaper than re-running elastix.
- On the CIFS/SMB lab mount, `result.<params>.nrrd` are 1067-byte XSym
  symlinks to `<params>/result.0.nrrd`. A symlink audit surfaces thousands of
  these; they are temporary files.

## Intended end state, and finding folders that missed cleanup

`dmo_pipeline.sh` cleans up as it goes:

- `rm -rvf timepoints/t0000_elastix` immediately after the single test
  alignment that confirms elastix produces output
- `find timepoints/ -type f -name '*.nrrd' -delete` once
  `dmo5_combine_timepoints.py` has combined the primary channel. Deletes
  **only** the `.nrrd` files; the `timepoints/` tree and every transform
  parameter file stay.
- for the second channel, `timepoints/` and `timepoints_transformed/` are
  removed outright at the end, since its transforms live in the primary
  channel's folder.

A correctly finished primary-channel folder therefore keeps its full
`timepoints/` tree with **zero `.nrrd` files** in it, typically a few hundred
MB. Running the `dmo1..dmo5` steps by hand, or interrupting the pipeline,
leaves many GB of `.nrrd` behind.

Find folders that missed cleanup:

```bash
for d in */*/*_demotion */*_demotion; do
    [ -d "$d/timepoints" ] || continue
    n=$(find "$d/timepoints" -name '*.nrrd' -type f 2>/dev/null | wc -l)
    [ "$n" -gt 0 ] && echo "$n uncleaned nrrd files in $d"
done
```

To clean one up, replicate the primary-channel deletion. Confirm the raw
`<scan>/<scan>_<channel>.nrrd` still exists first — it is the only
irreplaceable input. If so, delete like so:

```bash
find <scan>/<scan>_<channel>_demotion/timepoints -type f -name '*.nrrd' -delete
```

**Never `rm -rf timepoints/`** — that discards the transform parameters too.

A missing `<scan>_demotioned.nrrd` means only that no final parameter set was
blessed; the folder is still safe to clean.

Note for agents: Harness settings may deny `find -delete`, `xargs rm`, and/or
globbed `rm`. Do not rephrase around these. Instead write the deletion as a
script driven by a pre-audited file manifest, and have the user run it
themselves.

## Related

- `scape-processing-pipeline` — runs demotion as one stage of the full
  SCAPE + behavior pipeline. It routes its "demotion" sub-mode here.
- `using-scapeio` — loading the demotioned scan volumes for analysis.
