# building_service.py

Arquivo: `app/services/building_service.py`.

## O que e

Duas responsabilidades pequenas: entregar uma construcao (criando-a na primeira vez) e calcular a integridade do abrigo.

## Como foi feito

### Geracao sob demanda

```python
    if building_id in state.buildings:
        return state.buildings[building_id]

    cell = state.cell_for_building(building_id)
    rng = random.Random(f"{state.seed}:building:{building_id}")
    building = BuildingGenerator.generate(cell.sector_type.value, building_id, rng)
    state.buildings[building_id] = building
    return building
```

1. Se a construcao ja existe em `state.buildings`, devolve a mesma.
2. Senao, descobre o setor da celula e gera.
3. O gerador aleatorio e semeado com `semente:building:identificador`, e **nao** com `state.rng(...)`.

### Por que a semente nao usa o contador

`state.rng` incrementa `rng_counter`, entao o resultado dependeria de quantos sorteios aconteceram antes. Se o jogador visitasse a casa A antes da casa B, ou o contrario, cada casa sairia diferente. Com a semente derivada so do identificador, a casa `b-13-5` e sempre a mesma, em qualquer ordem de visita. O teste `test_building_is_generated_once_and_deterministically` verifica isso gerando em uma partida clonada.

### Integridade

```python
    ratios = [
        0.0 if a.state == ApertureState.BROKEN else min(a.health, balance.FORTIFIED_HEALTH)
        / balance.FORTIFIED_HEALTH
        for a in apertures
    ]
    building.overall_integrity = round(100 * sum(ratios) / len(ratios))
```

Cada abertura vale de 0 a 1: quebrada vale zero; as demais valem `saude / 150`, com teto em 1. A integridade e a media em porcentagem. Sem aberturas, a integridade e 0.

### Busca de abertura

`find_aperture` percorre os comodos e devolve `(comodo, abertura)` ou `None`. E usada por [base_service](base_service.md).

## Por que assim

- **`FORTIFIED_HEALTH = 150`.** Uma porta de casa comeca com 100 (66%) e uma janela com 50 (33%). Cada reforco soma de 28 a 100 pontos (conforme a habilidade de construcao), entao algumas rodadas levam as aberturas a 100%. Isso da ao jogador uma meta visivel: encher a barra de integridade antes da noite.
- **Quebrada vale zero mesmo com saude positiva.** Uma abertura quebrada e uma entrada livre, entao a integridade deve cair a pique, nao uma fracao.
