import glob
import pickle
import tables
import nibabel as nib
import numpy as np
import sys
import subprocess
from numpy.random import default_rng
from data import find_valid_vox, save_s_lights, scans_to_clips
from s_light import optimal_events, compile_optimal_events, \
                    fit_HMM, compile_fit_HMM, \
                    shift_corr, compile_shift_corr


fpath = '/data/neurogroup/anticipation_rg/'
fpath_out = '/data/neurogroup/anticipation_rg/'
header_fpath = 'MNI152_T1_brain_resample.nii'


############################
#       ONE TIME RUN       #
############################

# Save clips to save time during the analysis
#scans_to_clips(fpath, subjects)

# # Create valid_vox.nii mask
#find_valid_vox(fpath + 'pre_outputs/', subjects)

# Create a separate data file for each searchlight
non_nan = nib.load(fpath + 'processed_data2/valid_vox.nii').get_fdata().T > 0
#save_s_lights(fpath + 'pre_outputs/', non_nan, fpath + 'pre_outputs/SL/')

############################

# Compile results into final maps
SL_allvox = pickle.load(open(fpath + 'processed_data2/SL/SL_allvox.p', 'rb')) #??

compile_optimal_events(fpath_out + 'out2/perm/', non_nan, SL_allvox,
                        header_fpath, fpath_out + 'out2/proc2-output/')

opt_event = nib.load(fpath_out + 'out2/proc2-output/optimal_events.nii').get_fdata().T
compile_fit_HMM(fpath_out + 'out2/perm/', non_nan, SL_allvox,
                header_fpath, fpath_out + 'out2/proc2-output/', opt_event)

compile_shift_corr(fpath_out + 'out2/perm/', non_nan, SL_allvox,
                header_fpath, fpath_out + 'out2/proc2-output/')