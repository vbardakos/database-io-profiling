import asyncio, os
from fastapi import FastAPI
from easyjobs.manager import EasyJobsManager


server = FastAPI()


@server.on_event('startup')
async def startup():
    job_manager = await EasyJobsManager.create(
        server,
        server_secret='abcd1234'
    )
