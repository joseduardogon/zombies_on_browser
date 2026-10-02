# building_generator.py

Arquivo: `app/services/building_generator.py`.

## O que e

Fabrica de construcoes. Cada tipo de setor gera uma planta propria, com sua pilhagem e a chance de abrigar um sobrevivente isolado.

## Como foi feito

### Pilhagem por tipo

```python
LOOT_RANGES: dict[str, dict[str, tuple[int, int]]] = {
    "residential": {
        "food": (2, 6),
        "water": (2, 5),
        "wood": (0, 3),
        "scrap": (0, 2),
        "medicine": (0, 2),
        "ammo": (0, 3),
    },
```

A tabela tem uma entrada por tipo de construcao. A ideia: casas dao comida e agua, lojas dao mais comida e remedios, fabricas dao sucata e madeira, florestas dao madeira e agua. `roll_loot` sorteia dentro de cada faixa:

```python
    return Resources(
        **{name: rng.randint(low, high) for name, (low, high) in LOOT_RANGES[kind].items()}
    )
```

### Comodos com identificadores previsiveis

```python
        self._rooms += 1
        room_id = f"{self.building_id}_r{self._rooms}"
```

```python
        return Aperture(
            id=f"{room_id}_a{index}",
```

Um comodo se chama `b-13-5_r1`; sua primeira abertura, `b-13-5_r1_a1`. Antes os identificadores eram UUIDs aleatorios, o que impedia gerar a mesma construcao duas vezes igual. Agora, dada a semente, o resultado e identico.

### Variacao de casas

```python
        if rng.random() < 0.5:
            rooms.append(
                factory.room(
                    "Guest Bedroom", RoomType.BEDROOM, (3, 4),
                    [("window", 40)], insulation=55, security=25,
                )
            )
```

Cada casa pode ter um quarto de hospedes (50%) e uma garagem (40%). Mais comodos significam mais aberturas, e portanto um abrigo mais dificil de defender, mas tambem mais espaco para o grupo.

### Ponto unico de entrada

```python
        return generators.get(kind, BuildingGenerator.generate_residential)(building_id, rng)
```

`BuildingGenerator.generate(kind, id, rng)` escolhe o gerador pelo nome e cai em casa residencial para tipos desconhecidos, mantendo o comportamento da rota original.

## O que mudou

- Os geradores recebem `rng` e usam `_RoomFactory`, que elimina a repeticao de `Room(...)` e `Aperture(...)` do codigo anterior.
- `_finish` monta a construcao com `loot` e `survivor_present`, sorteado com `balance.SURVIVOR_CHANCE`.
- A loja ganhou um deposito e uma segunda vitrine, e a fabrica ganhou um deposito de pecas.

## Por que assim

- **Aberturas sao o coracao da defesa.** Cada tipo tem durabilidades diferentes de proposito: uma vitrine de loja (`20`) e fraca, uma porta de galpao (`200`) e forte. O jogador escolhe um abrigo pesando espaco, pilhagem e quantos pontos fracos precisara reforcar.
