# Comparativo Fiscal dos Estados — 2025

Ranking dos 26 estados + DF em seis indicadores fiscais de 2025, calculados de forma idêntica
a partir da API de dados abertos do **SICONFI/STN** (RREO 6º bimestre e RGF 3º quadrimestre).

`index.html` é um painel estático e autocontido (dados embutidos, SVG próprio, sem CDN).

**🔗 Painel no ar:** https://couri-consult.github.io/ranking-fiscal-estados/

## Indicadores

| # | Indicador | Numerador | Denominador | Fonte |
|---|-----------|-----------|-------------|-------|
| 1 | Investimento / RCL | Investimentos (GND 4) liquidados | RCL 12 meses | RREO A01 + A03 |
| 2 | Transferências / Receita Corrente | Transferências correntes realizadas | Receitas correntes realizadas | RREO A01 |
| 3 | Pessoal / RCL | Pessoal e encargos (GND 1) empenhados | RCL 12 meses | RREO A01 + A03 |
| 4 | Despesa Corrente / Receita Corrente | Despesas correntes liquidadas | Receitas correntes realizadas | RREO A01 |
| 5 | Saúde + Educação + Segurança / Despesa Primária | Funções 10 + 12 + 06 liquidadas (incl. intra) | Despesa primária total liquidada | RREO A02 + A06 |
| 6 | DCL / RCL | Dívida consolidada líquida | RCL ajustada p/ endividamento | RGF A02 |

## Estrutura

```
estados/
├── index.html                 # painel
├── dados/
│   ├── indicadores_2025.csv   # tabela final (; como separador) com bases em R$ e indicadores em %
│   ├── indicadores_2025.json
│   └── raw/                   # JSON bruto da API por UF/anexo (não versionado) + manifesto de períodos
└── scripts/
    ├── coletar.py             # baixa RREO A01/A02/A03/A06 e RGF A01/A02 dos 27 entes
    ├── processar.py           # calcula os indicadores → dados/indicadores_<ano>.{csv,json}
    ├── painel.py              # injeta os dados no template → index.html
    └── painel_template.html   # HTML/CSS/JS do painel (identidade visual padrão)
```

## Atualizar

```bash
pip install requests
python scripts/coletar.py      # ~10 min (162 chamadas à API); aceita códigos IBGE como argumento p/ recoletar só alguns
python scripts/processar.py
python scripts/painel.py
```

`ANO=2026 python scripts/coletar.py` etc. para outro exercício (o coletor cai para o último
período disponível se o 6º bimestre / 3º quadrimestre ainda não estiver homologado; o painel
sinaliza os entes com período divergente).
