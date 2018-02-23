#!/bin/sh
#
#SBATCH --account=dsi # The account name for the job.
#SBATCH --job-name=AUDIOSET_CONVERSION # The job name.
#SBATCH -c 1 # The number of cpu cores to use.
#SBATCH --time=24:00 # The time the job will take to run.
#SBATCH --mem-per-cpu=1gb # The memory the job will use per cpu core.

module load anaconda

source activate preprocessing

#Command to execute Python program
python combine_vctk_gaussian.py \
    /rigel/dsi/users/oc2241/VCTK \
    /rigel/dsi/users/oc2241/VCTK_GAUSSIAN

#End of script
