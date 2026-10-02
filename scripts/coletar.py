# -*- coding: utf-8 -*-
"""Coleta, na API do SICONFI, os anexos do RREO (6º bimestre) e do RGF (3º quadrimestre)
de 2025 para os 27 estados. Salva JSON bruto em dados/raw/ e um manifesto com o período
efetivamente obtido por ente/anexo (cai para o período anterior se o último não existir)."""
import requests, json, os, time, sys

BASE = "https://apidatalake.tesouro.gov.br/ords/siconfi/tt"
ANO = int(os.environ.get("ANO", "2025"))
HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "..", "dados", "raw")
os.makedirs(RAW, exist_ok=True)

UFS = {11:"RO",12:"AC",13:"AM",14:"RR",15:"PA",16:"AP",17:"TO",21:"MA",22:"PI",23:"CE",
       24:"RN",25:"PB",26:"PE",27:"AL",28:"SE",29:"BA",31:"MG",32:"ES",33:"RJ",35:"SP",
       41:"PR",42:"SC",43:"RS",50:"MS",51:"MT",52:"GO",53:"DF"}

RREO_ANEXOS = ["RREO-Anexo 01", "RREO-Anexo 02", "RREO-Anexo 03", "RREO-Anexo 06",
               "RREO-Anexo 09", "RREO-Anexo 13"]
RGF_ANEXOS  = ["RGF-Anexo 01", "RGF-Anexo 02", "RGF-Anexo 03", "RGF-Anexo 04"]

# ANEXOS="09,13,rgf03" limita a coleta a esses anexos (util para completar o que falta
# sem rebaixar o que ja esta em disco). Vazio = todos.
SO_ANEXOS = [a.strip().lower() for a in os.environ.get("ANEXOS", "").split(",") if a.strip()]

def quer(anexo):
    if not SO_ANEXOS:
        return True
    t = tag(anexo).lower()
    return any(f == t or f == t.replace("rreo", "").replace("rgf", "") for f in SO_ANEXOS)

def get(endpoint, **params):
    for attempt in range(4):
        try:
            r = requests.get(f"{BASE}/{endpoint}", params=params, timeout=180)
            if r.status_code == 200:
                return r.json().get("items", [])
            time.sleep(2)
        except Exception as e:
            print(f"   ! erro {endpoint} {params.get('id_ente')} {params.get('no_anexo')}: {e}")
            time.sleep(3)
    return []

def tag(anexo):
    return anexo.replace("RREO-Anexo ", "rreo").replace("RGF-Anexo ", "rgf").replace(" ", "")

def collect_rreo(ente, anexo):
    for per in range(6, 0, -1):
        items = get("rreo", an_exercicio=ANO, nr_periodo=per, co_tipo_demonstrativo="RREO",
                    no_anexo=anexo, co_esfera="E", id_ente=ente)
        if items:
            return per, items
    return None, []

def collect_rgf(ente, anexo):
    for per in range(3, 0, -1):
        items = get("rgf", an_exercicio=ANO, in_periodicidade="Q", nr_periodo=per,
                    co_tipo_demonstrativo="RGF", no_anexo=anexo, co_poder="E",
                    co_esfera="E", id_ente=ente)
        if items:
            return per, items
    return None, []

def main():
    manifest = {}
    so = [int(x) for x in sys.argv[1:]] or list(UFS)
    for ente in so:
        uf = UFS[ente]; manifest[uf] = {}
        print(f"\n=== {uf} ({ente}) ===", flush=True)
        for anexo in RREO_ANEXOS:
            if not quer(anexo):
                continue
            fn = os.path.join(RAW, f"{uf}_{ANO}_{tag(anexo)}.json")
            per, items = collect_rreo(ente, anexo)
            json.dump(items, open(fn, "w", encoding="utf-8"), ensure_ascii=False)
            manifest[uf][anexo] = {"periodo": per, "n": len(items)}
            print(f"  {anexo}: periodo={per} n={len(items)}", flush=True)
        for anexo in RGF_ANEXOS:
            if not quer(anexo):
                continue
            fn = os.path.join(RAW, f"{uf}_{ANO}_{tag(anexo)}.json")
            per, items = collect_rgf(ente, anexo)
            json.dump(items, open(fn, "w", encoding="utf-8"), ensure_ascii=False)
            manifest[uf][anexo] = {"periodo": per, "n": len(items)}
            print(f"  {anexo}: periodo={per} n={len(items)}", flush=True)
    mf = os.path.join(RAW, f"_manifest_{ANO}.json")
    old = json.load(open(mf, encoding="utf-8")) if os.path.exists(mf) else {}
    for uf, anexos in manifest.items():
        old.setdefault(uf, {}).update(anexos)
    json.dump(old, open(mf, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("\nManifesto salvo em", mf)

if __name__ == "__main__":
    main()
