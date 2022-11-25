import asyncio
import subprocess as sub
from fastapi import FastAPI, APIRouter
from easyjobs.workers.worker import EasyJobsWorker
from profiler.libs.connector import DbConn, docker_compose
from profiler.app.pipe_manager import PipeManager
from typing import Optional


server = FastAPI()


@server.on_event('startup')
async def setup():
    worker = await EasyJobsWorker.create(
        server,
        server_secret='abcd1234',
        manager_host='0.0.0.0',
        manager_port=8220,
        manager_secret='abcd1234',
        jobs_queue='ETL',
        max_tasks_per_worker=5
    )

    pipeline_manager: PipeManager = PipeManager()

    @worker.task()
    def reset_pipeline_manager():
        nonlocal pipeline_manager
        pipeline_manager = PipeManager()
        return 'ReInitializes Pipeline Manager'

    @worker.task(run_after=['setup_container'])
    def configure_connection(user: str = None, password: str = None, host: str = None, port: int = 5432):
        if all([user, password, host, port]):
            pipeline_manager.set_new_connection(user, password, host, port)
        else:
            pipeline_manager.set_default_connection()

        return {'default': pipeline_manager.conn.is_default, 'name': 'profiler'}

    @worker.task()
    def setup_container(default: bool, name: str):
        if default is True:
            if not bool(sub.check_output(['docker', 'ps', '-q', '-f', f'name={name}_'])):
                sub.run(['docker-compose', 'up', '-d'])
                return "Container is set up successfully"
            else:
                return "Container is already up"
        else:
            return "Container setup skipped - use of external connection"

    @worker.task()
    def configure_pipeline(functions: str, statement: str, iterations: int = 1):
        pipeline_manager.select_functions(functions)
        pipeline_manager.add_statement(statement)
        pipeline_manager.add_iterations(iterations)
        return pipeline_manager.as_dictionary

    # @worker.task(run_after=['deploy_environment'], schedule=every_minute, default_args=default_args)
    # def configure_connection(user: Optional[str] = None, password: Optional[str] = None,
    #                          host: Optional[str] = None, port: int = 5432):
    #     print('parses conn')
    #     conn = DbConn(user, password, host, port) if all([user, password, host, port]) else DbConn()
    #     return parse_connection_response(conn)
    #
    # @worker.task(run_after=['create_connection'])
    # def deploy_environment(connection: dict):
    #     print('deploys')
    #     defaults = {'connection': connection}
    #     return defaults
    #
    # @worker.task()
    # def create_connection(*args, **kwargs):
    #     print('creates connection')
    #     return {'info': args, 'other': kwargs}


    # @worker.task(run_after=['deploy_environment'], default_args={'args': [-1]})
    # def configure_environment(x: int):
    #     print(f'configure: {x}')
    #     return {'data': x * 10, 'other_info': 'hello'}
    #
    # @worker.task()
    # def deploy_environment(data: int, *args, **kwargs):
    #     print(f"deploy_environment - started: {args} {kwargs}")
    #     print(f"deploy_environment - completed: {data}")
    #     return {'data': data * 10}
