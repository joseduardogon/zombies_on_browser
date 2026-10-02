"""Ponto de entrada da API Zombies on Browser."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.building_routes import router as building_router
from app.api.world_routes import router as world_router

ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
]

app = FastAPI(title="Zombies on Browser API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(world_router, prefix="/api/world", tags=["world"])
app.include_router(building_router, prefix="/api/building", tags=["building"])


@app.get("/")
def read_root() -> dict[str, str]:
    """Retorna a mensagem de status da API.

    Returns:
        Dicionario com o status e uma mensagem de boas-vindas.
    """
    return {"status": "ok", "message": "Zombie Prevention Protocol Active"}


@app.get("/health")
def health_check() -> dict[str, str]:
    """Verifica se a API esta respondendo.

    Returns:
        Dicionario com o estado de saude do servico.
    """
    return {"status": "healthy"}
