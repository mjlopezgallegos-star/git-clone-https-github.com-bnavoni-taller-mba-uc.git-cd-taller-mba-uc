"""Scraper de Portal Inmobiliario para el item 2 del backlog.

Trae las propiedades publicadas en la zona ya definida en specs.md y las
guarda en un snapshot crudo, antes de filtrar o transformar nada.

Gramatica del portal decodificada a mano el 2026-09-12, abriendo la pagina
real (ver SKILL.md). Si el portal cambia su HTML, este parseo se rompe y
hay que volver a decodificarlo — no asumir que sigue igual.
"""

import argparse
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import sync_playwright

DEFAULT_URL = (
    "https://www.portalinmobiliario.com/venta/departamento/"
    "_DisplayType_M_item*location_lat:-33.41047153320048*-33.295617358112594,"
    "lon:-70.63295590026856*-70.42095409973145?polygon_location="
    "rkjjEn%7BlmL%7DPj_A%5DpbA%60P%7Ej%40fh%40l%60AxQtHtfA%3FjlBiRjU_NzHrHgErt"
    "%40rJvIzY%60%40vRuIZqaA%60a%40%7D%5BtRm%60Af_%40a%5DxQk_AzYa%5DtAg%7E%40"
    "wZcjAgy%40_k%40su%40yYwRkSa%7DAzi%40s%7E%40dkAi_%40eBoTzZynAtcA%7DG%7EMf"
    "EpGmCcA"
)
DEFAULT_TOPE = 150
DEFAULT_TIMEOUT_MIN = 10
PAGE_SIZE = 100  # confirmado a mano: el portal entrega 100 cards por pagina
DEPARTAMENTO_MARKER = "/departamento/"


def build_page_url(base_url: str, page: int, page_size: int = PAGE_SIZE) -> str:
    """La pagina 1 es la URL tal cual. Desde la 2, el portal inserta un
    segmento _Desde_<N>_ justo despues de /departamento/, donde N es el
    numero de resultado por el que arranca esa pagina (1-indexado)."""
    if page <= 1:
        return base_url
    desde = (page - 1) * page_size + 1
    idx = base_url.find(DEPARTAMENTO_MARKER)
    if idx == -1:
        raise ValueError(f"No se encontro '{DEPARTAMENTO_MARKER}' en la URL base")
    insert_at = idx + len(DEPARTAMENTO_MARKER)
    # sin guion bajo final: lo que sigue (ej. "_DisplayType...") ya arranca
    # con "_", y el portal no duplica el separador.
    return f"{base_url[:insert_at]}_Desde_{desde}{base_url[insert_at:]}"


def extract_id(href: str | None) -> str | None:
    if not href:
        return None
    m = re.search(r"(MLC-\d+)", href)
    if m:
        return m.group(1)
    # fallback: no deberia pasar segun lo observado, pero no se descarta
    # silenciosamente una propiedad por esto.
    return href.split("?")[0].split("#")[0]


def parse_price(card) -> dict:
    prefix_el = card.query_selector(".poly-price__prefix")
    es_rango_precio = prefix_el is not None

    amount_el = card.query_selector(".andes-money-amount")
    moneda = None
    monto = None
    if amount_el:
        aria_label = amount_el.get_attribute("aria-label") or ""
        m = re.match(r"([\d.,]+)\s*(unidades de fomento|pesos)", aria_label)
        if m:
            monto = float(m.group(1).replace(".", "").replace(",", "."))
            moneda = "UF" if "fomento" in m.group(2) else "CLP"
        else:
            # fallback: leer simbolo + fraccion mostrados en pantalla
            currency_el = card.query_selector(".andes-money-amount__currency-symbol")
            fraction_el = card.query_selector(".andes-money-amount__fraction")
            if currency_el:
                moneda = "UF" if "UF" in currency_el.inner_text() else "CLP"
            if fraction_el:
                monto = float(
                    fraction_el.inner_text().strip().replace(".", "").replace(",", ".")
                )

    return {
        "moneda": moneda,
        "precio_min": monto,
        "precio_max": monto,  # si es rango, no hay forma de saber el maximo desde la card
        "es_rango_precio": es_rango_precio,
    }


_RANGO_RE = re.compile(r"^(\d+)\s*(?:a|-)\s*(\d+)\s*(.+)$")
_FIJO_RE = re.compile(r"^(\d+)\s*(.+)$")


def _parse_attr_text(texto: str):
    """('2 a 3 dormitorios') -> (2, 3, 'dormitorios')
    ('4 dormitorios') -> (4, 4, 'dormitorios')
    devuelve (None, None, texto) si no matchea ningun patron numerico."""
    m = _RANGO_RE.match(texto)
    if m:
        return int(m.group(1)), int(m.group(2)), m.group(3).strip()
    m = _FIJO_RE.match(texto)
    if m:
        v = int(m.group(1))
        return v, v, m.group(2).strip()
    return None, None, texto


def parse_attributes(card) -> dict:
    items = card.query_selector_all(".poly-attributes_list__item")
    out = {
        "dormitorios_min": None, "dormitorios_max": None,
        "banos_min": None, "banos_max": None,
        "m2_util_min": None, "m2_util_max": None,
    }
    for item in items:
        texto = item.inner_text().strip()
        vmin, vmax, etiqueta = _parse_attr_text(texto)
        if vmin is None:
            continue
        etiqueta_low = etiqueta.lower()
        if "dormitorio" in etiqueta_low:
            out["dormitorios_min"], out["dormitorios_max"] = vmin, vmax
        elif "baño" in etiqueta_low or "bano" in etiqueta_low:
            out["banos_min"], out["banos_max"] = vmin, vmax
        elif "m²" in etiqueta_low or "m2" in etiqueta_low:
            out["m2_util_min"], out["m2_util_max"] = vmin, vmax
    return out


def parse_card(card) -> dict | None:
    title_el = card.query_selector("a.poly-component__title")
    if title_el is None:
        return None  # card sin titulo/link: no es una propiedad utilizable

    href = title_el.get_attribute("href")
    prop_id = extract_id(href)
    if prop_id is None:
        return None

    pill_el = card.query_selector(".poly-pill__pill")
    es_proyecto = bool(pill_el and "PROYECTO" in pill_el.inner_text().upper())

    agencia = None
    badge_img = card.query_selector(".poly-component__badge img")
    if badge_img:
        agencia = badge_img.get_attribute("alt")

    prop = {
        "id": prop_id,
        "titulo": title_el.inner_text().strip(),
        "url": href,
        "es_proyecto": es_proyecto,
        "agencia": agencia,
    }
    prop.update(parse_price(card))
    prop.update(parse_attributes(card))
    return prop


def scrape(url: str, tope: int, timeout_min: int, out_dir: Path, headless: bool = True) -> dict:
    raw_dir = out_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    inicio = time.monotonic()
    deadline = inicio + timeout_min * 60

    propiedades: list[dict] = []
    ids_vistos: set[str] = set()
    duplicados_descartados = 0
    motivo_corte = None
    pagina = 1

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1366, "height": 900},
            locale="es-CL",
        )
        page = context.new_page()

        while True:
            if time.monotonic() >= deadline:
                motivo_corte = f"timeout de {timeout_min} minutos alcanzado"
                break

            page_url = build_page_url(url, pagina)
            page.goto(page_url, wait_until="domcontentloaded", timeout=45000)
            page.wait_for_timeout(3000)

            html = page.content()
            (raw_dir / f"pagina_{pagina:03d}.html").write_text(html, encoding="utf-8")

            cards = page.query_selector_all("li.ui-search-layout__item")
            n_cards = len(cards)

            for card in cards:
                prop = parse_card(card)
                if prop is None:
                    continue
                if prop["id"] in ids_vistos:
                    duplicados_descartados += 1
                    continue
                ids_vistos.add(prop["id"])
                propiedades.append(prop)
                if len(propiedades) >= tope:
                    break

            if len(propiedades) >= tope:
                motivo_corte = f"tope de {tope} propiedades alcanzado"
                break
            if n_cards < PAGE_SIZE:
                motivo_corte = (
                    f"ultima pagina: trajo {n_cards} resultados, "
                    f"menos que el maximo de {PAGE_SIZE} por pagina"
                )
                break

            pagina += 1

        browser.close()

    snapshot = {
        "generado_en": datetime.now(timezone.utc).isoformat(),
        "url_origen": url,
        "tope_definido": tope,
        "timeout_min_definido": timeout_min,
        "motivo_corte": motivo_corte,
        "paginas_leidas": pagina,
        "duplicados_descartados": duplicados_descartados,
        "total_propiedades": len(propiedades),
        "propiedades": propiedades,
    }

    snapshot_path = out_dir / "snapshot.json"
    snapshot_path.write_text(
        json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return snapshot


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--tope", type=int, default=DEFAULT_TOPE)
    parser.add_argument("--timeout-min", type=int, default=DEFAULT_TIMEOUT_MIN)
    parser.add_argument(
        "--out-dir",
        default=str(Path(__file__).resolve().parents[3] / "data" / "scraper"),
    )
    parser.add_argument(
        "--headed", action="store_true", help="corre el navegador visible (debug)"
    )
    args = parser.parse_args()

    snapshot = scrape(
        url=args.url,
        tope=args.tope,
        timeout_min=args.timeout_min,
        out_dir=Path(args.out_dir),
        headless=not args.headed,
    )

    print(f"Motivo de corte: {snapshot['motivo_corte']}")
    print(f"Paginas leidas: {snapshot['paginas_leidas']}")
    print(f"Propiedades: {snapshot['total_propiedades']}")
    print(f"Duplicados descartados: {snapshot['duplicados_descartados']}")
    print(f"Snapshot guardado en: {Path(args.out_dir) / 'snapshot.json'}")


if __name__ == "__main__":
    main()
