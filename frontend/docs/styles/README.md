# Modulo styles

Arquivos: `src/index.css` e `src/city-3d.css`.

- `index.css`: importa o Tailwind (`@import "tailwindcss";`) e define o tema escuro e o reset do `body`.
- `city-3d.css`: tudo o que o mapa isometrico precisa e que o Tailwind nao cobre, como transformacoes 3D e animacoes.

O resto da interface usa classes utilitarias do Tailwind direto no JSX.

## Como o mapa 3D funciona

### Perspectiva e plano

```css
.viewport-3d {
    perspective: 2000px;
    position: relative;
    overflow: hidden;
    width: 100%;
    height: 100%;
```

`perspective` da a profundidade a tudo o que estiver dentro. A area ocupa 100% do contêiner pai, e nao mais `100vw x 100vh` como no prototipo: com a barra superior e os paineis laterais, o mapa tem que caber no espaco que sobra.

```css
.city-plane {
    transform: rotateX(60deg) rotateZ(-45deg);
    transform-style: preserve-3d;
    pointer-events: none;
```

O plano gira 60° em X (inclina) e -45° em Z (vira em diagonal), o que da a visao isometrica. A transformacao do CSS e sobrescrita em linha pelo componente com a camera (`translate` e `scale`, ver [city-map-3d](../components/city-map-3d.md)); o valor aqui e o padrao.

### Pointer events

```css
.city-cell {
    position: relative;
    width: 40px;
    height: 40px;
    transform-style: preserve-3d;
    cursor: pointer;
    pointer-events: auto;
}
```

O plano ignora o mouse (`pointer-events: none`) e so as celulas o recebem (`auto`). Os blocos 3d dentro das celulas tambem ignoram (`.block-3d { pointer-events: none; }`), entao o alvo de todo clique e o elemento `.city-cell`.

Isso corrige um defeito real encontrado ao testar no navegador: o fundo do plano e a base de cada celula ficam na mesma profundidade, e o navegador escolhia entre eles sem criterio estavel. Os cliques "caiam" no plano e nenhum lote era selecionado.

### Caixas 3D

Cada construcao e uma caixa com topo e duas laterais, controlada por variaveis CSS:

```css
.face-top {
    transform: translateZ(var(--height, 0px));
    background: var(--color-top);
    box-shadow: inset 0 0 10px rgba(0, 0, 0, 0.2);
}
```

Cada setor define a sua altura e as suas cores:

```css
.type-commercial {
    --height: 60px;
    --color-top: #e0f2fe;
    --color-side: #0ea5e9;
    --color-side-dark: #0284c7;
}
```

Alturas: residencial 16px, industrial 25px, comercial 60px, via 1px. Predios comerciais altos no centro e casas baixas em volta dao a leitura de cidade sem nenhuma imagem.

## Estados do jogo no mapa

As classes abaixo sao adicionadas pelo componente conforme o estado da partida.

```css
.city-cell.is-explored .face-side-1,
.city-cell.is-explored .face-side-2 {
    filter: saturate(0.35) brightness(0.7);
}
```

Lotes ja vasculhados ficam dessaturados e escuros: o jogador ve de relance onde ainda ha o que coletar.

```css
.city-cell.is-base .face-top {
    box-shadow: inset 0 0 0 4px #38bdf8, 0 0 18px #38bdf8;
}

.city-cell.is-selected .face-top {
    box-shadow: inset 0 0 0 4px #facc15;
}
```

Abrigo em azul brilhante e selecao em amarelo, ambos so na face de cima, para nao alterar a geometria.

```css
.city-cell.is-target .face-top {
    animation: target-pulse 1s ease-in-out infinite alternate;
}
```

Lotes que sao destino de uma expedicao pulsam em laranja.

## O que mudou

- Os comentarios do arquivo foram removidos (a regra do projeto permite apenas docstrings), e esta pagina passou a explicar o que eles diziam.
- Removidos a transicao de `transform` do plano e o `:hover` que subia a celula; ambos mexiam na geometria sob o cursor.
- O `App.css` do template do Vite, que nao era importado em lugar nenhum, foi apagado.
