#!/usr/bin/env python3
import argparse
import sys
from utils.create_parent_mmd import create_parent_mmd
from utils.update_parent_mmd import update_parent_mmd
import os
import re
from pathlib import Path
import yaml


def get_config():
    file_path = "config/config.yml"
    with open(file_path, "r") as yaml_file:
        cfg = yaml.safe_load(yaml_file)
        return cfg


def get_child_path(child,cfg):
    mmd_records_filepath = cfg['mmd_records_filepath']
    product_type = child.split('_')[0]
    if product_type.startswith('S1'):
        beam = child.split('_')[1]
    date_match = re.search(r'(\d{4})(\d{2})(\d{2})T', child)
    year = date_match.group(1)
    month = date_match.group(2)
    day = date_match.group(3)
    if product_type.startswith('S1'):
        child_path = Path(mmd_records_filepath + '/' + product_type + '/' + year + '/' + month + '/' + day + '/' + beam + '/' + 'metadata/' + child)
    elif product_type.startswith('S2'):
        child_path = Path(mmd_records_filepath + '/' + product_type + '/' + year + '/' + month + '/' + day + '/' + 'metadata/' + child)
    if os.path.exists(child_path):
        return child_path
    else:
        sys.exit(f"Could not find product at {child_path}")


def main(args):

    child = args.child
    parent = args.parent

    cfg = get_config()
    child_path = get_child_path(child, cfg)
    print(f'Child MMD file path: {child_path}')

    if os.path.exists(parent):
        print("Parent {parent} exists. Updating it with metadata from new child.")
        update_parent_mmd(parent, child_path, cfg)
    else:
        print("Parent {parent} does not exist. Creating one")
        create_parent_mmd(parent, child_path, cfg)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Script to create or update virtual parent MMD files "
                    "for NBS products"
        )

    parser.add_argument(
        "--parent",
        type=str,
        required=True,
        help="Filepath to the parent MMD file"
    )

    parser.add_argument(
        "--child",
        type=str,
        required=True,
        help="File name of the child MMD file"
    )

    args = parser.parse_args()

    main(args)