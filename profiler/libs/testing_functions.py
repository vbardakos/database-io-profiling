import psycopg
from multiprocessing import Pool
from concurrent.futures import ThreadPoolExecutor
from profiler.libs.profiler.c_profiler import Profiler


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
def concurrent_fetchall(connection: str, stmt: str, iterations: int):
    parameters = [(connection, stmt, 1)] * iterations
    with ThreadPoolExecutor() as executor:
        executor.map(lambda args: plain_fetchall(*args), parameters)
