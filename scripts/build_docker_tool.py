"""Build containerised smart tool."""

import os
import shutil
import argparse
import subprocess

import yaml

from dtoolutils import temp_working_dir


docker_template = """
FROM jicscicomp/bioformats

RUN rpm --import https://packages.irods.org/irods-signing-key.asc
RUN wget -qO - https://packages.irods.org/renci-irods.yum.repo | tee /etc/yum.repos.d/renci-irods.yum.repo
RUN yum install -y irods-icommands tkinter

COPY requirements.txt .
RUN pip install -r requirements.txt
ADD scripts.tar.gz .
"""


def build_docker_tool(name):

    cwd = os.getcwd()


    with temp_working_dir() as working_dir:

        # Package the scripts directory
        scripts_path = os.path.join(cwd, 'scripts')
        tarfile_path = os.path.join(working_dir, 'scripts.tar.gz')
        tar_command = ['tar', '-zvcf', tarfile_path, 'scripts']
        subprocess.call(tar_command)

        # Copy the requirements file
        requirements_path = os.path.join(cwd, 'requirements.txt')
        shutil.copy(requirements_path, working_dir)

        # Write the Dockerfile
        dockerfile_abspath = os.path.join(working_dir, 'Dockerfile')
        with open(dockerfile_abspath, 'w') as fh:
            fh.write(docker_template)

        # Build the image
        command = ['docker', 'build', '--no-cache', '-t', name, working_dir]
        subprocess.call(command)


def main():

    with open('project.yml') as fh:
        project = yaml.load(fh)

    project_name = project['name']

    docker_image_name = 'jicscicomp/{}'.format(project_name)

    build_docker_tool(docker_image_name)


if __name__ == '__main__':
    main()
