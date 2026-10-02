# Modulo store

Arquivo: `src/store/gameStore.ts`. Estado global com Zustand, exposto pelo hook `useGameStore`.

## O que e

Guarda o que a interface precisa saber e concentra todas as acoes que falam com o servidor.

## Como foi feito

### O estado

```ts
interface GameStore {
    game: GameView | null;
    loaded: boolean;
    busy: boolean;
    fatalError: string | null;
    notice: Notice | null;
    speed: Speed;
    selectedCell: WorldCell | null;
    selectedBuilding: Building | null;
    saves: SaveInfo[];
```

- `game` e a verdade: a ultima resposta do servidor. A interface nunca calcula estado do jogo, so o exibe.
- `busy` impede duas acoes ao mesmo tempo (um tick e um clique em "Reinforce" simultaneos).
- `fatalError` e falha de conexao; `notice` e um aviso de regra ("Not enough wood").
- `speed` e a velocidade do relogio: `0 | 1 | 2 | 4`.

### `run`: o caminho unico das acoes

```ts
    const run = async (action: () => Promise<GameView>): Promise<boolean> => {
        set({ busy: true });
        try {
            applyGame(await action());
            set({ busy: false, fatalError: null });
            return true;
        } catch (err) {
            if (err instanceof ApiError && err.status === 0) {
                set({ busy: false, fatalError: err.message, speed: 0 });
            } else {
                set({ busy: false, notice: { kind: 'error', message: messageOf(err) } });
            }
            return false;
        }
    };
```

Toda acao que devolve uma partida passa por aqui: marca `busy`, aplica a resposta e trata o erro. Falha de rede vira erro fatal e **pausa o relogio** (`speed: 0`), para nao disparar centenas de ticks falhos; falha de regra vira um aviso.

### `applyGame`: manter a selecao coerente

```ts
        set({
            game,
            selectedCell: fresh,
            speed: game.status === 'playing' ? get().speed : 0,
        });
        if (fresh?.building_id && selectedBuilding && !selectedBuilding.searched && fresh.is_explored) {
            void get().selectCell(fresh);
        }
```

Cada resposta traz um mapa novo, entao a celula selecionada e substituida pela versao atual. Se ela acabou de ser explorada por uma expedicao, a construcao e consultada de novo para mostrar a pilhagem que sobrou. Quando a partida termina, a velocidade volta a 0.

### Selecionar uma celula

```ts
        selectCell: async (cell) => {
            set({ selectedCell: cell, selectedBuilding: null });
            if (!cell?.building_id) return;
            try {
                const building = await gameApi.getBuilding(cell.building_id);
                if (get().selectedCell?.building_id === cell.building_id) {
                    set({ selectedBuilding: building });
                }
```

A construcao e buscada sob demanda. A checagem seguinte descarta a resposta se o jogador ja clicou em outra celula enquanto esperava: sem ela, uma resposta lenta poderia sobrescrever a selecao mais nova.

### Tick e velocidade

```ts
        tick: async (hours) => {
            if (get().busy) return;
            await run(() => gameApi.tick(hours));
        },
```

Se uma acao esta em curso, o tick e **pulado**, e nao enfileirado. Em velocidades altas isso mantem o relogio sincronizado com o servidor em vez de acumular pedidos.

## Por que assim

- **O servidor e a unica fonte da verdade.** O store troca `game` inteiro a cada resposta; nao ha logica duplicada, e um bug de regra se corrige so no backend.
- **`get()` dentro das acoes.** Garante ler o estado mais recente depois de um `await`, em vez de uma copia velha capturada antes.
- **Antes**, o store tinha apenas `generateWorld`, `fetchWorldState` e `fetchBuilding`; todos foram substituidos, porque o prototipo gerava dados soltos.
