from utils.mmd_class import Parent, Child

def update_parent_mmd(parent_filepath, child_filepath):
    '''
    Function to update parent MMD file
    With metadata from newly added child
    '''
    parent_mmd = Parent(parent_filepath)
    child_mmd = Child(child_filepath)
    parent_mmd.read()
    child_mmd.read()
    parent_mmd.update_elements(child_mmd)
    parent_mmd.write()