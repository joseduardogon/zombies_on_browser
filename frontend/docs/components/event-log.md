# EventLog

Arquivo: `src/components/EventLog.tsx`.

## O que e

O diario da partida: tudo o que o servidor registrou, do evento mais recente ao mais antigo.

## Como foi feito

```tsx
const KIND_STYLE: Record<LogKind, string> = {
    info: 'text-gray-300',
    success: 'text-green-400',
    warning: 'text-yellow-400',
    danger: 'text-red-400',
};
```

Cada entrada tem uma severidade escolhida pelo backend (`LogKind`), e o componente so a traduz em cor: cinza para rotina, verde para conquistas (retorno de expedicao, tratamento), amarelo para alertas (anoitecer, encontro com zumbis) e vermelho para perigo (porta quebrada, invasao, morte).

```tsx
            {[...log].reverse().map((entry, index) => (
                <li key={`${log.length - index}`} className={KIND_STYLE[entry.kind]}>
```

O diario chega do mais antigo ao mais recente; a copia invertida poe o mais novo no topo. A chave e `log.length - index`, a posicao original da entrada. Como o servidor so acrescenta no fim (e descarta as mais antigas), a posicao identifica a entrada de forma estavel enquanto a lista nao passa de 200 itens.

## Por que assim

- **Mensagens prontas do servidor.** O cliente nao monta frases; o backend ja envia "Olivia returned with food 4, water 2". Assim o texto fica junto da regra que o gerou.
- **O diario e a unica forma de ver o que aconteceu enquanto o tempo corria.** Em 4x, uma noite inteira passa em tres segundos; o diario guarda cada tiro, quebra e morte.
