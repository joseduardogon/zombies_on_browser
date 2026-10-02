# Modulo types

Arquivo: `src/types/game.ts`.

## O que e

Os tipos TypeScript que espelham as respostas do backend. Sao a "tradução" dos modelos Pydantic ([models](../../../backend/docs/models/README.md)).

## Como foi feito

### Unioes em vez de enums

```ts
/** Fase da partida. */
export type GameStatus = 'setup' | 'playing' | 'won' | 'lost';

/** Funcao de um sobrevivente. */
export type SurvivorRole = 'leader' | 'scavenger' | 'builder' | 'guard' | 'idle';
```

O `tsconfig` ativa `erasableSyntaxOnly`, que proibe `enum` do TypeScript. Unioes de strings sao apagadas na compilacao e casam exatamente com os valores que o backend envia (`"playing"`, `"guard"`).

### Recursos

```ts
export const RESOURCE_KEYS = ['food', 'water', 'wood', 'scrap', 'medicine', 'ammo'] as const;

/** Nome de um recurso. */
export type ResourceKey = (typeof RESOURCE_KEYS)[number];

/** Estoque de recursos. */
export type Resources = Record<ResourceKey, number>;
```

A lista existe como constante para a interface poder **iterar** os recursos (barra superior, pilhagem restante) e, a partir dela, o tipo `ResourceKey` e derivado. Acrescentar um recurso e mudar uma linha.

### A resposta principal

```ts
export interface GameView {
    id: string;
    seed: number;
    status: GameStatus;
    clock: Clock;
    target_day: number;
    world: WorldMap;
    survivors: Survivor[];
    resources: Resources;
    base_building: Building | null;
    base_cell: Coordinates | null;
    expeditions: Expedition[];
    siege: Siege;
    log: LogEntry[];
    total_zombies_killed: number;
}
```

E identica ao `GameView` de [schemas](../../../backend/docs/api/schemas.md). Todas as acoes do jogador a devolvem.

## Por que assim

- **Nomes iguais aos do servidor.** Os campos mantem o `snake_case` do JSON (`sector_type`, `is_explored`). Converter para `camelCase` exigiria um passo de mapeamento a cada resposta, e uma chance de erro a cada campo novo.
- **Um arquivo so.** O dominio e pequeno e os tipos se referenciam uns aos outros; dividir em muitos arquivos aumentaria os imports sem ganhar clareza.
