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
DOT  = ["DOTAÇÃO ATUALIZADA (e)", "DOTAÇÃO ATUALIZADA"]
RPI  = ["INSCRITAS EM RESTOS A PAGAR NÃO PROCESSADOS (k)", "INSCRITAS EM RESTOS A PAGAR NÃO PROCESSADOS"]

def funcao(a2, nome, cols):
    """Despesa por função (exceto intra + intra-orçamentárias)."""
    ex = pick(a2, "RREO2TotalDespesas", cols, conta=nome)
    intra = pick(a2, "RREO2TotalDespesasIntra", cols, conta=nome) or 0.0
    return None if ex is None else ex + intra

def soma(*vals):
    """Soma ignorando None; devolve None se todos forem None."""
    ok = [v for v in vals if v is not None]
    return sum(ok) if ok else None

def process(uf, manifest):
    a1 = load(uf, "rreo01"); a2 = load(uf, "rreo02"); a3 = load(uf, "rreo03"); a6 = load(uf, "rreo06")
    a9 = load(uf, "rreo09"); a13 = load(uf, "rreo13")
    g1 = load(uf, "rgf01");  g2 = load(uf, "rgf02"); g3 = load(uf, "rgf03"); g4 = load(uf, "rgf04")
    m = manifest.get(uf, {})
    d = {"uf": uf, "nome": NOMES[uf], "regiao": REGIAO[uf],
         "periodo_rreo": m.get("RREO-Anexo 01", {}).get("periodo"),
         "periodo_rgf": m.get("RGF-Anexo 02", {}).get("periodo")}
    pop = next((i.get("populacao") for i in a1 if i.get("populacao")), None)
    d["populacao"] = pop

    # --- bases (R$) ---
    d["receita_corrente"]   = pick(a1, "ReceitasCorrentes", REC)
    d["receita_tributaria"] = pick(a1, "ReceitaTributaria", REC)
    d["transf_correntes"]   = pick(a1, "TransferenciasCorrentes", REC)
    d["transf_corr_uniao"]  = pick(a1, "TransferenciasCorrentesDaUniaoEDeSuasEntidades", REC)
    d["desp_corrente_liq"]  = pick(a1, "DespesasCorrentes", LIQ)
    d["desp_corrente_emp"]  = pick(a1, "DespesasCorrentes", EMP)
    d["pessoal_emp"]        = pick(a1, "PessoalEEncargosSociais", EMP)
    d["pessoal_liq"]        = pick(a1, "PessoalEEncargosSociais", LIQ)
    d["juros_emp"]          = pick(a1, "JurosEEncargosDaDivida", EMP)
    d["amortizacao_emp"]    = pick(a1, "AmortizacaoDaDivida", EMP)
    d["invest_liq"]         = pick(a1, "Investimentos", LIQ)
    d["invest_emp"]         = pick(a1, "Investimentos", EMP)
    d["invest_dot"]         = pick(a1, "Investimentos", DOT)
    d["inversoes_liq"]      = pick(a1, "InversoesFinanceiras", LIQ)
    d["inversoes_dot"]      = pick(a1, "InversoesFinanceiras", DOT)
    # restos a pagar não processados inscritos no exercício (correntes + capital)
    d["rp_inscritos"] = soma(pick(a1, "DespesasCorrentes", RPI), pick(a1, "DespesasDeCapital", RPI))
    d["rcl"] = pick(a3, "RREO3ReceitaCorrenteLiquida", ["TOTAL (ÚLTIMOS 12 MESES)", "TOTAL"]) \
               or pick(a3, "ReceitaCorrenteLiquida", ["TOTAL (ÚLTIMOS 12 MESES)", "TOTAL"])
    d["desp_primaria_liq"]  = pick(a6, "RREO6TotalDespesaPrimaria", ["DESPESAS LIQUIDADAS"])
    d["desp_primaria_emp"]  = pick(a6, "RREO6TotalDespesaPrimaria", ["DESPESAS EMPENHADAS"])
    d["resultado_primario"] = pick(a6, "ResultadoPrimarioComRPPSAcimaDaLinha", ["VALOR"]) \
                              or pick(a6, "RREO6ResultadoPrimarioEstadosMunicipios", ["VALOR"])
    d["receita_primaria"]   = pick(a6, "RREO6TotalReceitaPrimaria", ["RECEITAS REALIZADAS (a)"])
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
    d["pessoal_limite_lrf"] = pick(g1, "LimiteMaximoDespesaComPessoalTotal", ["% sobre a RCL Ajustada", "% sobre a RCL"])

    # --- limites legais (RGF Anexos 03 e 04; RREO Anexos 09 e 13) ---
    # Nos três anexos abaixo, o ente que não tem o item simplesmente omite a linha e
    # publica só RCL e limites — ausência de linha com anexo entregue significa zero.
    d["garantias"]        = pick(g3, "TotalGarantiasConcedidas", QUAD)
    d["garantias_pct"]    = pick(g3, "PercentualDoTotalDasGarantiasSobreARCL", QUAD)
    if g3 and d["garantias"] is None:
        d["garantias"] = d["garantias_pct"] = 0.0
    rcl_g3               = pick(g3, "ReceitaCorrenteLiquidaAjustadaParaCalculoDosLimitesDeEndividamento", QUAD) \
                           or pick(g3, "RGF3ReceitaCorrenteLiquida", QUAD)
    lim_g3               = pick(g3, "LimiteDefinidoPorResolucaoDoSenadoFederal", QUAD)
    # Res. Senado 43/2001, art. 9º: 22% da RCL, ou 32% quando há contragarantias qualificadas
    # (§1º). Fora da faixa 15–40% o valor publicado está inconsistente — usa-se o padrão de 22%.
    gl = pct(lim_g3, rcl_g3)
    d["garantias_limite"] = gl if (gl is not None and 15 <= gl <= 40) else 22.0
    VALOC = ["% SOBRE A RCL AJUSTADA"]
    d["opcredito_pct"]    = pick(g4, "TotalConsideradoParaFinsDaApuracaoDoCumprimentoDoLimiteOperacoesDeCredito", VALOC)
    d["opcredito"]        = pick(g4, "TotalConsideradoParaFinsDaApuracaoDoCumprimentoDoLimiteOperacoesDeCredito", ["VALOR"])
    if g4 and d["opcredito"] is None:
        d["opcredito"] = d["opcredito_pct"] = 0.0
    d["opcredito_limite"] = pick(g4, "LimiteGeralDefinidoPorResolucaoDoSenadoFederalParaAsOperacoesDeCreditoInternasEExternas", VALOC)
    EC = ["EXERCÍCIO CORRENTE (EC)"]
    d["ppp_pct"]          = pick(a13, "TotalDespesasPPPPercentualRCL", EC)
    d["ppp_desp"]         = pick(a13, "RREO13TotalDespesasPPP", EC) or pick(a13, "TotalDespesasPPP", EC)
    if a13 and d["ppp_pct"] is None:
        d["ppp_pct"] = d["ppp_desp"] = 0.0                # anexo entregue sem PPP contratada
    # Regra de ouro: receita de op. crédito realizada contra despesa de capital empenhada
    # — o par (e − b) do próprio anexo. Misturar previsão com dotação distorce o resultado.
    d["ouro_opcredito"]    = pick(a9, "RREO9ReceitasDeOperacoesDeCredito", ["RECEITAS REALIZADAS (b)"])
    d["ouro_desp_capital"] = pick(a9, "DespesaDeCapitalLiquida", ["DESPESAS EMPENHADAS (e)"])
    if a9 and d["ouro_opcredito"] is None and d["ouro_desp_capital"] is not None:
        d["ouro_opcredito"] = 0.0                         # sem operação de crédito no exercício

    # --- indicadores (%) ---
    d["i1_invest_rcl"]      = pct(d["invest_liq"], d["rcl"])
    d["i2_transf_reccorr"]  = pct(d["transf_correntes"], d["receita_corrente"])
    d["i3_pessoal_rcl"]     = pct(d["pessoal_emp"], d["rcl"])
    d["i4_despcorr_reccorr"] = pct(d["desp_corrente_liq"], d["receita_corrente"])
    soc = soma(d["saude_liq"], d["educacao_liq"], d["seguranca_liq"]) \
          if None not in (d["saude_liq"], d["educacao_liq"], d["seguranca_liq"]) else None
    d["social_liq"] = soc
    d["i5_social_despprim"] = pct(soc, d["desp_primaria_liq"])
    d["i6_dcl_rcl"]         = pct(d["dcl"], d["rcl_rgf"])
    # novos — resultado e rigidez
    d["i7_resprim_rcl"]     = pct(d["resultado_primario"], d["rcl"])
    # denominador alternativo, de base única com o numerador (ver nota metodológica no painel)
    d["i7b_resprim_recprim"] = pct(d["resultado_primario"], d["receita_primaria"])
    d["rcl_sobre_recprim"]  = pct(d["rcl"], d["receita_primaria"])
    d["servico_divida"]     = soma(d["juros_emp"], d["amortizacao_emp"]) \
                              if None not in (d["juros_emp"], d["amortizacao_emp"]) else None
    d["i8_servdivida_rcl"]  = pct(d["servico_divida"], d["rcl"])
    # novos — investimento e execução
    d["invest_ampliado"]    = soma(d["invest_liq"], d["inversoes_liq"]) \
                              if None not in (d["invest_liq"], d["inversoes_liq"]) else None
    d["i9_investampl_rcl"]  = pct(d["invest_ampliado"], d["rcl"])
    d["i10_execucao_invest"] = pct(d["invest_liq"], d["invest_dot"])
    d["i11_rp_despprim"]    = pct(d["rp_inscritos"], d["desp_primaria_liq"])
    # novos — receita
    d["i12_recpropria_pc"]  = None if not (d["receita_tributaria"] and pop) else round(d["receita_tributaria"] / pop, 2)
    # novos — endividamento e limites
    d["i13_dc_rcl"]         = pct(d["dc"], d["rcl_rgf"])
    d["i14_garantias_rcl"]  = d["garantias_pct"] if d["garantias_pct"] is not None else pct(d["garantias"], d["rcl_rgf"])
    d["i15_opcredito_rcl"]  = d["opcredito_pct"]
    d["i16_ppp_rcl"]        = d["ppp_pct"]
    d["i17_regra_ouro"]     = pct(d["ouro_opcredito"], d["ouro_desp_capital"])

    # --- uso dos limites legais (% do limite consumido) ---
    d["uso_pessoal"]   = pct(d["dtp_pct_rcl_rgf"], d["pessoal_limite_lrf"] or 49)
    d["uso_divida"]    = pct(d["i6_dcl_rcl"], 200)
    d["uso_garantias"] = pct(d["i14_garantias_rcl"], d["garantias_limite"] or 32)
    d["uso_opcredito"] = pct(d["i15_opcredito_rcl"], d["opcredito_limite"] or 16)
    d["uso_ppp"]       = pct(d["i16_ppp_rcl"], 5)
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
    cols = [("i1", "i1_invest_rcl"), ("i2", "i2_transf_reccorr"), ("i3", "i3_pessoal_rcl"),
            ("i4", "i4_despcorr_reccorr"), ("i5", "i5_social_despprim"), ("i6", "i6_dcl_rcl"),
            ("i7prim", "i7_resprim_rcl"), ("i8serv", "i8_servdivida_rcl"), ("i9ampl", "i9_investampl_rcl"),
            ("i10exe", "i10_execucao_invest"), ("i11rp", "i11_rp_despprim"), ("i12pc", "i12_recpropria_pc"),
            ("i13dc", "i13_dc_rcl"), ("i14gar", "i14_garantias_rcl"), ("i15oc", "i15_opcredito_rcl"),
            ("i16ppp", "i16_ppp_rcl"), ("i17ouro", "i17_regra_ouro")]
    f = lambda x: "   n.d." if x is None else f"{x:7.1f}"
    print("UF |" + "|".join(f"{n:>7s}" for n, _ in cols))
    for d in data:
        print(f"{d['uf']} |" + "|".join(f(d[k]) for _, k in cols))
    faltas = {k: sum(1 for d in data if d[k] is None) for _, k in cols}
    print("\nsem dado por indicador:", {k: v for k, v in faltas.items() if v})

if __name__ == "__main__":
    main()
