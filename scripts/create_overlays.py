"""Varcan smart tool."""

import os

import click

from dtoolcore import DataSet

def create_useful_name_overlay(dataset):

    def name_from_identifier(identifier):
        path = dataset.item_properties(identifier)['relpath']
        return path.rsplit('.', 1)[0]

    useful_name_overlay = {
        identifier: name_from_identifier(identifier)
        for identifier in dataset.identifiers
    }

    dataset.put_overlay("useful_name", useful_name_overlay)


@click.command()
@click.argument('uri')
def main(uri):

    dataset = DataSet.from_uri(uri)
    # manifest = dataset._manifest

    # def name_from_identifier(identifier):
    #     path = manifest["items"][identifier]['path']
    #     return path.rsplit('.', 1)[0]

    # useful_name_overlay = {
    #     identifier: name_from_identifier(identifier)
    #     for identifier in dataset.identifiers
    # }

    # dataset.put_overlay("useful_name", useful_name_overlay)
    create_useful_name_overlay(dataset)

if __name__ == '__main__':
    main()
