#!/bin/sh

#SBATCH --time=1-00:00:00
#SBATCH --mem=5G 

here=/storage/basic/micromet/Tier_processing/rv006011/PycharmProjects/scintillometer_footprints/scint_fp/

SCRIPT=main_create_footprints.py

cd $here

module load python3/anaconda/5.1.0
source activate rv006011

python $SCRIPT > $SCRIPT.log 2>$SCRIPT.2.log
