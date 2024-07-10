#!/bin/bash -f
#$ -N parent_mmd
#$ -S /bin/bash
#$ -pe shmem-1 1
#$ -l h_rss=8G,mem_free=8G,h_data=8G 
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

config_file="config/config.yml"
directory=$(awk '/mmd_records_filepath:/ {print $2}' "$config_file")

# File containing list of file paths
file="invalid_identifiers.txt"

# Loop through each line in the file
while IFS= read -r line; do
    # Extract filename from filepath
    xml_file=$(basename -- "$line")
    python3 link_child_with_parent.py --child "$xml_file"
done < "$file"
