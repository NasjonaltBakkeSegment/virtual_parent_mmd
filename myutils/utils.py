import re
from pathlib import Path
import yaml
import os

def get_config(root_dir):
    '''
    Loading in the configuration file
    '''
    file_path = os.path.join(root_dir, "config/config.yml")
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
    # TODO: Add functionality for S3 and S5 products

    if os.path.exists(child_path):
        return child_path
    else:
        return child_path