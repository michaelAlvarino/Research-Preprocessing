#!/bin/sh
#
#SBATCH --account=dsi # The account name for the job.
#SBATCH --job-name=AUDIOSET_CONVERSION # The job name.
#SBATCH -c 1 # The number of cpu cores to use.
#SBATCH --time=24:00 # The time the job will take to run.
#SBATCH --mem-per-cpu=1gb # The memory the job will use per cpu core.

module load anaconda

source activate preprocessing

#python download_extract_demand.py \
#    --log_level DEBUG \
#    --demand_dir /rigel/dsi/users/oc2241/DEMAND


#Command to execute Python program
python combine_vctk_demand.py \
    --url http://homepages.inf.ed.ac.uk/jyamagis/release/VCTK-Corpus.tar.gz \
    --log_level INFO \
    --demand_dir /rigel/dsi/users/oc2241/DEMAND \
    --vctk_dir /rigel/dsi/users/oc2241/VCTK/VCTK-Corpus \
    --output_dir /rigel/dsi/users/oc2241/VCTK_DEMAND

#End of script
