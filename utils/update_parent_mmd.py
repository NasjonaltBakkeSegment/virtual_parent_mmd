import yaml
from utils.parent_mmd_class import Parent_MMD

# with open('../config/attrs_to_update_when_new_child_added.yaml', "r") as file:
#     attributes_to_update = yaml.safe_load(file)

def update_parent_mmd(parent, child):
    '''
    Function to update parent MMD file
    With metadata from newly added child
    '''
    print(parent, child)