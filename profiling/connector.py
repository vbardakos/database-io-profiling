import environs
from dataclasses import dataclass, fields


env = environs.Env()
env.read_env()


@dataclass(frozen=True, init=False)
class Connector:
    user: str = env.str('PG_USERNAME', 'postgres')
    password: str = env.str('PG_PASSWORD', 'secret')
    port: str = env.str('PG_PORT', '5432')
    host: str = env.str('PG_HOST', 'postgres')

    def _conn_field(self, field_name: str):
        return f'{field_name}={getattr(self, field_name)}'

    @property
    def connection_info(self):
        return ' '.join([self._conn_field(field.name) for field in fields(self)])
