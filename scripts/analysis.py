"""seed_cell_size_2d analysis."""

import os
import json
import logging
import argparse

import dtool

import numpy as np

from scipy.misc import imsave

import skimage.filters
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


@transformation
def threshold_adaptive(image, block_size=91):

    thresholded = skimage.filters.threshold_adaptive(image, block_size)

    return thresholded


def parameterise_cells(segmentation):

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

    image = identity(image)
    image = threshold_adaptive(image)
    image = remove_small_objects(image)
    image = invert(image)
    image = remove_small_objects(image)
    image = invert(image)

    segmentation = connected_components(image, background=False)
    segmentation = clear_border(segmentation)
    segmentation = remove_small_regions(segmentation)

    return segmentation


def write_cell_info_to_csv(cell_info, csv_path):
    """Take the list of dictionaries provided by cell_info and write it in
    tabular form to the CSV file csv_path."""

    # Turn this into a variable to keep a consistent ordering
    headers = cell_info[0].keys()

    with open(csv_path, 'w') as fh:
        header_line = ','.join(headers) + '\n'
        fh.write(header_line)

        for entry in cell_info:
            data = [str(entry[h]) for h in headers]
            line = ','.join(data) + '\n'
            fh.write(line)


def analyse_file(fpath, output_directory):
    """Analyse a single file."""
    logging.info("Analysing file: {}".format(fpath))
    image = Image.from_file(fpath)

    print("analysing {}".format(fpath))

    segmentation = preprocess_and_segment(image)

    cell_info = parameterise_cells(segmentation)

    csv_path = os.path.join(output_directory, 'results.csv')

    write_cell_info_to_csv(cell_info, csv_path)


def output_name_from_dataset_and_identifier(dataset, identifier):

    rel_path = dataset.item_path_from_hash(identifier)

    basename = os.path.basename(rel_path)

    name, ext = os.path.splitext(basename)

    return name


def analyse_dataset(dataset_dir, i, output_dir):
    """Analyse all the files in the dataset."""
    dataset = dtool.DataSet.from_path(dataset_dir)

    rel_path = dataset.item_path_from_hash(i)

    output_basename = output_name_from_dataset_and_identifier(dataset, i)
    output_dirname = os.path.join(output_dir, output_basename)
    if not os.path.isdir(output_dirname):
        os.mkdir(output_dirname)

    analyse_file(rel_path, output_dirname)


def main():
    # Parse the command line arguments.
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-path", help="Input dataset directory")
    parser.add_argument("--output-directory", help="Output directory")
    parser.add_argument("--identifier", help="Identifier to analyse")
    parser.add_argument("--debug", default=True, action="store_true",
                        help="Write out intermediate images")
    args = parser.parse_args()

    if not os.path.isdir(args.dataset_path):
        parser.error("Not a directory: {}".format(args.dataset_dir))

    # Create the output directory if it does not exist.
    if not os.path.isdir(args.output_directory):
        os.mkdir(args.output_directory)
    AutoName.directory = args.output_directory

    # Only write out intermediate images in debug mode.
    if not args.debug:
        AutoWrite.on = False

    # Setup a logger for the script.
    log_fname = "audit.log"
    log_fpath = os.path.join(args.output_directory, log_fname)
    logging_level = logging.INFO
    if args.debug:
        logging_level = logging.DEBUG
    logging.basicConfig(filename=log_fpath, level=logging_level)

    # Log some basic information about the script that is running.
    logging.info("Script name: {}".format(__file__))
    logging.info("Script version: {}".format(__version__))

    analyse_dataset(args.dataset_path, args.identifier, args.output_directory)

if __name__ == "__main__":
    main()
