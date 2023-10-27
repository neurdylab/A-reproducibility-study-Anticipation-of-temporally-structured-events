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


fpath = '/data/neurogroup/anticipation/'
fpath_out = '/data/neurogroup/anticipation_rg/'
header_fpath = 'MNI152_T1_brain_resample.nii'
#subjects = list(range(1,31))
#subjects = [str(i).zfill(2) for i in subjects]
#subjects = ['sub-'+i for i in subjects]
subjects = glob.glob(fpath_out + 'processed_data2/*sub*/')
print(subjects)

############################
#       ONE TIME RUN       #
############################

# Save clips to save time during the analysis
#scans_to_clips(fpath, fpath_out, subjects)

# # Create valid_vox.nii mask
#find_valid_vox(fpath_out + 'processed_data2/', subjects)

# Create a separate data file for each searchlight
#print("test1")
non_nan = nib.load(fpath_out + 'processed_data2/valid_vox.nii').get_fdata().T > 0
#print("test2")
save_s_lights(fpath_out + 'processed_data2/', non_nan, fpath_out + 'pre_outputs2/SL/')