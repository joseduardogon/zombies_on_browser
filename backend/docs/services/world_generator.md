# world_generator.py

Arquivo: `app/services/world_generator.py`.

## O que e

Gera o mapa da cidade. Esta logica estava dentro da rota `POST /api/world/generate`; foi movida para um servico para poder ser testada e reutilizada pela criacao de partida.

## Como foi feito

### Identificador estavel por lote

```python
def building_id_for(x: int, y: int) -> str:
    return f"b-{x}-{y}"
```

Todo lote recebe o identificador `b-x-y`. Como ele e calculado da posicao, nao precisa ser guardado em tabela alguma, e o frontend consegue deduzir qual construcao uma celula contem.

### Vias, lotes e setores

```python
            if x % balance.ROAD_SPACING == 0 or y % balance.ROAD_SPACING == 0:
                cells.append(
                    WorldCell(
                        coordinates=coordinates,
                        sector_type=SectorType.ROAD,
                        is_explored=True,
                    )
                )
```

Linhas e colunas multiplas de 4 sao vias e ja nascem exploradas. Os demais lotes passam por `pick_sector`, que decide pela distancia ao centro:

```python
    if dist_center_x < width * 0.2 and dist_center_y < height * 0.2:
        sector = SectorType.COMMERCIAL
    elif dist_center_x > width * 0.38 or dist_center_y > height * 0.38:
        sector = SectorType.FOREST
    else:
        sector = SectorType.RESIDENTIAL
```

### Limites de tamanho

```python
    limits = range(balance.MIN_WORLD_SIZE, balance.MAX_WORLD_SIZE + 1)
    if width not in limits or height not in limits:
```

Mapas fora de 8 a 40 celulas sao recusados com `GameError`, para impedir que um pedido enorme trave o servidor.

## O que mudou

- **A floresta nunca aparecia.** O limite original era `0.45`. Em um mapa 20x20 a distancia maxima de um lote ate o centro e 9, e `9 > 20 * 0.45` e falso, entao nenhum lote virava floresta, nem as arvores nem a regra de floresta existiam na pratica. O limite foi para `0.38`, e o teste `test_default_world_has_every_sector_type` impede a regressao.
- **O sorteio usa `random.Random` recebido.** Antes usava o modulo global `random`; agora o gerador vem de fora, o que torna o mapa reproduzivel por semente.

## Por que assim

- **Mundo gerado so uma vez, construcoes depois.** Gerar 400 construcoes de uma vez custaria tempo e dados que o jogador talvez nunca veja. O mapa so reserva o identificador; a construcao nasce na primeira visita (ver [building_service](building_service.md)).
