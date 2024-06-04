#!/usr/bin/env python3

import os
import sys

try:
    from elastixclasses import ElastixLog
except ImportError:
    print('Could not import ElastixLog from elastixclasses')
    print("Make sure run_elastix's scripts folder is on your PYTHONPATH")
    sys.exit(1)

verbose = False
move_failures = False
correlation_threshold = 0.95
bending_threshold = 0.000004
filenames = []
have_processed_n_next_args = 0
for n, arg in enumerate(sys.argv[1:]):
    if have_processed_n_next_args:
        have_processed_n_next_args -= 1
        continue
    elif arg == '-v':
        verbose = True
    elif arg == '-m':
        move_failures = True
    elif arg == '-c':
        correlation_threshold = float(sys.argv[n+2])
        have_processed_n_next_args = 1
    elif arg == '-b':
        bending_threshold = float(sys.argv[n+2])
        have_processed_n_next_args = 1
    else:
        filenames.append(arg)



#data = []
pf = {'pass': 0, 'fail': 0}
for fn in filenames:
    log = ElastixLog(fn)
    #data.append([log.final_correlation,
    #             log.final_bending_metric])
    #             log.asgd_settings()['SP_a']])
    if not log.good_results(correlation_threshold=correlation_threshold,
                            bending_threshold=bending_threshold,
                            verbose=False):
        print(f'Bad results: {fn}, {log.final_correlation}, {log.final_bending_metric}')
        pf['fail'] += 1
        # Rename the folder to append a _fail to the end
        if move_failures:
            if 'fail' in fn:
                print(f'File {fn} already has _fail in the name, not renaming')
                continue
            failnum = 1
            while os.path.exists(fn + f'_fail{failnum}'):
                print(f'File {fn}_fail{failnum} already exists')
                failnum += 1
            print(f'Renaming {fn} to {fn}_fail{failnum}')
            os.rename(fn, fn + f'_fail{failnum}')
    else:
        if verbose:
            print(f'Pass: {fn}, {log.final_correlation}, {log.final_bending_metric}')
        pf['pass'] += 1

print(f'Pass: {pf["pass"]}, Fail: {pf["fail"]}')

#from matplotlib import pyplot as plt
## Scatter plot data[0] vs data[2][-1]
#plt.scatter([d[0] for d in data], [d[2][-1] for d in data])
#plt.xlabel('Final correlation')
#plt.ylabel('SP_a[1]')
#plt.savefig('correlation_vs_SP_a1.png')
#plt.clf()
## Scatter plot data[1] vs data[2][-1]
#plt.scatter([d[1] for d in data], [d[2][-1] for d in data])
#plt.xlabel('Final bending metric')
#plt.ylabel('SP_a[1]')
#plt.savefig('bending_vs_SP_a1.png')
