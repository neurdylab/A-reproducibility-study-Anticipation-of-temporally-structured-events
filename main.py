import glob
import pickle
import tables
import nibabel as nib
import numpy as np
import sys
from numpy.random import default_rng
from data import find_valid_vox, save_s_lights, scans_to_clips
from s_light import optimal_events, compile_optimal_events, \
                    fit_HMM, compile_fit_HMM, \
                    shift_corr, compile_shift_corr

nSL = 5247 # 5354 # ??
nPerm = 3 #100
max_lag = 10

fpath = '/media/bayrakrg/digbata2/anticipation/'
header_fpath = 'MNI152_T1_brain_resample.nii'
subjects = glob.glob(fpath + 'pre_outputs/*sub*')


############################
#       ONE TIME RUN       #
############################

# Save clips to save time during the analysis
scans_to_clips(fpath, subjects)

# # Create valid_vox.nii mask
find_valid_vox(fpath + 'pre_outputs/', subjects)

# Create a separate data file for each searchlight
non_nan = nib.load(fpath + 'pre_outputs/valid_vox.nii').get_fdata().T > 0
save_s_lights(fpath + 'pre_outputs/', non_nan, fpath + 'pre_outputs/SL/')

############################

# Run all analyses in each searchlight
# This will take ~1000 CPU hours, and so should be run
# in parallel on a cluster if possible


for sl_i in range(nSL):

    # Load data for this searchlight
    sl_h5 = tables.open_file(fpath + 'pre_outputs/SL/%d.h5' % sl_i, mode='r')
    data_list_orig = []
    for subj in subjects:
        subjname = '/subj_' + subj.split('/')[-1]
        d = sl_h5.get_node(subjname, 'IN').read()
        data_list_orig.append(d)
    sl_h5.close()
    nSubj = len(data_list_orig)

    sl_K = []
    sl_seg = []
    sl_shift_corr = []
    rng = default_rng(0)
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

    # Save results for this searchlight
    pickle.dump(sl_K,
                open(fpath + 'out/perm/optimal_events_%d.p' % sl_i, 'wb'))
    pickle.dump(sl_seg,
                open(fpath + 'out/perm/fit_HMM_%d.p' % sl_i, 'wb'))
    pickle.dump(sl_shift_corr,
                open(fpath + 'out/perm/shift_corr_%d.p' % sl_i, 'wb'))

# Compile results into final maps
SL_allvox = pickle.load(open(fpath + 'pre_outputs/SL/SL_allvox.p', 'rb'))
#SL_allvox = list(reversed(SL_allvox[5791:5792]))

compile_optimal_events(fpath + 'out/perm/', non_nan, SL_allvox,
                        header_fpath, fpath + 'out/')

opt_event = nib.load(fpath + 'out/optimal_events.nii').get_fdata().T
compile_fit_HMM(fpath + 'out/perm/', non_nan, SL_allvox,
                header_fpath, fpath + 'out/', opt_event)

compile_shift_corr(fpath + 'out/perm/', non_nan, SL_allvox,
                header_fpath, fpath + 'out/')