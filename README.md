# Zombies on Browser

Jogo de sobrevivência contra zumbis para navegador, inspirado em Infection Free Zone. O jogador comanda um grupo de sobreviventes em uma cidade tomada por zumbis: explora o mapa, vasculha construções, reforça abrigos e tenta resistir.

Este repositório reúne os dois projetos do jogo:

| Pasta | Projeto | Tecnologias |
|-------|---------|-------------|
| [backend](backend) | API e regras do jogo | Python 3.12, FastAPI, Pydantic, Poetry |
| [frontend](frontend) | Interface no navegador | React 19, TypeScript, Vite, Tailwind CSS 4, Zustand |

Cada projeto tem sua própria pasta `docs`, com uma subpasta por módulo.

## Como o jogo funciona

### A ideia

A referência é o estilo de Infection Free Zone: um jogo de gerenciamento e sobrevivência visto de cima, em que o foco não é atirar, e sim administrar recursos, pessoas e defesas. A interface imita um painel de comando ("Commander Interface // Z-CITY"), com visual de terminal verde sobre fundo escuro.

O loop pretendido é:

1. O jogador vê a cidade em um mapa isométrico.
2. Escolhe uma construção e entra nela para ver a planta.
3. Sobreviventes saem para coletar recursos, reforçam as aberturas (portas e janelas) e montam a defesa do abrigo.
4. Os zumbis atacam as aberturas. Quanto mais frágil a barricada, mais fácil a invasão.
5. Fome, sede, cansaço, moral e saúde dos sobreviventes limitam o que o grupo consegue fazer.

### O mundo

O mapa é uma grade (20x20 por padrão) gerada pelo servidor a cada partida:

- **Vias:** toda linha ou coluna múltipla de 4 vira rua. As ruas já começam exploradas.
- **Setores:** as demais células são lotes, definidos pela distância ao centro.
  - Centro: comercial (prédios altos de vidro).
  - Zona intermediária: residencial.
  - Periferia: floresta.
  - Fora da floresta, cada lote tem 10% de chance de ser industrial.
- **Exploração:** cada célula guarda se já foi explorada e, no futuro, qual construção ela contém.

### As construções

Ao entrar em um lote, o servidor gera uma construção conforme o setor:

| Setor | Resultado | Integridade |
|-------|-----------|-------------|
| Residencial | Casa com sala, cozinha e quarto | 100 |
| Comercial | Loja de salão único com porta de vidro e vitrine | 80 |
| Industrial | Galpão com porta reforçada e uma janela | 90 |
| Floresta | Clareira com uma barraca abandonada | 10 |

Cada construção é formada por cômodos (com dimensões, isolamento e segurança) e cada cômodo tem aberturas: portas e janelas com estado (aberta, fechada, barricada, quebrada) e durabilidade. As aberturas são o centro da mecânica de defesa: é por elas que os zumbis entram.

### Os sobreviventes

O modelo já está definido, mas ainda não é usado pelo jogo. Cada sobrevivente tem:

- **Função:** líder, coletor, construtor, guarda ou ocioso.
- **Necessidades (0 a 100):** fome, sede, cansaço, moral e saúde.
- **Habilidades:** construção, combate, coleta e medicina.
- **Localização** no mapa e **construção** em que está alocado.

## Arquitetura

```
navegador  ->  frontend (Vite, porta 5173)  ->  /api (proxy)  ->  backend (FastAPI, porta 8000)
```

O frontend é só a apresentação: o estado do mundo e das construções é gerado e guardado pelo backend. Em desenvolvimento, o Vite encaminha as chamadas de `/api` para `http://127.0.0.1:8000`, e o backend libera CORS para as portas 5173 e 5174.

### Backend

```
backend/app/
  main.py        aplicação, CORS e registro das rotas
  api/           rotas HTTP (mundo e construções)
  models/        modelos Pydantic (mundo, construção, sobrevivente)
  services/      geração procedural de construções
```

Rotas existentes:

| Método | Caminho | Função |
|--------|---------|--------|
| GET | `/` e `/health` | Status da API |
| POST | `/api/world/generate?width=&height=` | Gera um novo mundo |
| GET | `/api/world/state` | Retorna o mundo atual |
| POST | `/api/building/generate/{tipo}` | Gera uma construção |
| GET | `/api/building/{id}` | Busca uma construção gerada |

### Frontend

```
frontend/src/
  App.tsx                  raiz; gera o mundo ao abrir e trata carregamento e erro
  components/CityMap3D.tsx mapa isométrico em CSS 3D
  components/BuildingView  planta da construção selecionada
  store/gameStore.ts       estado global (Zustand) e chamadas à API
  lib/api.ts               cliente HTTP
  city-3d.css              estilos do mapa 3D
```

O mapa não usa canvas nem WebGL: cada célula é um elemento HTML transformado com CSS 3D, com alturas e cores por setor (comercial 60px, industrial 25px, residencial 16px). Florestas têm árvores e algumas ruas têm um carro animado.

## Estado atual

Funciona hoje:

- Gerar o mundo e exibi-lo em visão isométrica.
- Clicar em uma célula e ver a planta da construção correspondente, com cômodos e aberturas.
- Tratamento de falha de conexão com o servidor.

Ainda não existe:

- Sobreviventes em jogo (só o modelo).
- Passagem de tempo, dia e noite.
- Coleta de recursos, inventário e construção.
- Zumbis e simulação de ataque.
- Persistência: tudo fica em memória e some ao reiniciar o servidor.
- Vínculo entre célula e construção: hoje cada clique gera uma construção nova.
- Arrastar para mover a câmera (o HUD já anuncia como "em breve").
- Testes automatizados.

## Como executar

Em dois terminais, a partir da raiz do repositório:

```bash
cd backend
poetry install
poetry run uvicorn app.main:app --reload --port 8000
```

```bash
cd frontend
npm install
npm run dev
```

Abra `http://localhost:5173`. A documentação interativa da API fica em `http://127.0.0.1:8000/docs`.

## Próximos passos sugeridos

1. Associar `building_id` a cada célula, para que a mesma construção seja reaberta.
2. Criar o relógio do jogo (turnos, dia e noite) no backend.
3. Expor sobreviventes pela API e exibi-los na interface.
4. Implementar coleta, inventário e barricadas.
5. Simular ondas de zumbis atacando as aberturas.
6. Persistir o estado em SQLite e cobrir as regras com testes.

## Convenções

- Comentários no código somente no formato de docstrings do Google (docstrings em Python e JSDoc em TypeScript).
- Cada projeto mantém sua documentação em `docs`, com uma subpasta por módulo e arquivos Markdown.
- Nenhuma mensagem de commit ou arquivo cita ferramentas de IA.
