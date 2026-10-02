# Zombies on Browser - Backend

API em FastAPI do jogo de sobrevivencia zumbi para navegador, inspirado em Infection Free Zone.

## Requisitos

- Python 3.12 ou superior
- Poetry

## Execucao

```bash
poetry install
poetry run uvicorn app.main:app --reload --port 8000
```

Testes:

```bash
poetry run pytest
```

O caminho do banco pode ser trocado com a variavel de ambiente `ZOB_DB_PATH`. As dependencias de desenvolvimento (`pytest` e `httpx`) foram declaradas em `pyproject.toml`; rode `poetry lock` para atualizar o `poetry.lock`.

A documentacao interativa fica em `http://127.0.0.1:8000/docs`.

## Estrutura

```
app/
  main.py        aplicacao, CORS, tratamento de erros e retomada do save
  core/          balanceamento, erros de dominio e configuracao
  api/           rotas HTTP e esquemas de requisicao/resposta
  models/        modelos Pydantic do dominio e o estado da partida
  services/      regras do jogo, geracao, simulacao e persistencia
tests/           testes automatizados (pytest)
docs/            documentacao por modulo
data/            banco SQLite local (ignorado pelo Git)
```

## Documentacao

Cada modulo tem uma subpasta em [docs](docs) com seus arquivos Markdown:

- [core](docs/core/README.md)
- [api](docs/api/README.md)
- [models](docs/models/README.md)
- [services](docs/services/README.md)
- [tests](docs/tests/README.md)

## Convencoes

- Comentarios no codigo somente no formato de docstrings do Google.
- Toda alteracao de modulo atualiza a documentacao correspondente em `docs`.
