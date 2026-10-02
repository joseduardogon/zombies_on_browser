# expedition_routes.py

Arquivo: `app/api/expedition_routes.py`. Prefixo: `/api/expeditions`.

## O que e

Envia um sobrevivente a vasculhar uma construcao.

```python
@router.post("", response_model=GameView)
def create_expedition(request: ExpeditionRequest) -> GameView:
    with manager.session() as state:
        expedition_service.start_expedition(state, request.survivor_id, request.building_id)
        return build_view(state)
```

Corpo: `{"survivor_id": "s3", "building_id": "b-13-6"}`.

A resposta traz `expeditions` com `ticks_total` e `ticks_remaining`, e o sobrevivente com `status: "away"`. Quando o tempo passa, o retorno acontece dentro de `POST /api/game/tick`; nao ha rota para "concluir" a expedicao, porque quem manda no tempo e o servidor.

Recusas: sobrevivente fora do abrigo, com menos de 25 de saude, alvo igual ao abrigo (400); sobrevivente ou construcao inexistente (404).

## Por que assim

- **O alvo e a construcao, nao a celula.** O identificador `b-x-y` e unico e ja carrega a posicao; evita que o cliente mande coordenadas de uma via.
- **Uma expedicao por pessoa.** O status `away` impede enviar a mesma pessoa duas vezes e, ao mesmo tempo, a tira da defesa do abrigo.
