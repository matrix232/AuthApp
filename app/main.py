from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from loguru import logger

from app.auth.router import router as router_auth


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[dict, None]:
    logger.info("Инициализация приложения...")
    yield
    logger.info("Завершнения работы приложения...")


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    app.add_middleware(CORSMiddleware, allow_origins=["*"],
                       allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

    register_routers(app)

    return app


def register_routers(app: FastAPI) -> None:
    root_router = APIRouter()

    @root_router.get("/", tags=['root'])
    def home_page():
        return {"message": "Добро пожаловать!"}

    app.include_router(root_router, tags=['root'])
    app.include_router(router_auth, prefix='/auth', tags=['Auth'])


app = create_app()
