#!/bin/bash
#SBATCH --mail-user=rithwik.r.guntaka@vanderbilt.edu
#SBATCH --mail-type=ALL
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --mem=32G
#SBATCH --time=0-00:10:00
#SBATCH --output=anticipation_test2.out
#SBATCH --error=anticipation_test2.err
#SBATCH --job-name=anticipation_test2
#SBATCH --array=0-5205%10


# Put commands for executing job below this line
#echo $SLURM_ARRAY_TASK_ID
# array job
#singularity exec /scratch/guntakrr/proc2/anticipation6.sif python3 /scratch/guntakrr/proc2/main2.py 0
#/bin/bash /scratch/guntakrr/proc2/anticipation.sh 1
mapfile -t cmds < /data/neurogroup/anticipation_rg/og-code/anticipation_subjects2.csv
eval ${cmds[$SLURM_ARRAY_TASK_ID]}
#0-5205%10