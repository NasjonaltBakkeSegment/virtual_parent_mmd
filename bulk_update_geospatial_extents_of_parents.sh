#!/bin/bash -f
#$ -N geospatial_extents
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

# Script to bulk update the geospatial extents of parent MMD files based on
# all active children within the MMD folder.
# Only files that intersect the AOI polygon are included.

# Define the Python script command as a variable
PYTHON_SCRIPT="python3 bulk_update_geospatial_extents_of_parents.py"

# Run the Python script for each product type
$PYTHON_SCRIPT S1A
$PYTHON_SCRIPT S1B
$PYTHON_SCRIPT S2A
$PYTHON_SCRIPT S2B

