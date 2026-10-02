# main.py

Arquivo: `app/main.py`.

## O que e

O ponto de entrada: cria o `FastAPI`, libera CORS, registra o tratador de `GameError` e monta os seis routers.

## Como foi feito

### Roteamento

```python
app.include_router(game_router, prefix="/api/game", tags=["game"])
app.include_router(world_router, prefix="/api/world", tags=["world"])
app.include_router(building_router, prefix="/api/building", tags=["building"])
app.include_router(base_router, prefix="/api/base", tags=["base"])
app.include_router(survivor_router, prefix="/api/survivors", tags=["survivors"])
app.include_router(expedition_router, prefix="/api/expeditions", tags=["expeditions"])
```

Cada router tem seu documento em [api](../api/README.md).

### Tratamento de erros

```python
@app.exception_handler(GameError)
def handle_game_error(_: Request, error: GameError) -> JSONResponse:
    return JSONResponse(status_code=error.status_code, content={"detail": error.message})
```

Qualquer `GameError` levantada em qualquer rota vira uma resposta JSON com o status que a propria excecao escolheu. O campo se chama `detail` de proposito: e o mesmo que o FastAPI usa em seus erros de validacao (422) e em `HTTPException`, entao o cliente le o mesmo campo sempre.

### Retomada da partida

```python
@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    manager.load_autosave()
    yield
```

Ao iniciar o servidor, a ultima partida salva automaticamente volta para a memoria. Sem isso, reiniciar o backend apagaria a partida em andamento, que era uma das limitacoes listadas no README raiz.

## Por que assim

- **`lifespan` em vez de `on_event`.** E o mecanismo atual do FastAPI; `on_event` esta depreciado.
- **Imports no topo.** O arquivo original importava os routers no meio do codigo, depois de definir as rotas. Agora todos os imports ficam no inicio, e a ordem do arquivo e: importar, configurar, registrar.
- **Rotas de status mantidas.** `/` e `/health` continuam como estavam, porque sao usadas para verificar se o servidor esta de pe.
