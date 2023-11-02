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

#header_fpath = '../data/0407161_predtrw02/filtFuncMNI_Intact_Rep1.nii'
header_fpath = 'MNI152_T1_brain_resample.nii'

# Create a separate data file for each searchlight
non_nan = nib.load('../processed_data2/valid_vox.nii').get_fdata().T > 0

# Compile results into final maps
SL_allvox = pickle.load(open('../processed_data2/SL/SL_allvox.p', 'rb'))
compile_optimal_events('../out2/perm/', non_nan, SL_allvox,
                        header_fpath, '../out2/og-output/')
opt_event = nib.load('../out2/optimal_events.nii').get_fdata().T
compile_fit_HMM('../out2/perm/', non_nan, SL_allvox,
                header_fpath, '../out2/og-output/', opt_event)
compile_shift_corr('../out2/perm/', non_nan, SL_allvox,
                   header_fpath, '../out2/og-output/')
