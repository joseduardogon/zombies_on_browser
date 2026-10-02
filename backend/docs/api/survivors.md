# survivor_routes.py

Arquivo: `app/api/survivor_routes.py`. Prefixo: `/api/survivors`.

## O que e

A API dos sobreviventes. O modelo existia desde o inicio, mas nenhuma rota o expunha.

## Endpoints

### GET /

```python
    with manager.session() as state:
        return state.survivors
```

Lista todos, vivos ou mortos.

### POST /{survivor_id}/role

```python
        survivor_service.set_role(state, survivor_id, request.role)
        return build_view(state)
```

Corpo: `{"role": "guard"}`. Funcoes aceitas: `leader`, `scavenger`, `builder`, `guard`, `idle`. A funcao nao e so um rotulo:

- `guard` defende o abrigo a noite;
- `builder` reforca 50% mais;
- `scavenger` leva 10 pontos a mais de pilhagem por expedicao.

Mortos nao mudam de funcao (400).

### POST /{survivor_id}/treat

```python
        survivor_service.treat(state, survivor_id)
        return build_view(state)
```

Gasta um remedio e cura de 35 pontos para cima, conforme a melhor habilidade de medicina do abrigo. Responde 400 sem remedio, com o paciente fora do abrigo ou com saude cheia.

## Por que assim

- **A funcao e a unica alavanca de microgestao.** Comer, beber e dormir sao automaticos; o que o jogador decide e quem faz o que. Por isso `role` tem rota propria e efeito mecanico.
- **O tratamento e opcional.** Sem ele a saude se recupera devagar (0,5 por hora com necessidades em dia). O remedio acelera a volta de um guarda ferido antes de uma noite dificil.
