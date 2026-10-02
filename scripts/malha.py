# -*- coding: utf-8 -*-
"""Baixa a malha das UFs do IBGE, simplifica e salva em dados/geo_uf.json.

A malha é embutida no painel para desenhar o mapa em SVG, sem bibliotecas externas.
Rodar só quando quiser atualizar a geometria — ela praticamente não muda.
"""
import json, os, sys

import requests

HERE = os.path.dirname(os.path.abspath(__file__))
DADOS = os.path.join(HERE, "..", "dados")
URL = ("https://servicodados.ibge.gov.br/api/v3/malhas/paises/BR"
       "?formato=application/vnd.geo+json&qualidade=minima&intrarregiao=UF")
TOL = 0.06        # tolerância do Douglas-Peucker, em graus (~6 km) — suficiente a 600 px
CASAS = 2         # arredondamento das coordenadas (~1 km)

COD = {11: "RO", 12: "AC", 13: "AM", 14: "RR", 15: "PA", 16: "AP", 17: "TO", 21: "MA", 22: "PI",
       23: "CE", 24: "RN", 25: "PB", 26: "PE", 27: "AL", 28: "SE", 29: "BA", 31: "MG", 32: "ES",
       33: "RJ", 35: "SP", 41: "PR", 42: "SC", 43: "RS", 50: "MS", 51: "MT", 52: "GO", 53: "DF"}


def simplifica(pts, tol):
    """Douglas-Peucker: descarta vértices que não alteram a forma além da tolerância."""
    if len(pts) < 3:
        return pts

    def dist(p, a, b):
        (x, y), (x1, y1), (x2, y2) = p, a, b
        dx, dy = x2 - x1, y2 - y1
        if dx == 0 and dy == 0:
            return ((x - x1) ** 2 + (y - y1) ** 2) ** .5
        t = max(0, min(1, ((x - x1) * dx + (y - y1) * dy) / (dx * dx + dy * dy)))
        return ((x - (x1 + t * dx)) ** 2 + (y - (y1 + t * dy)) ** 2) ** .5

    dmax, idx = 0, 0
    for i in range(1, len(pts) - 1):
        d = dist(pts[i], pts[0], pts[-1])
        if d > dmax:
            dmax, idx = d, i
    if dmax > tol:
        return simplifica(pts[:idx + 1], tol)[:-1] + simplifica(pts[idx:], tol)
    return [pts[0], pts[-1]]


def main():
    sys.setrecursionlimit(10000)
    g = requests.get(URL, timeout=180).json()
    out = {}
    for f in g["features"]:
        uf = COD[int(f["properties"]["codarea"])]
        gm = f["geometry"]
        rings = gm["coordinates"] if gm["type"] == "Polygon" else [p[0] for p in gm["coordinates"]]
        aneis = []
        for ring in rings:
            pts = simplifica([(round(x, CASAS), round(y, CASAS)) for x, y in ring], TOL)
            lim = [pts[0]]
            for p in pts[1:]:
                if p != lim[-1]:
                    lim.append(p)
            if len(lim) >= 4:
                aneis.append(lim)
        aneis.sort(key=len, reverse=True)
        out[uf] = aneis[:3]          # descarta ilhas irrelevantes na escala do painel
    fn = os.path.join(DADOS, "geo_uf.json")
    json.dump(out, open(fn, "w"), separators=(",", ":"))
    v = sum(len(r) for a in out.values() for r in a)
    print(f"{len(out)} UFs, {v} vértices, {os.path.getsize(fn)} bytes → {fn}")


if __name__ == "__main__":
    main()
