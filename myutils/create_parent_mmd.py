from myutils.mmd_class import Parent, Child


def create_parent_mmd(parent_filepath, child_filepath, cfg, parent_id, metadata):
    '''
    Function to create a new parent MMD file
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
    if len(conditions_not_met) > 0:
        with open(cfg['orphans_file'], 'a') as file:
            file.write(child_filepath + '\n')
        raise ValueError(
            "The child MMD file does not contain all the elements required to create the parent MMD file"
            )
    else:
        child_mmd.copy(parent_mmd.filepath)
        parent_mmd.read()
        parent_mmd.update_elements_first_child(child_mmd)
        parent_mmd.remove_elements()
        parent_mmd.write()
