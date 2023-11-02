import glob
import pickle
import tables
import nibabel as nib
import numpy as np
from numpy.random import default_rng
from data import find_valid_vox, save_s_lights
from s_light import optimal_events, compile_optimal_events, \
                    fit_HMM, compile_fit_HMM, \
                    shift_corr, compile_shift_corr

subjects = glob.glob('../processed_data2/*sub*')
#header_fpath = 'MNI152_T1_brain_resample.nii'

# Create valid_vox.nii mask
find_valid_vox('../processed_data2/', subjects)

# Create a separate data file for each searchlight
non_nan = nib.load('../processed_data2/valid_vox.nii').get_fdata().T > 0
save_s_lights('../processed_data2/', non_nan, '../processed_data2/SL/')