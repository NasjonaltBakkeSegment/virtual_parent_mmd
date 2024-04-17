# Script for linking all children to parents in the NBS mmd products directory

config_file="config/config.yml"
directory=$(awk '/mmd_records_filepath:/ {print $2}' "$config_file")

# Find all XML files recursively in the directory and loop through them
find "$directory" -type f -name '*.xml' | while read -r xml_file_path; do
    xml_file=$(basename "$xml_file_path")
    python3 link_child_with_parent.py --child "$xml_file"
done