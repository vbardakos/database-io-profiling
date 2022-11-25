from profiler.libs.connector import DbConn
from profiler.libs.testing_functions import Profiler


class PipeManager:
    def __init__(self):
        self.conn = DbConn()
        self.stmt = ''
        self.iter = 1
        self.func = set()

    def set_new_connection(self, user: str, password: str, host: str, port: int):
        self.conn = DbConn(user, password, host, port)

    def set_default_connection(self):
        self.conn = DbConn()

    def add_statement(self, stmt: str):
        self.stmt = stmt

    def add_iterations(self, iters: int):
        self.iter = iters

    def select_functions(self, funcs: str):
        funcs = funcs.replace(' ', '').split(',')
        self.func = {func for func in funcs if func in Profiler.registered}

    @property
    def as_dictionary(self):
        dictionary = self.__dict__.copy()
        dictionary.update({'conn': self.conn.as_dict, 'default': self.conn.is_default})
        return dictionary
