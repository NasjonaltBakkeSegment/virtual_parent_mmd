#!/usr/bin/env python3
import argparse
import sys
from utils.create_parent_mmd import create_parent_mmd
from utils.update_parent_mmd import update_parent_mmd
import os


def main(args):

    child = args.child
    parent = args.parent

    create_parent_mmd(parent, child)

    # if os.path.exists(parent):
    #     print("Parent {parent} exists. Updating it with metadata from new child.")
    #     update_parent_mmd(parent, child)
    # else:
    #     print("Parent {parent} does not exist. Creating one")
    #     create_parent_mmd(parent, child)


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
        help="Filepath to the child MMD file"
    )

    args = parser.parse_args()

    # Check if the --child file exists
    if not os.path.exists(args.child):
        print(f"Error: The specified --child '{args.child}' does not exist.")
        sys.exit()

    main(args)