"""Show information about analysis progress."""

import json
import yaml
import click

from collections import defaultdict

from dtool_azure import AzureDataSet, AzureProtoDataSet


def capture_data():

    blob_generator = output_dataset._storage_broker._blobservice.list_blobs(
        output_dataset.uuid,
        include='metadata'
    )

    blob_tuples = [
        (blob.name, blob.metadata.get('path', ''))
        for blob in blob_generator
    ]

    with open('blobinfo.json', 'w') as fh:
        fh.write(json.dumps(blob_tuples))


def input_dataset_stuff():

    input_identifiers = set(input_dataset.identifiers)

    input_dataset.access_overlay('useful_name')


def find_incomplete():
    with open('blobinfo.json') as fh:
        blobinfo = json.load(fh)

    namecounts = defaultdict(int)
    lookup = {}
    for blobname, blobpath in blobinfo:
        if len(blobpath):
            blob_basename = blobpath.rsplit('/', 1)[0]
            namecounts[blob_basename] += 1
            lookup[blobpath] = blobname


@click.command()
@click.option('--config-path')
def main(config_path=None):

    with open('analysis.yml') as fh:
        analyis_config = yaml.load(fh)

    input_uuid = analyis_config['input_dataset']
    output_uuid = analyis_config['output_dataset']

    input_dataset = AzureDataSet.from_uri(input_uuid, config_path=config_path)
    output_dataset = AzureProtoDataSet.from_uri(output_uuid)

    with open('blobinfo.json') as fh:
        blobinfo = json.load(fh)

    completed = set([])
    for blobname, blobpath in blobinfo:
        if len(blobpath):
            blob_basename = blobpath.rsplit('/', 1)[0]
            completed.add(blob_basename)

    names_to_process = set(
        input_dataset.access_overlay('useful_name').values()
    )

    work_remaining = names_to_process - completed

    useful_name_overlay = input_dataset.access_overlay('useful_name')

    print(len(useful_name_overlay))
    print(len(names_to_process))
    # find_incomplete()

    # for blob in blob_generator:
    #     if 'type' in blob.metadata:
    #         if blob.metadata['type'] == 'item':
    #             yield blob.name
    # output_dataset = AzureProtoDataSet.from_uri(output_uuid)

    # input_identifiers = set(input_dataset.identifiers)

    # completed_identifers = set([
    #     output_dataset._item_metadata(identifier)['from']
    #     for identifier in output_dataset._iteridentifiers()
    # ])

    # uncompleted_identififers = input_identifiers - completed_identifers

    # print("Completed {} of {}".format(
    #     len(completed_identifers),
    #     len(input_identifiers)
    #     )


if __name__ == '__main__':
    main()
