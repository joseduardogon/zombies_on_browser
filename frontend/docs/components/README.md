# Modulo components

Pasta: `src/components/`. Componentes de interface. Todos leem o estado do [store](../store/README.md) e disparam suas acoes; nenhum guarda regra de jogo.

| Arquivo | Documento | Papel |
|---------|-----------|-------|
| `StartScreen.tsx` | [start-screen](start-screen.md) | Nova partida e saves |
| `TopBar.tsx` | [top-bar](top-bar.md) | Dia, hora, velocidade, recursos, menu |
| `CityMap3D.tsx` | [city-map-3d](city-map-3d.md) | Mapa isometrico com camera |
| `SurvivorsPanel.tsx` | [survivors-panel](survivors-panel.md) | Cartoes dos sobreviventes |
| `SidePanel.tsx` | [side-panel](side-panel.md) | Abas Location, Shelter e Journal |
| `CellPanel.tsx` | [cell-panel](cell-panel.md) | Local selecionado, escolha do abrigo, expedicao |
| `ShelterPanel.tsx` | [shelter-panel](shelter-panel.md) | Comodos e reforco das aberturas |
| `EventLog.tsx` | [event-log](event-log.md) | Diario de eventos |
| `Overlays.tsx` | [overlays](overlays.md) | Cerco, noite, avisos, fim de jogo |
| `ui/Bar.tsx` | [bar](bar.md) | Barra de progresso reutilizavel |

## Removido

`BuildingView.tsx`, o painel de tela cheia do prototipo que mostrava a planta de uma construcao gerada ao acaso. A planta do abrigo agora esta em [shelter-panel](shelter-panel.md), e um resumo de qualquer construcao, em [cell-panel](cell-panel.md).

## Convencao de espelho

Tres componentes repetem constantes do backend que o cliente precisa para mostrar numeros antes de pedir ao servidor: `TILES_PER_HOUR`, `SEARCH_HOURS` e `MIN_EXPEDITION_HEALTH` em `CellPanel`, e `WOOD_COST` e `HEALTH_CAP` em `ShelterPanel`. Cada uma tem um comentario de documentacao dizendo qual constante do backend espelha. O servidor continua sendo quem decide; esses valores so evitam mostrar um botao habilitado que o servidor recusaria.
