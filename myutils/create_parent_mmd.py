from myutils.mmd_class import Parent, Child

def create_parent_mmd(parent_filepath, child_filepath, parent_id):
    '''
    Function to create a new parent MMD file
    '''
    parent_mmd = Parent(parent_filepath, parent_id)
    child_mmd = Child(child_filepath)
    child_mmd.read()
    child_mmd.copy(parent_mmd.filepath)
    parent_mmd.read()
    parent_mmd.update_elements_first_child(child_mmd)
    parent_mmd.remove_elements()
    parent_mmd.write()
