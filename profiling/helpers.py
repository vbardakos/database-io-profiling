import environs
import argparse
import functools
from pathlib import Path
from importlib import import_module
from typing import Callable, Iterable
from dataclasses import dataclass, fields


env = environs.Env()
env.read_env()


@dataclass(frozen=True, init=False)
class Connector:
    user: str = env.str('PG_USERNAME', 'postgres')
    password: str = env.str('PG_PASSWORD', 'secret')
    port: str = env.str('PG_PORT', '5432')
    host: str = env.str('PG_HOST', 'localhost')

    def _conn_field(self, field_name: str):
        return f'{field_name}={getattr(self, field_name)}'

    @property
    def connection_info(self):
        return ' '.join([self._conn_field(field.name) for field in fields(self)])


def _parameter_scraper(function: Callable, arguments: tuple, kw_arguments: dict) -> str:
    """
    transforms a function's params into a string
    e.g. paramA=1,paramB='a',...
    """
    argument_names: tuple = function.__code__.co_varnames
    new_kw_arguments: dict = {key: value for key, value in zip(argument_names, arguments)}
    kw_arguments.update(new_kw_arguments)

    def _scraper(kw_params):
        if kw_params:
            k, v = kw_params.popitem()
            if isinstance(v, str):
                v = f"'{v}'"
            elif isinstance(v, Iterable):
                raise NotImplementedError('Iterables cannot be scraped')
            return [f'{k}={v}'] + _scraper(kw_params)
        else:
            return []

    return ','.join(_scraper(kw_arguments))


def c_profiling_parser(function: Callable):
    """
    cProfile only accepts statements & functions in string format;
    Functions called under c_profiling_parser return a string ready for eval().
    """
    @functools.wraps(function)
    def inner(*args, **kwargs) -> str:
        function_name = function.__name__
        arguments = _parameter_scraper(function, args, kwargs)
        return f'{function_name}.__wrapped__({arguments})'
    return inner


def get_namespace(arguments: list[str], testing_choices: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(dest='command', required=True)

    show_command = subparsers.add_parser(name='show')
    show_command.add_argument('-f', '--files', type=str, nargs='+', help='Files to visualise;')

    run_command = subparsers.add_parser(name='run')
    run_command.add_argument('-f', '--func', type=str, metavar='FUNC',
                             choices=testing_choices, help=f'Choose from: {testing_choices}')
    run_command.add_argument('-s', '--stmt', type=str, help='SQL Statement')
    run_command.add_argument('-i', '--iter', type=int, default=1, help='Iterations')
    run_command.add_argument('-m', '--memory', type=float, default=0.0, help='Max memory in MB')
    run_command.add_argument('-c', '--cpus', type=float, default=0.0, help='Max cpus available')
    run_command.add_argument('-n', '--name', type=str, default=None, help='Save name')
    run_command.add_argument('-v', '--view', action='store_true', help='View results')
    run_command.add_argument('--local', action='store_true', help='run locally')

    # run_command.add_argument('-V', action='store_true', help='Only View results')

    return parser.parse_args(arguments[1:])
