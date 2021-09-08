#!/bin/bash 
#SBATCH --partition=short-serial 
#SBATCH -o exp_0_542_med.out 
#SBATCH -e exp_0_542_med.err 
#SBATCH --time=02:00:00 
cd /home/users/ewanp82/projects/ret_tool_s3
module unload jaspy 
module load jaspy/2.7 
echo which python 
python run_retr_new.py 0 542_med True True 20170323 20170720