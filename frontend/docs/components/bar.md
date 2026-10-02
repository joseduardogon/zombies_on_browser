# Bar

Arquivo: `src/components/ui/Bar.tsx`.

## O que e

Uma barra horizontal rotulada. Serve para as necessidades dos sobreviventes, a integridade do abrigo e a saude das aberturas.

## Como foi feito

```tsx
export const Bar = ({ label, value, max = 100, color }: BarProps) => {
    const percent = Math.max(0, Math.min(100, (value / max) * 100));
```

O preenchimento e `valor / maximo`, limitado entre 0 e 100. O maximo padrao e 100 (necessidades); a saude das aberturas passa `max={300}`.

```tsx
                <div className={`h-full ${color}`} style={{ width: `${percent}%` }} />
```

A cor chega como classe do Tailwind (`bg-red-500`) vinda de quem usa o componente.

```tsx
            <span className="w-7 text-right tabular-nums">{Math.round(value)}</span>
```

O valor e arredondado, porque as necessidades sao decimais (`98.5`), e usa digitos de largura fixa.

## Por que assim

- **Componente em `ui/`.** E a primeira peca generica da interface; uma subpasta propria separa o que e reutilizavel do que e especifico de uma tela.
- **A classe de cor e completa na chamada** (`bg-red-500`), nao montada por interpolacao: o Tailwind so gera as classes que enxerga como texto literal no codigo.
