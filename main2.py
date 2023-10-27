import glob
import pickle
import tables
import numpy as np
import sys
from numpy.random import default_rng
from data import find_valid_vox, save_s_lights, scans_to_clips
from s_light import optimal_events, compile_optimal_events, \
                    fit_HMM, compile_fit_HMM, \
                    shift_corr, compile_shift_corr

nPerm = 1
max_lag = 10

fpath = '/data/neurogroup/anticipation_rg/'
fpath_out = '/data/neurogroup/anticipation_rg/'
subjects = glob.glob(fpath + 'processed_data2/*sub*')
sl_i = int(sys.argv[1])
#sl_i = 0
sl_K = []
sl_seg = []
sl_shift_corr = []
rng = default_rng(0)
#if (sl_i < 5476):
print(sl_i)
# Load data for this searchlight
sl_h5 = tables.open_file(fpath_out + 'pre_outputs2/SL/%d.h5' % sl_i, mode='r')
data_list_orig = []
for subj in subjects:``
    subjname = subj.split('/')[-1]
    subjname = '/' + subjname.replace('-','_')
    d = sl_h5.get_node(subjname, 'IN').read()
    data_list_orig.append(d)
sl_h5.close()
nSubj = len(data_list_orig)

# Repeat analyses for each permutation
for p in range(nPerm):
    data_list = []
    for s in range(nSubj):
        if p == 0:
            # This is the real (non-permuted) analysis
            subj_perm = np.arange(6)
        else:
            subj_perm = rng.permutation(6)
        data_list.append(data_list_orig[s][subj_perm])

    # Run all three analysis types
    sl_K.append(optimal_events(data_list, subjects))
    sl_seg.append(fit_HMM(data_list))
    sl_shift_corr.append(shift_corr(data_list, max_lag))
#else:
#        sl_seg.append(float('nan'))
#        sl_shift_corr.append(float('nan'))

# Save results for this searchlight
pickle.dump(sl_K,
            open(fpath_out + 'out2/perm/optimal_events_%d.p' % sl_i, 'wb'))
pickle.dump(sl_seg,
            open(fpath_out + 'out2/perm/fit_HMM_%d.p' % sl_i, 'wb'))
pickle.dump(sl_shift_corr,
            open(fpath_out + 'out2/perm/shift_corr_%d.p' % sl_i, 'wb'))