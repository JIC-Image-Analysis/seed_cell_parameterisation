
import os
import csv
import json

import click

from dtoolcore import DataSet


def identifiers_where_overlay_is_true(dataset, overlay_name):

    overlay = dataset.get_overlay(overlay_name)

    selected = [identifier
                for identifier in dataset.identifiers
                if overlay[identifier]]

    return selected


def create_is_csv_overlay(dataset):

    def is_csv(identifier):
        relpath = dataset.item_properties(identifier)['relpath']
        _, ext = os.path.splitext(relpath)
        return ext == '.csv'

    is_csv_overlay = {
        identifier: is_csv(identifier)
        for identifier in dataset.identifiers
    }

    dataset.put_overlay("is_csv", is_csv_overlay)


def generate_header_list(unsorted_keys):
    """Return a list of headers for the CSV file, ensuing that the order of the
    first four headers is fixed and the remainder are sorted."""

    unsorted_keys.remove('identifier')

    sorted_remainder = sorted(unsorted_keys)

    header_list = ['identifier', 'label1', 'label2', 'label3']
    header_list += sorted_remainder

    return header_list


def build_master_csv(fpaths_and_extra_data, output_csv_fpath):

    extra_header_keys = ['label1', 'label2', 'label3']

    first_file_fpath = fpaths_and_extra_data[0][0]

    with open(first_file_fpath) as fh:
        reader = csv.DictReader(fh)
        row = reader.next()
        header_list = generate_header_list(row.keys())

    with open(output_csv_fpath, 'w') as fh:
        fh.write(','.join(header_list) + '\n')

    def add_to_output_csv(list_of_items):

        with open(output_csv_fpath, 'a') as fh:
            for entry in list_of_items:
                line = ','.join(str(entry[h]) for h in header_list)
                fh.write(line + '\n')

    for fpath, extra_values in fpaths_and_extra_data:

        extra_data = dict(zip(extra_header_keys, extra_values))

        with open(fpath) as fh:
            reader = csv.DictReader(fh)
            all_rows = list(reader)

        for items in all_rows:
            items.update(extra_data)

        add_to_output_csv(all_rows)


@click.command()
@click.argument('dataset-path')
def main(dataset_path):
    dataset = DataSet.from_uri(dataset_path)

    create_is_csv_overlay(dataset)

    def info_from_identifier(identifier):
        relpath = dataset.item_properties(identifier)['relpath']
        # label1 = "5A_CB_Rep3_T2"
        # compound = relpath
        # compound, _ = relpath.split('/')

        print(relpath)

        label1, compound, _ = relpath.split('/')

        try:
            label2, label3 = compound.rsplit('-', 1)
        except ValueError:
            label2, label3 = "?", "?"

        return label1, label2, label3

    fpaths_and_extra_data = [
        (
            dataset.item_content_abspath(identifier),
            info_from_identifier(identifier)
        )
        for identifier in identifiers_where_overlay_is_true(dataset, "is_csv")
    ]

    import pprint; pprint.pprint(fpaths_and_extra_data)

    build_master_csv(fpaths_and_extra_data, 'all_cells.csv')

if __name__ == '__main__':
    main()
