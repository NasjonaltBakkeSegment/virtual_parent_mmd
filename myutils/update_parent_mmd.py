from myutils.mmd_class import Parent, Child

def update_parent_mmd(parent_filepath, child_filepath, parent_id):
    '''
    Function to update parent MMD file
    With metadata from newly added child
    '''
    parent_mmd = Parent(parent_filepath, parent_id)
    child_mmd = Child(child_filepath)
    child_mmd.read()
    parent_mmd.read()
    parent_mmd.update_elements_new_child(child_mmd)
    parent_mmd.write()
