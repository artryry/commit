from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from routers import users
from database.database import create_tables
from logger import Logger
from synchronizer import Synchronizer


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not await Synchronizer.send_public_key():
        Logger.warning(f"Public key was not sent")
    else:
        Logger.info(f"Public key sent")
    await create_tables()
    yield


app = FastAPI(lifespan=lifespan, root_path="/auth")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(users.router)


# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)
