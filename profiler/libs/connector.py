import environs
from dataclasses import dataclass, fields, asdict


env = environs.Env()
env.read_env()


@dataclass(frozen=True)
class DbConn:
    user: str = env.str('PG_USERNAME', 'postgres')
    password: str = env.str('PG_PASSWORD', 'secret')
    port: str = env.str('PG_PORT', '5432')
    host: str = env.str('PG_HOST', 'localhost')

    def _conn_field(self, field_name: str) -> str:
        return f'{field_name}={getattr(self, field_name)}'

    @property
    def is_default(self) -> bool:
        return self == DbConn()

    @property
    def connection_info(self) -> str:
        return ' '.join([self._conn_field(field.name) for field in fields(self)])

    @property
    def as_dict(self) -> dict:
        return asdict(self)
