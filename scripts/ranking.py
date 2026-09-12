"""Ranking del paso 4 (priorizar). Aritmetica pura sobre datos observados:
UF/m2, mediana y percentil dentro de cada tipologia. Sin supuestos
financieros, sin score compuesto con pesos. El ranking ordena, no elige.

Uso: python3 ranking.py entrada.json salida.json
"""

import json
import sys


def uf_por_m2(propiedad: dict) -> float:
    """precio_min / m2_util_min.

    Para propiedades "proyecto" con rango de m2 (precio unico "Desde X"),
    empareja ese precio con el m2 minimo del rango: es la lectura mas
    razonable de un precio "Desde" (la unidad mas chica/barata), pero es
    un emparejamiento de datos, no un hecho observado con certeza — se
    marca con `es_rango_m2` para que quede visible.
    """
    return propiedad["precio_min"] / propiedad["m2_util_min"]


def percentil_rank(valor: float, valores_ordenados: list[float]) -> float:
    n = len(valores_ordenados)
    menores = sum(1 for v in valores_ordenados if v < valor)
    iguales = sum(1 for v in valores_ordenados if v == valor)
    return (menores + 0.5 * iguales) / n * 100


def mediana(valores: list[float]) -> float:
    s = sorted(valores)
    n = len(s)
    mid = n // 2
    if n % 2 == 0:
        return (s[mid - 1] + s[mid]) / 2
    return s[mid]


def rankear(propiedades: list[dict]) -> dict:
    grupos: dict[str, list[dict]] = {}
    for p in propiedades:
        grupos.setdefault(p["tipologia"], []).append(p)

    resultado_por_grupo = {}
    for tipologia, props in grupos.items():
        for p in props:
            p["uf_por_m2"] = round(uf_por_m2(p), 2)
            p["es_rango_m2"] = p["m2_util_min"] != p["m2_util_max"]

        props_ordenadas = sorted(props, key=lambda p: p["uf_por_m2"])
        ratios = [p["uf_por_m2"] for p in props_ordenadas]
        grupo_chico = len(props_ordenadas) < 5

        for i, p in enumerate(props_ordenadas):
            p["ranking_en_tipologia"] = i + 1
            p["percentil_en_tipologia"] = (
                None if grupo_chico else round(percentil_rank(p["uf_por_m2"], ratios), 1)
            )
            p["grupo_chico"] = grupo_chico

        resultado_por_grupo[tipologia] = {
            "cantidad": len(props_ordenadas),
            "grupo_chico": grupo_chico,
            "mediana_uf_m2": None if grupo_chico else round(mediana(ratios), 2),
            "propiedades": props_ordenadas,
        }

    return resultado_por_grupo


def main():
    if len(sys.argv) != 3:
        print("Uso: python3 ranking.py entrada.json salida.json")
        sys.exit(1)

    entrada, salida = sys.argv[1], sys.argv[2]
    propiedades = json.load(open(entrada, encoding="utf-8"))
    resultado = rankear(propiedades)

    with open(salida, "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    for tipologia, grupo in resultado.items():
        print(f"\n{tipologia} — {grupo['cantidad']} propiedades"
              f"{' (grupo chico, sin percentil)' if grupo['grupo_chico'] else ''}")
        if not grupo["grupo_chico"]:
            print(f"  mediana UF/m2: {grupo['mediana_uf_m2']}")
        for p in grupo["propiedades"]:
            flag = " [rango m2]" if p["es_rango_m2"] else ""
            print(f"  #{p['ranking_en_tipologia']} {p['id']} "
                  f"UF/m2={p['uf_por_m2']} percentil={p['percentil_en_tipologia']}{flag}")


if __name__ == "__main__":
    main()
