#!/bin/bash 
#SBATCH --partition=short-serial 
#SBATCH -o exp_0_508_low.out 
#SBATCH -e exp_0_508_low.err 
#SBATCH --time=02:00:00 
cd /home/users/ewanp82/projects/ret_tool_s3
module unload jaspy 
module load jaspy/2.7 
echo which python 
python run_retr_new.py 0 508_low True True 20170323 20170720
