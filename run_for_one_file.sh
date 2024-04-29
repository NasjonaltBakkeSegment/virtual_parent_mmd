#!/bin/bash -f
#$ -N parent_mmd
#$ -S /bin/bash
#$ -pe shmem-1 1
#$ -l h_rss=4G,mem_free=4G,h_data=4G 
#$ -q research-r8.q
#$ -M lukem@met.no
#$ -j y
#$ -m ba
#$ -wd /home/nbs/file_conversion_r8/virtual_parent_mmd/OUT.$JOB_ID
#$ -o /home/nbs/file_conversion_r8/virtual_parent_mmd/OUT.$JOB_ID
#$ -e /home/nbs/file_conversion_r8/virtual_parent_mmd/OUT.$JOB_ID
#$ -R y
#$ -r y
## ---------------------------

# Script for linking all children to parents in the NBS mmd products directory
python3 link_child_with_parent.py -c S2B_MSIL1C_20240423T125709_N0510_R038_T28WFE_20240423T135214

