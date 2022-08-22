import os

num_subj = 30
num_runs = 3

fname = '/media/bayrakrg/digbata1/anticipation/scripts/preproc/apply_trans_mat.sh'
top = '#!/bin/bash'
line = 'bash anticipation_proc.sh sub-{} run-0{}'

with open(fname, 'w') as f:
    f.write('{}\n'.format(top))

    for i in range(num_subj):
        for j in range(num_runs):
            run = line.format("%02d" % (i+1), j+1)
            f.write('{} & \n'.format(run))
            if j %2 == 1:
                f.write('wait \n'.format(run))