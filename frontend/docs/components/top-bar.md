# TopBar

Arquivo: `src/components/TopBar.tsx`.

## O que e

A barra superior: dia e hora, controle do tempo, recursos e o menu de salvamento.

## Como foi feito

### Dia e hora

```tsx
    const hour = String(game.clock.hour).padStart(2, '0');
    const night = game.clock.phase === 'night';
```

```tsx
                <span className={night ? 'text-indigo-300' : 'text-yellow-300'}>
                    {hour}:00 {night ? 'NIGHT' : 'DAY'}
                </span>
```

A fase vem pronta do servidor (`clock.phase`), entao o cliente nao repete a regra "noite entre 20h e 6h". A cor muda: amarelo de dia, anil de noite.

### Velocidade

```tsx
const SPEEDS: { value: Speed; label: string }[] = [
    { value: 0, label: 'Pause' },
    { value: 1, label: '1x' },
    { value: 2, label: '2x' },
    { value: 4, label: '4x' },
];
```

Os botoes alteram `speed` no store, e o hook [useGameClock](../hooks/README.md) faz o resto. O botao "+6h" pede seis horas de uma vez (`tick(6)`), util para esperar uma expedicao longa ou o amanhecer.

Os controles de tempo so existem durante a fase `playing`: antes do abrigo ou depois do fim, nao ha o que avancar.

### Recursos

```tsx
                    RESOURCE_KEYS.map((key) => (
                        <span key={key} className={`${RESOURCE_COLORS[key]} whitespace-nowrap`} title={key}>
                            {key} <b className="tabular-nums">{game.resources[key]}</b>
                        </span>
```

Os seis recursos sao desenhados a partir de `RESOURCE_KEYS` ([types](../types/README.md)), cada um com sua cor. `tabular-nums` usa digitos de largura fixa para a barra nao tremer quando um numero muda.

### Menu

```tsx
                        <button
                            onClick={() => {
                                void saveGame('manual');
                                setMenuOpen(false);
                            }}
```

"Save game" grava no espaco `manual`; cada save existente vira um item "Load"; "New game" recria a partida com o mesmo tamanho de mapa. O menu fecha ao escolher.

## Por que assim

- **O autosave e invisivel.** O servidor grava a cada acao ([game_manager](../../../backend/docs/services/game_manager.md)); o espaco `manual` existe para o jogador marcar um ponto ao qual queira voltar.
- **O texto do titulo foi corrigido** de "INTEFACE" para "INTERFACE".
