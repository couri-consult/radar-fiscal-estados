# -*- coding: utf-8 -*-
"""Gera index.html (painel autocontido) a partir de dados/indicadores_2025.json.
O HTML embute os dados e desenha os rankings em SVG inline (sem bibliotecas externas)."""
import json, os, datetime

ANO = int(os.environ.get("ANO", "2025"))
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
data = json.load(open(os.path.join(ROOT, "dados", f"indicadores_{ANO}.json"), encoding="utf-8"))
hoje = datetime.date.today().strftime("%d/%m/%Y")

# Definição dos indicadores: chave, título curto, título longo, fórmula, leitura, referência (linha) opcional
INDICADORES = [
    {"k": "i1_invest_rcl", "titulo": "Investimento / RCL",
     "longo": "Investimento liquidado (GND 4) sobre a Receita Corrente Líquida",
     "formula": "Investimentos liquidados (GND 4) ÷ RCL (12 meses) × 100",
     "num": "invest_liq", "den": "rcl",
     "leitura": "Quanto maior, maior o esforço de investimento direto do estado em relação à sua base de receita. Exclui inversões financeiras (aportes em estatais, PPP) e investimento de empresas estatais não dependentes.",
     "fonte": "RREO 6º bimestre — Anexo 01 (Investimentos, liquidadas até o bimestre) e Anexo 03 (RCL, total 12 meses)."},
    {"k": "i2_transf_reccorr", "titulo": "Transferências / Receita Corrente",
     "longo": "Transferências correntes recebidas sobre a receita corrente total",
     "formula": "Transferências Correntes realizadas ÷ Receitas Correntes realizadas × 100",
     "num": "transf_correntes", "den": "receita_corrente",
     "leitura": "Grau de dependência de transferências (FPE, Fundeb, SUS, convênios etc.) frente à arrecadação própria. Valores brutos, antes das deduções (Fundeb, repasses a municípios).",
     "fonte": "RREO 6º bimestre — Anexo 01 (receitas realizadas até o bimestre, exceto intra-orçamentárias)."},
    {"k": "i3_pessoal_rcl", "titulo": "Pessoal / RCL",
     "longo": "Despesa empenhada com pessoal e encargos (GND 1) sobre a RCL",
     "formula": "Pessoal e Encargos Sociais empenhados (GND 1) ÷ RCL (12 meses) × 100",
     "num": "pessoal_emp", "den": "rcl",
     "leitura": "Medida orçamentária ampla: inclui todos os Poderes e inativos/pensionistas custeados pelo Tesouro. NÃO é a Despesa Total com Pessoal da LRF (que deduz inativos com fonte própria, indenizações etc.) — o percentual do RGF aparece na tabela para referência.",
     "fonte": "RREO 6º bimestre — Anexo 01 (empenhadas até o bimestre) e Anexo 03 (RCL). Referência LRF: RGF 3º quadrimestre, Anexo 01 (Poder Executivo)."},
    {"k": "i4_despcorr_reccorr", "titulo": "Despesa Corrente / Receita Corrente",
     "longo": "Despesas correntes liquidadas sobre receitas correntes realizadas",
     "formula": "Despesas Correntes liquidadas ÷ Receitas Correntes realizadas × 100",
     "num": "desp_corrente_liq", "den": "receita_corrente",
     "leitura": "Rigidez orçamentária: quanto mais próximo (ou acima) de 100%, menor a poupança corrente disponível para investir e amortizar dívida. Base bruta, sem deduções da RCL.",
     "fonte": "RREO 6º bimestre — Anexo 01 (exceto intra-orçamentárias).", "ref": 100, "ref_label": "100% (sem poupança corrente)"},
    {"k": "i5_social_despprim", "titulo": "Saúde + Educação + Segurança / Despesa Primária",
     "longo": "Despesa liquidada nas funções Saúde, Educação e Segurança Pública sobre a despesa primária total",
     "formula": "(Saúde + Educação + Segurança Pública, liquidadas) ÷ Despesa Primária Total liquidada × 100",
     "num": "social_liq", "den": "desp_primaria_liq",
     "leitura": "Parcela do gasto primário direcionada às três funções finalísticas centrais dos estados. Inclui despesas intra-orçamentárias (contribuição patronal ao RPPS) nas funções, coerente com a despesa primária do Anexo 06.",
     "fonte": "RREO 6º bimestre — Anexo 02 (funções 06, 10 e 12, liquidadas) e Anexo 06 (Despesa Primária Total, liquidadas)."},
    {"k": "i6_dcl_rcl", "titulo": "DCL / RCL",
     "longo": "Dívida Consolidada Líquida sobre a Receita Corrente Líquida",
     "formula": "DCL ÷ RCL ajustada para limites de endividamento × 100",
     "num": "dcl", "den": "rcl_rgf",
     "leitura": "Alavancagem líquida (dívida menos disponibilidades e haveres financeiros). Limite da Resolução nº 40/2001 do Senado: 200% da RCL. Valores negativos indicam caixa e haveres superiores à dívida.",
     "fonte": "RGF 3º quadrimestre — Anexo 02 (Poder Executivo, consolidado do ente).", "ref": 200, "ref_label": "Limite Senado (200% da RCL)"},
]

payload = {"ano": ANO, "gerado": hoje, "estados": data, "indicadores": INDICADORES}

html = open(os.path.join(HERE, "painel_template.html"), encoding="utf-8").read()
html = html.replace("/*__DATA__*/null", json.dumps(payload, ensure_ascii=False))
open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(html)
print("index.html gerado.")
