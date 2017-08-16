"""Identify unprocessed identifiers."""

import yaml
import click

from dtool_azure import AzureDataSet, AzureProtoDataSet


@click.command()
@click.option('--config-path')
def main(config_path=None):

    with open('analysis.yml') as fh:
        analyis_config = yaml.load(fh)

    input_uuid = analyis_config['input_dataset']
    output_uuid = analyis_config['output_dataset']

    input_dataset = AzureDataSet.from_uri(input_uuid, config_path=config_path)
    output_dataset = AzureProtoDataSet.from_uri(output_uuid)

    input_identifiers = set(input_dataset.identifiers)

    completed_identifers = set([
        output_dataset._item_metadata(identifier)['from']
        for identifier in output_dataset._iteridentifiers()
    ])

    uncompleted_identififers = input_identifiers - completed_identifers

    print("Completed {} of {}".format(
        len(completed_identifers),
        len(input_identifiers)
        )
    )

if __name__ == '__main__':
    main()
