"""Ponto de entrada da API Zombies on Browser."""

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.base_routes import router as base_router
from app.api.building_routes import router as building_router
from app.api.expedition_routes import router as expedition_router
from app.api.game_routes import router as game_router
from app.api.survivor_routes import router as survivor_router
from app.api.world_routes import router as world_router
from app.core.config import get_static_dir
from app.core.errors import GameError
from app.services.game_manager import manager

ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
]


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Retoma a ultima partida salva ao iniciar o servidor.

    Args:
        _: Aplicacao FastAPI, nao utilizada.

    Yields:
        Nada; o servidor atende requisicoes enquanto o contexto esta aberto.
    """
    manager.load_autosave()
    yield


app = FastAPI(title="Zombies on Browser API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(GameError)
def handle_game_error(_: Request, error: GameError) -> JSONResponse:
    """Converte um erro de regra do jogo em resposta HTTP.

    Args:
        _: Requisicao, nao utilizada.
        error: Erro levantado pelas regras.

    Returns:
        Resposta JSON com o campo `detail` e o status do erro.
    """
    return JSONResponse(status_code=error.status_code, content={"detail": error.message})


app.include_router(game_router, prefix="/api/game", tags=["game"])
app.include_router(world_router, prefix="/api/world", tags=["world"])
app.include_router(building_router, prefix="/api/building", tags=["building"])
app.include_router(base_router, prefix="/api/base", tags=["base"])
app.include_router(survivor_router, prefix="/api/survivors", tags=["survivors"])
app.include_router(expedition_router, prefix="/api/expeditions", tags=["expeditions"])


@app.get("/health")
def health_check() -> dict[str, str]:
    """Verifica se a API esta respondendo.

    Returns:
        Dicionario com o estado de saude do servico.
    """
    return {"status": "healthy"}


static_dir = get_static_dir()
if static_dir is not None:
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="frontend")
else:

    @app.get("/")
    def read_root() -> dict[str, str]:
        """Retorna a mensagem de status da API.

        Returns:
            Dicionario com o status e uma mensagem de boas-vindas.
        """
        return {"status": "ok", "message": "Zombie Prevention Protocol Active"}
