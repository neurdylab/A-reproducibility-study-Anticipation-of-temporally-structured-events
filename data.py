import glob
import pickle
import tables
import numpy as np
import pandas as pd
import nibabel as nib
from s_light import get_s_lights
from utils import save_nii, load_sliced_nii

def find_valid_vox(fpath, subjects, min_subjs=15):
    """Loads data files to define valid_vox.nii

    Finds voxels that have data from at least min_subjs valid subjects and
    intersect with an MNI brain mask.

    Parameters
    ----------
    fpath : string
        Path to data directory
    subjects : list
        List of subjects to load
    min_subjs : int, optional
        Minimum number of subjects for a valid voxel
    """

    D_num_not_nan = []
    MNI_mask_path = fpath + 'scripts/preproc/MNI152_T1_brain_resample.nii' # used in both mainproc and preproc, should have in both?

    for subj in subjects:
        for run in range(3):
            sub_value = subj[subj.find('sub'):subj.find('sub')+6] # this takes subj and returns sub-01, etc
            run_value = 'run-0{}'.format(run+1) # this takes run # and returns run-01, etc
            fname = fpath + 'pre_outputs/{}/{}_{}_tf_func.nii.gz'.format(sub_value, sub_value, run_value)
            tsv_fpath = fpath + 'raw_data/{}/func/{}_task-movie_{}_events.tsv'.format(sub_value, sub_value, run_value)
            intact_data = load_sliced_nii(fname, tsv_fpath) # this is added to divide clips on the fly
            D_rep = np.zeros((121, 145, 121, 60))
            D_not_nan = np.zeros((121, 145, 121))

            for i in range(len(intact_data)):
                rep_z = intact_data[i].T
                nnan = ~np.all(rep_z == 0, axis=3) # nnan stands for not NaN
                rep_mean = np.mean(rep_z[nnan], axis=1, keepdims=True)
                rep_std = np.std(rep_z[nnan], axis=1, keepdims=True)
                rep_z[nnan] = (rep_z[nnan] - rep_mean)/rep_std # z scoring

                D_rep[nnan] += rep_z[nnan] # this is not used in this function, no need to calc
                D_not_nan[nnan] += 1 # adding 1 at every voxel that is 'valid' (not nan) from array of zeros

            D_num_not_nan.append(D_not_nan.T) # putting together all 3 runs for one subj

    non_nan_mask = np.min(D_num_not_nan, axis=0) # Min across reps (if value is 0 for any one of three reps, that is chosen)
    MNI_mask = nib.load(MNI_mask_path).get_fdata().astype(bool).T
    non_nan_mask = (non_nan_mask > (min_subjs - 1)) * MNI_mask # combined with MNI mask

    save_nii(fpath + 'pre_outputs/valid_vox.nii', fname, non_nan_mask)

def save_s_lights(fpath, non_nan_mask, savepath):
    """Save a separate data file for each searchlight

    Load subject data and divide into a separate file for each searchlight.
    This is helpful for parallelizing searchlight analyses in a cluster.

    Parameters
    ----------
    fpath : string
        Path to data directory
    non_nan_mask : ndarray
        3d boolean mask of valid voxels
    savepath : string
        Path to directory to save data files
    """

    subjects = glob.glob(fpath + '*sub*')
    coords = np.transpose(np.where(non_nan_mask)) # gets coords based on valid voxels from non_nan_mask
    SL_allvox = get_s_lights(coords) # every voxel that meets certain conditions gets turned into search light
    pickle.dump(SL_allvox, open(savepath + 'SL_allvox.p', 'wb'))
    nSL = 1 #len(SL_allvox) hardcoded for testing purposes

    for subj in subjects: # iterates over each subj (folder w/ 3 runs) and then over conditions (6 clips of each cond per subj)
        for cond in ['Intact', 'Fix', 'Rnd']:
            subjname = 'subj_' + subj.split('/')[-1]

            # this is added to divide clips on the fly
            sub_value = subj[subj.find('sub'):subj.find('sub')+6]
            all_intact_data = []
            for run in range(3):
                run_value = 'run-0{}'.format(run+1)
                intact_data = load_sliced_nii(sub_value, run_value, cond)
                all_intact_data.extend(intact_data)
        
            all_rep = []
            for i in range(6):
                # Load and z-score data
                rep_z = all_intact_data[i]
                rep_z = rep_z[:, non_nan_mask]
                nnan = ~np.all(rep_z == 0, axis=0)
                rep_mean = np.mean(rep_z[:,nnan], axis=0, keepdims=True)
                rep_std = np.std(rep_z[:,nnan], axis=0, keepdims=True)
                rep_z[:,nnan] = (rep_z[:,nnan] - rep_mean)/rep_std
                all_rep.append(rep_z) # z scored clip of len 60 being attached to all_rep

            # Append to SL hdf5 files
            for sl_i in range(nSL):
                sl_data = np.zeros((6, 60, len(SL_allvox[len(SL_allvox) - sl_i - 1]))) # iterating from the end because the first few are nans
                for i in range(6):
                    sl_data[i,:,:] = all_rep[i][:,SL_allvox[len(SL_allvox) - sl_i - 1]] # using coords of SL_allvox to find matching values in all_rep for each sl
                h5file = tables.open_file(savepath + str(sl_i) + '.h5', mode='a')

                if '/' + subjname not in h5file:
                    h5file.create_group('/', subjname)
                h5file.create_array('/' + subjname, cond, sl_data)
                h5file.close()