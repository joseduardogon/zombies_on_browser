# CityMap3D

Arquivo: `src/components/CityMap3D.tsx`. Estilos em `src/city-3d.css` (ver [styles](../styles/README.md)).

## O que e

O mapa da cidade em visao isometrica, feito com elementos HTML e transformacoes CSS 3D, sem canvas. Agora tem camera arrastavel, zoom, destaque do abrigo e selecao de lotes.

## Como foi feito

### A camera

```tsx
    const [offset, setOffset] = useState({ x: 0, y: 0 });
    const [zoom, setZoom] = useState(1);
```

A camera e a combinacao de um deslocamento e um zoom, aplicados na propria transformacao do plano da cidade:

```tsx
                    transform: `translate(${offset.x}px, ${offset.y}px) scale(${zoom}) rotateX(60deg) rotateZ(-45deg)`,
```

A ordem importa: `translate` e `scale` vem **antes** das rotacoes, entao o arrasto segue a tela e nao os eixos inclinados do mapa.

### Arrastar sem perder o clique

```tsx
        const onMove = (move: PointerEvent) => {
            const dx = move.clientX - startX;
            const dy = move.clientY - startY;
            if (Math.hypot(dx, dy) > DRAG_THRESHOLD) dragged.current = true;
            if (dragged.current) setOffset({ x: origin.x + dx, y: origin.y + dy });
        };
```

O movimento so conta como arrasto se passar de 5 pixels (`DRAG_THRESHOLD`). Abaixo disso, e um clique. A bandeira fica em um `useRef`, e nao em estado, porque ela e lida no momento do clique e nao deve provocar um novo desenho:

```tsx
            if (dragged.current) return;
            void selectCell(cell.building_id ? cell : null);
```

Se o gesto foi um arrasto, o clique que o navegador dispara ao soltar o mouse e ignorado. Os ouvintes `pointermove` e `pointerup` sao registrados na `window`, e nao no mapa, para o arrasto continuar mesmo que o cursor saia da area.

### Zoom

```tsx
        const factor = event.deltaY < 0 ? 1.1 : 0.9;
        setZoom((z) => Math.min(MAX_ZOOM, Math.max(MIN_ZOOM, z * factor)));
```

Cada rolagem multiplica o zoom por 1,1 ou 0,9, limitado entre 0,4 e 2,5.

### Marcadores por celula

```tsx
    const classes = [
        'city-cell',
        `type-${cell.sector_type}`,
        cell.is_explored && cell.sector_type !== 'road' ? 'is-explored' : '',
        isBase ? 'is-base' : '',
        isSelected ? 'is-selected' : '',
        isTarget ? 'is-target' : '',
    ]
```

Cada estado vira uma classe CSS: lotes explorados escurecem, o abrigo brilha em azul, o selecionado tem moldura amarela e os alvos de expedicao pulsam em laranja.

### Desempenho

```tsx
const MapCell = memo(({ cell, isBase, isSelected, isTarget, onSelect }: MapCellProps) => {
```

```tsx
const sameCell = (prev: MapCellProps, next: MapCellProps): boolean =>
    prev.cell.coordinates.x === next.cell.coordinates.x &&
```

O mapa tem 400 celulas e a cada hora de jogo chega um `GameView` novo, com objetos novos para todas elas. `memo` com uma funcao de comparacao propria redesenha apenas as celulas cujo desenho realmente mudaria (explorada, base, selecionada ou alvo). Sem isso, em 4x o mapa inteiro seria refeito quase tres vezes por segundo.

## O que mudou

- Antes, qualquer clique gerava uma construcao nova; agora `selectCell` seleciona a construcao fixa do lote.
- A frase "Drag to Pan (Coming Soon)" virou realidade.
- O componente deixou de ler `world` do estado antigo e usa seletores especificos (`useGameStore((s) => s.game?.world)`), que reduzem redesenhos.

## Por que assim

- **`pointer-events: none` no plano.** Em testes no navegador, o clique real caia no plano e nao na celula: o fundo do plano e a base da celula ficam na mesma profundidade e o navegador escolhia um dos dois sem criterio. Desligar os eventos do plano e religa-los so nas celulas (veja [styles](../styles/README.md)) resolveu.
- **Sem animacao de elevar a celula ao passar o mouse.** A versao original subia a celula 5 px no `:hover`. Isso foi trocado por um contorno, porque mover a geometria sob o cursor entre o `mousedown` e o `mouseup` pode mudar o alvo do clique. A causa comprovada do clique perdido foi a descrita no item anterior; o contorno e uma precaucao a mais, ja que nao desloca nada.
