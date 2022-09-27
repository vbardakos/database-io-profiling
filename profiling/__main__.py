import argparse
import subprocess
import sys
import pstats
import cProfile
from pathlib import Path
import profiling.testing_functions
from profiling.testing_functions import *
from profiling.helpers import get_namespace, Connector


def get_testing_functions(module: object):
    """ just gets the decorated functions """
    objects = map(lambda name: (name, getattr(module, name)), dir(module))
    return {name: obj for name, obj in objects if hasattr(obj, '__wrapped__')}


def get_file_name(namespace: argparse.Namespace):
    name = namespace.name
    name += f'-{namespace.cpus}T' if namespace.cpus else ''
    name += f'-{namespace.memory}MB' if namespace.memory else ''
    return f'{name}:{namespace.iter}.data'


def get_docker_run_command(namespace: argparse.Namespace) -> list[str]:
    docker_command = ['docker-compose', 'run', '--rm', 'client']
    docker_command.extend(['--cpus="{namespace.cpus}"'] if namespace.cpus else [])
    docker_command.extend(['-m', f'{namespace.memory}m'] if namespace.memory else [])

    python_command = ['python', '-m', 'profiling', 'run', '--local',
                      '-f', namespace.func,
                      '-s', f"'{namespace.stmt}'",
                      '-i', namespace.iter]
    return docker_command + python_command
    # python_command = f'python -m profiling run -f {namespace.func} -s \'{namespace.stmt}\' -i {namespace.iter} --local'
    # python_command += f' -n {namespace.name}' if namespace.name else ''
    # python_command += f' -v' if namespace.view else ''
    # docker_command = f'docker-compose run --rm client'
    # docker_command += f' --cpus="{namespace.cpus}"' if namespace.cpus else ''
    # docker_command += f' -m {namespace.memory}m' if namespace.memory else ''
    # return ' '.join([docker_command, python_command])


def main(argv):
    functions = get_testing_functions(profiling.testing_functions)
    namespace = get_namespace(argv, testing_choices=list(functions))
    results_directory = Path(__file__).parent.joinpath('results')

    match namespace.command:
        case 'run':
            if namespace.local:
                function = functions[namespace.func]
                profiler = cProfile.Profile()

                print(function(1, 2, 3))

                statistics = profiler.run(function(Connector().connection_info, namespace.stmt, namespace.iter))
                result = pstats.Stats(statistics).sort_stats('cumtime')

                if namespace.name:
                    filename = get_file_name(namespace)
                    results_directory.mkdir(parents=True, exist_ok=True)
                    result.dump_stats(results_directory.joinpath(filename))
                if namespace.view:
                    result.print_stats()
            else:
                docker_command_str = get_docker_run_command(namespace)
                subprocess.run(docker_command_str)
        case 'show':
            for file_name in namespace.files:
                file_directory = results_directory.joinpath(file_name)
                if file_directory.is_file():
                    subprocess.run(['snakeviz', str(file_directory)])
                else:
                    print(f'{file_directory} is not a file')


if __name__ == '__main__':
    main(sys.argv)
