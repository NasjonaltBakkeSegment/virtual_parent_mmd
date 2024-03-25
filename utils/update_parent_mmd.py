from utils.mmd_class import Parent, Child

def update_parent_mmd(parent_filepath, child_filepath, cfg, parent_id, metadata):
    '''
    Function to update parent MMD file
    With metadata from newly added child
    '''
    parent_mmd = Parent(parent_filepath, cfg)
    child_mmd = Child(child_filepath, cfg, parent_id, metadata)
    child_mmd.read()
    conditions_not_met = child_mmd.check()
    if len(conditions_not_met) > 0:
        # Trying to add the missing elements to the child and then checking again
        child_mmd.update(conditions_not_met)
        child_mmd.write()
        child_mmd.read()
        conditions_not_met = child_mmd.check()
    if "'related_dataset' element not found" in conditions_not_met:
        raise ValueError(
            "The child MMD file does not contain the ID of the parent, so can't add the child to a parent"
            )
    else:
        parent_mmd.read()
        parent_mmd.update_elements_new_child(child_mmd)
        parent_mmd.write()