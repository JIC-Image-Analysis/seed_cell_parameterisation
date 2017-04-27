"""seed_cell_size_2d analysis."""

import os
import logging
import argparse

import dtool

import numpy as np

from scipy.misc import imsave

from skimage.filters import threshold_adaptive

from jicbioimage.core.image import Image
from jicbioimage.core.transform import transformation
from jicbioimage.core.io import AutoName, AutoWrite
from jicbioimage.segment import connected_components

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


def preprocess_and_segment(image):

    thresholded = threshold_adaptive(image, block_size=91)

    image = remove_small_objects(thresholded)
    image = invert(image)
    image = remove_small_objects(image)
    image = invert(image)

    segmentation = connected_components(image, background=False)

    return segmentation


def analyse_file(fpath, output_directory):
    """Analyse a single file."""
    logging.info("Analysing file: {}".format(fpath))
    image = Image.from_file(fpath)
    print("analysing {}".format(fpath))
    print(image.shape)

    segmentation = preprocess_and_segment(image)

    print(segmentation.identifiers)


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
