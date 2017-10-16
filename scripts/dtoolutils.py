"""Helper functions for working with datasets."""

import os
import shutil
import tempfile

from contextlib import contextmanager

TMPDIR_PREFIX = os.path.expanduser('~/tmp')


@contextmanager
def temp_working_dir():
    working_dir = tempfile.mkdtemp(prefix=TMPDIR_PREFIX)

    try:
        yield working_dir
    finally:
        shutil.rmtree(working_dir)


def stage_outputs(
    outputs,
    working_dir,
    dataset,
    output_dataset,
    overlays_to_copy,
    identifier
):

    for filename, metadata in outputs:
        src_abspath = os.path.join(working_dir, filename)
        useful_name = dataset.get_overlay('useful_name')[identifier]
        relpath = os.path.join(useful_name, filename)
        print("Push {} as {}.".format(src_abspath, relpath))
        output_dataset.put_item(src_abspath, relpath)

        # Add 'from' overlay
        output_dataset.add_item_metadata(relpath, 'from', identifier)

        # Copy overlays
        for overlay_name in overlays_to_copy:
            value = dataset.get_overlay(overlay_name)[identifier]
            output_dataset.add_item_metadata(relpath, overlay_name, value)

        # Add extra metadata
        for k, v in metadata.items():
            output_dataset.add_item_metadata(relpath, k, v)
