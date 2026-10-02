# Modulo app

Arquivos: `src/main.tsx` e `src/App.tsx`.

## O que e

A raiz da aplicacao. `main.tsx` monta o React em `#root` dentro de `StrictMode`. `App` decide o que aparece na tela.

## Como foi feito

`App` tem quatro estados, escolhidos em cascata:

```tsx
      {!loaded ? (
        <div className="flex-1 flex items-center justify-center text-yellow-500 animate-pulse text-xl">
          ESTABLISHING SATELLITE UPLINK...
        </div>
      ) : fatalError ? (
```

| Condicao | Tela |
|----------|------|
| `!loaded` | "ESTABLISHING SATELLITE UPLINK..." enquanto o primeiro `GET /api/game` nao termina |
| `fatalError` | "SIGNAL LOST" com botao de nova tentativa |
| `!game` | [StartScreen](../components/start-screen.md) |
| demais | O jogo: barra superior, sobreviventes, mapa e painel lateral |

### Retomada automatica

```tsx
  useEffect(() => {
    void init();
  }, [init]);
```

Ao abrir a pagina, `init` consulta a partida corrente no servidor. Se o servidor tem uma partida salva, o jogador volta direto a ela; se responde 404, aparece a tela inicial. Ver [store](../store/README.md).

### Relogio

```tsx
  useGameClock();
```

Uma unica chamada liga o relogio em tempo real. O hook e descrito em [hooks](../hooks/README.md).

### O jogo montado

```tsx
          <TopBar />
          <div className="flex-1 flex min-h-0">
            <SurvivorsPanel />
            <main className="flex-1 relative bg-[#1e1e1e] min-w-0">
              <CityMap3D />
              <NightTint />
              <SiegeBanner />
            </main>
            <SidePanel />
          </div>
          <GameOverOverlay />
```

Tres colunas sob a barra superior: sobreviventes a esquerda, mapa no centro, abas a direita. `NightTint`, `SiegeBanner` e `GameOverOverlay` sao camadas sobrepostas ([Overlays](../components/overlays.md)).

## O que mudou

- O texto "COMMANDER INTEFACE" (erro de digitacao) foi para [TopBar](../components/top-bar.md), corrigido.
- A `App` nao gera mais um mundo ao abrir: ela retoma o salvo ou mostra a tela inicial. Antes, cada recarga da pagina gerava um mundo novo.
- O cabecalho e o rodape fixos sairam; o status agora esta na barra superior.

## Por que assim

- **Cascata de estados.** Cada situacao (carregando, falha, sem partida, jogando) e mutuamente exclusiva; uma cascata de ternarios deixa isso visivel em um so lugar.
- **`min-h-0` e `min-w-0`.** Sem eles, um painel com muita lista (como o diario) esticaria o layout para alem da tela, em vez de rolar internamente.
