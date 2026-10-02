# base_routes.py

Arquivo: `app/api/base_routes.py`. Prefixo: `/api/base`.

## O que e

As acoes sobre o abrigo: escolher onde ele fica e reforcar suas aberturas.

## Endpoints

### POST /claim

```python
    with manager.session() as state:
        game_factory.claim_base(state, request.building_id)
        return build_view(state)
```

Corpo: `{"building_id": "b-13-5"}`. So funciona na fase de preparacao e em lotes que nao sejam floresta. Cria os tres sobreviventes iniciais e o estoque inicial (ver [game_factory](../services/game_factory.md)).

### POST /reinforce

```python
        base_service.reinforce_aperture(state, request.aperture_id, request.survivor_id)
        return build_view(state)
```

Corpo: `{"aperture_id": "b-13-5_r1_a1", "survivor_id": "s1"}`. Gasta 2 madeiras e soma saude a abertura (ver [base_service](../services/base_service.md)). Responde 404 se a abertura nao pertence ao abrigo, e 400 se faltar madeira ou o trabalhador estiver fora.

## Por que assim

- **Dois verbos, uma resposta.** Ambos devolvem `GameView`; o frontend atualiza o painel do abrigo, os recursos e o diario de uma vez.
- **O identificador da abertura e legivel.** `b-13-5_r1_a1` diz a construcao, o comodo e a posicao da abertura, o que facilita depurar com um cliente HTTP.
