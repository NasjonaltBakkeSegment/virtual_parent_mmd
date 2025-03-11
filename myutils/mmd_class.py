import shutil
from lxml import etree
import os
from datetime import datetime, timezone
from shapely.geometry import Polygon, box

namespaces = {'mmd': 'http://www.met.no/schema/mmd'}
current_timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
polygon = Polygon([
    (-20.263238824222373, 84.8852877777822),
    (-36.25445787748578, 67.02581594412311),
    (11.148084316116405, 52.31593720759386),
    (45.98609725358305, 63.94940066151824),
    (89.96194965005743, 84.8341192704811),
    (-20.263238824222373, 84.8852877777822),
    (-20.263238824222373, 84.8852877777822)
    ])

class MMD:

    def __init__(self, filepath):
        self.filepath = str(filepath)
        self.filename = os.path.basename(self.filepath)

    def read(self):
        self.tree = etree.parse(self.filepath)
        self.root = self.tree.getroot()
        self.ns = self.root.nsmap

    def write(self):
        self.tree.write(
            self.filepath,
            pretty_print=True
        )

    def update_element(self, element_name, element_value, language=None):
        xml_element = self.root.find(
            element_name,
            namespaces=self.ns
        )
        if xml_element is not None:
            xml_element.text = element_value
        else:
            pass

    def remove_element(self, element):
        # Find all instances of element
        xml_element_list = self.root.findall(
            element,
            namespaces=self.ns
        )
        for xml_element in xml_element_list:
            if xml_element is not None:
                xml_element.getparent().remove(xml_element)

    def check_if_active(self):
        # Find the metadata_status element
        metadata_status = self.root.xpath('.//mmd:metadata_status', namespaces=self.ns)

        if metadata_status:
            # Check if the status is "Active"
            return metadata_status[0].text == "Active"
        else:
            return False

    def get_geospatial_extents(self):
        # Extract the geographic extent coordinates
        self.north = float(self.root.xpath('.//mmd:north', namespaces=self.ns)[0].text)
        self.south = float(self.root.xpath('.//mmd:south', namespaces=self.ns)[0].text)
        self.west = float(self.root.xpath('.//mmd:west', namespaces=self.ns)[0].text)
        self.east = float(self.root.xpath('.//mmd:east', namespaces=self.ns)[0].text)

    def check_if_within_polygon(self):

        # Create a shapely box (rectangle) from the geographic extent
        extent_box = box(self.west, self.south, self.east, self.north)

        # Check if the extent box overlaps with the given polygon
        return extent_box.intersects(polygon) # Returns True or False

    def update_geographic_extent(self, north, south, east, west):
        # Find the geographic extent elements and update them
        north_elem = self.root.find(".//mmd:geographic_extent/mmd:rectangle/mmd:north", namespaces=self.ns)
        south_elem = self.root.find(".//mmd:geographic_extent/mmd:rectangle/mmd:south", namespaces=self.ns)
        west_elem = self.root.find(".//mmd:geographic_extent/mmd:rectangle/mmd:west", namespaces=self.ns)
        east_elem = self.root.find(".//mmd:geographic_extent/mmd:rectangle/mmd:east", namespaces=self.ns)

        if north_elem is not None:
            north_elem.text = str(north)
        if south_elem is not None:
            south_elem.text = str(south)
        if west_elem is not None:
            west_elem.text = str(west)
        if east_elem is not None:
            east_elem.text = str(east)

class Child(MMD):

    def __init__(self, filepath):
        super().__init__(filepath)

    def copy(self, destination):
        '''
        Creating the parent MMD file by copying the child
        '''
        shutil.copy(self.filepath, destination)


class Parent(MMD):
    def __init__(self, filepath, parent_id):
        super().__init__(filepath)
        self.parent_id = parent_id

    def define_url(self):
        parent_url = f'https://data.met.no/dataset/{self.parent_id}'
        return parent_url

    def remove_elements(self):
        '''
        MMD elements in the child MMD file that should not be in parent
        These elements should be removed
        '''
        elements_to_remove = [
            './/mmd:storage_information',
            './/mmd:data_access',
            './/mmd:related_dataset',
            './/mmd:platform/mmd:ancillary',
            './/mmd:platform/mmd:orbit_relative',
            './/mmd:platform/mmd:orbit_absolute',
            './/mmd:platform/mmd:orbit_direction', # polygon
            './/mmd:geographic_extent/mmd:polygon',
            './/mmd:temporal_extent/mmd:end_date',
            './/mmd:dataset_citation/mmd:url'
        ]

        for element in elements_to_remove:
            self.remove_element(element)

        start_date_parent_element = self.root.find(
            ".//mmd:temporal_extent/mmd:start_date",
            namespaces=self.ns
        )
        start_date_parent_element.tail = '\n\t'

        rectangle_element = self.root.find(
            ".//mmd:geographic_extent/mmd:rectangle",
            namespaces=self.ns
        )
        rectangle_element.tail = '\n\t'

        instrument_element = self.root.find(
            ".//mmd:platform/mmd:instrument",
            namespaces=self.ns
        )
        instrument_element.tail = '\n\t'

        # Fixing indentation after last element
        children = self.root.getchildren()
        index_of_last_element = len(children) - 1
        last_element = children[index_of_last_element]
        last_element.tail = '\n'

    def update_bounding_box(self):
        north_element = self.root.find(
            ".//mmd:geographic_extent/mmd:rectangle/mmd:north",
            namespaces=self.root.nsmap
        )
        north_element.text = '90'

        south_element = self.root.find(
            ".//mmd:geographic_extent/mmd:rectangle/mmd:south",
            namespaces=self.root.nsmap
        )
        south_element.text = '-90'

        east_element = self.root.find(
            ".//mmd:geographic_extent/mmd:rectangle/mmd:east",
            namespaces=self.root.nsmap
        )
        east_element.text = '180'

        west_element = self.root.find(
            ".//mmd:geographic_extent/mmd:rectangle/mmd:west",
            namespaces=self.root.nsmap
        )
        west_element.text = '-180'


    def update_elements_first_child(self, child_MMD):
        '''
        Adding new elements or updating existing elements
        To be used only when the parent MMD file is first created
        '''
        title = self.filename.split('.')[0]
        parent_url = self.define_url()
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
            './/mmd:dataset_citation/mmd:title': title
        }

        for element, value in elements.items():
            self.update_element(element, value)

    def update_elements_new_child(self, child_MMD):
        '''
        Updating MMD elements for the parent each time a new child is added
        '''
        # temporal_extent_start_date
        start_date_parent_element = self.root.find(
            ".//mmd:temporal_extent/mmd:start_date",
            namespaces=self.ns
        )
        start_date_child_element = child_MMD.root.find(
            ".//mmd:temporal_extent/mmd:start_date",
            namespaces=child_MMD.root.nsmap
        )
        if start_date_parent_element is not None and start_date_child_element is not None:
            # Split at the 'T' to extract the date part
            parent_date_str = start_date_parent_element.text.partition('T')[0]
            child_date_str = start_date_child_element.text.partition('T')[0]

            parent_date = datetime.strptime(parent_date_str, '%Y-%m-%d')
            child_date = datetime.strptime(child_date_str, '%Y-%m-%d')

            if child_date < parent_date:
                start_date_parent_element.text = start_date_child_element.text
