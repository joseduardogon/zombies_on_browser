# building_routes.py

Arquivo: `app/api/building_routes.py`. Prefixo: `/api/building`.

## O que e

Entrega a planta de uma construcao.

```python
@router.get("/{building_id}", response_model=Building)
def get_building(building_id: str) -> Building:
    with manager.session() as state:
        return build_building_view(state, building_id)
```

O identificador tem a forma `b-x-y` (por exemplo `b-13-5`). Na primeira consulta a construcao e gerada e guardada; nas seguintes volta a mesma. Identificador desconhecido responde 404.

## O que mudou

- **`POST /generate/{type}` foi removida.** O prototipo gerava uma casa nova a cada clique, e a construcao sumia ao fechar o painel. Agora cada lote tem uma construcao fixa.
- **O tipo vem do mapa.** O cliente nao escolhe mais "o que" gerar; a celula ja sabe se e uma casa, loja, fabrica ou floresta.

## Por que assim

- **GET, nao POST.** Consultar uma construcao nao altera a partida do ponto de vista do jogador (a geracao e deterministica), entao o verbo correto e GET.
- **Esconde o que nao foi descoberto.** A resposta passa por `build_building_view` ([schemas](schemas.md)): pilhagem zerada antes da primeira expedicao e nunca revela sobrevivente isolado.
- **A sessao grava o autosave.** Gerar uma construcao muda `state.buildings`, e a sessao salva ao sair, entao um save nunca fica sem uma construcao ja vista.
