"""Smart tool."""

import os
import shlex
import shutil
import argparse
import tempfile
import subprocess

from contextlib import contextmanager

from dtool_azure import AzureDataSet, AzureProtoDataSet

TMPDIR_PREFIX = os.path.expanduser(
    "~/tmp/tmp"
)


@contextmanager
def temp_working_dir():
    working_dir = tempfile.mkdtemp(prefix=TMPDIR_PREFIX)

    try:
        yield working_dir
    finally:
        shutil.rmtree(working_dir)


class DockerAssist(object):

    def __init__(self, image_name, base_command):
        self.image_name = image_name
        self.base_command = base_command
        self.volume_mounts = []

    def add_volume_mount(self, outside, inside):
        self.volume_mounts.append((outside, inside))

    @property
    def command(self):
        command_string = ['docker', 'run', '--rm']

        for outside, inside in self.volume_mounts:
            command_string += ['-v', '{}:{}'.format(outside, inside)]

        command_string += [self.image_name]

        command_string += shlex.split(self.base_command)

        return command_string

    @property
    def command_string(self):
        return ' '.join(self.command)

    def run(self):
        subprocess.call(self.command)

    def run_and_capture_stdout(self):
        return subprocess.check_output(self.command)


class SmartTool(object):

    def __init__(self):
        parser = argparse.ArgumentParser()

        parser.add_argument(
            '-d',
            '--dataset',
            help='UUID of input dataset'
        )
        parser.add_argument(
            '-i',
            '--identifier',
            help='Identifier (hash) to process'
        )
        parser.add_argument(
            '-o',
            '--output-dataset',
            help='UUID of output dataset'
        )
        parser.add_argument(
            '--input-config-path',
            help='Path to Azure config for input dataset',
            default=None
        )

        args = parser.parse_args()

        self.input_dataset = AzureDataSet.from_uri(
            args.dataset,
            config_path=args.input_config_path
        )

        self.output_dataset = AzureProtoDataSet.from_uri(args.output_dataset)

        self.identifier = args.identifier

    def stage_outputs(self, working_directory):
        for filename in self.outputs:

            useful_name = self.input_dataset.access_overlay(
                'useful_name'
            )[self.identifier]

            fpath = os.path.join(working_directory, filename)
            relpath = os.path.join(useful_name, filename)
            out_id = self.output_dataset.put_item(fpath, relpath)
            self.output_dataset.add_item_metadata(
                out_id,
                'from',
                "{}/{}".format(self.input_dataset.uuid, self.identifier)
                )

    def run(self):
        input_file_path = self.input_dataset.item_contents_abspath(
            self.identifier
        )

        with temp_working_dir() as working_directory:
            runner = DockerAssist(self.container, self.command_string)
            runner.add_volume_mount(input_file_path, '/input1')
            runner.add_volume_mount(working_directory, '/output')

            runner.run()

            self.stage_outputs(working_directory)
