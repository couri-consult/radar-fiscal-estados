# -*- coding: utf-8 -*-
"""Gera o Radar Fiscal dos Estados: index.html (painel autocontido) a partir de dados/indicadores_2025.json.
O HTML embute os dados e desenha os rankings em SVG inline (sem bibliotecas externas)."""
import json, os, datetime, base64

ANO = int(os.environ.get("ANO", "2025"))
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
data = json.load(open(os.path.join(ROOT, "dados", f"indicadores_{ANO}.json"), encoding="utf-8"))
hoje = datetime.date.today().strftime("%d/%m/%Y")

RREO6 = "RREO 6º bimestre"
RGF3 = "RGF 3º quadrimestre"

# grupo: título da dimensão na navegação
# sentido: "alto_ruim" | "alto_bom" | "neutro" — orienta a leitura, não reordena o ranking
# unidade: "%" (padrão) ou "R$"
INDICADORES = [
    # ---------- A. Resultado e rigidez ----------
    {"k": "i4_despcorr_reccorr", "grupo": "Resultado e rigidez", "titulo": "Despesa Corrente / Receita Corrente",
     "longo": "Despesas correntes liquidadas sobre receitas correntes realizadas",
     "formula": "Despesas Correntes liquidadas ÷ Receitas Correntes realizadas × 100",
     "num": "desp_corrente_liq", "den": "receita_corrente", "sentido": "alto_ruim",
     "leitura": "Rigidez orçamentária: quanto mais próximo (ou acima) de 100%, menor a poupança corrente disponível para investir e amortizar dívida. Base bruta, sem deduções da RCL.",
     "fonte": f"{RREO6} — Anexo 01 (exceto intra-orçamentárias).", "ref": 100, "ref_label": "100% (sem poupança corrente)"},
    {"k": "i7_resprim_rcl", "grupo": "Resultado e rigidez", "titulo": "Resultado Primário / RCL",
     "longo": "Resultado primário do exercício sobre a Receita Corrente Líquida",
     "formula": "Resultado Primário (acima da linha) ÷ RCL (12 meses) × 100",
     "num": "resultado_primario", "den": "rcl", "sentido": "alto_bom",
     "leitura": "A medida-síntese do esforço fiscal do ano: receitas primárias menos despesas primárias, antes dos juros. Negativo significa que o estado gastou mais do que arrecadou sem contar o custo da dívida — déficit que terá de ser coberto por endividamento ou caixa acumulado. Atenção à base: o numerador cobre receita e despesa primárias totais, enquanto a RCL é um conceito restrito, que deduz transferências a municípios, Fundeb e contribuições ao RPPS — ela equivale a entre 74% e 97% da receita primária, conforme o ente. A RCL é usada aqui por ser a régua dos demais indicadores do painel; a razão sobre a receita primária, de base única, está na memória de cálculo e altera o nível, não a ordenação (23 das 27 posições são idênticas).",
     "fonte": f"{RREO6} — Anexo 06 (Resultado Primário e Nominal) e Anexo 03 (RCL).", "ref": 0, "ref_label": "Equilíbrio primário"},
    {"k": "i8_servdivida_rcl", "grupo": "Resultado e rigidez", "titulo": "Serviço da Dívida / RCL",
     "longo": "Juros, encargos e amortização empenhados sobre a Receita Corrente Líquida",
     "formula": "(Juros e Encargos + Amortização da Dívida, empenhados) ÷ RCL (12 meses) × 100",
     "num": "servico_divida", "den": "rcl", "sentido": "alto_ruim",
     "leitura": "O custo anual da dívida, que é o que de fato disputa caixa com saúde, educação e investimento — diferente do estoque (DCL/RCL), que mede o tamanho do passivo. Estados com dívida renegociada com a União podem ter estoque alto e serviço contido pelos limites de pagamento da Lei 9.496/1997 e da LC 156/2016.",
     "fonte": f"{RREO6} — Anexo 01 (GND 2 e 6, empenhadas) e Anexo 03 (RCL)."},
    # ---------- B. Pessoal e funções ----------
    {"k": "i3_pessoal_rcl", "grupo": "Pessoal e funções", "titulo": "Pessoal / RCL",
     "longo": "Despesa empenhada com pessoal e encargos (GND 1) sobre a RCL",
     "formula": "Pessoal e Encargos Sociais empenhados (GND 1) ÷ RCL (12 meses) × 100",
     "num": "pessoal_emp", "den": "rcl", "sentido": "alto_ruim",
     "leitura": "Medida orçamentária ampla: inclui todos os Poderes e inativos/pensionistas custeados pelo Tesouro. NÃO é a Despesa Total com Pessoal da LRF (que deduz inativos com fonte própria, indenizações etc.) — o percentual do RGF aparece na memória de cálculo para referência.",
     "fonte": f"{RREO6} — Anexo 01 (empenhadas) e Anexo 03 (RCL). Referência LRF: {RGF3}, Anexo 01 (Poder Executivo)."},
    {"k": "i5_social_despprim", "grupo": "Pessoal e funções", "titulo": "Saúde + Educação + Segurança / Despesa Primária",
     "longo": "Despesa liquidada nas funções Saúde, Educação e Segurança Pública sobre a despesa primária total",
     "formula": "(Saúde + Educação + Segurança Pública, liquidadas) ÷ Despesa Primária Total liquidada × 100",
     "num": "social_liq", "den": "desp_primaria_liq", "sentido": "neutro",
     "leitura": "Parcela do gasto primário direcionada às três funções finalísticas centrais dos estados. Inclui despesas intra-orçamentárias (contribuição patronal ao RPPS) nas funções, coerente com a despesa primária do Anexo 06. Mede direcionamento, não cumprimento dos mínimos constitucionais de saúde e educação — esses são apurados no SIOPS/SIOPE, fora do SICONFI.",
     "fonte": f"{RREO6} — Anexo 02 (funções 06, 10 e 12, liquidadas) e Anexo 06 (Despesa Primária Total)."},
    # ---------- C. Investimento e execução ----------
    {"k": "i1_invest_rcl", "grupo": "Investimento e execução", "titulo": "Investimento / RCL",
     "longo": "Investimento liquidado (GND 4) sobre a Receita Corrente Líquida",
     "formula": "Investimentos liquidados (GND 4) ÷ RCL (12 meses) × 100",
     "num": "invest_liq", "den": "rcl", "sentido": "alto_bom",
     "leitura": "Esforço de investimento direto frente à base de receita. Exclui inversões financeiras (aportes em estatais, aquisição de participações) e o investimento de empresas estatais não dependentes.",
     "fonte": f"{RREO6} — Anexo 01 (Investimentos, liquidadas) e Anexo 03 (RCL)."},
    {"k": "i9_investampl_rcl", "grupo": "Investimento e execução", "titulo": "Investimento Ampliado / RCL",
     "longo": "Investimentos mais inversões financeiras, liquidados, sobre a RCL",
     "formula": "(Investimentos + Inversões Financeiras, liquidados) ÷ RCL (12 meses) × 100",
     "num": "invest_ampliado", "den": "rcl", "sentido": "alto_bom",
     "leitura": "Captura a formação de capital que migra do GND 4 para o GND 5 — capitalização de estatais, aportes em PPP e aquisição de participações. A diferença entre este indicador e o anterior revela quanto do esforço de capital do estado passa por fora do investimento direto.",
     "fonte": f"{RREO6} — Anexo 01 (GND 4 e 5, liquidadas) e Anexo 03 (RCL)."},
    {"k": "i10_execucao_invest", "grupo": "Investimento e execução", "titulo": "Execução do Investimento",
     "longo": "Investimento liquidado sobre a dotação atualizada de investimento",
     "formula": "Investimentos liquidados ÷ Dotação Atualizada de Investimentos × 100",
     "num": "invest_liq", "den": "invest_dot", "sentido": "alto_bom",
     "leitura": "Separa quem não tem espaço fiscal de quem não consegue executar: o orçamento previa X de investimento e o estado liquidou qual fração? Taxas baixas indicam gargalo de capacidade (projetos, licitação, gestão), não falta de autorização orçamentária. Parte do não liquidado vira restos a pagar.",
     "fonte": f"{RREO6} — Anexo 01 (Investimentos: liquidadas e dotação atualizada)."},
    {"k": "i11_rp_despprim", "grupo": "Investimento e execução", "titulo": "Restos a Pagar Inscritos / Despesa Primária",
     "longo": "Restos a pagar não processados inscritos no exercício sobre a despesa primária",
     "formula": "RP não processados inscritos (correntes + capital) ÷ Despesa Primária liquidada × 100",
     "num": "rp_inscritos", "den": "desp_primaria_liq", "sentido": "alto_ruim",
     "leitura": "Grau de postergação: despesa empenhada mas não liquidada que atravessa o exercício e vira obrigação do ano seguinte. Valores altos antecipam pressão de caixa e, quando recorrentes, indicam orçamento sistematicamente apertado no fim do ano.",
     "fonte": f"{RREO6} — Anexo 01 (coluna de inscrição em RP não processados) e Anexo 06."},
    # ---------- D. Receita ----------
    {"k": "i2_transf_reccorr", "grupo": "Receita", "titulo": "Transferências / Receita Corrente",
     "longo": "Transferências correntes recebidas sobre a receita corrente total",
     "formula": "Transferências Correntes realizadas ÷ Receitas Correntes realizadas × 100",
     "num": "transf_correntes", "den": "receita_corrente", "sentido": "alto_ruim",
     "leitura": "Grau de dependência de transferências (FPE, Fundeb, SUS, convênios) frente à arrecadação própria. Valores brutos, antes das deduções (Fundeb, repasses a municípios).",
     "fonte": f"{RREO6} — Anexo 01 (receitas realizadas, exceto intra-orçamentárias)."},
    {"k": "i12_recpropria_pc", "grupo": "Receita", "titulo": "Receita Tributária per capita", "unidade": "R$",
     "longo": "Receita tributária própria por habitante",
     "formula": "Receita Tributária realizada ÷ população × 1",
     "num": "receita_tributaria", "den": "populacao", "sentido": "alto_bom",
     "leitura": "Esforço arrecadatório próprio em unidade comparável entre estados de portes distintos. Reflete sobretudo a base econômica (ICMS), não apenas a eficiência da administração tributária — estados com setor industrial e de serviços maior arrecadam mais por habitante com o mesmo esforço.",
     "fonte": f"{RREO6} — Anexo 01 (Receita Tributária) e população do próprio registro do SICONFI."},
    # ---------- E. Endividamento e limites ----------
    {"k": "i6_dcl_rcl", "grupo": "Endividamento e limites", "titulo": "DCL / RCL",
     "longo": "Dívida Consolidada Líquida sobre a Receita Corrente Líquida",
     "formula": "DCL ÷ RCL ajustada para limites de endividamento × 100",
     "num": "dcl", "den": "rcl_rgf", "sentido": "alto_ruim",
     "leitura": "Alavancagem líquida (dívida menos disponibilidades e haveres financeiros). Limite da Resolução nº 40/2001 do Senado: 200% da RCL. Valores negativos indicam caixa e haveres superiores à dívida.",
     "fonte": f"{RGF3} — Anexo 02 (Poder Executivo, consolidado do ente).", "ref": 200, "ref_label": "Limite Senado (200% da RCL)"},
    {"k": "i13_dc_rcl", "grupo": "Endividamento e limites", "titulo": "Dívida Bruta / RCL",
     "longo": "Dívida Consolidada (bruta) sobre a Receita Corrente Líquida",
     "formula": "Dívida Consolidada ÷ RCL ajustada para limites de endividamento × 100",
     "num": "dc", "den": "rcl_rgf", "sentido": "alto_ruim",
     "leitura": "O passivo antes de descontar caixa e haveres. A distância para a DCL mostra quanto de ativo financeiro o estado carrega: um ente com dívida bruta alta e líquida baixa depende de manter esse colchão, que pode estar vinculado (RPPS, depósitos judiciais) e não livre para uso.",
     "fonte": f"{RGF3} — Anexo 02 (Dívida Consolidada — DC)."},
    {"k": "i14_garantias_rcl", "grupo": "Endividamento e limites", "titulo": "Garantias Concedidas / RCL",
     "longo": "Total de garantias e contragarantias concedidas sobre a RCL",
     "formula": "Total das Garantias Concedidas ÷ RCL ajustada × 100",
     "num": "garantias", "den": "rcl_rgf", "sentido": "alto_ruim",
     "leitura": "Passivo contingente: dívida de terceiros (estatais, autarquias, municípios) que o estado honrará em caso de inadimplência. Não entra na DCL enquanto não for executada. Limite de 22% da RCL, elevado a 32% quando as contragarantias atendem ao §1º do art. 9º da Resolução nº 43/2001 do Senado — o painel usa o limite publicado por cada ente. Zero indica estado sem garantias vigentes no exercício.",
     "fonte": f"{RGF3} — Anexo 03 (Garantias e Contragarantias de Valores)."},
    {"k": "i15_opcredito_rcl", "grupo": "Endividamento e limites", "titulo": "Operações de Crédito / RCL",
     "longo": "Operações de crédito contratadas no exercício, sujeitas ao limite, sobre a RCL",
     "formula": "Total considerado para apuração do limite ÷ RCL ajustada × 100",
     "num": "opcredito", "den": "rcl_rgf", "sentido": "neutro",
     "leitura": "Endividamento novo contratado no ano. Limite de 16% da RCL (Resolução nº 43/2001 do Senado). Valor alto não é por si um problema — pode financiar investimento dentro da regra de ouro —, mas indica a velocidade com que o estoque de dívida está sendo realimentado.",
     "fonte": f"{RGF3} — Anexo 04 (Operações de Crédito).", "ref": 16, "ref_label": "Limite Senado (16% da RCL)"},
    {"k": "i16_ppp_rcl", "grupo": "Endividamento e limites", "titulo": "Despesas de PPP / RCL",
     "longo": "Despesas de caráter continuado derivadas de PPP sobre a RCL do exercício",
     "formula": "Total das Despesas de PPP do exercício corrente ÷ RCL × 100",
     "num": "ppp_desp", "den": "rcl", "sentido": "neutro",
     "leitura": "Contraprestações e aportes a parcerias público-privadas — compromisso plurianual que não aparece na dívida consolidada. Limite de 5% da RCL (art. 28 da Lei nº 11.079/2004, com a redação da Lei nº 12.766/2012). Zero indica estado sem PPP contratada em execução.",
     "fonte": f"{RREO6} — Anexo 13 (Projeção Atuarial das PPP).", "ref": 5, "ref_label": "Limite legal (5% da RCL)"},
    {"k": "i17_regra_ouro", "grupo": "Endividamento e limites", "titulo": "Regra de Ouro",
     "longo": "Receitas de operações de crédito sobre a despesa de capital líquida",
     "formula": "Receitas de Operações de Crédito ÷ Despesa de Capital Líquida × 100",
     "num": "ouro_opcredito", "den": "ouro_desp_capital", "sentido": "alto_ruim",
     "leitura": "Teste do art. 167, III da Constituição: o estado não pode captar dívida acima do que gasta em capital. Até 100% a regra é cumprida; acima disso, parte do endividamento estaria financiando despesa corrente. Apurado sobre previsão e dotação atualizadas, não sobre a execução.",
     "fonte": f"{RREO6} — Anexo 09 (Receitas de Operações de Crédito e Despesas de Capital).",
     "ref": 100, "ref_label": "Limite constitucional (100%)"},
]

LIMITES = [
    {"k": "uso_pessoal", "ind": "dtp_pct_rcl_rgf", "lim": "pessoal_limite_lrf", "pad": 49,
     "titulo": "Pessoal (LRF)", "norma": "LRF, art. 20 — 49% da RCL para o Executivo estadual", "fonte": "RGF Anexo 01"},
    {"k": "uso_divida", "ind": "i6_dcl_rcl", "lim": None, "pad": 200,
     "titulo": "Dívida (DCL)", "norma": "Res. Senado nº 40/2001 — 200% da RCL", "fonte": "RGF Anexo 02"},
    {"k": "uso_garantias", "ind": "i14_garantias_rcl", "lim": "garantias_limite", "pad": 32,
     "titulo": "Garantias", "norma": "Res. Senado nº 43/2001 — 22% da RCL (32% com contragarantias qualificadas)", "fonte": "RGF Anexo 03"},
    {"k": "uso_opcredito", "ind": "i15_opcredito_rcl", "lim": "opcredito_limite", "pad": 16,
     "titulo": "Op. de crédito", "norma": "Res. Senado nº 43/2001 — 16% da RCL", "fonte": "RGF Anexo 04"},
    {"k": "uso_ppp", "ind": "i16_ppp_rcl", "lim": None, "pad": 5,
     "titulo": "PPP", "norma": "Lei nº 11.079/2004, art. 28 — 5% da RCL", "fonte": "RREO Anexo 13"},
]

payload = {"ano": ANO, "gerado": hoje, "estados": data, "indicadores": INDICADORES, "limites": LIMITES}

html = open(os.path.join(HERE, "painel_template.html"), encoding="utf-8").read()
html = html.replace("/*__DATA__*/null", json.dumps(payload, ensure_ascii=False))

# a logo entra como data URI para o index.html continuar autocontido (não depende de assets/ em runtime)
logo = os.path.join(ROOT, "assets", "logo-cobertor-curto.webp")
with open(logo, "rb") as f:
    html = html.replace("/*__LOGO__*/", "data:image/webp;base64," + base64.b64encode(f.read()).decode())
open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(html)
print(f"index.html gerado — {len(INDICADORES)} indicadores, {len(LIMITES)} limites.")
