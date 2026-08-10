# Installing DeMotion5D

The authoritative install instructions live in the DeMotion5D repo
README (`../../README.md` in this repo, or
`https://github.com/NeLy-EPFL/DeMotion5D#installation`). Read that if
anything below is unclear or out of date.

## Dependency: run_elastix

DeMotion5D's registration steps are driven by `run_elastix`. Install it
first by following the README in `htem/run_elastix`
(`https://github.com/htem/run_elastix`). You can **skip** the part where
you're offered a standard template to align to and asked to set the path
to it — DeMotion5D registers your microscopy data to itself at different
time points, so no external template is needed.

## The DeMotion5D scripts

Clone the repo and put its scripts on `PATH` so `dmo_pipeline.sh` (and
the `dmo1..dmo5` steps it calls) resolve:

```bash
git clone https://github.com/NeLy-EPFL/DeMotion5D
```

The pipeline is `dmo_pipeline.sh`, which chains:

1. `dmo1_split_timepoints.py` — split a 4D volume (tzyx, one channel)
   into one nrrd per timepoint per channel
2. `dmo2_run_elastix.sh` — register each timepoint to a common target
3. `dmo4_apply_transforms.sh` — apply transforms to the other channels
4. `dmo5_combine_timepoints.py` — recombine into the final volume

(`dmo3_assess_registrations.py` is optional and not run by
`dmo_pipeline.sh`; use it to inspect and rerun poor alignments.)

## Troubleshooting

- `dmo_pipeline.sh: command not found` — the repo's scripts aren't on
  `PATH`. Add the DeMotion5D clone directory to `PATH`.
- elastix / registration errors — usually a `run_elastix` install
  problem, or missing voxel-size metadata on the input volumes
  (registration is done in physical units). Verify `run_elastix` runs
  standalone and that the input volumes carry correct voxel spacing.
- For anything else, consult the repo README.
