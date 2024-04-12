from lxml import etree
import os

class MMD:

    def __init__(self, filepath):
        self.filepath = filepath
        self.filename = os.path.basename(self.filepath)
        self.child_mmd_filename = self.filename

    def read(self):
        self.tree = etree.parse(self.filepath)
        self.root = self.tree.getroot()

    def write(self):
        self.tree.write(
            self.filepath,
            pretty_print=True
        )

    def add_element(self):

        # Create the new element
        # Find the parent element 'platform'
        platform_element = self.root.find(".//{http://www.met.no/schema/mmd}platform")

        # Find the 'instrument' element within the 'platform' element
        instrument_element = platform_element.find(".//{http://www.met.no/schema/mmd}instrument")

        # Create the new element 'product_type'
        product_type_element = etree.Element("{http://www.met.no/schema/mmd}product_type")
        product_type_element.text = "Your product_type value here"

        # Find the 'resource' element within the 'instrument' element
        resource_element = instrument_element.find(".//{http://www.met.no/schema/mmd}resource")

        # Add indentation to the 'tail' of the 'resource' element
        resource_element.tail = '\n\t\t\t'

        # Insert the 'product_type' element after the 'resource' element
        instrument_element.insert(instrument_element.index(resource_element) + 1, product_type_element)

        # Move the 'instrument' element to a new line
        product_type_element.tail = '\n\t\t'


mmd = MMD('/home/lukem/Documents/MET/Projects/ESA_NBS/Git_repos/virtual_parent_mmd/S1A_EW_GRDH_1SDH_20231016T071258_20231016T071502_050787_061EE6_78D6.xml')
mmd.read()
mmd.add_element()
mmd.write()