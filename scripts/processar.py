# -*- coding: utf-8 -*-
"""Lê os JSON brutos de dados/raw/ e calcula os seis indicadores comparativos por estado.
Gera dados/indicadores_2025.json e dados/indicadores_2025.csv."""
import json, os, csv

ANO = int(os.environ.get("ANO", "2025"))
HERE = os.path.dirname(os.path.abspath(__file__))
DADOS = os.path.join(HERE, "..", "dados")
RAW = os.path.join(DADOS, "raw")

UFS = ["AC","AL","AM","AP","BA","CE","DF","ES","GO","MA","MG","MS","MT","PA","PB","PE","PI",
       "PR","RJ","RN","RO","RR","RS","SC","SE","SP","TO"]
NOMES = {"AC":"Acre","AL":"Alagoas","AM":"Amazonas","AP":"Amapá","BA":"Bahia","CE":"Ceará",
         "DF":"Distrito Federal","ES":"Espírito Santo","GO":"Goiás","MA":"Maranhão",
         "MG":"Minas Gerais","MS":"Mato Grosso do Sul","MT":"Mato Grosso","PA":"Pará",
         "PB":"Paraíba","PE":"Pernambuco","PI":"Piauí","PR":"Paraná","RJ":"Rio de Janeiro",
         "RN":"Rio Grande do Norte","RO":"Rondônia","RR":"Roraima","RS":"Rio Grande do Sul",
         "SC":"Santa Catarina","SE":"Sergipe","SP":"São Paulo","TO":"Tocantins"}
REGIAO = {"AC":"N","AM":"N","AP":"N","PA":"N","RO":"N","RR":"N","TO":"N",
          "AL":"NE","BA":"NE","CE":"NE","MA":"NE","PB":"NE","PE":"NE","PI":"NE","RN":"NE","SE":"NE",
          "DF":"CO","GO":"CO","MS":"CO","MT":"CO",
          "ES":"SE","MG":"SE","RJ":"SE","SP":"SE",
          "PR":"S","RS":"S","SC":"S"}

def load(uf, tag):
    fn = os.path.join(RAW, f"{uf}_{ANO}_{tag}.json")
    return json.load(open(fn, encoding="utf-8")) if os.path.exists(fn) else []

def num(v):
    try:
        return None if v in (None, "") else float(v)
    except Exception:
        return None

def pick(items, code, col_patterns, conta=None):
    """Primeiro valor de cod_conta==code cuja coluna casa (prefixo/substring) com algum padrão,
    na ordem de prioridade. `conta` filtra pelo texto exato da linha (usado no Anexo 02)."""
    cand = [i for i in items if i["cod_conta"] == code and (conta is None or i["conta"].strip() == conta)]
    for pat in col_patterns:
        pl = pat.lower()
        for i in cand:
            col = i["coluna"].strip().lower()
            if col.startswith(pl) or pl in col:
                v = num(i["valor"])
                if v is not None:
                    return v
    return None

def pct(a, b):
    return None if a is None or not b else round(100.0 * a / b, 2)

REC  = ["Até o Bimestre (c)"]
EMP  = ["DESPESAS EMPENHADAS ATÉ O BIMESTRE (f)", "DESPESAS EMPENHADAS ATÉ O BIMESTRE"]
LIQ  = ["DESPESAS LIQUIDADAS ATÉ O BIMESTRE (h)", "DESPESAS LIQUIDADAS ATÉ O BIMESTRE"]
LIQ2 = ["DESPESAS LIQUIDADAS ATÉ O BIMESTRE (d)", "DESPESAS LIQUIDADAS ATÉ O BIMESTRE"]
EMP2 = ["DESPESAS EMPENHADAS ATÉ O BIMESTRE (b)", "DESPESAS EMPENHADAS ATÉ O BIMESTRE"]
QUAD = ["Até o 3º Quadrimestre", "Até o 2º Quadrimestre", "Até o 1º Quadrimestre"]

def funcao(a2, nome, cols):
    """Despesa por função (exceto intra + intra-orçamentárias)."""
    ex = pick(a2, "RREO2TotalDespesas", cols, conta=nome)
    intra = pick(a2, "RREO2TotalDespesasIntra", cols, conta=nome) or 0.0
    return None if ex is None else ex + intra

def process(uf, manifest):
    a1 = load(uf, "rreo01"); a2 = load(uf, "rreo02"); a3 = load(uf, "rreo03"); a6 = load(uf, "rreo06")
    g1 = load(uf, "rgf01");  g2 = load(uf, "rgf02")
    m = manifest.get(uf, {})
    d = {"uf": uf, "nome": NOMES[uf], "regiao": REGIAO[uf],
         "periodo_rreo": m.get("RREO-Anexo 01", {}).get("periodo"),
         "periodo_rgf": m.get("RGF-Anexo 02", {}).get("periodo")}
    pop = next((i.get("populacao") for i in a1 if i.get("populacao")), None)
    d["populacao"] = pop

    # --- bases (R$) ---
    d["receita_corrente"]   = pick(a1, "ReceitasCorrentes", REC)
    d["transf_correntes"]   = pick(a1, "TransferenciasCorrentes", REC)
    d["transf_corr_uniao"]  = pick(a1, "TransferenciasCorrentesDaUniaoEDeSuasEntidades", REC)
    d["desp_corrente_liq"]  = pick(a1, "DespesasCorrentes", LIQ)
    d["desp_corrente_emp"]  = pick(a1, "DespesasCorrentes", EMP)
    d["pessoal_emp"]        = pick(a1, "PessoalEEncargosSociais", EMP)
    d["pessoal_liq"]        = pick(a1, "PessoalEEncargosSociais", LIQ)
    d["invest_liq"]         = pick(a1, "Investimentos", LIQ)
    d["invest_emp"]         = pick(a1, "Investimentos", EMP)
    d["rcl"] = pick(a3, "RREO3ReceitaCorrenteLiquida", ["TOTAL (ÚLTIMOS 12 MESES)", "TOTAL"]) \
               or pick(a3, "ReceitaCorrenteLiquida", ["TOTAL (ÚLTIMOS 12 MESES)", "TOTAL"])
    d["desp_primaria_liq"]  = pick(a6, "RREO6TotalDespesaPrimaria", ["DESPESAS LIQUIDADAS"])
    d["desp_primaria_emp"]  = pick(a6, "RREO6TotalDespesaPrimaria", ["DESPESAS EMPENHADAS"])
    d["saude_liq"]     = funcao(a2, "Saúde", LIQ2)
    d["educacao_liq"]  = funcao(a2, "Educação", LIQ2)
    d["seguranca_liq"] = funcao(a2, "Segurança Pública", LIQ2)
    d["saude_emp"]     = funcao(a2, "Saúde", EMP2)
    d["educacao_emp"]  = funcao(a2, "Educação", EMP2)
    d["seguranca_emp"] = funcao(a2, "Segurança Pública", EMP2)
    d["dcl"]           = pick(g2, "DividaConsolidadaLiquida", QUAD)
    d["dc"]            = pick(g2, "DividaConsolidada", QUAD)
    d["rcl_rgf"]       = pick(g2, "ReceitaCorrenteLiquidaAjustadaParaCalculoDosLimitesDeEndividamento", QUAD) \
                         or pick(g2, "RGF2ReceitaCorrenteLiquida", QUAD)
    d["dcl_pct_rcl_rgf"] = pick(g2, "PercentualDaDCLSobreARCL", QUAD)
    d["dtp_pct_rcl_rgf"] = pick(g1, "DespesaComPessoalTotal", ["% sobre a RCL Ajustada", "% sobre a RCL"])

    # --- indicadores (%) ---
    d["i1_invest_rcl"]      = pct(d["invest_liq"], d["rcl"])
    d["i2_transf_reccorr"]  = pct(d["transf_correntes"], d["receita_corrente"])
    d["i3_pessoal_rcl"]     = pct(d["pessoal_emp"], d["rcl"])
    d["i4_despcorr_reccorr"] = pct(d["desp_corrente_liq"], d["receita_corrente"])
    soc = None
    if None not in (d["saude_liq"], d["educacao_liq"], d["seguranca_liq"]):
        soc = d["saude_liq"] + d["educacao_liq"] + d["seguranca_liq"]
    d["social_liq"] = soc
    d["i5_social_despprim"] = pct(soc, d["desp_primaria_liq"])
    d["i6_dcl_rcl"]         = pct(d["dcl"], d["rcl_rgf"])
    return d

def main():
    mf = os.path.join(RAW, f"_manifest_{ANO}.json")
    manifest = json.load(open(mf, encoding="utf-8")) if os.path.exists(mf) else {}
    data = [process(uf, manifest) for uf in UFS]
    json.dump(data, open(os.path.join(DADOS, f"indicadores_{ANO}.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    with open(os.path.join(DADOS, f"indicadores_{ANO}.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(data[0].keys()), delimiter=";")
        w.writeheader(); w.writerows(data)
    print("UF | per | I1 inv/RCL | I2 transf/RC | I3 pess/RCL | I4 DC/RC | I5 soc/DP | I6 DCL/RCL | DCL%RGF | DTP%RGF")
    f = lambda x: "  n.d." if x is None else f"{x:6.1f}"
    for d in data:
        print(f"{d['uf']} | {d['periodo_rreo']}/{d['periodo_rgf']} | {f(d['i1_invest_rcl'])} | {f(d['i2_transf_reccorr'])} |"
              f" {f(d['i3_pessoal_rcl'])} | {f(d['i4_despcorr_reccorr'])} | {f(d['i5_social_despprim'])} |"
              f" {f(d['i6_dcl_rcl'])} | {f(d['dcl_pct_rcl_rgf'])} | {f(d['dtp_pct_rcl_rgf'])}")

if __name__ == "__main__":
    main()
