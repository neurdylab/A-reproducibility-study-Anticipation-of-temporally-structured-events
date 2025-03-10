import glob
import pickle
import tables
import numpy as np
import pandas as pd
import pandas as pd
import nibabel as nib
import os
from s_light import get_s_lights
from utils import save_nii, save_clip_nii

def scans_to_clips(fpath, subjects):
    """Splits each subject scan into clips based on their tsv file and writes out these as nii images.

    There is total of 6 clips per scans. 2 intact (IN), 2 scrambled fixed (SF), 2 scrambled random (SR). 

    Parameters
    ----------
    fpath : string
        Path to data directory
    subjects : list
        List of subjects to process

    """
    for subj in subjects:
        for run in os.listdir(subj):
            if 'func_brain.nii.gz' in run:
                print('Processing ' + run)
                sub_id = run[run.find('sub'):run.find('sub')+6] # this takes subj and returns sub-01, etc
                fname = fpath + 'pre_outputs/' + sub_id + '/' + run # preprocessed functional file
                run_str = run[run.find('run'):run.find('run')+6] # this takes subj and returns sub-01, etc
                tsv_fpath = fpath + 'raw_data/{}/func/{}_task-movie_{}_events.tsv'.format(sub_id, sub_id, run_str)
                save_clip_nii(fname, tsv_fpath) # this is added to divide clips before the analysis


def find_valid_vox(fpath, subjects, min_subjs=15):
    """Loads data files to define valid_vox.nii

    Finds voxels that have data from at least min_subjs valid subjects and
    intersect with an MNI brain mask.

    Parameters
    ----------
    fpath : string
        Path to data directory
    subjects : list
        List of subjects to use
    min_subjs : int, optional
        Minimum number of subjects for a valid voxel
    """

    D_num_not_nan = []
    MNI_path = 'MNI152_T1_brain_resample.nii'
    print("Loading data", end='', flush=True)
    for rep in range(6):
        # D_rep = np.zeros((121, 145, 121, 60))
        D_not_nan = np.zeros((121, 145, 121))
        for subj in subjects:
            print('.', end='', flush=True)
            fname = glob.glob(subj + '/*IN*' +
                            str(rep + 1) + '.nii.gz')

            assert len(fname) == 1, \
                    "More than one file found for subject " + subj
            
            print(fname[0])

            rep_z = nib.load(fname[0]).get_fdata()
            # nnan = ~np.all(rep_z == 0, axis=3) 
            nnan = ~np.squeeze(np.std(rep_z, axis=3, keepdims=True) == 0) # find voxels with std == 0
            # nnan = ~np.all(rep_z <= np.percentile(rep_z, 10), axis=3) 
            # rep_mean = np.mean(rep_z[nnan], axis=1, keepdims=True) # mean for each voxel
            # rep_std = np.std(rep_z[nnan], axis=1, keepdims=True) # std for each voxel
            # rep_z[nnan] = (rep_z[nnan] - rep_mean)/rep_std

            # D_rep[nnan] += rep_z[nnan]
            D_not_nan[nnan] += 1

        D_num_not_nan.append(D_not_nan.T)
    print(' ')

    non_nan_mask = np.min(D_num_not_nan, axis=0) # Min across reps
    MNI_mask = nib.load(MNI_path).get_fdata().astype(bool).T
    non_nan_mask = (non_nan_mask > (min_subjs - 1)) * MNI_mask

    save_nii(fpath + 'valid_vox.nii', MNI_path, non_nan_mask)

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
    coords = np.transpose(np.where(non_nan_mask))
    SL_allvox = get_s_lights(coords) # returns indices of coordinates in a searchlight
    pickle.dump(SL_allvox, open(savepath + 'SL_allvox.p', 'wb')) # you need to have the right version of python to open it
    nSL = len(SL_allvox)

    for subj in subjects:
        subjname = 'subj_' + subj.split('/')[-1]
        print(subjname)
        for cond in ['IN', 'SF', 'SR']:
            print("   " + cond)
            all_rep = []
            for i in range(6):
                # Load and z-score data
                fname = glob.glob(subj + '/*' +
                                cond + '*' + str(rep + 1) + '.nii.gz')
                rep_z = nib.load(fname[0]).get_fdata().T
                rep_z = rep_z[:, non_nan_mask]

                nnan = ~np.squeeze(np.std(rep_z, axis=0, keepdims=True) == 0) # find voxels with std == 0
                # nnan = ~np.all(rep_z == 0, axis=0) 

                rep_mean = np.mean(rep_z[:,nnan], axis=0, keepdims=True)
                rep_std = np.std(rep_z[:,nnan], axis=0, keepdims=True)

                rep_z[:,nnan] = (rep_z[:,nnan] - rep_mean)/rep_std
                all_rep.append(rep_z)

                # look at nii img
                # img = rep_z.reshape(((60, 121, 145, 121)))
                # data = nib.load(fname[0])
                # new_img = nib.Nifti1Image(img.T, data.affine, data.header)
                # nib.save(new_img, '/media/bayrakrg/digbata2/anticipation/pre_outputs/test.nii')

            # Append to SL hdf5 files
            for sl_i in range(nSL):
                sl_data = np.zeros((6, 60, len(SL_allvox[sl_i])))
                for rep in range(6):
                    sl_data[rep,:,:] = all_rep[rep][:,SL_allvox[sl_i]]
                h5file = tables.open_file(savepath + str(sl_i) + '.h5',
                                        mode='a')

                if '/' + subjname not in h5file:
                    h5file.create_group('/', subjname)
                h5file.create_array('/' + subjname, cond, sl_data)
                h5file.close()