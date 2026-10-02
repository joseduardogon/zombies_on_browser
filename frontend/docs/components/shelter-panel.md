# ShelterPanel

Arquivo: `src/components/ShelterPanel.tsx`.

## O que e

A aba "Shelter": a planta do abrigo, comodo por comodo, com a saude de cada porta e janela e o botao para reforca-las. E onde o jogador prepara a defesa para a noite.

## Como foi feito

### Integridade geral

```tsx
                <Bar label="Integrity" value={base.overall_integrity} color="bg-sky-500" />
```

A barra no topo e a `overall_integrity` calculada pelo servidor, a media da saude das aberturas ([building_service](../../../backend/docs/services/building_service.md)). E o numero a ser levado para perto de 100 antes de anoitecer.

### Quem trabalha

```tsx
    const workers = game.survivors.filter((s) => s.status === 'home');
    const workerId = workers.some((s) => s.id === chosen) ? chosen : workers[0]?.id ?? '';
    const canAfford = game.resources.wood >= WOOD_COST;
```

O seletor lista quem esta no abrigo e mostra a habilidade de construcao de cada um, porque ela define quanto cada reforco rende. Como no [CellPanel](cell-panel.md), se a escolha deixa de valer, o seletor volta ao primeiro.

### Cada abertura

```tsx
                                    disabled={
                                        busy ||
                                        !workerId ||
                                        !canAfford ||
                                        aperture.health >= HEALTH_CAP
                                    }
```

O botao fica desabilitado quando nao ha trabalhador, madeira (2 unidades) ou a abertura ja esta no teto de 300. O texto muda conforme o estado:

```tsx
                                    {aperture.state === 'broken' ? 'Repair' : 'Reinforce'} ({WOOD_COST} wood)
```

Uma abertura quebrada oferece "Repair"; as demais, "Reinforce". No servidor sao a mesma acao ([base_service](../../../backend/docs/services/base_service.md)).

```tsx
                            <Bar
                                label="HP"
                                value={aperture.health}
                                max={HEALTH_CAP}
                                color={aperture.state === 'broken' ? 'bg-red-600' : 'bg-green-500'}
                            />
```

A barra de cada abertura usa o teto de 300 como maximo, entao uma porta de 100 aparece com um terco cheio: o jogador ve quanto ainda pode reforcar. Ficam vermelhas quando quebradas.

## Por que assim

- **Mostrar todas as aberturas de uma vez.** Os zumbis atacam a mais fraca, entao o jogador precisa **ver** qual e. As barras lado a lado respondem isso sem calculo.
- **Estados com cor.** `open` (amarelo) e `broken` (vermelho) chamam atencao; `barricaded` (verde) tranquiliza.
