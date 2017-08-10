"""seed_cell_size_2d analysis."""

import os
import json
import logging
import argparse

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

from jicbioimage.illustrate import AnnotatedImage

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

        centroid_row, centroid_col = props.centroid
        cell_entry = dict(
            width=int(props.minor_axis_length),
            length=int(props.major_axis_length),
            area=props.area,
            identifier=props.label,
            perimeter=props.perimeter,
            convex_area=props.convex_area,
            centroid_row=centroid_row,
            centroid_col=centroid_col
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

    # Turn this into a variable to keep a consistent ordering. Sort and make
    # sure that identifier is first
    headers = cell_info[0].keys()
    headers.sort()
    headers.remove('identifier')
    headers.insert(0, 'identifier')

    with open(csv_path, 'w') as fh:
        header_line = ','.join(headers) + '\n'
        fh.write(header_line)

        for entry in cell_info:
            data = [str(entry[h]) for h in headers]
            line = ','.join(data) + '\n'
            fh.write(line)


def write_segmented_image_as_rgb(segmented_image, output_fpath):

    segmentation_as_rgb = segmented_image.unique_color_image

    with open(output_fpath, 'wb') as f:
        f.write(segmentation_as_rgb.png())


def generate_label_image(segmentation):

    base_for_ann = 100 * (segmentation > 0)
    ann = AnnotatedImage.from_grayscale(base_for_ann)

    for sid in segmentation.identifiers:
        c = segmentation.region_by_identifier(sid).centroid
        ann.text_at(
            str(sid),
            map(int, c),
            size=30,
            color=(255, 255, 0),
            center=True
        )

    return ann


def analyse_file(fpath, output_directory):
    """Analyse a single file."""
    logging.info("Analysing file: {}".format(fpath))
    image = Image.from_file(fpath)

    image_output_fpath = os.path.join(output_directory, 'original.png')
    with open(image_output_fpath, 'wb') as fh:
        fh.write(image.png())

    segmentation = preprocess_and_segment(image)

    false_colour_fpath = os.path.join(output_directory, 'false_color.png')
    with open(false_colour_fpath, 'wb') as fh:
        fh.write(segmentation.png())

    rgb_segmentation_fpath = os.path.join(output_directory, 'segmentation.png')
    write_segmented_image_as_rgb(segmentation, rgb_segmentation_fpath)

    cell_info = parameterise_cells(segmentation)
    csv_fpath = os.path.join(output_directory, 'results.csv')
    write_cell_info_to_csv(cell_info, csv_fpath)

    label_image = generate_label_image(segmentation)
    label_image_fpath = os.path.join(output_directory, 'labels.png')
    with open(label_image_fpath, 'wb') as fh:
        fh.write(label_image.png())


def main():
    # Parse the command line arguments.
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-file", "-i", help="Input file")
    parser.add_argument("--output-directory", "-o", help="Output directory")
    parser.add_argument("--debug", default=False, action="store_true",
                        help="Write out intermediate images")
    args = parser.parse_args()

    if not os.path.isdir(args.output_directory):
        parser.error("Not a directory: {}".format(args.output_directory))

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

    analyse_file(args.input_file, args.output_directory)

if __name__ == "__main__":
    main()
