from utils.mmd_class import Parent, Child


def create_parent_mmd(parent_filepath, child_filepath):
    '''
    Function to create a new parent MMD file
    '''
    parent_mmd = Parent(parent_filepath)
    child_mmd = Child(child_filepath)
    child_mmd.copy(parent_mmd.filepath)
    parent_mmd.read()
    child_mmd.read()
    parent_mmd.add_or_change_elements(child_mmd)
    parent_mmd.remove_elements()
    parent_mmd.write()
