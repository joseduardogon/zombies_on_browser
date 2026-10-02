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

A documentacao interativa fica em `http://127.0.0.1:8000/docs`.

## Estrutura

```
app/
  main.py        aplicacao e configuracao de CORS
  api/           rotas HTTP
  models/        modelos Pydantic do dominio
  services/      regras e geradores
tests/           testes automatizados
docs/            documentacao por modulo
```

## Documentacao

Cada modulo tem uma subpasta em [docs](docs) com seus arquivos Markdown:

- [core](docs/core/README.md)
- [api](docs/api/README.md)
- [models](docs/models/README.md)
- [services](docs/services/README.md)

## Convencoes

- Comentarios no codigo somente no formato de docstrings do Google.
- Toda alteracao de modulo atualiza a documentacao correspondente em `docs`.
