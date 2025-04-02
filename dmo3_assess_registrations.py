#!/usr/bin/env python3
"""
Example usage:
dmo3_assess_registrations.py timepoints/t*elastix/Bspline/48spacing_300bendingweight -m
"""

import os
import sys
from datetime import datetime
import math

try:
    from elastixclasses import ElastixLog
except ImportError:
    print('Could not import ElastixLog from elastixclasses')
    print("Make sure run_elastix's scripts folder is on your PYTHONPATH")
    sys.exit(1)

if len(sys.argv) < 2:
    print('Usage: dmo3_assess_regstrations.py [-v|--verbose] [-l|--log-to-file]'
          ' [-m|--move-bad-results] [-c correlation_threshold] [-b bending_threshold]'
          ' <elastix_results_folders>')
    sys.exit(1)

verbose = False
log_file = None
move_failures = False
delete_failures = False
correlation_threshold = 0.90
bending_threshold = 1e-5
filenames = []
have_processed_n_next_args = 0
for n, arg in enumerate(sys.argv[1:]):
    if have_processed_n_next_args:
        have_processed_n_next_args -= 1
        continue
    elif arg in ['-v', '--verbose']:
        verbose = True
    elif arg in ['-l', '--log-to-file']:
        log_file = open(f'registration_assessment_{datetime.now().strftime("%y%m%d%H%M%S")}.txt', 'w')
    elif arg in ['-m', '--move-bad-results']:
        move_failures = True
    elif arg in ['-d', '--delete-bad-results']:
        delete_failures = True
    elif arg == '-c':
        correlation_threshold = float(sys.argv[n+2])
        have_processed_n_next_args = 1
    elif arg == '-b':
        bending_threshold = float(sys.argv[n+2])
        have_processed_n_next_args = 1
    else:
        filenames.append(arg)
if move_failures and delete_failures:
    print('Cannot both move (-m) and delete (-d) bad results')
    sys.exit(1)


def lprint(*args, **kwargs):
    """Print to both stdout and a log file if one has been opened"""
    if log_file:
        print(*args, **kwargs, file=log_file)
    print(*args, **kwargs)


lprint('Using bending threshold:', bending_threshold)
lprint('Using correlation threshold:', correlation_threshold)

data = []
pf = {'pass': 0, 'fail': 0}
for fn in filenames:
    log = ElastixLog(fn)
    if not log.exists():
        lprint(f'No log file found for {fn}')
        continue
    if log.crashed():
        lprint(f'CRASHED: {fn}')
        continue

    bending = int(log.final_bending_metric*1e6) if not math.isnan(log.final_bending_metric) else math.nan
    data.append([fn,
                 log.final_correlation,
                 bending])

    if not log.good_results(correlation_threshold=correlation_threshold,
                            bending_threshold=bending_threshold,
                            verbose=False):
        lprint(f'Bad results: {fn}, {log.final_correlation}, {bending}')
        pf['fail'] += 1
        if delete_failures:
            raise NotImplementedError('delete_failures not implemented because it\'s scary')
        # Rename the folder to append a _fail to the end
        elif move_failures:
            if 'fail' in fn:
                lprint(f'File {fn} already has _fail in the name, not renaming')
                continue
            failnum = 1
            while os.path.exists(fn + f'_fail{failnum}'):
                lprint(f'File {fn}_fail{failnum} already exists')
                failnum += 1
            lprint(f'Renaming {fn} to {fn.rstrip("/")}_fail{failnum}')
            os.rename(fn, fn.rstrip('/') + f'_fail{failnum}')
    else:
        if verbose:
            lprint(f'Pass: {fn}, {log.final_correlation}, {bending}')
        pf['pass'] += 1

nans = [d for d in data if math.isnan(d[1]) or math.isnan(d[2])]
if len(nans) > 0:
    lprint('Some results have NaNs:')
    for n in nans:
        lprint(n)
lprint('\nWorst 25 results by bending metric:')
data = sorted(data, key=lambda x: x[2] if not math.isnan(x[2]) else math.inf, reverse=True)
for d in data[:25]:
    lprint(d[0], d[2])

lprint(f'Pass: {pf["pass"]}, Fail: {pf["fail"]}')

if log_file:
    log_file.close()
