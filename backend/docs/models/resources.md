# resources.py

Arquivo: `app/models/resources.py`.

## O que e

`Resources` representa uma quantidade de cada recurso: comida, agua, madeira, sucata, remedios e municao. E usado em tres papeis: o estoque do abrigo, a pilhagem restante de uma construcao e o que uma expedicao traz de volta.

## Como foi feito

Os campos:

```python
class Resources(BaseModel):
    food: int = 0
    water: int = 0
    wood: int = 0
    scrap: int = 0
    medicine: int = 0
    ammo: int = 0
```

Quatro metodos operam sobre qualquer combinacao de recursos sem precisar citar cada campo. Eles iteram sobre `model_dump()`:

```python
    def add(self, other: "Resources") -> None:
        for name, value in other.model_dump().items():
            setattr(self, name, getattr(self, name) + value)
```

```python
    def subtract(self, other: "Resources") -> None:
        for name, value in other.model_dump().items():
            setattr(self, name, max(0, getattr(self, name) - value))
```

`subtract` nunca deixa o valor ficar negativo (`max(0, ...)`). `covers` diz se um estoque paga um custo, e `describe` monta o texto usado no diario:

```python
        parts = [f"{name} {value}" for name, value in self.model_dump().items() if value]
        return ", ".join(parts) if parts else "nothing"
```

Assim o diario mostra `Olivia returned with food 4, water 2, wood 1` e nunca lista recursos zerados.

## Por que assim

- **Um modelo para tres usos.** Estoque, pilhagem e carga de expedicao tem o mesmo formato; reaproveitar o modelo evita conversoes. Em [expedition_service](../services/expedition_service.md), `building.loot.subtract(taken)` e `state.resources.add(taken)` movem a carga de um lado ao outro com as mesmas duas chamadas.
- **Sem acesso por nome de campo nas operacoes.** Acrescentar um recurso novo (por exemplo, combustivel) exige apenas um campo novo; `add`, `subtract`, `covers` e `describe` continuam corretos.
- **`subtract` satura em zero.** O jogo nunca guarda quantidade negativa; as regras que precisam impedir gasto sem estoque verificam antes (por exemplo, `if state.resources.wood < balance.BARRICADE_WOOD_COST`).
