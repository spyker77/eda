import logging

from fastapi import FastAPI
from routers import router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
app.include_router(router)


@app.on_event("startup")
async def startup_event():
    pass


@app.on_event("shutdown")
async def shutdown_event():
    global channel_pool
    channel_pool.close()
    await channel_pool.wait_closed()
