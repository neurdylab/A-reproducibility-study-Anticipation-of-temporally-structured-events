#!/bin/bash

cd ..
# Generate the subject list to make modifying this script
# to run just a subset of subjects easier.
# 

# `seq -w 1 30`
# "sub-$id"
for id in `seq -w 16 30` ; do
#for id in `seq 1` ; do
    for id2 in `seq 1 3` ; do
    #for id2 in `seq 1` ; do
        #subj="sub-$id"
        subj="sub-$id"
        run="run-0$id2"
        #subj="sub-14"
        #run="run-03"
        echo "===> Starting processing of $subj  $run"
        cd raw_data/$subj

        # If the anatomical is not stripped, create it
        if [ ! -f anat/${subj}_T1w_brain.nii.gz ]; then
            echo "Skull-stripped brain anat not found, using bet with a fractional intensity threshold of 0.5"
            bet2 anat/${subj}_T1w.nii.gz \
                anat/${subj}_T1w_brain.nii.gz -f 0.5 ## not sure about 0.5
        fi

        # If the functional is not stripped, create it
        if [ ! -f func/${subj}_task-movie_${run}_bold_brain.nii.gz ]; then
            echo "Skull-stripped brain func not found, using bet with a fractional intensity threshold of 0.5"
            bet func/${subj}_task-movie_${run}_bold.nii.gz \
                func/${subj}_task-movie_${run}_bold_brain.nii.gz  -F -f 0.5 ## not sure about 0.5
        fi

        # If averaged mag fmap doesn't exist, create it
        if [ !  -f fmap/${subj}_magnitude_mean.nii.gz ]; then
            echo "Averaged magnitude fmap not found, using fslmaths"
            fslmaths fmap/${subj}_magnitude1.nii.gz \
                -add fmap/${subj}_magnitude2.nii.gz \
                -div 2 fmap/${subj}_magnitude_mean.nii.gz
        fi

        # If the averaged mag fmap is not stripped, create it
        if [ ! -f fmap/${subj}_magnitude_mean_brain.nii.gz ]; then
            echo "Skull-stripped brain average mag fmap not found, using bet with a fractional intensity threshold of 0.5"
            bet2 fmap/${subj}_magnitude_mean.nii.gz \
                fmap/${subj}_magnitude_mean_brain.nii.gz -f 0.5 ## not sure about 0.5
        fi

        # If the phase fmap is not in rad/sec, convert it
        if [ ! -f fmap/${subj}_phasediff_radsec.nii.gz ]; then
            echo "Converting phasediff fieldmap to rad/sec"
            fslmaths fmap/${subj}_phasediff.nii.gz \
                -div 4096 -mul 3.14159 \
                fmap/${subj}_phasediff_radsec.nii.gz
        fi

        # If the phase rad/sec fmap is not pre-smoothed, smooth it
        if [ ! -f fmap/${subj}_phasediff_radsec_sm2.nii.gz ]; then
            echo "Pre-smoothing phase field map with Guassian kernel mm = 2"
            fslmaths fmap/${subj}_phasediff_radsec.nii.gz \
                -s 2 fmap/${subj}_phasediff_radsec_sm2.nii.gz
        fi

        # Copy fsf files into the subject directory, and then
        # change “sub-01” to the current subject number
        rm preproc_template.fsf
        cp ../../scripts/preproc_template.fsf .

        sed -i '' "s|sub-01|${subj}|g" \
            preproc_template.fsf
        sed -i '' "s|run-01|${run}|g" \
            preproc_template.fsf

        # Run FEAT analysis
        echo "Starting feat analysis"
        feat preproc_template.fsf

        cd ../../feat_data/${subj}-${run}.feat

        cd reg
        echo "Starting FLIRT transformation functional to standard"
        flirt -in ../../../raw_data/$subj/func/${subj}_task-movie_${run}_bold_brain.nii.gz \
            -ref standard.nii.gz -applyxfm \
            -init example_func2standard.mat \
            -out ../${subj}_${run}_tf_func.nii.gz

        echo "Starting FLIRT transformation highres to standard"
        flirt -in highres.nii.gz \
            -ref standard.nii.gz -applyxfm \
            -init highres2standard.mat \
            -out ../${subj}_${run}_tf_highres.nii.gz
        cd ..

        echo "Starting quality assurance check of $subj  $run"
        mkdir -p QA_imgs
        slicer "reg/example_func2standard.nii.gz" "reg/standard.nii.gz" -s 2 \
            -x 0.35 "QA_imgs/sla.png" -x 0.45 "QA_imgs/slb.png" -x 0.55 "QA_imgs/slc.png" -x 0.65 "QA_imgs/sld.png" \
            -y 0.35 "QA_imgs/sle.png" -y 0.45 "QA_imgs/slf.png" -y 0.55 "QA_imgs/slg.png" -y 0.65 "QA_imgs/slh.png" \
            -z 0.35 "QA_imgs/sli.png" -z 0.45 "QA_imgs/slj.png" -z 0.55 "QA_imgs/slk.png" -z 0.65 "QA_imgs/sll.png"

        pngappend "QA_imgs/sla.png" + "QA_imgs/slb.png" + "QA_imgs/slc.png" + "QA_imgs/sld.png" + "QA_imgs/sle.png" \
            + "QA_imgs/slf.png" + "QA_imgs/slg.png" + "QA_imgs/slh.png" + "QA_imgs/sli.png" + "QA_imgs/slj.png" \
            + "QA_imgs/slk.png" + "QA_imgs/sll.png" "${subj}_${run}_QA_image.png"

        cd ../..

    done
done