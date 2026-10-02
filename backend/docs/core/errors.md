# errors.py

Arquivo: `app/core/errors.py`.

## O que e

`GameError` e a unica excecao que as regras do jogo levantam quando o jogador pede algo invalido: enviar para expedicao quem esta ferido, reforcar sem madeira, escolher abrigo duas vezes.

## Como foi feito

```python
class GameError(Exception):
    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
```

A excecao carrega o status HTTP desejado. O padrao e 400 (pedido invalido). Os servicos usam outros valores quando faz sentido:

- `404` para algo que nao existe, como em `GameState.find_survivor`: `raise GameError("Survivor not found", 404)`;
- `409` para algo que conflita com a fase da partida, como em `GameState.require_playing`: `raise GameError(f"Game is not in progress ({self.status.value})", 409)`.

A conversao para HTTP acontece em um unico lugar, o handler registrado em `app/main.py` (ver [main](main.md)).

## Por que assim

- **Os servicos nao conhecem HTTP.** `services/` nao importa FastAPI; so levanta `GameError`. Isso permite testar as regras chamando funcoes diretas, sem cliente HTTP.
- **Nada de `HTTPException` espalhada.** Se cada rota convertesse erros por conta propria, os formatos de resposta divergiriam. Com o handler unico, toda falha chega ao frontend como `{"detail": "..."}`, e o cliente le sempre o mesmo campo.
- **O status viaja com o erro.** Quem levanta sabe se o problema e "nao existe" ou "fase errada"; quem trata so repassa.
