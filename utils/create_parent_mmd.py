import yaml
from utils.parent_mmd_class import Parent_MMD


def create_parent_mmd(parent, child):
    '''
    Function to create a new parent MMD file
    '''
    parent_mmd = Parent_MMD(parent, child)
    parent_mmd.copy_mmd_of_child()
    parent_mmd.read_parent_mmd()
    parent_mmd.read_child_mmd()
    parent_mmd.add_or_change_attributes()
    parent_mmd.remove_attributes()
    parent_mmd.save_parent_mmd()
