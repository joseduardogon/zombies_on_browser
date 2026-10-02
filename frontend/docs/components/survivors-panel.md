# SurvivorsPanel

Arquivo: `src/components/SurvivorsPanel.tsx`.

## O que e

A coluna da esquerda: um cartao por sobrevivente, com necessidades, habilidades e as duas decisoes que o jogador toma sobre uma pessoa (funcao e tratamento).

## Como foi feito

### Cartao

```tsx
                    <div className="space-y-1">
                        <Bar label="Health" value={needs.health} color="bg-red-500" />
                        <Bar label="Hunger" value={needs.hunger} color="bg-orange-500" />
                        <Bar label="Thirst" value={needs.thirst} color="bg-sky-500" />
                        <Bar label="Energy" value={needs.fatigue} color="bg-yellow-400" />
                        <Bar label="Morale" value={needs.morale} color="bg-purple-400" />
                    </div>
```

Cinco barras, uma por necessidade. Todas funcionam do mesmo jeito (cheia e bom), porque o backend modela fome e sede como **saciedade** ([survivor](../../../backend/docs/models/survivor.md)). Cada uma tem uma cor propria para ser reconhecida sem ler.

As habilidades ficam em uma linha de siglas pequenas:

```tsx
                        <span>BLD {skills.construction}</span>
                        <span>CMB {skills.combat}</span>
                        <span>SCV {skills.scavenging}</span>
                        <span>MED {skills.medicine}</span>
```

### Funcao

```tsx
                        <select
                            value={survivor.role}
                            disabled={busy}
                            onChange={(e) => void setRole(survivor.id, e.target.value as SurvivorRole)}
```

Trocar a funcao no seletor chama a API na hora. A funcao tem efeito real: o guarda defende, o construtor reforca mais, o coletor traz mais.

### Tratar

```tsx
                        {survivor.status === 'home' && needs.health < 100 && medicine > 0 && (
                            <button
```

O botao "Treat" so aparece quando faz sentido: a pessoa esta no abrigo, esta ferida e ha remedio no estoque. Assim o jogador nunca clica em uma acao que o servidor recusaria por falta de condicao.

### Ordem

```tsx
    const ordered = [...survivors].sort(
        (a, b) => Number(a.status === 'dead') - Number(b.status === 'dead'),
    );
```

Os mortos vao para o fim da lista, esmaecidos, sem barras. A copia (`[...survivors]`) evita ordenar o array do estado, que e imutavel.

## Por que assim

- **O status colorido** (`home` verde, `away` laranja, `dead` vermelho) mostra de relance quem esta em casa e disponivel.
- **Sem cartao colapsavel.** Em um jogo de poucos sobreviventes (3 a 12), ver todas as barras de uma vez e mais util do que economizar espaco.
