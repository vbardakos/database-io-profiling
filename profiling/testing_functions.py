import psycopg
from multiprocessing import Pool
from profiling.helpers import c_profiling_parser


@c_profiling_parser
def plain_fetchall(connection: str, stmt: str, iterations: int):
    for _ in range(iterations):
        with psycopg.connect(conninfo=connection) as conn:
            with conn.cursor() as cursor:
                cursor.execute(stmt)
                cursor.fetchall()


@c_profiling_parser
async def async_fetchall(connection: str, stmt: str, iterations: int):
    for _ in range(iterations):
        async with await psycopg.AsyncConnection.connect(connection) as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(stmt)
                await cursor.fetchall()


@c_profiling_parser
def plain_multiprocessing_fetchall(connection: str, stmt: str, iterations: int):
    parameters = [(connection, stmt, 1)] * iterations
    with Pool() as pool:
        pool.starmap(plain_fetchall.__wrapped__, parameters)


@c_profiling_parser
def async_multiprocessing_fetchall(connection: str, stmt: str, iterations: int):
    parameters = [(connection, stmt, 1)] * iterations
    with Pool() as pool:
        pool.starmap_async(plain_fetchall.__wrapped__, parameters).get()


@c_profiling_parser
def async_multiprocessing_fetchall_with_async(connection: str, stmt: str, iterations: int):
    parameters = [(connection, stmt, 1)] * iterations
    with Pool() as pool:
        pool.starmap_async(async_fetchall.__wrapped__, parameters).get()
