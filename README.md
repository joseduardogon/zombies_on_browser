# Zombies on Browser

Jogo de sobrevivência contra zumbis para navegador, inspirado em Infection Free Zone. O jogador comanda um grupo de sobreviventes em uma cidade tomada por zumbis: escolhe um abrigo, vasculha construções atrás de suprimentos, reforça portas e janelas e tenta resistir por 30 dias.

Este repositório reúne os dois projetos do jogo:

| Pasta | Projeto | Tecnologias |
|-------|---------|-------------|
| [backend](backend) | API e regras do jogo | Python 3.12, FastAPI, Pydantic, SQLite, Poetry |
| [frontend](frontend) | Interface no navegador | React 19, TypeScript, Vite, Tailwind CSS 4, Zustand |

Cada projeto tem sua própria pasta `docs`, com uma subpasta por módulo e arquivos Markdown que explicam o que foi feito, como e por quê, citando o código.

## Como o jogo funciona

### Objetivo

Sobreviver até o fim do dia 30. O jogo termina em derrota se todos os sobreviventes morrem. A interface imita um painel de comando ("Commander Interface // Z-City"), com visual de terminal verde sobre fundo escuro.

### Fluxo de uma partida

1. **Nova partida.** O jogador escolhe o tamanho do mapa e, se quiser, uma semente. A mesma semente gera o mesmo mapa.
2. **Escolha do abrigo.** O mapa aparece em visão isométrica. O jogador seleciona uma casa, loja ou fábrica e a transforma em abrigo. A escolha importa: cada tipo tem número de comodos, aberturas e durabilidade diferentes.
3. **Grupo inicial.** Nascem três sobreviventes (um líder, um guarda e um coletor) e um estoque de comida, água, madeira, sucata, remédios e munição.
4. **Passagem do tempo.** O relógio avança uma hora de jogo a cada 1,5 s reais (pausa, 1x, 2x ou 4x). Cada hora desgasta os sobreviventes e pode disparar eventos.
5. **Dia: preparar e coletar.** O jogador envia sobreviventes em expedições, reforça aberturas com madeira, trata feridos e distribui funções.
6. **Noite: resistir.** Às 20h chega uma onda de zumbis que cerca o abrigo até as 6h.
7. **Fim.** Vitória ao chegar ao dia 31 (30 dias vividos); derrota se todos morrerem.

### O mundo

O mapa é uma grade gerada pelo servidor (20x20 por padrão, de 8 a 40):

- **Vias:** toda linha ou coluna múltipla de 4. Já começam exploradas.
- **Setores:** os demais lotes são definidos pela distância ao centro: comercial no centro, residencial na zona intermediária e floresta na periferia. Fora da floresta, 10% dos lotes viram industriais.
- **Construções:** cada lote tem uma construção fixa, gerada na primeira vez que alguém olha para ela. Casas têm sala, cozinha, quartos e talvez garagem; lojas têm salão e depósito; fábricas têm galpão e depósito; florestas têm uma clareira e uma barraca.

### Sobreviventes

Cada um tem:

- **Necessidades (0 a 100):** saúde, fome, sede, energia e moral. Comer e beber é automático quando há estoque.
- **Habilidades:** construção, combate, coleta e medicina. Sobem com o uso.
- **Função:** líder, coletor, construtor, guarda ou ocioso. A função muda o que a pessoa faz melhor: guardas defendem à noite, construtores reforçam 50% mais, coletores trazem mais.
- **Situação:** no abrigo, em expedição ou morto.

Guardas vigiam à noite e dormem de dia. Quem está com energia ou moral abaixo de 20 rende metade. Sobreviventes isolados podem ser encontrados nas construções e se juntar ao grupo (até 12).

### Expedições

Um sobrevivente sai, viaja até uma construção (3 células por hora), vasculha por uma hora e volta. A viagem é de ida e volta. Ao voltar, traz uma fração da pilhagem do local, maior com mais habilidade de coleta. O que sobra fica lá para uma próxima visita. Há risco de encontrar zumbis: depende do setor, sobe à noite e pode ferir ou matar. Enquanto está fora, a pessoa não defende o abrigo.

### Defesa

Cada porta e janela do abrigo tem durabilidade. O jogador gasta 2 madeiras para reforçá-la (até 300 pontos), e uma abertura quebrada pode ser consertada do mesmo jeito. A integridade do abrigo é a média da saúde das aberturas.

### A noite

- A onda do dia cresce com o tempo (cerca de 5 zumbis no dia 1 e 70 no dia 30) e chega em oito rodadas, das 22h às 5h.
- Os guardas aptos atiram: cada um abate `1 + combate / 2` zumbis por rodada, mais 2 se gastar uma munição.
- Os zumbis que sobram batem na **abertura mais fraca**. Se ela quebra, eles entram, ferem sobreviventes e derrubam a moral.
- Ao amanhecer, quem restou recua.

O desafio é equilibrar suprimentos, madeira, munição e gente: cada pessoa fora coletando é uma a menos defendendo.

## Arquitetura

```
navegador  ->  frontend (Vite, porta 5173)  ->  /api (proxy)  ->  backend (FastAPI, porta 8000)
                                                                       |
                                                                  SQLite (autosave)
```

O frontend só exibe e pede ações. **Toda regra roda no servidor**, que também decide o que acontece a cada hora. O relógio do frontend apenas pede "avance 1 hora" em intervalos, então o jogo é igual em qualquer velocidade. Cada ação devolve a partida inteira atualizada, e a interface troca seu estado por ela.

A partida é salva automaticamente a cada ação e retomada ao reiniciar o servidor.

### Backend

```
backend/app/
  main.py        aplicação, CORS, tratamento de erros e retomada do save
  core/          balanceamento, erros de domínio e configuração
  api/           rotas HTTP e esquemas
  models/        modelos Pydantic e o estado da partida
  services/      regras, geração, simulação e persistência
```

Rotas:

| Método | Caminho | Função |
|--------|---------|--------|
| POST | `/api/game/new` | Cria partida (tamanho e semente) |
| GET | `/api/game` | Consulta a partida corrente |
| POST | `/api/game/tick` | Avança de 1 a 24 horas |
| GET / POST | `/api/game/saves`, `/save`, `/load` | Lista, grava e carrega saves |
| GET | `/api/world/state` | Mapa da cidade |
| GET | `/api/building/{id}` | Planta de uma construção |
| POST | `/api/base/claim` | Escolhe o abrigo |
| POST | `/api/base/reinforce` | Reforça ou conserta uma abertura |
| GET | `/api/survivors` | Lista sobreviventes |
| POST | `/api/survivors/{id}/role` | Muda a função |
| POST | `/api/survivors/{id}/treat` | Trata um ferido |
| POST | `/api/expeditions` | Envia uma expedição |

Erros de regra respondem `{"detail": "..."}` com status 400, 404 ou 409.

### Frontend

```
frontend/src/
  App.tsx          raiz: carregamento, erro, tela inicial e jogo
  components/      tela inicial, barra superior, mapa 3D, painéis, sobreposições
  hooks/           relógio em tempo real
  store/           estado global (Zustand)
  lib/             cliente HTTP e chamadas tipadas
  types/           tipos que espelham o backend
```

O mapa não usa canvas nem WebGL: cada célula é um elemento HTML transformado com CSS 3D. Arrastar move a câmera e a roda do mouse dá zoom.

## Estado atual

Implementado:

- Geração de mundo e de construções, reproduzíveis por semente, com construção fixa por lote.
- Relógio do jogo com dia e noite, velocidades e avanço manual.
- Sobreviventes com necessidades, habilidades, funções, cura e morte.
- Expedições de coleta com viagem, risco, pilhagem finita e resgate de sobreviventes.
- Reforço e conserto de aberturas com madeira.
- Ondas noturnas, guardas, munição, cerco à abertura mais fraca e invasão.
- Condições de vitória e derrota, com tela de fim de jogo.
- Persistência em SQLite: autosave e saves nomeados.
- Interface com mapa 3D arrastável, painéis de sobreviventes, abrigo, local e diário.
- Testes automatizados do backend (58).

Ainda não existe:

- Construção de novas estruturas além do reforço de aberturas, e fabricação de itens (sucata ainda não tem uso).
- Eventos aleatórios além dos encontros em expedições, e variedade de zumbis.
- Mais de um abrigo ou expansão do território.
- Som, animações de sobreviventes e zumbis no mapa.
- Testes automatizados do frontend.
- Equilíbrio fino: um jogador automático simples vence cerca de 58% das partidas, e os números ficam em `backend/app/core/balance.py`.

## Como executar

Em dois terminais, a partir da raiz do repositório:

```bash
cd backend
poetry lock
poetry install
poetry run uvicorn app.main:app --reload --port 8000
```

```bash
cd frontend
npm install
npm run dev
```

O `poetry lock` só é necessário uma vez: as dependências de desenvolvimento (`pytest` e `httpx`) foram acrescentadas ao `pyproject.toml` sem regenerar o `poetry.lock`. Abra `http://localhost:5173`. A documentação interativa da API fica em `http://127.0.0.1:8000/docs`.

### Docker (tudo em um container, porta 7001)

Um unico comando constroi a imagem e sobe o jogo:

```bash
docker compose up --build -d
```

Abra `http://localhost:7001`. Os saves ficam no volume `zombies-data`. Para parar: `docker compose down` (o volume continua; use `docker compose down -v` para apagar os saves). O `Dockerfile` compila o frontend em um estagio e o entrega ao backend, que o serve na mesma porta da API.

Testes do backend: `poetry run pytest` dentro de `backend`. Verificações do frontend: `npm run lint` e `npm run build` dentro de `frontend`.

## Próximos passos sugeridos

1. Dar uso à sucata: oficina para fabricar munição e reforços melhores.
2. Estruturas do abrigo (horta, coletor de água, enfermaria) que produzam recursos e exijam trabalhadores.
3. Eventos aleatórios e zumbis de tipos diferentes.
4. Testes do frontend e de ponta a ponta.
5. Ajuste de dificuldade com base em partidas reais.

## Convenções

- Comentários no código somente no formato de docstrings do Google (docstrings em Python e JSDoc em TypeScript).
- Cada projeto mantém sua documentação em `docs`, com uma subpasta por módulo e arquivos Markdown. Toda feature nova atualiza a documentação do módulo que alterou.
