import shutil
from lxml import etree


namespaces = {'mmd': 'http://www.met.no/schema/mmd'}


class Parent_MMD:

    def __init__(self, parent_mmd, child_mmd):
        self.child_mmd = child_mmd
        self.parent_mmd = parent_mmd

    def copy_mmd_of_child(self):
        '''
        Creating the parent MMD file by copying the child
        '''
        shutil.copy(self.child_mmd, self.parent_mmd)

    def read_child_mmd(self):
        self.child_tree = etree.parse(self.child_mmd)

    def read_parent_mmd(self):
        self.parent_tree = etree.parse(self.parent_mmd)

    def save_parent_mmd(self):
        self.parent_tree.write(
            self.parent_mmd
        )

    def add_or_change_attributes(self, attributes_to_add_or_change):
        '''
        Adding new attributes or updating existing attributes
        To be used only when the parent MMD file is first created
        '''
        #collection_name = 'METNCS'

        for attribute, value in attributes_to_add_or_change.items():
            xml_element = self.parent_tree.find(
                f".//mmd:{attribute}",
                namespaces=namespaces
            )
            if xml_element is not None:
                # Update element
                if value is None:
                    print(f'Updating element {attribute}')

                    if attribute == 'title':
                        xml_element.text = 'my title'

                    elif attribute == 'metadata_identifier':
                        xml_element.text = (
                            self.child_tree.find(
                                ".//mmd:related_dataset",
                                namespaces={
                                    "mmd": "http://www.met.no/schema/mmd"
                                }
                            ).text
                        )

                elif isinstance(value, str):
                    xml_element.text = value

                elif isinstance(value, dict):
                    for key, val in value.items():
                        if isinstance(val, str):
                            continue


            else:
                # Add element
                print(f'Adding element {attribute}')
                print(type(value))

    """
    def remove_attributes(self,attributes_to_remove):
        '''
        MMD attributes in the child MMD file that should not be in parent
        These attributes should be removed
        '''

    def update_attributes(self, attributes_to_update):
        '''
        Updating MMD attributes for the parent each time a new child is added
        '''
    """
