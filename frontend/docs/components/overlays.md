# Overlays

Arquivo: `src/components/Overlays.tsx`.

## O que e

Quatro camadas sobrepostas ao jogo: o aviso de cerco, o escurecimento noturno, os avisos temporarios e a tela de fim de jogo.

## Como foi feito

### SiegeBanner

```tsx
    const siege = useGameStore((s) => s.game?.siege);
    const status = useGameStore((s) => s.game?.status);
    if (!siege || siege.wave_size === 0 || status !== 'playing') return null;
```

Aparece apenas durante o cerco, ou seja, quando `wave_size` e maior que zero (das 20h as 6h), e somente com a partida em andamento: se o jogo termina no meio da noite, o aviso some e a tela de fim de jogo assume. Mostra o andamento da onda:

```tsx
            Horde {siege.arrived}/{siege.wave_size} arrived - {siege.at_gate} at the gate -{' '}
            {siege.killed} killed
```

"arrived" cresce a cada rodada; "at the gate" sao os zumbis ainda atacando; "killed" sao os abatidos. Se `at_gate` sobe noite adentro, a defesa nao esta dando conta.

### NightTint

```tsx
    if (phase !== 'night') return null;
    return <div className="absolute inset-0 z-10 bg-indigo-950/50 pointer-events-none" />;
```

Uma camada anil semitransparente sobre o mapa. O `pointer-events-none` deixa os cliques passarem para o mapa por baixo, e o jogador continua podendo selecionar lotes a noite.

### NoticeToast

```tsx
        if (!notice || notice.kind === 'error') return;
        const timer = window.setTimeout(dismissNotice, NOTICE_MS);
        return () => window.clearTimeout(timer);
```

Avisos informativos ("Game saved") somem sozinhos apos 4 segundos. **Erros ficam** ate o jogador clicar: uma recusa como "Not enough wood" precisa ser lida, e o jogador pode estar olhando outro lugar. A funcao de limpeza cancela o temporizador se outro aviso chegar antes.

### GameOverOverlay

```tsx
    if (!game || (game.status !== 'won' && game.status !== 'lost')) return null;
```

```tsx
                    {won ? 'RESCUED' : 'OVERRUN'}
```

Ao vencer ou perder, uma tela cobre o jogo com o balanco: sobreviventes vivos, zumbis abatidos e horas vividas. O botao "New game" recria a partida com o mesmo tamanho de mapa.

## Por que assim

- **Todas leem o store diretamente.** Nenhuma recebe propriedades; cada uma se inscreve so no pedaco que usa (`s.game?.siege`, `s.game?.clock.phase`), e por isso so se redesenha quando esse pedaco muda.
- **Sobreposicoes, nao paginas.** Mostrar o fim de jogo sobre o mapa mantem o cenario visivel ao fundo, o que da um fechamento melhor do que uma tela em branco.
