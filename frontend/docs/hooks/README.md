# Modulo hooks

Arquivo: `src/hooks/useGameClock.ts`.

## O que e

O relogio em tempo real do jogo. Transforma a velocidade escolhida (pausa, 1x, 2x, 4x) em pedidos periodicos de "avance uma hora" ao servidor.

## Como foi feito

```ts
export const BASE_TICK_MS = 1500;
```

Uma hora de jogo dura 1,5 s reais em 1x. Um dia inteiro leva 36 s; os 30 dias, cerca de 18 minutos, ou 4,5 minutos em 4x.

```ts
    useEffect(() => {
        if (speed === 0 || status !== 'playing') return;
        const timer = window.setInterval(() => {
            void tick(1);
        }, BASE_TICK_MS / speed);
        return () => window.clearInterval(timer);
    }, [speed, status, tick]);
```

- Em pausa ou fora da fase `playing`, nenhum intervalo existe.
- O intervalo e `1500 / velocidade`: 1500 ms, 750 ms ou 375 ms.
- A funcao de limpeza cancela o intervalo ao trocar a velocidade, ao terminar o jogo ou ao desmontar o componente. Sem ela, mudar de 1x para 4x deixaria dois relogios rodando.

## Por que assim

- **O hook nao tem logica de jogo.** Ele so pede `tick(1)`. Quem decide se houve ataque, fome ou morte e o servidor ([simulation](../../../backend/docs/services/simulation.md)); por isso o jogo se comporta igual em qualquer velocidade.
- **Um tick por vez.** Em vez de pedir 4 horas de uma vez no 4x, o hook pede 1 hora a cada 375 ms. A tela atualiza a cada hora, o jogador ve cada evento do diario e pode pausar a tempo de reagir a uma onda.
- **O `tick` ja ignora chamadas ocupadas** ([store](../store/README.md)), entao um intervalo mais rapido que a rede nao empilha requisicoes.
