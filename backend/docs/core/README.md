# Modulo core

Pasta: `app/core/`. Reune o que nao pertence a nenhuma regra especifica do jogo, mas e usado por todas elas.

| Arquivo | Documento | Papel |
|---------|-----------|-------|
| `balance.py` | [balance](balance.md) | Todas as constantes de balanceamento |
| `errors.py` | [errors](errors.md) | `GameError`, o erro de regra do jogo |
| `config.py` | [config](config.md) | Caminho do banco de dados |

A aplicacao FastAPI em si (`app/main.py`) tambem esta documentada aqui, em [main](main.md).

## Por que existe

Antes desta etapa os numeros do jogo (tamanho das ondas, fome por hora, custo de barricada) estariam espalhados dentro das funcoes. Concentra-los em um unico arquivo permite ajustar a dificuldade sem tocar nas regras, e permite que os testes troquem um valor com `monkeypatch` para forcar um cenario.
