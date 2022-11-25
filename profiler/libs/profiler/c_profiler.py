import cProfile
from typing import Callable
from profiler.libs.profiler.function_factory import FunctionFactory


class MetaDecorator(type):
    factory = FunctionFactory()

    def __call__(cls, function: Callable, *args, **kwargs):
        instance = super(MetaDecorator, cls).__call__(function, *args, **kwargs)
        cls.factory.register(function, instance)
        return instance

    @property
    def registered(cls) -> list[str]:
        return cls.factory.names

    def __repr__(cls):
        return f'{cls.__name__}{cls.registered}'


class Profiler(metaclass=MetaDecorator):
    def __init__(self, function: Callable):
        self.cls_name = type(self).__name__
        self.fun_name = function.__name__

    def __call__(self, *args, **kwargs):
        statement = self.stmt_builder(*args, **kwargs)
        return cProfile.run(statement)

    @classmethod
    def decorated(cls, name: str, *args, **kwargs) -> Callable:
        return cls.factory.get_instance(name)(*args, **kwargs)

    @classmethod
    def unwrapped(cls, name: str, *args, **kwargs):
        return cls.factory.get_function(name)(*args, **kwargs)

    def stmt_builder(self, *args, **kwargs) -> str:
        kw_arguments = self._kw_scrapper(args, kwargs)
        return f'{self.cls_name}.unwrapped("{self.fun_name}",{kw_arguments})'

    @staticmethod
    def _kw_scrapper(arguments, kw_arguments) -> str:
        arguments = list(map(repr, arguments))
        arguments.extend(f'{k}={repr(v)}' for k, v in kw_arguments.items())
        return ','.join(arguments)
