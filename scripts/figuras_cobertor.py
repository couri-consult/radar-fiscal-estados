# -*- coding: utf-8 -*-
"""Gera as figuras do Radar Fiscal dos Estados na identidade visual do Cobertor Curto.

Saída em figuras/: um ranking por indicador (barras horizontais) e o painel de folga
nos limites legais (heatmap). Os dados vêm de dados/indicadores_<ano>.json.
"""
import json, os, sys

sys.path.insert(0, r"C:\Users\couri\.claude\skills\identidade-cobertor-curto")
import estilo
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.ticker import MaxNLocator
import matplotlib.image as mpimg

ANO = int(os.environ.get("ANO", "2025"))
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
SAIDA = os.path.join(ROOT, "figuras")
os.makedirs(SAIDA, exist_ok=True)

E = json.load(open(os.path.join(ROOT, "dados", f"indicadores_{ANO}.json"), encoding="utf-8"))
FONTE = f"Fonte: SICONFI/Tesouro Nacional (RREO do 6º bimestre e RGF do 3º quadrimestre de {ANO})"
ESCURO = "#643126"   # terracota escurecido — topo da escala, usado para quem passa da referência
LOGO = os.path.join(ROOT, "assets", "logo-cobertor-curto.png")


def marca(fig, altura=0.068, topo=0.978, direita=0.985):
    """Logo do Cobertor Curto no canto superior direito, preservando a proporção."""
    if not os.path.exists(LOGO):
        return
    img = mpimg.imread(LOGO)
    larg_fig, alt_fig = fig.get_size_inches()
    largura = altura * alt_fig * (img.shape[1] / img.shape[0]) / larg_fig
    ax = fig.add_axes([direita - largura, topo - altura, largura, altura], zorder=10)
    ax.imshow(img); ax.axis("off")

# Título afirmativo + subtítulo com unidade e recorte, no padrão editorial do Cobertor Curto.
# ref: linha de referência legal; sentido: orienta a leitura ("alto_ruim" destaca quem está acima.)
FIGS = [
    {"arq": "01-despesa-corrente", "k": "i4_despcorr_reccorr",
     "titulo": "Quase todo o dinheiro do ano vai embora no custeio",
     "sub": "Despesa corrente como % da receita corrente, estados, 2025",
     "apoio": "Quanto mais perto de 100%, menos sobra para investir e pagar dívida.",
     "ref": 100, "ref_txt": "100% — nada sobra"},
    {"arq": "02-resultado-primario", "k": "i7_resprim_rcl",
     "titulo": "Quase metade dos estados gastou mais do que arrecadou",
     "sub": "Resultado primário como % da receita corrente líquida, estados, 2025",
     "apoio": "Receitas menos despesas antes dos juros da dívida. Negativo = déficit.",
     "ref": 0, "ref_txt": "equilíbrio"},
    {"arq": "03-servico-divida", "k": "i8_servdivida_rcl",
     "titulo": "O custo anual da dívida vai de 0,3% a 17% da receita",
     "sub": "Juros e amortização como % da receita corrente líquida, estados, 2025",
     "apoio": "O que a dívida consome por ano — diferente do tamanho do estoque.",
     "nota": "Rio Grande do Sul, Rio de Janeiro, Minas Gerais e Goiás tiveram pagamentos suspensos ou reduzidos por regimes de recuperação fiscal."},
    {"arq": "04-pessoal", "k": "i3_pessoal_rcl",
     "titulo": "Em 22 dos 27 estados, a folha passa de metade da receita",
     "sub": "Pessoal e encargos empenhados como % da receita corrente líquida, estados, 2025",
     "apoio": "Medida orçamentária ampla: inclui todos os Poderes e os inativos pagos pelo Tesouro."},
    {"arq": "05-saude-educacao-seguranca", "k": "i5_social_despprim",
     "titulo": "Saúde, educação e segurança ficam com 37% a 54% do gasto",
     "sub": "Despesa nas três funções como % da despesa primária, estados, 2025",
     "apoio": "Mede para onde vai o gasto, não o cumprimento dos pisos de saúde e educação."},
    {"arq": "06-investimento", "k": "i1_invest_rcl",
     "titulo": "Investimento é o que sobra — e sobra pouco",
     "sub": "Investimento liquidado como % da receita corrente líquida, estados, 2025",
     "apoio": "Obras e equipamentos (GND 4). Não inclui aportes em estatais nem PPP."},
    {"arq": "07-investimento-ampliado", "k": "i9_investampl_rcl",
     "titulo": "Com aportes em estatais e PPP, o esforço de capital muda de patamar",
     "sub": "Investimento mais inversões financeiras, em % da receita corrente líquida, estados, 2025",
     "apoio": "Inversões financeiras captam capitalização de estatais e aquisição de participações."},
    {"arq": "08-execucao-investimento", "k": "i10_execucao_invest",
     "titulo": "Estados deixam de executar boa parte do investimento autorizado",
     "sub": "Investimento liquidado como % da dotação orçamentária, estados, 2025",
     "apoio": "Separa quem não tem espaço fiscal de quem não consegue executar o orçamento.",
     "sentido": "alto_bom"},
    {"arq": "09-restos-a-pagar", "k": "i11_rp_despprim",
     "titulo": "Despesa empurrada para o ano seguinte",
     "sub": "Restos a pagar inscritos como % da despesa primária, estados, 2025",
     "apoio": "Despesa empenhada que não foi liquidada e atravessa o exercício."},
    {"arq": "10-transferencias", "k": "i2_transf_reccorr",
     "titulo": "Em oito estados, transferências passam da metade da receita",
     "sub": "Transferências correntes como % da receita corrente, estados, 2025",
     "apoio": "FPE, Fundeb, SUS e convênios, antes das deduções."},
    {"arq": "11-receita-per-capita", "k": "i12_recpropria_pc", "unidade": "R$",
     "titulo": "A arrecadação própria por habitante varia quatro vezes",
     "sub": "Receita tributária por habitante, em reais, estados, 2025",
     "apoio": "Reflete sobretudo a base econômica do estado, não só a eficiência da arrecadação.",
     "sentido": "alto_bom",
     "nota": "O Distrito Federal acumula as competências tributárias de estado e de município, o que eleva sua arrecadação por habitante."},
    {"arq": "12-dcl", "k": "i6_dcl_rcl",
     "titulo": "Rio de Janeiro passa do limite de endividamento do Senado",
     "sub": "Dívida consolidada líquida como % da receita corrente líquida, estados, 2025",
     "apoio": "Dívida menos caixa e haveres. Valores negativos: o estado tem mais caixa que dívida.",
     "ref": 200, "ref_txt": "limite do Senado (200%)"},
    {"arq": "13-divida-bruta", "k": "i13_dc_rcl",
     "titulo": "Três estados devem perto de duas receitas anuais, ou mais",
     "sub": "Dívida consolidada bruta como % da receita corrente líquida, estados, 2025",
     "apoio": "O passivo antes de abater disponibilidades e haveres financeiros."},
    {"arq": "14-garantias", "k": "i14_garantias_rcl",
     "titulo": "Garantias concedidas estão longe do teto em todos os estados",
     "sub": "Garantias concedidas como % da receita corrente líquida, estados, 2025",
     "apoio": "Dívida de terceiros que o estado honra se houver calote. Limite de 22% a 32% da receita.",
     "ref": 22, "ref_txt": "limite usual (22%)"},
    {"arq": "15-operacoes-credito", "k": "i15_opcredito_rcl",
     "titulo": "Piauí chega perto do teto de endividamento novo",
     "sub": "Operações de crédito contratadas como % da receita corrente líquida, estados, 2025",
     "apoio": "Dívida nova contratada no ano, sujeita ao limite da Resolução 43/2001 do Senado.",
     "ref": 16, "ref_txt": "limite do Senado (16%)"},
    {"arq": "16-ppp", "k": "i16_ppp_rcl",
     "titulo": "PPP ainda pesa pouco no orçamento dos estados",
     "sub": "Despesas com parcerias público-privadas como % da receita corrente líquida, estados, 2025",
     "apoio": "Compromisso de longo prazo que não entra na dívida consolidada. Limite de 5% da receita.",
     "ref": 5, "ref_txt": "limite legal (5%)",
     "nota": "MT, PA, PB, RJ e RR não publicaram o demonstrativo de PPP."},
    {"arq": "17-regra-de-ouro", "k": "i17_regra_ouro",
     "titulo": "Nenhum estado furou a regra de ouro em 2025",
     "sub": "Operações de crédito como % da despesa de capital, estados, 2025",
     "apoio": "A Constituição proíbe captar dívida acima do que se gasta em capital (art. 167, III).",
     "ref": 100, "ref_txt": "limite constitucional (100%)"},
]

LIMITES = [("uso_pessoal", "Pessoal", "49% da receita"), ("uso_divida", "Dívida", "200% da receita"),
           ("uso_garantias", "Garantias", "22% a 32%"), ("uso_opcredito", "Op. de crédito", "16% da receita"),
           ("uso_ppp", "PPP", "5% da receita")]


def fmt_val(v, unidade):
    """Número no padrão brasileiro, com sinal menos tipográfico (U+2212)."""
    if v is None:
        return "n.d."
    t = ("R$ " + estilo.fmt(v, 0)) if unidade == "R$" else estilo.fmt(v, 1) + "%"
    return t.replace("-", "−")


def ranking(f):
    k, unidade = f["k"], f.get("unidade", "%")
    linhas = sorted([e for e in E if e[k] is not None], key=lambda e: e[k], reverse=True)
    sem = [e["uf"] for e in E if e[k] is None]
    vals = [e[k] for e in linhas]
    n = len(linhas)
    med = sorted(vals)[n // 2] if n % 2 else (sorted(vals)[n // 2 - 1] + sorted(vals)[n // 2]) / 2

    fig = plt.figure(figsize=(11, 9.6), facecolor=estilo.FUNDO)
    ax = fig.add_axes([0.175, 0.075, 0.80, 0.755])
    y = range(n)
    ref = f.get("ref")
    # terracota uniforme; terracota escurecido quando o valor passa da referência legal
    cores = [ESCURO if (ref is not None and ref > 0 and v > ref) else estilo.BASE for v in vals]
    ax.barh(y, vals, color=cores, height=0.72, zorder=3)
    ax.invert_yaxis()
    ax.set_yticks(list(y))
    ax.set_yticklabels([e["nome"] for e in linhas], fontsize=10.5)
    ax.tick_params(axis="y", length=0, pad=6)
    ax.tick_params(axis="x", labelsize=10)
    ax.grid(axis="x", lw=0.8, zorder=0)
    ax.set_axisbelow(True)
    for lado in ("left", "bottom"):
        ax.spines[lado].set_visible(False)

    lo, hi = min(0, min(vals)), max(vals)
    if ref is not None:
        hi = max(hi, ref)
    folga = (hi - lo) * 0.14 or 1
    ax.set_xlim(lo - (folga if lo < 0 else 0), hi + folga)
    # ticks inteiros: com passo fracionário o rótulo arredondado mentiria (−7,5% viraria "−8%")
    ax.xaxis.set_major_locator(MaxNLocator(nbins=7, integer=True))
    if unidade == "R$":
        ax.xaxis.set_major_formatter(lambda v, _: estilo.fmt(v, 0).replace("-", "−"))
    else:
        ax.xaxis.set_major_formatter(lambda v, _: estilo.fmt(v, 0).replace("-", "−") + "%")

    # rótulo de dado em cada barra
    desloc = (hi - lo) * 0.012
    for i, (e, v) in enumerate(zip(linhas, vals)):
        neg = v < 0
        ax.text(v + (-desloc if neg else desloc), i, fmt_val(v, unidade),
                va="center", ha="right" if neg else "left", fontsize=9.5, color=estilo.TEXTO,
                **({"family": "Aptos", "weight": "semibold"}))
    if min(vals) < 0:
        ax.axvline(0, color=estilo.TEXTO, lw=0.9, zorder=4)

    # mediana e referência legal, anotadas acima da primeira barra em linhas separadas
    tem_ref = ref is not None and ref != 0
    ax.set_ylim(n - 0.4, -2.5 if tem_ref else -1.5)
    ax.axvline(med, color=estilo.TEXTO_APOIO, lw=1, ls=(0, (2, 3)), zorder=5)
    ax.text(med, -0.95, f"mediana {fmt_val(med, unidade)}", fontsize=9, color=estilo.TEXTO_APOIO,
            ha="center", va="bottom")
    if tem_ref:
        ax.axvline(ref, color=ESCURO, lw=1.2, ls=(0, (4, 3)), zorder=5)
        # ancora o rótulo pelo lado que couber dentro do eixo
        x0, x1 = ax.get_xlim()
        perto_da_borda = ref > x0 + (x1 - x0) * 0.72
        ax.text(ref, -1.95, f["ref_txt"], fontsize=9, color=ESCURO,
                ha="right" if perto_da_borda else "center", va="bottom")

    estilo.cabecalho(fig, f["titulo"], f["sub"], f.get("apoio"), x=0.02, topo=0.955, tam_titulo=19)
    marca(fig)
    notas = f.get("nota", "")
    if sem and not notas:
        notas = "Sem dado publicado: " + ", ".join(sem) + "."
    estilo.rodape(fig, FONTE, notas=notas or None, x=0.02, y=0.016)
    estilo.salvar(fig, os.path.join(SAIDA, f["arq"] + ".png"))
    return f["arq"]


def painel_folga():
    """Heatmap do uso dos limites legais, em escala sequencial de terracota."""
    faixas = [(0, 70), (70, 90), (90, 100), (100, 10 ** 9)]
    cores = estilo.tons(4)
    rotulos = ["até 70%", "70% a 90%", "90% a 100%", "100% ou mais"]

    def cor(u):
        # uso negativo (DCL negativa: caixa e haveres maiores que a dívida) é folga máxima,
        # não estouro — tem de cair na faixa mais clara.
        if u is None:
            return estilo.SEM_DADO
        if u < faixas[0][1]:
            return cores[0]
        for (a, b), c in zip(faixas[1:], cores[1:]):
            if a <= u < b:
                return c
        return cores[-1]

    linhas = sorted(E, key=lambda e: max([e[k] for k, _, _ in LIMITES if e[k] is not None] or [-1]), reverse=True)
    n, m = len(linhas), len(LIMITES)
    fig = plt.figure(figsize=(11, 9.6), facecolor=estilo.FUNDO)
    ax = fig.add_axes([0.175, 0.075, 0.80, 0.725])
    ax.set_xlim(0, m); ax.set_ylim(0, n); ax.invert_yaxis(); ax.axis("off")

    for j, (k, titulo, lim) in enumerate(LIMITES):
        ax.text(j + 0.5, -0.52, titulo, ha="center", va="bottom", fontsize=10.5,
                family="Aptos", weight="semibold", color=estilo.TEXTO)
        ax.text(j + 0.5, -0.16, lim, ha="center", va="bottom", fontsize=8.5, color=estilo.TEXTO_APOIO)
    for i, e in enumerate(linhas):
        ax.text(-0.08, i + 0.5, e["nome"], ha="right", va="center", fontsize=10.5, color=estilo.TEXTO)
        for j, (k, _, _) in enumerate(LIMITES):
            u = e[k]
            ax.add_patch(Rectangle((j + 0.03, i + 0.08), 0.94, 0.84, facecolor=cor(u), edgecolor="none"))
            claro = u is not None and u >= 90
            ax.text(j + 0.5, i + 0.5, "n.d." if u is None else estilo.fmt(u, 0).replace("-", "−") + "%",
                    ha="center", va="center", fontsize=9.5,
                    color="white" if claro else estilo.TEXTO,
                    family="Aptos", weight="semibold" if claro else "normal")

    # legenda da escala, canto inferior esquerdo
    for i, (c, r) in enumerate(zip(cores + [estilo.SEM_DADO], rotulos + ["sem dado"])):
        x = 0.02 + i * 0.135
        fig.patches.append(Rectangle((x, 0.845), 0.018, 0.013, facecolor=c, edgecolor="none",
                                     transform=fig.transFigure, figure=fig))
        fig.text(x + 0.024, 0.8515, r, fontsize=9, color=estilo.TEXTO, va="center")

    estilo.cabecalho(fig, "Quanto cada estado já consumiu dos limites legais",
                     "Uso do limite de cada regra fiscal, em %, estados, 2025",
                     "100% significa estar exatamente no teto da norma. Ordenado pelo caso mais apertado de cada estado.",
                     x=0.02, topo=0.965, tam_titulo=19)
    marca(fig)
    estilo.rodape(fig, FONTE,
                  notas="Limites: pessoal (LRF, art. 20), dívida e operações de crédito (Resoluções 40 e 43 de 2001 do Senado),\n"
                        "garantias (Resolução 43/2001, art. 9º) e PPP (Lei 11.079/2004, art. 28). Uso negativo da dívida indica caixa\n"
                        "e haveres maiores que o passivo. Comparação com os limites nominais; não substitui a apuração oficial.",
                  x=0.02, y=0.016)
    estilo.salvar(fig, os.path.join(SAIDA, "00-painel-de-folga.png"))


def main():
    estilo.aplicar()
    painel_folga()
    print("00-painel-de-folga")
    for f in FIGS:
        print(ranking(f))
    print(f"\n{len(FIGS) + 1} figuras em {os.path.abspath(SAIDA)}")


if __name__ == "__main__":
    main()
