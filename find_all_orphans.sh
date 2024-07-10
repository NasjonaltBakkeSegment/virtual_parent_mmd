#!/bin/bash -f
#$ -N orphans
#$ -S /bin/bash
#$ -pe shmem-1 1
#$ -l h_rss=8G,mem_free=8G,h_data=8G 
#$ -q research-r8.q
#$ -M lukem@met.no
#$ -j y
#$ -m ba
#$ -wd /home/nbs/file_conversion_r8/virtual_parent_mmd/find_orphans.$JOB_ID
#$ -o /home/nbs/file_conversion_r8/virtual_parent_mmd/find_orphans.$JOB_ID
#$ -e /home/nbs/file_conversion_r8/virtual_parent_mmd/find_orphans.$JOB_ID
#$ -R y
#$ -r y
## ---------------------------

# Script for linking all children to parents in the NBS mmd products directory

config_file="config/config.yml"
directory=$(awk '/mmd_records_filepath:/ {print $2}' "$config_file")

# Find all XML files recursively in the directory and loop through them
find "$directory" -type f -name 'S*.xml' | while read -r xml_file_path; do
    xml_file=$(basename "$xml_file_path")
    python3 check_if_orphan.py --child "$xml_file"
done
