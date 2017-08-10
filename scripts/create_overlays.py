"""Varcan smart tool."""

import os

import click

from dtool_azure import AzureDataSet


def create_useful_name_overlay(dataset):

    def name_from_identifier(identifier):
        path = dataset.item_properties(identifier)['path']
        return path.split('.')[0]

    identifier = dataset.identifiers[0]

    useful_name_overlay = {
        identifier: name_from_identifier(identifier)
        for identifier in dataset.identifiers
    }

    dataset.put_overlay("useful_name", useful_name_overlay)


@click.command()
@click.argument('uuid')
@click.option('--config-path', type=click.Path(exists=True))
def main(uuid, config_path=None):

    dataset = AzureDataSet.from_uri(uuid, config_path=config_path)

    create_useful_name_overlay(dataset)

if __name__ == '__main__':
    main()
