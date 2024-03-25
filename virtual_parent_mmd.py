#!/usr/bin/env python3
import argparse
import sys
from utils.create_parent_mmd import create_parent_mmd
from utils.update_parent_mmd import update_parent_mmd
import os
import re
from pathlib import Path
import yaml
from sentinel_parent_id_generator.generate_parent_id import generate_parent_id


def get_config():
    file_path = "config/config.yml"
    with open(file_path, "r") as yaml_file:
        cfg = yaml.safe_load(yaml_file)
        return cfg


def get_parent_path(parent_name,cfg):
    mmd_records_filepath = cfg['mmd_records_filepath']
    platform = parent_name.split('_')[0]
    parent_path = Path(mmd_records_filepath + '/' + platform + '/' + parent_name + '.xml')
    return parent_path


def get_child_path(child,cfg):
    mmd_records_filepath = cfg['mmd_records_filepath']
    platform = child.split('_')[0]
    if platform.startswith('S1'):
        beam = child.split('_')[1]
    date_match = re.search(r'(\d{4})(\d{2})(\d{2})T', child)
    year = date_match.group(1)
    month = date_match.group(2)
    day = date_match.group(3)
    if platform.startswith('S1'):
        child_path = Path(mmd_records_filepath + '/' + platform + '/' + year + '/' + month + '/' + day + '/' + beam + '/' + 'metadata/' + child)
    elif platform.startswith('S2'):
        child_path = Path(mmd_records_filepath + '/' + platform + '/' + year + '/' + month + '/' + day + '/' + 'metadata/' + child)
    if os.path.exists(child_path):
        return child_path
    else:
        sys.exit(f"Could not find product at {child_path}")


def main(args):

    child = args.child

    cfg = get_config()
    child_path = get_child_path(child, cfg)
    print(f'Child MMD file path: {child_path}')

    parent_id, metadata, parent_name = generate_parent_id(child)
    parent_path = get_parent_path(parent_name, cfg)

    if os.path.exists(parent_path):
        print("Parent {parent_path} exists. Updating it with metadata from new child.")
        update_parent_mmd(parent_path, child_path, cfg, parent_id, metadata)
    else:
        print("Parent {parent_path} does not exist. Creating one")
        create_parent_mmd(parent_path, child_path, cfg, parent_id, metadata)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Script to create or update virtual parent MMD files "
                    "for NBS products"
        )

    parser.add_argument(
        "--child",
        type=str,
        required=True,
        help="File name of the child MMD file"
    )

    args = parser.parse_args()

    main(args)