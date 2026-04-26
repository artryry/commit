from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import cfg
from api.routes import auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # TODO: add startup and shutdown events
    yield


app = FastAPI(lifespan=lifespan, root_path="/auth")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cfg.ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router)
