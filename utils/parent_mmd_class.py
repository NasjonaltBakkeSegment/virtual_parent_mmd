import shutil
from lxml import etree
import os
from datetime import datetime, timezone

namespaces = {'mmd': 'http://www.met.no/schema/mmd'}
current_timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

class Parent_MMD:

    def __init__(self, parent_mmd, child_mmd):
        self.child_mmd = child_mmd
        self.parent_mmd = parent_mmd
        self.child_mmd_filename = os.path.basename(self.child_mmd)

    def copy_mmd_of_child(self):
        '''
        Creating the parent MMD file by copying the child
        '''
        shutil.copy(self.child_mmd, self.parent_mmd)

    def read_child_mmd(self):
        self.child_tree = etree.parse(self.child_mmd)
        self.child_root = self.child_tree.getroot()

    def read_parent_mmd(self):
        self.parent_tree = etree.parse(self.parent_mmd)
        self.parent_root = self.parent_tree.getroot()

    def save_parent_mmd(self):
        self.parent_tree.write(
            self.parent_mmd,
            pretty_print=True
        )

    def create_parent_id(self):
        related_dataset = self.parent_tree.find(
            f".//mmd:related_dataset",
            namespaces=namespaces
        ).text
        self.parent_id = related_dataset.split(':')[1]

    def create_parent_url(self):
        self.create_parent_id()
        parent_url = f'https://data.met.no/dataset/{self.parent_id}'
        return parent_url

    def create_parent_title(self):
        try:
            # Title should be function of platform and orbit number
            orbit_number = self.parent_tree.find(
                f".//mmd:orbit_absolute",
                namespaces=namespaces
            ).text

            product_type = self.parent_tree.find(
                f".//mmd:product_type",
                namespaces=namespaces
            ).text

            mode = self.parent_tree.find(
                f".//mmd:mode",
                namespaces=namespaces
            ).text

            # Platform is first part of child title
            old_title = self.child_mmd_filename.split('_')[0]
            platform = old_title.split('_')[0]
            title = f'{platform}_{mode}_{product_type}_orbit_{orbit_number}'
        except:
            title = 'Dummy title for old XML files without product info'
        return title

    def add_or_change_attribute(self, element_name, element_value, language=None):
        xml_element = self.parent_root.find(
            element_name,
            namespaces=self.parent_root.nsmap
        )
        if xml_element is not None:
            xml_element.text = element_value
        else:
            # Create the new element
            pass
            '''
            # Code doesn't work
            # Create the new element
            new_element = etree.Element("{%s}blob" % self.parent_root.nsmap)
            new_element.text = "something"

            # Append the new element to the root
            self.parent_root.append(new_element)
            '''

    def add_or_change_attributes(self):
        '''
        Adding new attributes or updating existing attributes
        To be used only when the parent MMD file is first created
        '''

        title = self.create_parent_title()
        metadata_identifier = (
            self.parent_root.find(
                ".//mmd:related_dataset",
                namespaces=self.parent_root.nsmap
            ).text
        )

        attributes = {
            './/mmd:last_metadata_update/mmd:update/mmd:datetime': current_timestamp,
            './/mmd:last_metadata_update/mmd:update/mmd:type': 'Created',
            ".//mmd:title": title,
            ".//mmd:metadata_identifier": metadata_identifier,
            ".//mmd:dataset_production_status": 'Ongoing',
            './/mmd:dataset_citation/mmd:publication_date': current_timestamp,
            './/mmd:dataset_citation/mmd:title': title,
            './/mmd:dataset_citation/mmd:url': self.create_parent_url(),
        }

        for attribute, value in attributes.items():
            self.add_or_change_attribute(attribute, value)

    def remove_attributes(self):
        '''
        MMD attributes in the child MMD file that should not be in parent
        These attributes should be removed
        '''

        attributes_to_remove = [
            './/mmd:storage_information',
            './/mmd:data_access',
            './/mmd:related_dataset'
        ]

        for attribute in attributes_to_remove:

            # Find all instances of attribute
            xml_element_list = self.parent_root.findall(
                attribute,
                namespaces=self.parent_root.nsmap
            )
            for xml_element in xml_element_list:
                if xml_element is not None:
                    xml_element.getparent().remove(xml_element)


    def update_attributes(self):
        '''
        Updating MMD attributes for the parent each time a new child is added
        '''

        attributes = {
            './/mmd:last_metadata_update/mmd:update/mmd:datetime': current_timestamp,
            #'.//mmd:last_metadata_update/mmd:update/mmd:type': 'Created',

        }

        for attribute, value in attributes.items():
            self.add_or_change_attribute(attribute, value)

        # temporal_extent_start_date
        start_date_parent_element = self.parent_root.find(
            ".//mmd:temporal_extent/mmd:start_date",
            namespaces=self.parent_root.nsmap
        )
        start_date_child_element = self.child_root.find(
            ".//mmd:temporal_extent/mmd:start_date",
            namespaces=self.child_root.nsmap
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
        end_date_parent_element = self.parent_root.find(
            ".//mmd:temporal_extent/mmd:end_date",
            namespaces=self.parent_root.nsmap
        )
        end_date_child_element = self.child_root.find(
            ".//mmd:temporal_extent/mmd:end_date",
            namespaces=self.child_root.nsmap
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
        north_parent_element = self.parent_root.find(
            ".//mmd:geographic_extent/mmd:rectangle/mmd:north",
            namespaces=self.parent_root.nsmap
        )
        north_child_element = self.child_root.find(
            ".//mmd:geographic_extent/mmd:rectangle/mmd:north",
            namespaces=self.child_root.nsmap
        )
        if north_parent_element is not None and north_child_element is not None:
            north_parent_text = north_parent_element.text
            north_child_text = north_child_element.text
            if north_child_text > north_parent_text:
                north_parent_element.text = north_child_element.text
            else:
                pass

        # geographic extent rectangle east
        east_parent_element = self.parent_root.find(
            ".//mmd:geographic_extent/mmd:rectangle/mmd:east",
            namespaces=self.parent_root.nsmap
        )
        east_child_element = self.child_root.find(
            ".//mmd:geographic_extent/mmd:rectangle/mmd:east",
            namespaces=self.child_root.nsmap
        )
        if east_parent_element is not None and east_child_element is not None:
            east_parent_text = east_parent_element.text
            east_child_text = east_child_element.text
            if east_child_text > east_parent_text:
                east_parent_element.text = east_child_element.text
            else:
                pass

        # geographic extent rectangle south
        south_parent_element = self.parent_root.find(
            ".//mmd:geographic_extent/mmd:rectangle/mmd:south",
            namespaces=self.parent_root.nsmap
        )
        south_child_element = self.child_root.find(
            ".//mmd:geographic_extent/mmd:rectangle/mmd:south",
            namespaces=self.child_root.nsmap
        )
        if south_parent_element is not None and south_child_element is not None:
            south_parent_text = south_parent_element.text
            south_child_text = south_child_element.text
            if south_child_text < south_parent_text:
                south_parent_element.text = south_child_element.text
            else:
                pass

        # geographic extent rectangle west
        west_parent_element = self.parent_root.find(
            ".//mmd:geographic_extent/mmd:rectangle/mmd:west",
            namespaces=self.parent_root.nsmap
        )
        west_child_element = self.child_root.find(
            ".//mmd:geographic_extent/mmd:rectangle/mmd:west",
            namespaces=self.child_root.nsmap
        )
        if west_parent_element is not None and west_child_element is not None:
            west_parent_text = west_parent_element.text
            west_child_text = west_child_element.text
            if west_child_text < west_parent_text:
                west_parent_element.text = west_child_element.text
            else:
                pass
