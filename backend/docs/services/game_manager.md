# game_manager.py

Arquivo: `app/services/game_manager.py`.

## O que e

Segura a partida corrente na memoria do processo, serializa o acesso a ela e a grava a cada alteracao. Existe uma unica instancia, `manager`, usada por todas as rotas.

## Como foi feito

### A sessao

```python
    @contextmanager
    def session(self) -> Iterator[GameState]:
        with self._lock:
            if self.state is None:
                raise GameError("No game in progress", 404)
            yield self.state
            self.repository.save(balance.AUTOSAVE_SLOT, self.state)
```

Toda rota que mexe na partida abre uma sessao. A rota de tick, por exemplo:

```python
    with manager.session() as state:
        state.require_playing()
        simulation.advance_hours(state, request.hours)
        return build_view(state)
```

A sessao:

1. toma o lock;
2. entrega a partida (ou responde 404 se nao ha nenhuma);
3. ao sair **sem erro**, grava o autosave.

Se a regra levanta `GameError`, o `yield` propaga a excecao e a linha do `save` nao executa: uma acao invalida nunca grava estado.

### O lock

```python
        self._lock = threading.RLock()
```

O FastAPI executa rotas sincronas em varias threads. Se o relogio do frontend pedisse um tick enquanto o jogador reforca uma porta, as duas alteracoes se misturariam. Com o lock, uma espera a outra. `RLock` (reentrante) permite que um metodo ja dentro do lock chame outro, como `load_slot` chamando `replace`.

### Repositorio sob demanda

```python
        if self._repository is None:
            self._repository = GameRepository(get_db_path())
        return self._repository
```

O banco so e aberto quando alguem precisa dele. `configure(repo)` troca o repositorio e zera a partida; os testes usam isso para apontar a um banco temporario.

### Retomada

`load_autosave` carrega o slot `autosave` ao iniciar o servidor (veja [main](../core/main.md)). `load_slot` carrega um espaco nomeado e o transforma na partida corrente, gravando-o tambem como autosave.

## Por que assim

- **A partida fica na memoria.** Ler do banco a cada hora seria desperdicio; o banco e so durabilidade.
- **Autosave a cada acao.** Fechar o navegador ou derrubar o servidor nunca perde mais que a acao em curso.
- **Uma partida por servidor.** O jogo e de um jogador; nao ha contas nem varias partidas simultaneas. Se isso mudar, `manager` se transforma em um dicionario por identificador de sessao sem alterar as regras em `services/`.
