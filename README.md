# Comparativo Fiscal dos Estados — 2025

Ranking dos 26 estados + DF em **17 indicadores fiscais** de 2025, agrupados em cinco dimensões e
calculados de forma idêntica a partir da API de dados abertos do **SICONFI/STN** (RREO 6º bimestre
e RGF 3º quadrimestre). Inclui um **painel de folga** que mostra quanto cada ente já consumiu dos
limites legais de pessoal, dívida, garantias, operações de crédito e PPP.

`index.html` é um painel estático e autocontido (dados embutidos, SVG próprio, sem CDN).

**🔗 Painel no ar:** https://couri-consult.github.io/ranking-fiscal-estados/

## Indicadores

| # | Dimensão | Indicador | Fonte |
|---|---|---|---|
| 1 | Resultado e rigidez | Despesa corrente / receita corrente | RREO A01 |
| 2 | Resultado e rigidez | Resultado primário / RCL | RREO A06 + A03 |
| 3 | Resultado e rigidez | Serviço da dívida (juros + amortização) / RCL | RREO A01 + A03 |
| 4 | Pessoal e funções | Pessoal empenhado (GND 1) / RCL | RREO A01 + A03 |
| 5 | Pessoal e funções | Saúde + educação + segurança / despesa primária | RREO A02 + A06 |
| 6 | Investimento e execução | Investimento liquidado (GND 4) / RCL | RREO A01 + A03 |
| 7 | Investimento e execução | Investimento ampliado (GND 4 + 5) / RCL | RREO A01 + A03 |
| 8 | Investimento e execução | Execução do investimento (liquidado ÷ dotação) | RREO A01 |
| 9 | Investimento e execução | Restos a pagar inscritos / despesa primária | RREO A01 + A06 |
| 10 | Receita | Transferências correntes / receita corrente | RREO A01 |
| 11 | Receita | Receita tributária per capita (R$/hab.) | RREO A01 |
| 12 | Endividamento e limites | DCL / RCL | RGF A02 |
| 13 | Endividamento e limites | Dívida bruta / RCL | RGF A02 |
| 14 | Endividamento e limites | Garantias concedidas / RCL | RGF A03 |
| 15 | Endividamento e limites | Operações de crédito / RCL | RGF A04 |
| 16 | Endividamento e limites | Despesas de PPP / RCL | RREO A13 |
| 17 | Endividamento e limites | Regra de ouro (op. crédito ÷ despesa de capital) | RREO A09 |

### Painel de folga

Consolida o uso dos limites legais (100% = exatamente no teto):

| Dimensão | Limite | Norma |
|---|---|---|
| Pessoal | 49% da RCL (Executivo estadual) | LRF, art. 20 |
| Dívida (DCL) | 200% da RCL | Res. Senado 40/2001 |
| Garantias | 22% da RCL (32% com contragarantias qualificadas) | Res. Senado 43/2001, art. 9º |
| Operações de crédito | 16% da RCL | Res. Senado 43/2001 |
| PPP | 5% da RCL | Lei 11.079/2004, art. 28 |

**Não disponível no SICONFI:** os mínimos constitucionais de saúde e educação (RREO Anexos 8 e 12)
não são retornados pela API — são apurados no SIOPS/SIOPE. O indicador 5 mede *direcionamento* do
gasto por função, não cumprimento de piso.

## Estrutura

```
estados/
├── index.html                 # painel
├── dados/
│   ├── indicadores_2025.csv   # tabela final (; como separador) com bases em R$ e indicadores em %
│   ├── indicadores_2025.json
│   └── raw/                   # JSON bruto da API por UF/anexo (não versionado) + manifesto de períodos
└── scripts/
    ├── coletar.py             # baixa RREO A01/A02/A03/A06/A09/A13 e RGF A01-A04 dos 27 entes
    ├── processar.py           # calcula os indicadores → dados/indicadores_<ano>.{csv,json}
    ├── painel.py              # injeta os dados no template → index.html
    └── painel_template.html   # HTML/CSS/JS do painel (identidade visual padrão)
```

## Atualizar

```bash
pip install requests
python scripts/coletar.py      # ~15 min (270 chamadas à API); aceita códigos IBGE como argumento p/ recoletar só alguns
# ANEXOS="rreo09,rgf03" python scripts/coletar.py    # recoleta só os anexos indicados
python scripts/processar.py
python scripts/painel.py
```

`ANO=2026 python scripts/coletar.py` etc. para outro exercício (o coletor cai para o último
período disponível se o 6º bimestre / 3º quadrimestre ainda não estiver homologado; o painel
sinaliza os entes com período divergente).
