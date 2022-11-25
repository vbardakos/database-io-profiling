import psycopg
from multiprocessing import Pool
from profiler.libs.profiler.c_profiler import Profiler


@Profiler
def test(*args): return sum(args)


@Profiler
def plain_fetchall(connection: str, stmt: str, iterations: int):
    for _ in range(iterations):
        with psycopg.connect(conninfo=connection) as conn:
            with conn.cursor() as cursor:
                cursor.execute(stmt)
                cursor.fetchall()


@Profiler
async def async_fetchall(connection: str, stmt: str, iterations: int):
    for _ in range(iterations):
        async with await psycopg.AsyncConnection.connect(connection) as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(stmt)
                await cursor.fetchall()


@Profiler
def plain_multiprocessing_fetchall(connection: str, stmt: str, iterations: int):
    parameters = [('plain_fetchall', connection, stmt, 1)] * iterations
    with Pool() as pool:
        pool.starmap(Profiler.unwrapped, parameters)


@Profiler
def async_multiprocessing_fetchall(connection: str, stmt: str, iterations: int):
    parameters = [('plain_fetchall', connection, stmt, 1)] * iterations
    with Pool() as pool:
        pool.starmap_async(Profiler.unwrapped, parameters).get()


@Profiler
def async_multiprocessing_fetchall_with_async(connection: str, stmt: str, iterations: int):
    parameters = [('async_fetchall', connection, stmt, 1)] * iterations
    with Pool() as pool:
        pool.starmap_async(Profiler.unwrapped, parameters).get()
