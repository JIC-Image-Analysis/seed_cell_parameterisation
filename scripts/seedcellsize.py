"""Wrapper script for seed cell size analysis."""

import os
import argparse
import subprocess

from dtoolcore import DataSet, ProtoDataSet

from dtoolutils import temp_working_dir, stage_outputs


class PythonSmartTool(object):

    def __init__(self):
        parser = argparse.ArgumentParser()

        parser.add_argument(
            '-d',
            '--dataset',
            help='URI of input dataset'
        )
        parser.add_argument(
            '-i',
            '--identifier',
            help='Identifier (hash) to process'
        )
        parser.add_argument(
            '-o',
            '--output-dataset',
            help='URI of output dataset'
        )

        args = parser.parse_args()

        self.input_dataset = DataSet.from_uri(args.dataset)
        self.output_dataset = ProtoDataSet.from_uri(args.output_dataset)

        self.identifier = args.identifier

    def run(self):

        input_path = self.input_dataset.item_content_abspath(self.identifier)

        with temp_working_dir() as tmpdir:
            command = ["python", "/scripts/analysis.py"]
            command += ["-i", input_path]
            command += ["-o", tmpdir]

            subprocess.call(command)

            outputs_with_metadata = [(o, {}) for o in self.outputs]

            stage_outputs(
                outputs_with_metadata,
                tmpdir,
                self.input_dataset,
                self.output_dataset,
                [],
                self.identifier
            )


def main():

    tool = PythonSmartTool()

    # tool.run()
    # tool.container = "jicscicomp/seedcellsize"
    # tool.command_string = "python /scripts/analysis.py -i /input1 -o /output"
    tool.outputs = [
        'original.png',
        'segmentation.png',
        'labels.png',
        'false_color.png',
        'results.csv'
    ]

    tool.run()


if __name__ == '__main__':
    main()
