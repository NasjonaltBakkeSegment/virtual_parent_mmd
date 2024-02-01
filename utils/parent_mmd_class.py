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
            self.parent_mmd
        )

    def get_parent_id(self):
        related_dataset = self.parent_tree.find(
            f".//mmd:related_dataset",
            namespaces=namespaces
        ).text
        self.parent_id = related_dataset.split(':')[1]

    def get_parent_url(self):
        self.get_parent_id()
        parent_url = f'https://data.met.no/dataset/{self.parent_id}'
        return parent_url

    def get_parent_title(self):
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

    def add_or_change_attributes(self, attributes_to_add_or_change):
        '''
        Adding new attributes or updating existing attributes
        To be used only when the parent MMD file is first created
        '''

        # last_metadata_update_datetime
        last_metadata_update_datetime = self.parent_root.find(
            ".//mmd:last_metadata_update/mmd:update/mmd:datetime",
            namespaces=self.parent_root.nsmap
        )
        if last_metadata_update_datetime is not None:
            last_metadata_update_datetime.text = current_timestamp

        # last_metadata_update_type
        last_metadata_update_type = self.parent_root.find(
            ".//mmd:last_metadata_update/mmd:update/mmd:type",
            namespaces=self.parent_root.nsmap
        )
        if last_metadata_update_type is not None:
            last_metadata_update_type.text = 'Created'

        for attribute, value in attributes_to_add_or_change.items():
            xml_element = self.parent_root.find(
                f".//mmd:{attribute}",
                namespaces=self.parent_root.nsmap
            )
            if xml_element is not None:
                # Update element
                if value is None:
                    # Populate element based on values in this script
                    print(f'Updating element {attribute}')

                    if attribute == 'title':

                        xml_element.text = self.get_parent_title()

                    elif attribute == 'metadata_identifier':
                        xml_element.text = (
                            self.parent_root.find(
                                ".//mmd:related_dataset",
                                namespaces=self.parent_root.nsmap
                            ).text
                        )

                elif isinstance(value, str):
                    # Populate element based on value in config file
                    print(f'Populate element based on value in config file: {attribute} - {value}')
                    xml_element.text = value

                elif isinstance(value, dict):
                    # Nested attributes
                    print(f'Nested attribute key: {attribute}')

                    for child_attribute, val in value.items():
                        if val is None:
                            # Populate element based on values in this script

                            # Find the nested child element under the parent
                            child_element = xml_element.find(
                                f"./mmd:{child_attribute}",
                                namespaces=self.parent_root.nsmap
                            ) # This is returning None when it shouldn't for title under dataset citation

                            print(child_element)

                            if child_element is not None:
                                if child_attribute == 'title':
                                    child_element.text = self.get_parent_title()

                                elif child_attribute in ['publication_date']:
                                    child_element.text = current_timestamp

                                elif child_attribute == 'url':
                                    child_element.text = self.get_parent_url()

                        elif isinstance(val, str):
                            # Populate element based on value in config file
                            print(f'Populate element based on value in config file: {attribute}: {child_attribute} - {val}')
                            child_element.text = val


            else:
                # Add element
                print(f'Adding element {attribute}')
                print(type(value))

    def remove_attributes(self,attributes_to_remove):
        '''
        MMD attributes in the child MMD file that should not be in parent
        These attributes should be removed
        '''
        for attribute, value in attributes_to_remove.items():

            # Find all instances of attribute
            xml_element_list = self.parent_root.findall(
                f".//mmd:{attribute}",
                namespaces=self.parent_root.nsmap
            )
            for xml_element in xml_element_list:
                if xml_element is not None:
                    # Remove element
                    if isinstance(value, dict) == False:
                        xml_element.getparent().remove(xml_element)


    def update_attributes(self):
        '''
        Updating MMD attributes for the parent each time a new child is added
        '''
        print('updating attributes')

        # last_metadata_update_datetime
        last_metadata_update_datetime = self.parent_root.find(
            ".//mmd:last_metadata_update/mmd:update/mmd:datetime",
            namespaces=self.parent_root.nsmap
        )
        if last_metadata_update_datetime is not None:
            last_metadata_update_datetime.text = current_timestamp

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
