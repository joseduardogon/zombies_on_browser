# Modulo lib

Arquivos: `src/lib/api.ts` e `src/lib/gameApi.ts`.

## O que e

A camada de acesso ao servidor. `api.ts` e o cliente HTTP; `gameApi.ts` e uma funcao tipada para cada endpoint.

## Como foi feito

### Cliente base

```ts
const api = axios.create({
    headers: {
        'Content-Type': 'application/json',
    },
});
```

Sem `baseURL`: as chamadas a `/api/...` passam pelo proxy do Vite (`vite.config.ts`), que as encaminha para `http://127.0.0.1:8000`. Assim o navegador conversa so com um endereco e nao ha problema de CORS em desenvolvimento.

### Erros com mensagem pronta

```ts
export class ApiError extends Error {
    /** Status HTTP, ou 0 se o servidor nao respondeu. */
    readonly status: number;
```

```ts
            if (err.response) {
                const detail = err.response.data?.detail;
                const message = typeof detail === 'string' ? detail : err.response.statusText;
                throw new ApiError(message || 'Request failed', err.response.status);
            }
            throw new ApiError('Network Error: Unreachable (Check Backend)', 0);
```

A funcao `call` envolve cada requisicao e traduz falhas em `ApiError`:

- com resposta, a mensagem e o campo `detail` que o backend envia (por exemplo, "Not enough wood");
- sem resposta (servidor fora do ar), o status e `0`.

O `status` e o que permite ao [store](../store/README.md) distinguir **falha de regra** (mostra um aviso e o jogo segue) de **falha de conexao** (mostra "SIGNAL LOST").

### Uma funcao por endpoint

```ts
    reinforce: (apertureId: string, survivorId: string) =>
        call<GameView>(() =>
            api.post('/api/base/reinforce', { aperture_id: apertureId, survivor_id: survivorId }),
        ),
```

O componente chama `gameApi.reinforce(...)` e recebe um `GameView` tipado. A traducao de `camelCase` para o corpo `snake_case` do servidor fica toda aqui.

## Por que assim

- **Rotas em um unico lugar.** Se um caminho mudar no backend, so este arquivo muda.
- **Generico em `call<T>`.** O tipo da resposta e declarado uma vez por funcao, e o resto do codigo nao precisa de `any`.
- **O store anterior usava `any` no `catch`.** Agora o tratamento fica em `call` e o resto trabalha com `ApiError`.
