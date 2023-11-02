#!/bin/bash
#SBATCH --mail-user=rithwik.r.guntaka@vanderbilt.edu
#SBATCH --mail-type=ALL
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --mem=64G
#SBATCH --time=0-12:00:00
#SBATCH --output=anticipation_test3.out
#SBATCH --error=anticipation_test3.err
#SBATCH --job-name=anticipation_test3

# Put commands for executing job below this line

singularity exec /data/neurogroup/anticipation_rg/proc2/anticipation6.sif python3 /data/neurogroup/anticipation_rg/og-code/main3.py
