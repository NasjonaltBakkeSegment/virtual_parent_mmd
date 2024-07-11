import os
import argparse
from myutils.mmd_class import Parent, Child
from myutils.utils import get_parent_path, get_config
from sentinel_parent_id_generator.generate_parent_id import generate_parent_id
import logging
import sys
from lxml import etree

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)

logger = logging.getLogger(__name__)

geospatial_limits_placeholder = 999

def find_extremes(child_mmd, parent_mmd):
    """
    Determine the extreme geospatial extents between a child MMD and a parent MMD.
    """
    logger.debug(f'Child N: {child_mmd.north} S: {child_mmd.south} E: {child_mmd.east} W: {child_mmd.west}')
    logger.debug(f'Parent N: {parent_mmd.north} S: {parent_mmd.south} E: {parent_mmd.east} W: {parent_mmd.west}')
    if int(parent_mmd.north) == int(geospatial_limits_placeholder):
        # If the parent MMD has a placeholder for north extent, return the child's extents
        return child_mmd.north, child_mmd.south, child_mmd.east, child_mmd.west

    # Compare the child's and parent's extents to find the maximum north and east and minimum south and west
    max_north = max(child_mmd.north, parent_mmd.north)
    min_south = min(child_mmd.south, parent_mmd.south)
    max_east = max(child_mmd.east, parent_mmd.east)
    min_west = min(child_mmd.west, parent_mmd.west)

    return max_north, min_south, max_east, min_west

def compare_geospatial_extent_against_parent(parent_filepath, child_filepath, cfg, parent_id, metadata):
    """
    Update the geospatial extents of the parent MMD by comparing it with the child MMD.

    :param parent_filepath: Filepath to the parent MMD XML.
    :param child_filepath: Filepath to the child MMD XML.
    :param cfg: Configuration dictionary.
    :param parent_id: Identifier for the parent MMD.
    :param metadata: Metadata dictionary for the child MMD.
    """
    parent_mmd = Parent(parent_filepath, cfg)
    child_mmd = Child(child_filepath, cfg, parent_id, metadata)
    child_mmd.read()

    # Check if the child MMD is active and within the defined polygon
    active = child_mmd.check_if_active()
    child_mmd.get_geospatial_extents()
    within_polygon = child_mmd.check_if_within_polygon()

    if active and within_polygon:
        parent_mmd.read()
        parent_mmd.get_geospatial_extents()

        # Find the extreme geospatial extents between parent and child
        max_north, min_south, max_east, min_west = find_extremes(child_mmd, parent_mmd)
        # Update the parent's geospatial extents
        parent_mmd.update_geographic_extent(max_north, min_south, max_east, min_west)
        parent_mmd.write()

def find_xml_files(directory, product_type):
    """
    Find all XML files in the metadata directories for the given product type.
    Scans all subdirectories of the given directory and returns a list of file paths to the XML files.

    :param directory: The top-level directory to search.
    :param product_type: The product type to search for (e.g., S2A, S1A).
    :return: List of file paths to the XML files.
    """
    subdirectory_path = os.path.join(directory, product_type)
    xml_files = []

    # Traverse the directory tree to find XML files
    for root, dirs, files in os.walk(subdirectory_path):
        for file in files:
            if file.endswith(".xml") and file.startswith("S") and len(file) > 40:
                xml_files.append(os.path.join(root, file))
    return xml_files

def find_relevant_parents(directory, product_type):
    """
    Find all the relevant parent MMD files for a given product type within the given directory.

    :param directory: The top-level directory to search.
    :param product_type: The product type to search for (e.g., S2A, S1A).
    :return: List of file paths to the relevant parent MMD files.
    """
    subdirectory_path = os.path.join(directory, product_type)
    parents = []

    # Check if the subdirectory exists and is a directory
    if os.path.exists(subdirectory_path) and os.path.isdir(subdirectory_path):
        # List all files in the subdirectory
        for file in os.listdir(subdirectory_path):
            file_path = os.path.join(subdirectory_path, file)
            if os.path.isfile(file_path) and file.endswith('.xml'):
                parents.append(file_path)

        return parents

    return []

def clear_parent_geospatial_limits(directory, product_type):
    """
    Find all relevant parent MMD files and replace their geospatial limits values with a placeholder.

    :param directory: The top-level directory to search.
    :param product_type: The product type to search for (e.g., S2A, S1A).
    """
    parents = find_relevant_parents(directory, product_type)

    for parent in parents:
        tree = etree.parse(parent)
        root = tree.getroot()
        ns = root.nsmap

        # Define the elements to update
        elements = ['north', 'south', 'west', 'east']

        # Update the geospatial limit elements with the placeholder
        for elem in elements:
            elem_path = f".//mmd:geographic_extent/mmd:rectangle/mmd:{elem}"
            elem_obj = root.find(elem_path, namespaces=ns)
            if elem_obj is not None:
                elem_obj.text = str(geospatial_limits_placeholder)

        # Write the updated XML back to the file
        tree.write(parent, pretty_print=True)

def main():
    """
    Main function to parse arguments and initiate the process.
    """
    parser = argparse.ArgumentParser(description='Process XML files to remove data access elements if corresponding NC file is not found.')
    parser.add_argument('product_type', type=str, help='Product type to search for (e.g., S2A, S1A)')

    args = parser.parse_args()

    # Log to console
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    log_info = logging.StreamHandler(sys.stdout)
    log_info.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(log_info)

    # Get the configuration settings
    logger.info("Retrieving configuration settings...")
    cfg = get_config(script_dir)
    directory = cfg['mmd_records_filepath']
    logger.info("Configuration settings retrieved.")

    logger.info(f"Starting process for product type: {args.product_type}")

    # Clear geospatial limits in parent MMDs
    logger.info("Clearing geospatial limits in parent MMDs...")
    clear_parent_geospatial_limits(directory, args.product_type)
    logger.info("Finished clearing geospatial limits in parent MMDs.")

    # Find all relevant XML files for the given product type
    logger.info(f"Finding XML files in directory: {directory} for product type: {args.product_type}...")
    xml_files = find_xml_files(directory, args.product_type)
    logger.info(f"Found {len(xml_files)} XML files.")

    # Process each XML file
    for xml_file in xml_files:
        logger.debug(f"Processing XML file: {xml_file}")
        try:
            child_path = xml_file.split('.')[0] + '.xml'
            child = os.path.basename(child_path)
            parent_id, metadata, parent_name = generate_parent_id(child)
            parent_path = get_parent_path(parent_name, cfg)

            # Compare and update geospatial extents
            compare_geospatial_extent_against_parent(parent_path, child_path, cfg, parent_id, metadata)
            logger.debug(f"Successfully processed XML file: {xml_file}")
        except Exception as e:
            logger.error(f"Error processing XML file: {xml_file}. Error: {e}")

    logger.info("Process completed.")

if __name__ == "__main__":
    main()