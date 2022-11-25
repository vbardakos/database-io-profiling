from typing import Callable
from dataclasses import dataclass, field


class FactoryError(Exception):
    pass


@dataclass
class Entry:
    name: str = field(init=False)
    function: Callable
    instance: object

    def __post_init__(self):
        self.name = self.function.__name__

    def __hash__(self):
        return hash(id(self.name))

    def __eq__(self, other):
        return self.name == other.name


class FunctionFactory:
    def __init__(self):
        self.entries = set()

    def register(self, function: Callable, instance: object):
        entry = Entry(function, instance)
        if entry not in self.entries:
            self.entries.add(entry)
        else:
            raise FactoryError(f'Attempt to insert duplicated entry: "{entry}"')

    def get_entry(self, name: str) -> Entry:
        if name in self.names:
            return next(entry for entry in self.entries if entry.name == name)
        else:
            raise FactoryError(f'Cannot get Entry; "{name}" does not exist')

    def get_instance(self, name: str) -> Callable:
        return self.get_entry(name).instance

    def get_function(self, name: str) -> Callable:
        return self.get_entry(name).function

    @property
    def names(self) -> list[str]:
        return [entry.name for entry in self.entries]
