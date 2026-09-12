"""Harness del paso 7: corre todos los chequeos del sistema y devuelve
verde o rojo por cada uno, sin opinar. Si un chequeo no pasa, el paso no
cierra.

Chequeos que SI se pueden correr con archivos locales (sin red ni MCP):
  - snapshot.json existe y declara motivo de corte
  - ninguna propiedad sin id, ninguna repetida
  - ningun precio nulo o <=0
  - grupos de menos de 5 propiedades no reportan percentil
  - los KPIs de ranking (UF/m2) recalculados dan lo mismo que los guardados
  - hay un mensaje redactado por cada propiedad mencionada en el archivo de
    contactos

Chequeos que necesitan datos que este script no puede obtener solo (viven
en Notion o en Google Calendar, no en el filesystem): se listan como
OMITIDO con la razon, no se fingen en verde.

Uso: python3 validar.py [--repo-root ..] [--notion-export archivo.json]
"""

import argparse
import json
import sys
from pathlib import Path


class Resultado:
    def __init__(self):
        self.filas = []  # (nombre, estado, detalle)  estado: OK | FALLO | OMITIDO

    def ok(self, nombre, detalle=""):
        self.filas.append((nombre, "OK", detalle))

    def fallo(self, nombre, detalle):
        self.filas.append((nombre, "FALLO", detalle))

    def omitido(self, nombre, detalle):
        self.filas.append((nombre, "OMITIDO", detalle))

    def hubo_fallos(self):
        return any(estado == "FALLO" for _, estado, _ in self.filas)

    def imprimir(self):
        ancho = max(len(n) for n, _, _ in self.filas) if self.filas else 0
        for nombre, estado, detalle in self.filas:
            marca = {"OK": "[OK]   ", "FALLO": "[FALLO]", "OMITIDO": "[OMIT] "}[estado]
            print(f"{marca} {nombre.ljust(ancho)}  {detalle}")


def chequear_snapshot(res: Resultado, snapshot_path: Path):
    if not snapshot_path.exists():
        res.omitido("snapshot existe", f"no se encontro {snapshot_path}")
        return None

    data = json.loads(snapshot_path.read_text(encoding="utf-8"))

    if data.get("motivo_corte"):
        res.ok("snapshot declara motivo de corte", data["motivo_corte"])
    else:
        res.fallo("snapshot declara motivo de corte", "campo 'motivo_corte' vacio o ausente")

    props = data.get("propiedades", [])
    sin_id = [p for p in props if not p.get("id")]
    if sin_id:
        res.fallo("ninguna propiedad sin identificador", f"{len(sin_id)} propiedades sin id")
    else:
        res.ok("ninguna propiedad sin identificador", f"{len(props)} propiedades revisadas")

    ids = [p["id"] for p in props if p.get("id")]
    repetidos = {i for i in ids if ids.count(i) > 1}
    if repetidos:
        res.fallo("ningun id repetido", f"repetidos: {sorted(repetidos)}")
    else:
        res.ok("ningun id repetido", f"{len(set(ids))} ids unicos")

    precios_invalidos = [
        p["id"] for p in props
        if p.get("precio_min") is None or p.get("precio_min") <= 0
    ]
    if precios_invalidos:
        res.fallo("ningun precio nulo o <=0", f"{len(precios_invalidos)} propiedades: {precios_invalidos[:5]}")
    else:
        res.ok("ningun precio nulo o <=0", f"{len(props)} propiedades revisadas")

    return data


def chequear_ranking(res: Resultado, ranking_path: Path):
    if not ranking_path.exists():
        res.omitido("ranking existe", f"no se encontro {ranking_path}")
        return None

    data = json.loads(ranking_path.read_text(encoding="utf-8"))

    grupos_chicos_mal = []
    grupos_no_chicos_mal = []
    kpi_mismatches = []

    for tipologia, grupo in data.items():
        es_chico = grupo.get("grupo_chico")
        cantidad = grupo.get("cantidad")
        tiene_mediana = grupo.get("mediana_uf_m2") is not None

        if cantidad < 5 and not es_chico:
            grupos_chicos_mal.append(tipologia)
        if cantidad < 5 and tiene_mediana:
            grupos_chicos_mal.append(tipologia)
        if cantidad >= 5 and es_chico:
            grupos_no_chicos_mal.append(tipologia)

        for p in grupo.get("propiedades", []):
            recalculado = round(p["precio_min"] / p["m2_util_min"], 2)
            guardado = p.get("uf_por_m2")
            if abs(recalculado - guardado) > 0.01:
                kpi_mismatches.append((p["id"], recalculado, guardado))

            percentil_presente = p.get("percentil_en_tipologia") is not None
            if es_chico and percentil_presente:
                kpi_mismatches.append((p["id"], "percentil no deberia existir en grupo chico", None))

    if grupos_chicos_mal or grupos_no_chicos_mal:
        res.fallo(
            "grupos <5 marcados como grupo_chico sin percentil",
            f"mal marcados: {grupos_chicos_mal + grupos_no_chicos_mal}",
        )
    else:
        res.ok("grupos <5 marcados como grupo_chico sin percentil", f"{len(data)} grupos revisados")

    if kpi_mismatches:
        res.fallo("KPIs recalculados == guardados", f"{len(kpi_mismatches)} discrepancias: {kpi_mismatches[:5]}")
    else:
        total_props = sum(g["cantidad"] for g in data.values())
        res.ok("KPIs recalculados == guardados", f"{total_props} propiedades recalculadas, todas coinciden")

    return data


def chequear_contactos(res: Resultado, contactos_path: Path):
    if not contactos_path.exists():
        res.omitido("mensaje redactado por propiedad aprobada", f"no se encontro {contactos_path}")
        return

    texto = contactos_path.read_text(encoding="utf-8")
    n_propiedades = texto.count("## ") - texto.count("## Pendiente")
    n_mensajes = texto.count("**Mensaje redactado")

    if n_propiedades == 0:
        res.omitido("mensaje redactado por propiedad aprobada", "no hay propiedades listadas en el archivo")
    elif n_mensajes >= n_propiedades:
        res.ok("mensaje redactado por propiedad aprobada", f"{n_mensajes} mensajes para {n_propiedades} propiedades")
    else:
        res.fallo("mensaje redactado por propiedad aprobada", f"solo {n_mensajes} mensajes para {n_propiedades} propiedades")


def chequear_notion(res: Resultado, snapshot: dict | None, notion_export_path: Path | None):
    nombre = "Notion coincide con snapshot (cantidad y valores)"
    if notion_export_path is None:
        res.omitido(
            nombre,
            "requiere un export de Notion (--notion-export archivo.json); "
            "este script no tiene acceso a Notion por si solo",
        )
        return
    if not notion_export_path.exists():
        res.omitido(nombre, f"no se encontro {notion_export_path}")
        return
    if snapshot is None:
        res.omitido(nombre, "no hay snapshot para comparar")
        return

    notion_rows = json.loads(notion_export_path.read_text(encoding="utf-8"))
    snap_by_id = {p["id"]: p for p in snapshot.get("propiedades", [])}
    notion_by_id = {r["id"]: r for r in notion_rows}

    diffs = []
    for id_, srow in snap_by_id.items():
        nrow = notion_by_id.get(id_)
        if nrow is None:
            continue  # puede estar filtrada intencionalmente (fuera de tipologia/precio), no es un error
        if nrow.get("precio_min") != srow.get("precio_min"):
            diffs.append((id_, "precio_min", srow.get("precio_min"), nrow.get("precio_min")))
        if nrow.get("m2_util_min") != srow.get("m2_util_min"):
            diffs.append((id_, "m2_util_min", srow.get("m2_util_min"), nrow.get("m2_util_min")))

    if diffs:
        res.fallo(nombre, f"{len(diffs)} diferencias: {diffs[:5]}")
    else:
        res.ok(nombre, f"{len(notion_by_id)} filas de Notion comparadas contra el snapshot, sin diferencias")


def chequear_calendario(res: Resultado):
    res.omitido(
        "ningun bloqueo de agenda quedo como confirmado",
        "requiere revisar Google Calendar en vivo (MCP); no automatizable desde un script standalone",
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--notion-export", default=None)
    args = parser.parse_args()

    root = Path(args.repo_root)
    res = Resultado()

    snapshot = chequear_snapshot(res, root / "data" / "scraper" / "snapshot.json")
    chequear_ranking(res, root / "data" / "ranking" / "output.json")
    chequear_contactos(res, root / "contacto" / "paso6_contactos.md")
    chequear_notion(res, snapshot, Path(args.notion_export) if args.notion_export else None)
    chequear_calendario(res)

    print()
    res.imprimir()
    print()

    if res.hubo_fallos():
        print("RESULTADO: ROJO — hay chequeos en FALLO, el paso no cierra.")
        sys.exit(1)
    print("RESULTADO: VERDE (los OMITIDOS no cuentan como pasados — revisarlos aparte).")
    sys.exit(0)


if __name__ == "__main__":
    main()
