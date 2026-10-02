# StartScreen

Arquivo: `src/components/StartScreen.tsx`.

## O que e

A tela de abertura, exibida quando o servidor nao tem partida. Permite criar uma partida nova ou retomar um save.

## Como foi feito

### Nova partida

```tsx
    const start = () => {
        const parsed = seed.trim() === '' ? undefined : Number(seed);
        void newGame(size, size, Number.isFinite(parsed) ? parsed : undefined);
    };
```

O jogador escolhe um mapa quadrado (12, 20 ou 28 celulas) e, opcionalmente, uma semente. Campo vazio vira `undefined`, e o servidor sorteia. O mapa e sempre quadrado para simplificar a escolha; a API aceita larguras e alturas diferentes.

### Somente digitos na semente

```tsx
                            onChange={(e) => setSeed(e.target.value.replace(/\D/g, ''))}
```

A semente do servidor e um inteiro. Remover tudo que nao e digito na digitacao evita enviar um valor que o servidor recusaria com 422.

### Saves

```tsx
                        {saves.map((save) => (
                            <button
                                key={save.slot}
                                disabled={busy}
                                onClick={() => void loadGame(save.slot)}
```

Cada espaco salvo vira um botao mostrando o dia e a fase da partida.

## Por que assim

- **A semente e visivel.** Quem encontrar um mapa bom pode repeti-lo ou compartilhar a semente; a mesma semente com as mesmas acoes da o mesmo jogo ([game](../../../backend/docs/models/game.md)).
- **Botoes desabilitados enquanto `busy`.** Evita criar duas partidas com um duplo clique.
