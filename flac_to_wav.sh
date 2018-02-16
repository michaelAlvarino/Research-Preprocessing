#!/bin/sh
#
#SBATCH --account=dsi # The account name for the job.
#SBATCH --job-name=AUDIOSET_CONVERSION # The job name.
#SBATCH -c 1 # The number of cpu cores to use.
#SBATCH --time=1:00 # The time the job will take to run.
#SBATCH --mem-per-cpu=1gb # The memory the job will use per cpu core.
 
module load anaconda

conda install -c conda-forge sox
 
#Command to execute Python program
python flac_to_wav.py \
 	--audioset_root /rigel/dsi/users/oc2241/AUDIOSET/data \
 	--output_dir /rigel/dsi/users/oc2241/AUDIOSET_WAV
 
#End of script
