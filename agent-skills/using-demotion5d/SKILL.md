---
name: using-demotion5d
description: Remove sample motion from 5D (xyz + time + color) microscopy data via 3D image volume alignment. Load when user mentions DeMotion5D, demotion, dmo, dmo_pipeline, motion correction, demotioned data, sample movement, or registering/aligning 3D volumes.
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

## Downstream: always analyze the demotioned data

All downstream analysis (ROI trace extraction, unmixing, encoding
models) must run on the demotioned volumes, never on the raw
`<scan>_red.nrrd` / `<scan>_green.nrrd`, which still contain motion that
corrupts per-pixel brightness traces. Load the demotioned data through
`scapeio.load_scan(scan)` (its `demotioned=True` default already does
this) rather than reading the `.nrrd` yourself — see the `using-scapeio`
skill for the loading/caching details.

## Related

- `scape-processing-pipeline` — runs demotion as one stage of the full
  SCAPE + behavior pipeline. It routes its "demotion" sub-mode here.
- `using-scapeio` — loading the demotioned scan volumes for analysis.
