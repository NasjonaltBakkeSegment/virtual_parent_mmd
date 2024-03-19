from utils.mmd_class import Parent, Child


def create_parent_mmd(parent_filepath, child_filepath):
    '''
    Function to create a new parent MMD file
    '''
    parent_mmd = Parent(parent_filepath)
    child_mmd = Child(child_filepath)
    child_mmd.read()
    conditions_not_met = child_mmd.check()
    if len(conditions_not_met) > 0:
        # Trying to add the missing elements to the child and then checking again
        child_mmd.update(conditions_not_met)
        child_mmd.write()
        child_mmd.read()
        conditions_not_met = child_mmd.check()
    if len(conditions_not_met) > 0:
        raise ValueError(
            "The child MMD file does not contain all the elements required to create the parent MMD file"
            )
    # else:
    #     child_mmd.copy(parent_mmd.filepath)
    #     parent_mmd.read()
    #     parent_mmd.add_or_change_elements(child_mmd)
    #     parent_mmd.remove_elements()
    #     parent_mmd.write()
