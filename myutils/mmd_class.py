import shutil
from lxml import etree
import os
from datetime import datetime, timezone
from sentinel_parent_id_generator.generate_parent_id import generate_parent_id
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

    def __init__(self, filepath, cfg):
        self.filepath = str(filepath)
        self.filename = os.path.basename(self.filepath)
        self.cfg = cfg

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

    def __init__(self, filepath, cfg, parent_id=None, metadata=None):
        super().__init__(filepath, cfg)
        self.parent_id = parent_id
        self.metadata = metadata

    def update(self, conditions_not_met):

        if "'product_type' element not found" in conditions_not_met or "'mode' element not found" in conditions_not_met:
            # Find the parent element 'platform'
            platform_element = self.root.find(".//{http://www.met.no/schema/mmd}platform")
            # Find the 'instrument' element within the 'platform' element
            instrument_element = platform_element.find(".//{http://www.met.no/schema/mmd}instrument")
            if instrument_element is None:
                tail = '\n\t\t'
                instrument_element = self.root.find(".//{http://www.met.no/schema/mmd}instrument")
            else:
                tail = '\n\t\t\t'

            if "'mode' element not found" in conditions_not_met:
                # Create the new element 'mode'
                mode_element = etree.Element("{http://www.met.no/schema/mmd}mode")
                mode_element.text = self.metadata['mode']
                # Insert the 'mode' element at the beginning of the 'instrument' element
                instrument_element.insert(0, mode_element)
                mode_element.tail = tail

            if "'product_type' element not found" in conditions_not_met:
                # Create the new element 'product_type'
                product_type_element = etree.Element("{http://www.met.no/schema/mmd}product_type")
                product_type_element.text = self.metadata['producttype']
                # Insert the 'product_type' element at the beginning of the 'instrument' element
                instrument_element.insert(0, product_type_element)
                product_type_element.tail = tail

        if "'related_dataset' element not found" in conditions_not_met:
            # Create the new element 'related_dataset'
            related_dataset_element = etree.Element("{http://www.met.no/schema/mmd}related_dataset")
            related_dataset_element.set("relation_type", "parent")
            related_dataset_element.text = self.parent_id

            children = self.root.getchildren()
            index_of_last_element = len(children) - 1
            last_element = children[index_of_last_element]
            last_element.tail = '\n  '
            self.root.insert(index_of_last_element+1,related_dataset_element)
            related_dataset_element.tail = '\n'


    def check(self):
        '''
        Check the child MMD file to make sure it has everything required to create the parent from
        If required elements are missing, add them
        '''

        conditions_not_met = []

        # All platforms except S3 should have a 'product_type' element
        if not self.filename.startswith('S3'):
            product_type = self.tree.find(
                f".//mmd:product_type",
                namespaces=namespaces
            )
            if product_type is None:
                conditions_not_met.append("'product_type' element not found")

        # Only S1 products need to have a 'mode' element
        if self.filename.startswith('S1'):
            mode = self.tree.find(
                f".//mmd:mode",
                namespaces=namespaces
            )
            if mode is None:
                conditions_not_met.append("'mode' element not found")

        # Only S3 products need to have an 'instrument' element
        # TODO: It is not decided how instrument will be encoded in S3 MMD products so this should be revisted.
        if self.filename.startswith('S3'):
            mode = self.tree.find(
                f".//mmd:instrument",
                namespaces=namespaces
            )
            if mode is None:
                conditions_not_met.append("'instrument' element not found")

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

        # Fixing indentation after last element
        children = self.root.getchildren()
        index_of_last_element = len(children) - 1
        last_element = children[index_of_last_element]
        last_element.tail = '\n'

    def update_elements_first_child(self, child_MMD):
        '''
        Adding new elements or updating existing elements
        To be used only when the parent MMD file is first created
        '''
        title = self.filename
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
            start_date_parent_text = start_date_parent_element.text
            start_date_child_text = start_date_child_element.text
            start_date_parent_dt = datetime.strptime(start_date_parent_text, '%Y-%m-%dT%H:%M:%S.%fZ')
            try:
                start_date_child_dt = datetime.strptime(start_date_child_text, '%Y-%m-%dT%H:%M:%S.%fZ')
            except:
                start_date_child_text = start_date_child_text + 'T00:00:00.000Z'
                start_date_child_dt = datetime.strptime(start_date_child_text, '%Y-%m-%dT%H:%M:%S.%fZ')
            if start_date_child_dt < start_date_parent_dt:
                start_date_parent_element.text = start_date_child_element.text
            else:
                pass

        # temporal_extent_end_date
        end_date_parent_element = self.root.find(
            ".//mmd:temporal_extent/mmd:end_date",
            namespaces=self.ns
        )
        end_date_child_element = child_MMD.root.find(
            ".//mmd:temporal_extent/mmd:end_date",
            namespaces=child_MMD.root.nsmap
        )
        if end_date_parent_element is not None and end_date_child_element is not None:
            end_date_parent_text = end_date_parent_element.text
            end_date_child_text = end_date_child_element.text
            end_date_parent_dt = datetime.strptime(end_date_parent_text, '%Y-%m-%dT%H:%M:%S.%fZ')
            try:
                end_date_child_dt = datetime.strptime(end_date_child_text, '%Y-%m-%dT%H:%M:%S.%fZ')
            except:
                end_date_child_text = end_date_child_text + 'T00:00:00.000Z'
                end_date_child_dt = datetime.strptime(end_date_child_text, '%Y-%m-%dT%H:%M:%S.%fZ')
            if end_date_child_dt > end_date_parent_dt:
                end_date_parent_element.text = end_date_child_element.text
            else:
                pass

        # Extent looks off in parent products so removing this code and populating manually
        # Based on child products already there (covering several years)
        # geographic extent rectangle north
        #north_parent_element = self.root.find(
        #    ".//mmd:geographic_extent/mmd:rectangle/mmd:north",
        #    namespaces=self.ns
        #)
        #north_child_element = child_MMD.root.find(
        #    ".//mmd:geographic_extent/mmd:rectangle/mmd:north",
        #    namespaces=child_MMD.root.nsmap
        #)
        #if north_parent_element is not None and north_child_element is not None:
        #    north_parent_text = north_parent_element.text
        #    north_child_text = north_child_element.text
        #    if north_child_text > north_parent_text:
        #        north_parent_element.text = north_child_element.text
        #    else:
        #        pass

        # geographic extent rectangle east
        #east_parent_element = self.root.find(
        #    ".//mmd:geographic_extent/mmd:rectangle/mmd:east",
        #    namespaces=self.ns
        #)
        #east_child_element = child_MMD.root.find(
        #    ".//mmd:geographic_extent/mmd:rectangle/mmd:east",
        #    namespaces=child_MMD.root.nsmap
        #)
        #if east_parent_element is not None and east_child_element is not None:
        #    east_parent_text = east_parent_element.text
        #    east_child_text = east_child_element.text
        #    if east_child_text > east_parent_text:
        #        east_parent_element.text = east_child_element.text
        #    else:
        #        pass

        # geographic extent rectangle south
        #south_parent_element = self.root.find(
        #    ".//mmd:geographic_extent/mmd:rectangle/mmd:south",
        #    namespaces=self.ns
        #)
        #south_child_element = child_MMD.root.find(
        #    ".//mmd:geographic_extent/mmd:rectangle/mmd:south",
        #    namespaces=child_MMD.root.nsmap
        #)
        #if south_parent_element is not None and south_child_element is not None:
        #    south_parent_text = south_parent_element.text
        #    south_child_text = south_child_element.text
        #    if south_child_text < south_parent_text:
        #        south_parent_element.text = south_child_element.text
        #    else:
        #        pass

        # geographic extent rectangle west
        #west_parent_element = self.root.find(
        #    ".//mmd:geographic_extent/mmd:rectangle/mmd:west",
        #    namespaces=self.ns
        #)
        #west_child_element = child_MMD.root.find(
        #    ".//mmd:geographic_extent/mmd:rectangle/mmd:west",
        #    namespaces=child_MMD.root.nsmap
        #)
        #if west_parent_element is not None and west_child_element is not None:
        #    west_parent_text = west_parent_element.text
        #    west_child_text = west_child_element.text
        #    if west_child_text < west_parent_text:
        #        west_parent_element.text = west_child_element.text
        #    else:
        #        pass
