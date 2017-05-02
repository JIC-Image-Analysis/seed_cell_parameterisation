"""seed_cell_size_2d analysis."""

import os
import json
import logging
import argparse

import dtool

import numpy as np

from scipy.misc import imsave

from skimage.filters import threshold_adaptive

import skimage.segmentation

from skimage.measure import regionprops

from jicbioimage.core.image import Image
from jicbioimage.core.transform import transformation
from jicbioimage.core.io import AutoName, AutoWrite
from jicbioimage.segment import connected_components
from jicbioimage.segment import SegmentedImage

from jicbioimage.transform import (
    invert,
    threshold_otsu,
    remove_small_objects
)

__version__ = "0.0.1"

AutoName.prefix_format = "{:03d}_"


@transformation
def identity(image):
    """Return the image as is."""
    return image


@transformation
def clear_border(image):
    cleared = skimage.segmentation.clear_border(image)

    return cleared.view(SegmentedImage)


@transformation
def remove_small_regions(segmentation, threshold=1000):

    for id in segmentation.identifiers:
        if segmentation.region_by_identifier(id).area < threshold:
            segmentation.remove_region(id)

    return segmentation


def parameterise_cells(segmentation):
    # all_props = regionprops(segmentation)

    # for props in all_props:
    #     print(props.major_axis_length, props.minor_axis_length)

    # cell_information = []
    # for cell_id in segmentation.identifiers:
    #     if cell_id != 0:
    #         cell_region = segmentation.region_by_identifier(cell_id)
    #         region_props = regionprops(cell_region)[0]
    #         print(props.major_axis_length)
    #         cell_entry = dict(identifier=cell_id, area=cell_region.area)
    #         cell_information.append(cell_entry)

    all_cell_props = regionprops(segmentation)

    cell_information = []
    for props in all_cell_props:

        cell_entry = dict(
            width=int(props.minor_axis_length),
            length=int(props.major_axis_length),
            area=props.area,
            identifier=props.label
        )

        cell_information.append(cell_entry)

    return cell_information


def preprocess_and_segment(image):

    thresholded = threshold_adaptive(image, block_size=91)

    image = remove_small_objects(thresholded)
    image = invert(image)
    image = remove_small_objects(image)
    image = invert(image)

    segmentation = connected_components(image, background=False)
    segmentation = clear_border(segmentation)
    segmentation = remove_small_regions(segmentation)

    return segmentation


def analyse_file(fpath, output_directory):
    """Analyse a single file."""
    logging.info("Analysing file: {}".format(fpath))
    image = Image.from_file(fpath)
    print("analysing {}".format(fpath))
    print(image.shape)

    segmentation = preprocess_and_segment(image)


    cell_info = parameterise_cells(segmentation)

    headers = cell_info[0].keys()

    print(','.join(headers))
    for entry in cell_info:
        data = [entry[h] for h in headers]
        print(','.join(str(d) for d in data))


def analyse_dataset(dataset_dir, output_dir):
    """Analyse all the files in the dataset."""
    dataset = dtool.DataSet.from_path(dataset_dir)
    logging.info("Analysing files in dataset: {}".format(dataset.name))

    i = dataset.identifiers[0]

    rel_path = dataset.item_path_from_hash(i)

    analyse_file(rel_path, output_dir)


def main():
    # Parse the command line arguments.
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset_dir", help="Input dataset directory")
    parser.add_argument("output_dir", help="Output directory")
    parser.add_argument("--debug", default=False, action="store_true",
                        help="Write out intermediate images")
    args = parser.parse_args()

    if not os.path.isdir(args.dataset_dir):
        parser.error("Not a directory: {}".format(args.dataset_dir))

    # Create the output directory if it does not exist.
    if not os.path.isdir(args.output_dir):
        os.mkdir(args.output_dir)
    AutoName.directory = args.output_dir

    # Only write out intermediate images in debug mode.
    if not args.debug:
        AutoWrite.on = False

    # Setup a logger for the script.
    log_fname = "audit.log"
    log_fpath = os.path.join(args.output_dir, log_fname)
    logging_level = logging.INFO
    if args.debug:
        logging_level = logging.DEBUG
    logging.basicConfig(filename=log_fpath, level=logging_level)

    # Log some basic information about the script that is running.
    logging.info("Script name: {}".format(__file__))
    logging.info("Script version: {}".format(__version__))

    analyse_dataset(args.dataset_dir, args.output_dir)

if __name__ == "__main__":
    main()
