#!/usr/bin/env python3
import argparse
import sys
import os
import re
from pathlib import Path
import yaml
import logging

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)

from sentinel_parent_id_generator.generate_parent_id import generate_parent_id
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


def get_parent_path(parent_name,cfg):
    '''
    Computing the filepath for the parent MMD file
    '''
    mmd_records_filepath = cfg['mmd_records_filepath']
    platform = parent_name.split('_')[0]
    parent_path = Path(mmd_records_filepath + '/' + platform + '/' + parent_name + '.xml')
    return parent_path


def get_child_path(child,cfg):
    '''
    Finding the absolute filepath of the child MMD file from the product name
    '''
    mmd_records_filepath = cfg['mmd_records_filepath']
    logger.info(f"MMD records filepath: {mmd_records_filepath}")
    platform = child.split('_')[0]
    if platform.startswith('S1'):
        beam = child.split('_')[1]
    date_match = re.search(r'(\d{4})(\d{2})(\d{2})T', child)
    year = date_match.group(1)
    month = date_match.group(2)
    day = date_match.group(3)
    logger.info("Date info retrieved okay")
    if platform.startswith('S1'):
        child_path = Path(mmd_records_filepath + '/' + platform + '/' + year + '/' + month + '/' + day + '/' + beam + '/' + 'metadata/' + child)
    elif platform.startswith('S2'):
        child_path = Path(mmd_records_filepath + '/' + platform + '/' + year + '/' + month + '/' + day + '/' + 'metadata/' + child)
    # TODO: Add functionality for S3 and S5 products
    logger.info(f"Child path: {child_path}")
    if os.path.exists(child_path):
        return child_path
    else:
        logger.info(f"Could not find product at {child_path}")
        return child_path


def assign_parent_to_child(child):

    # Log to console
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    log_info = logging.StreamHandler(sys.stdout)
    log_info.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(log_info)

    child = child.split('.')[0] + '.xml'
    cfg = get_config()

    try:
        logger.info("Trying to create or update parent")
        child_path = get_child_path(child, cfg)
        parent_id, metadata, parent_name = generate_parent_id(child)
        parent_path = get_parent_path(parent_name, cfg)
        logger.info(f"Parent path: {parent_path}")

        if os.path.exists(parent_path):
            logger.info(f"Parent {parent_path} exists. Trying to update it with metadata from new child.")
            update_parent_mmd(parent_path, child_path, cfg, parent_id, metadata)
            logger.info(f"Parent {parent_path} updated successfully.")
        else:
            logger.info(f"Parent {parent_path} does not exist. Trying to create it.")
            create_parent_mmd(parent_path, child_path, cfg, parent_id, metadata)
            logger.info(f"Parent {parent_path} created successfully.")

    except:
        logger.info(f"Parent not assigned for {child}. Adding to list of orphans at {cfg['orphans_file']}")

        # Create the file if it doesn't exist
        if not os.path.exists(cfg['orphans_file']):
            with open(cfg['orphans_file'], 'w'):
                pass

        with open(cfg['orphans_file'], 'r') as file:
            lines = file.readlines()
            if child + '\n' in lines:
                return  # Line already exists, so no need to append it

        # If the line doesn't exist, append it to the file
        with open(cfg['orphans_file'], 'a') as file:
            file.write(child + '\n')


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Script to create or update virtual parent MMD files "
                    "for NBS products"
        )

    parser.add_argument(
        "-c",
        "--child",
        type=str,
        required=True,
        help="File name of the child MMD file"
    )

    args = parser.parse_args()
    child = args.child

    assign_parent_to_child(child)
