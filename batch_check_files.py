import shutil
from lxml import etree
import os
from datetime import datetime, timezone
import glob
import time

namespaces = {'mmd': 'http://www.met.no/schema/mmd'}
current_timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

class MMD:

    def __init__(self, filepath):
        self.filepath = filepath
        self.filename = os.path.basename(self.filepath)
        self.child_mmd_filename = self.filename

    def read(self):
        self.tree = etree.parse(self.filepath)
        self.root = self.tree.getroot()

    def check(self):
        '''
        Check the child MMD file to make sure it has everything required to create the parent from
        If required elements are missing, add them
        '''
        #TODO: Do I also need geographic extent and anything else modified in the parent? Or can I assume that this is there?
        #TODO: If not, then the child can be an orphan to perhaps address later?

        conditions_not_met = []

        # orbit_absolute = self.tree.find(
        #     f".//mmd:orbit_absolute",
        #     namespaces=namespaces
        # )
        # if orbit_absolute is None:
        #     conditions_not_met.append("'orbit_absolute' element not found")

        # product_type = self.tree.find(
        #     f".//mmd:product_type",
        #     namespaces=namespaces
        # )
        # if product_type is None:
        #     conditions_not_met.append("'product_type' element not found")

        # mode = self.tree.find(
        #     f".//mmd:mode",
        #     namespaces=namespaces
        # )
        # if mode is None:
        #     conditions_not_met.append("'mode' element not found")

        related_dataset = self.tree.find(
            f".//mmd:related_dataset",
            namespaces=namespaces
        )
        if related_dataset is None:
            conditions_not_met.append("'related_dataset' element not found")

        return conditions_not_met

no_related_dataset = 'no_related_dataset.txt'
no_orbit_absolute = 'no_orbit_absolute.txt'
no_product_type = 'no_product_type.txt'
no_mode = 'no_mode.txt'
no_errors = 'no_errors.txt'
root_dir = '/home/lukem/Documents/MET/Projects/ESA_NBS/Git_repos/nbs-md-records'
mmds = glob.glob(root_dir + '/**/*.xml', recursive=True)

files = [
    no_related_dataset,
    # no_orbit_absolute,
    # no_product_type,
    # no_mode,
    no_errors
]
for file in files:
    if not os.path.exists(file):
        open(file, 'a').close()

with open(no_related_dataset, 'a') as related_dataset_file, \
     open(no_errors, 'a') as no_errors_file:
    #  open(no_orbit_absolute, 'a') as orbit_absolute_file, \
    #  open(no_product_type, 'a') as product_type_file, \
    #  open(no_mode, 'a') as mode_file, \
    for mmd_filepath in mmds:
        mmd = MMD(mmd_filepath)
        mmd.read()
        conditions_not_met = mmd.check()
        # Check conditions for each MMD
        if len(conditions_not_met) > 0:
            # if "'related_dataset' element not found" in conditions_not_met:
            #     related_dataset_file.write(mmd_filepath + '\n')
            # if "'orbit_absolute' element not found" in conditions_not_met:
            #     orbit_absolute_file.write(mmd_filepath + '\n')
            # if "'product_type' element not found" in conditions_not_met:
            #     product_type_file.write(mmd_filepath + '\n')
            # if "'mode' element not found" in conditions_not_met:
            #     mode_file.write(mmd_filepath + '\n')
            pass
        else:
            no_errors_file.write(mmd_filepath + '\n')
