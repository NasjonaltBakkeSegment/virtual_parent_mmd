from utils.parent_mmd_class import Parent_MMD

def update_parent_mmd(parent, child):
    '''
    Function to update parent MMD file
    With metadata from newly added child
    '''
    parent_mmd = Parent_MMD(parent, child)

    parent_mmd.read_parent_mmd()
    parent_mmd.read_child_mmd()

    parent_mmd.update_attributes()

    parent_mmd.save_parent_mmd()