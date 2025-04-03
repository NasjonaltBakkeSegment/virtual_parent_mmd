#!/usr/bin/env python3
import argparse
import sys
import os
import glob
import re
from pathlib import Path
import yaml
import logging
import pandas as pd

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)

from myutils.create_parent_mmd import create_parent_mmd
from myutils.update_parent_mmd import update_parent_mmd

logger = logging.getLogger(__name__)

def get_config():
    '''
    Loading in the configuration file
    '''
    file_path = os.path.join(script_dir, "config/config.yml")
    with open(file_path, "r") as yaml_file:
        cfg = yaml.safe_load(yaml_file)
        return cfg

def get_parent_id(mapping_file, platform, product_type):
    '''
    Loading in the configuration file
    '''
    with open(mapping_file, "r") as yaml_file:
        mapping = yaml.safe_load(yaml_file)

    return mapping[platform][product_type]


def list_all_children(platform, product_type, root_path):
    '''
    Find all children MMD files for the platform and product_type combination.

    Searches recursively in root_path/platform for XML files that match
    the pattern: platform*product_type*.xml.

    Returns a list of absolute file paths.
    '''
    search_path = os.path.join(root_path, platform)
    pattern = f"{platform}*{product_type}*.xml"

    return [os.path.abspath(f) for f in glob.iglob(os.path.join(search_path, '**', pattern), recursive=True)]


def get_parent_path(platform, product_type, root_path):
    '''
    Compute the absolute filepath of the parent MMD file to be created
    The resulting path follows the structure:
    root_path/platform/product_type.xml
    '''
    return os.path.join(root_path, platform, f"{platform}-{product_type}.xml")

def get_filename_product_type(csv_filepath, product_type):

    df = pd.read_csv(csv_filepath)
    filename_product_type = df.loc[df['product_type'] == product_type, 'Alias (ESA product type)'].iloc[0]
    return filename_product_type


def main(platform, product_type):

    # Log to console
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    log_info = logging.StreamHandler(sys.stdout)
    log_info.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(log_info)

    logger.info(f"Platform: {platform}, Product Type: {product_type}")

    cfg = get_config()
    root_path = cfg['root_path']
    parent_id = get_parent_id(cfg['parent_id_mapping'], platform, product_type)

    filename_product_type = get_filename_product_type(cfg['product_metadata_csv'], product_type)
    children = list_all_children(platform, filename_product_type, root_path)
    parent_path = get_parent_path(platform, product_type, root_path)

    for child_path in children:
        logger.info(f'Processing child: {child_path}')
        if os.path.exists(parent_path):
            logger.info(f"Parent {parent_path} exists. Trying to update it with metadata from new child.")
            update_parent_mmd(parent_path, child_path, parent_id)
            logger.info(f"Parent {parent_path} updated successfully.")
        else:
            logger.info(f"Parent {parent_path} does not exist. Trying to create it.")
            create_parent_mmd(parent_path, child_path, parent_id)
            logger.info(f"Parent {parent_path} created successfully.")

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Script to create or update virtual parent MMD files "
                    "for NBS products"
        )

    parser.add_argument(
        "-pr",
        "--product_type",
        type=str,
        required=True,
        help="Product type to create parent for"
    )

    parser.add_argument(
        "-pl",
        "--platform",
        type=str,
        required=True,
        help="Platform to create parent for"
    )

    args = parser.parse_args()

    platform = args.platform
    product_type = args.product_type

    main(platform, product_type)

# TODO: As we move away from the ESA software, geospatial extent should be whole globe.
