import json
import time
import shlex
import subprocess

import click
import redis


def execute_task(task):

    command = ['python'] + shlex.split(task["tool_path"])
    command += ['-d', task["input_uuid"]]
    command += ['-i', task["identifier"]]
    command += ['-o', task["output_uuid"]]

    return subprocess.call(command)


@click.command()
@click.option('--redis-host', envvar='REDIS_HOST')
def main(redis_host):
    r = redis.StrictRedis(host=redis_host, port=6379)

    while True:
        task_identifier = r.brpoplpush('workqueue', 'inprogress')

        raw_task = r.hget('tasks', task_identifier)
        task = json.loads(raw_task)

        return_code = execute_task(task)

        if return_code is 0:
            r.lrem('inprogress', 1, task_identifier)
            r.lpush('completed', task_identifier)
        else:
            raise("BLEW UP HORRIBLY on {}".format(task["identifier"]))


if __name__ == '__main__':
    main()
