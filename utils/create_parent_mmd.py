import yaml
from utils.parent_mmd_class import Parent_MMD


def create_parent_mmd(parent, child):
    '''
    Function to create a new parent MMD file
    '''
    parent_mmd = Parent_MMD(parent, child)
    parent_mmd.copy_mmd_of_child()

    with open('config/attrs_to_add_or_change_when_new_parent_created.yaml', "r") as file:
        attributes_to_add_or_change = yaml.safe_load(file)

    with open('config/attrs_to_remove_when_parent_created.yaml', "r") as file:
        attributes_to_remove = yaml.safe_load(file)

    parent_mmd.read_parent_mmd()
    parent_mmd.read_child_mmd()
    parent_mmd.add_or_change_attributes(attributes_to_add_or_change)
    parent_mmd.remove_attributes(attributes_to_remove)
    parent_mmd.save_parent_mmd()
