# CellPanel

Arquivo: `src/components/CellPanel.tsx`.

## O que e

O painel da aba "Location": o que se sabe do lote selecionado e o que o jogador pode fazer ali. Muda conforme a fase da partida.

## Como foi feito

### Espelhos do backend

```tsx
/** Celulas percorridas por hora; espelha `TILES_PER_HOUR` do backend. */
const TILES_PER_HOUR = 3;

/** Horas de busca no local; espelha `SEARCH_HOURS` do backend. */
const SEARCH_HOURS = 1;
```

O painel mostra o tempo da viagem **antes** de enviar o pedido, e para isso reproduz a formula do servidor ([expedition_service](../../../backend/docs/services/expedition_service.md)):

```tsx
        const distance = Math.abs(game.base_cell.x - x) + Math.abs(game.base_cell.y - y);
        eta = 2 * Math.max(1, Math.ceil(distance / TILES_PER_HOUR)) + SEARCH_HOURS;
```

Se a regra mudar no backend, estas constantes precisam acompanhar; por isso cada uma cita a original.

### Fase de preparacao: escolher o abrigo

```tsx
            {game.status === 'setup' && canBeShelter && (
                <button
                    disabled={busy}
                    onClick={() => void claimBase(selectedCell.building_id!)}
```

Antes de o jogo comecar, selecionar um lote mostra o botao "Make this my shelter". Florestas mostram um aviso em vermelho, porque nao servem de abrigo.

### Durante a partida: expedicao

```tsx
    const candidates = game.survivors.filter(
        (s) => s.status === 'home' && s.needs.health >= MIN_EXPEDITION_HEALTH,
    );
    const survivorId = candidates.some((s) => s.id === chosen) ? chosen : candidates[0]?.id ?? '';
```

Apenas quem esta no abrigo e tem saude de pelo menos 25 aparece na lista. A escolha do jogador fica em `chosen`; se essa pessoa deixar de ser candidata (saiu em outra expedicao, por exemplo), o seletor volta ao primeiro da lista, em vez de enviar alguem invalido.

```tsx
                                Scavenge here ({eta}h round trip)
```

O botao mostra a duracao da ida e volta. Se ja ha uma expedicao para aquele lote, o painel mostra "X is on the way (N h left)" no lugar do botao.

### O que se sabe do lote

```tsx
                    {selectedBuilding.searched && (
                        <p className="text-xs text-gray-300">
                            Left to loot:{' '}
```

Ate a primeira expedicao so se conhece o numero de comodos e aberturas. Depois dela, aparece a pilhagem que sobrou, o que ajuda a decidir se vale voltar. Isso e coerente com o backend, que esconde a pilhagem de lotes nao vasculhados ([schemas](../../../backend/docs/api/schemas.md)).

## Por que assim

- **Um painel, tres situacoes.** Escolher abrigo, enviar coletor e ver o abrigo sao a mesma pergunta ("o que faco com este lote?"); concentrar tudo em um painel evita que o jogador procure a acao em varios lugares.
- **O `!` em `building_id!`.** Nesse ponto o codigo ja retornou cedo se `building_id` fosse `null`, entao a asserção e segura; evita repetir a checagem em cada botao.
