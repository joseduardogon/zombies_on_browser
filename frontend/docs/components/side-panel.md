# SidePanel

Arquivo: `src/components/SidePanel.tsx`.

## O que e

A coluna da direita, organizada em tres abas: Location ([CellPanel](cell-panel.md)), Shelter ([ShelterPanel](shelter-panel.md)) e Journal ([EventLog](event-log.md)).

## Como foi feito

```tsx
const TABS = [
    { id: 'location', label: 'Location' },
    { id: 'shelter', label: 'Shelter' },
    { id: 'journal', label: 'Journal' },
] as const;

type TabId = (typeof TABS)[number]['id'];
```

`as const` faz o TypeScript tratar os `id` como literais (`'location' | 'shelter' | 'journal'`), e `TabId` e derivado da propria lista. Adicionar uma aba e acrescentar uma linha em `TABS` e uma linha de renderizacao.

```tsx
                {tab === 'location' && <CellPanel />}
                {tab === 'shelter' && <ShelterPanel />}
                {tab === 'journal' && <EventLog />}
```

Apenas a aba ativa e renderizada. O estado da aba e local (`useState`): nao precisa estar no store, porque nada fora do painel se importa com ela.

## Por que assim

- **Abas em vez de tudo empilhado.** O painel tem 320 px de largura; as tres areas juntas exigiriam rolar muito. O jogador alterna sem perder o mapa.
- **Altura propria com rolagem.** O contêiner `flex-1 overflow-y-auto` rola por dentro, e o resto da tela fica fixo.
