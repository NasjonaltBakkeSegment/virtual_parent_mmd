# Script for generating a parent XML file from 2 children

# Set the directory path
directory="/home/lukem/Documents/MET/Projects/ESA_NBS/Git_repos/nbs-md-records/S2B/"

# Find all XML files recursively in the directory and loop through them
find "$directory" -type f -name '*.xml' | while read -r xml_file_path; do
    xml_file=$(basename "$xml_file_path")
    python3 virtual_parent_mmd.py --child "$xml_file"
done