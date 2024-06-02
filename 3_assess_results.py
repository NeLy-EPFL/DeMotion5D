#!/usr/bin/env python3

import os
import sys

try:
    from elastixclasses import ElastixLog
except ImportError:
    print('Could not import ElastixLog from elastixclasses')
    print("Make sure run_elastix's scripts folder is on your PYTHONPATH")
    sys.exit(1)

move_failures = False
if '-m' in sys.argv:
    move_failures = True
    sys.argv.remove('-m')

fns = sys.argv[1:]

#data = []
pf = {'pass': 0, 'fail': 0}
for fn in fns:
    log = ElastixLog(fn)
    #data.append([log.final_correlation,
    #             log.final_bending_metric])
    #             log.asgd_settings()['SP_a']])
    if not log.good_results(correlation_threshold=0.95,
                            bending_threshold=0.000004,
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
        #print(f'Pass: {fn}')
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
