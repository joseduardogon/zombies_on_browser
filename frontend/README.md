# Zombies on Browser - Frontend

Interface do jogo de sobrevivencia zumbi para navegador, inspirado em Infection Free Zone. Feita com React 19, TypeScript, Vite, Tailwind CSS 4 e Zustand.

## Requisitos

- Node.js 20 ou superior
- Backend em execucao em `http://127.0.0.1:8000` (o Vite faz proxy de `/api`)

## Execucao

```bash
npm install
npm run dev
```

Outros scripts: `npm run build`, `npm run lint`, `npm run preview`.

## Estrutura

```
src/
  App.tsx          raiz: carregamento, erro, tela inicial e jogo
  components/      componentes de interface
  hooks/           relogio do jogo em tempo real
  store/           estado global (Zustand)
  lib/             cliente HTTP e chamadas tipadas a API
  types/           tipos que espelham o backend
  city-3d.css      estilos do mapa 3D
  index.css        estilos globais e Tailwind
docs/              documentacao por modulo
```

## Documentacao

Cada modulo tem uma subpasta em [docs](docs) com seus arquivos Markdown:

- [app](docs/app/README.md)
- [components](docs/components/README.md)
- [store](docs/store/README.md)
- [hooks](docs/hooks/README.md)
- [lib](docs/lib/README.md)
- [types](docs/types/README.md)
- [styles](docs/styles/README.md)

## Convencoes

- Comentarios no codigo somente no formato JSDoc, equivalente aos docstrings do Google.
- Toda alteracao de modulo atualiza a documentacao correspondente em `docs`.
