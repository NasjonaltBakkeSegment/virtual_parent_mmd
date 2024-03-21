import shutil
from lxml import etree
import os
from datetime import datetime, timezone
from sentinelsat import SentinelAPI
from sentinel_parent_id_generator.generate_parent_id import generate_parent_id

namespaces = {'mmd': 'http://www.met.no/schema/mmd'}
current_timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

class MMD:

    def __init__(self, filepath, cfg):
        self.filepath = filepath
        self.filename = os.path.basename(self.filepath)
        self.child_mmd_filename = self.filename
        self.cfg = cfg

    def read(self):
        self.tree = etree.parse(self.filepath)
        self.root = self.tree.getroot()

    def write(self):
        self.tree.write(
            self.filepath,
            pretty_print=True
        )

    def add_or_change_element(self, element_name, element_value, language=None):
        xml_element = self.root.find(
            element_name,
            namespaces=self.root.nsmap
        )
        if xml_element is not None:
            xml_element.text = element_value
        else:
            # Create the new element
            pass
            '''
            # Code doesn't work
            # Create the new element
            new_element = etree.Element("{%s}blob" % self.root.nsmap)
            new_element.text = "something"

            # Append the new element to the root
            self.root.append(new_element)
            '''

    def remove_element(self, element):
        # Find all instances of element
        xml_element_list = self.root.findall(
            element,
            namespaces=self.root.nsmap
        )
        for xml_element in xml_element_list:
            if xml_element is not None:
                xml_element.getparent().remove(xml_element)

class Child(MMD):

    def __init__(self, filepath, cfg):
        super().__init__(filepath, cfg)
        self.parent_id, self.metadata = generate_parent_id(self.filename)

    def update(self, conditions_not_met):

        if "'product_type' element not found" in conditions_not_met or "'mode' element not found" in conditions_not_met:
            # Find the parent element 'platform'
            platform_element = self.root.find(".//{http://www.met.no/schema/mmd}platform")
            # Find the 'instrument' element within the 'platform' element
            instrument_element = platform_element.find(".//{http://www.met.no/schema/mmd}instrument")

            if "'mode' element not found" in conditions_not_met:
                # Create the new element 'mode'
                mode_element = etree.Element("{http://www.met.no/schema/mmd}mode")
                mode_element.text = self.get_mode()
                # Insert the 'mode' element at the beginning of the 'instrument' element
                instrument_element.insert(0, mode_element)
                mode_element.tail = '\n\t\t\t'

            if "'product_type' element not found" in conditions_not_met:
                # Create the new element 'product_type'
                product_type_element = etree.Element("{http://www.met.no/schema/mmd}product_type")
                product_type_element.text = self.get_product_type()
                # Insert the 'product_type' element at the beginning of the 'instrument' element
                instrument_element.insert(0, product_type_element)
                product_type_element.tail = '\n\t\t\t'

        if "'related_dataset' element not found" in conditions_not_met:
            # Create the new element 'related_dataset'
            related_dataset_element = etree.Element("{http://www.met.no/schema/mmd}related_dataset")
            related_dataset_element.set("relation_type", "parent")
            related_dataset_element.text = self.parent_id

            children = self.root.getchildren()
            index_of_last_element = len(children) - 1
            last_element = children[index_of_last_element]
            last_element.tail = '\n\t'
            self.root.insert(index_of_last_element+1,related_dataset_element)
            related_dataset_element.tail = '\n'


    def check(self):
        '''
        Check the child MMD file to make sure it has everything required to create the parent from
        If required elements are missing, add them
        '''

        conditions_not_met = []

        product_type = self.tree.find(
            f".//mmd:product_type",
            namespaces=namespaces
        )
        if product_type is None:
            conditions_not_met.append("'product_type' element not found")

        if self.filename.startswith('S1'):
            mode = self.tree.find(
                f".//mmd:mode",
                namespaces=namespaces
            )
            if mode is None:
                conditions_not_met.append("'mode' element not found")

        related_dataset = self.tree.find(
            f".//mmd:related_dataset",
            namespaces=namespaces
        )
        if related_dataset is None:
            conditions_not_met.append("'related_dataset' element not found")

        return conditions_not_met

    def copy(self, destination):
        '''
        Creating the parent MMD file by copying the child
        '''
        shutil.copy(self.filepath, destination)


class Parent(MMD):
    def __init__(self, filepath, cfg):
        super().__init__(filepath, cfg)

    def define_url(self, child_MMD):
        parent_url = f'https://data.met.no/dataset/{child_MMD.parent_id}'
        return parent_url

    def define_title(self, child_MMD):
        try:
            # Title should be function of platform and orbit number
            orbit_number = child_MMD.tree.find(
                f".//mmd:orbit_absolute",
                namespaces=namespaces
            ).text

            product_type = child_MMD.tree.find(
                f".//mmd:product_type",
                namespaces=namespaces
            ).text

            mode = child_MMD.tree.find(
                f".//mmd:mode",
                namespaces=namespaces
            ).text

            # Platform is first part of child title
            old_title = child_MMD.filename.split('_')[0]
            platform = old_title.split('_')[0]
            title = f'{platform}_{mode}_{product_type}_orbit_{orbit_number}'
        except:
            title = 'Dummy title for old XML files without product info'
        return title

    def remove_elements(self):
        '''
        MMD elements in the child MMD file that should not be in parent
        These elements should be removed
        '''
        elements_to_remove = [
            './/mmd:storage_information',
            './/mmd:data_access',
            './/mmd:related_dataset'
        ]
        for element in elements_to_remove:
            self.remove_element(element)

    def add_or_change_elements(self, child_MMD):
        '''
        Adding new elements or updating existing elements
        To be used only when the parent MMD file is first created
        '''
        title = self.define_title(child_MMD)
        parent_url = self.define_url(child_MMD)
        metadata_identifier = (
            child_MMD.root.find(
                ".//mmd:related_dataset",
                namespaces=child_MMD.root.nsmap
            ).text
        )

        elements = {
            './/mmd:last_metadata_update/mmd:update/mmd:datetime': current_timestamp,
            './/mmd:last_metadata_update/mmd:update/mmd:type': 'Created',
            ".//mmd:title": title,
            ".//mmd:metadata_identifier": metadata_identifier,
            ".//mmd:dataset_production_status": 'Ongoing',
            './/mmd:dataset_citation/mmd:publication_date': current_timestamp,
            './/mmd:dataset_citation/mmd:title': title,
            './/mmd:dataset_citation/mmd:url': parent_url,
            './/mmd:related_information/mmd:resource': parent_url
        }

        for element, value in elements.items():
            self.add_or_change_element(element, value)

    def update_elements(self, child_MMD):
        '''
        Updating MMD elements for the parent each time a new child is added
        '''

        # elements = {
        #     './/mmd:last_metadata_update/mmd:update/mmd:datetime': current_timestamp,
        #     #'.//mmd:last_metadata_update/mmd:update/mmd:type': 'Created',

        # }

        # for element, value in elements.items():
        #     self.add_or_change_element(element, value)

        # temporal_extent_start_date
        start_date_parent_element = self.root.find(
            ".//mmd:temporal_extent/mmd:start_date",
            namespaces=self.root.nsmap
        )
        start_date_child_element = child_MMD.root.find(
            ".//mmd:temporal_extent/mmd:start_date",
            namespaces=child_MMD.root.nsmap
        )
        if start_date_parent_element is not None and start_date_child_element is not None:
            start_date_parent_text = start_date_parent_element.text
            start_date_child_text = start_date_child_element.text
            start_date_parent_dt = datetime.strptime(start_date_parent_text, '%Y-%m-%dT%H:%M:%S.%fZ')
            start_date_child_dt = datetime.strptime(start_date_child_text, '%Y-%m-%dT%H:%M:%S.%fZ')
            if start_date_child_dt < start_date_parent_dt:
                start_date_parent_element.text = start_date_child_element.text
            else:
                pass

        # temporal_extent_end_date
        end_date_parent_element = self.root.find(
            ".//mmd:temporal_extent/mmd:end_date",
            namespaces=self.root.nsmap
        )
        end_date_child_element = child_MMD.root.find(
            ".//mmd:temporal_extent/mmd:end_date",
            namespaces=child_MMD.root.nsmap
        )
        if end_date_parent_element is not None and end_date_child_element is not None:
            end_date_parent_text = end_date_parent_element.text
            end_date_child_text = end_date_child_element.text
            end_date_parent_dt = datetime.strptime(end_date_parent_text, '%Y-%m-%dT%H:%M:%S.%fZ')
            end_date_child_dt = datetime.strptime(end_date_child_text, '%Y-%m-%dT%H:%M:%S.%fZ')
            if end_date_child_dt > end_date_parent_dt:
                end_date_parent_element.text = end_date_child_element.text
            else:
                pass

        # geographic extent rectangle north
        north_parent_element = self.root.find(
            ".//mmd:geographic_extent/mmd:rectangle/mmd:north",
            namespaces=self.root.nsmap
        )
        north_child_element = child_MMD.root.find(
            ".//mmd:geographic_extent/mmd:rectangle/mmd:north",
            namespaces=child_MMD.root.nsmap
        )
        if north_parent_element is not None and north_child_element is not None:
            north_parent_text = north_parent_element.text
            north_child_text = north_child_element.text
            if north_child_text > north_parent_text:
                north_parent_element.text = north_child_element.text
            else:
                pass

        # geographic extent rectangle east
        east_parent_element = self.root.find(
            ".//mmd:geographic_extent/mmd:rectangle/mmd:east",
            namespaces=self.root.nsmap
        )
        east_child_element = child_MMD.root.find(
            ".//mmd:geographic_extent/mmd:rectangle/mmd:east",
            namespaces=child_MMD.root.nsmap
        )
        if east_parent_element is not None and east_child_element is not None:
            east_parent_text = east_parent_element.text
            east_child_text = east_child_element.text
            if east_child_text > east_parent_text:
                east_parent_element.text = east_child_element.text
            else:
                pass

        # geographic extent rectangle south
        south_parent_element = self.root.find(
            ".//mmd:geographic_extent/mmd:rectangle/mmd:south",
            namespaces=self.root.nsmap
        )
        south_child_element = child_MMD.root.find(
            ".//mmd:geographic_extent/mmd:rectangle/mmd:south",
            namespaces=child_MMD.root.nsmap
        )
        if south_parent_element is not None and south_child_element is not None:
            south_parent_text = south_parent_element.text
            south_child_text = south_child_element.text
            if south_child_text < south_parent_text:
                south_parent_element.text = south_child_element.text
            else:
                pass

        # geographic extent rectangle west
        west_parent_element = self.root.find(
            ".//mmd:geographic_extent/mmd:rectangle/mmd:west",
            namespaces=self.root.nsmap
        )
        west_child_element = child_MMD.root.find(
            ".//mmd:geographic_extent/mmd:rectangle/mmd:west",
            namespaces=child_MMD.root.nsmap
        )
        if west_parent_element is not None and west_child_element is not None:
            west_parent_text = west_parent_element.text
            west_child_text = west_child_element.text
            if west_child_text < west_parent_text:
                west_parent_element.text = west_child_element.text
            else:
                pass
