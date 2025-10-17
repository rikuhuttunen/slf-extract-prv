#!/bin/bash
#SBATCH --job-name extract-prv # Name for your job
#SBATCH --ntasks 2              # Number of (cpu) tasks
#SBATCH --time 1200               # Runtime in minutes.
#SBATCH --mem=20000             # Reserve 20 GB RAM for the job
#SBATCH --partition small         # Partition to submit
#SBATCH --output slurm_outputs/slf-extract-prv_%j.txt       # Standard out goes to this file
#SBATCH --error slurm_outputs/slf-extract-prv_%j.txt        # Standard err goes to this file

# Activate conda env
eval "$(conda shell.bash hook)"
conda activate slf-extract-prv

# RUN BENCHMARK
python src/slf_extract_prv/extract_ibis.py --ds-dir $DS_DIR \
  --ppg-key $PPG_KEY \
  --fs-interp $FS_INTERP \
  --peak-detection-window-length ${PEAK_DETECTION_WINDOW_LENGTH:-'60'} \
  --peak-detection-overlap ${PEAK_DETECTION_OVERLAP:-'0.2'} \
  --lp-cutoff ${LP_CUTOFF:-'8.0'} \
  --hp-cutoff ${HP_CUTOFF:-'0.5'} \
  --peak-correction ${PEAK_CORRECTION:-'true'}
