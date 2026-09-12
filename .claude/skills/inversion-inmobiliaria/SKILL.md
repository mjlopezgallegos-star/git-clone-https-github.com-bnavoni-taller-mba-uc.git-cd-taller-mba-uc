---
name: inversion-inmobiliaria
description: Scrapea Portal Inmobiliario para una zona ya definida en specs.md y guarda un snapshot crudo de las propiedades publicadas (departamentos), respetando un tope de propiedades y un timeout como reglas de corte. Usar cuando se pida correr, actualizar o volver a correr la búsqueda de propiedades del ítem 2 del backlog ("skill del portal", "scraper", "traer propiedades de Portal Inmobiliario").
---

# Inversión inmobiliaria — scraper de Portal Inmobiliario

Trae las propiedades publicadas en la zona definida en `specs.md` (URL con el
polígono ya dibujado) y las guarda en un snapshot crudo, antes de filtrar o
transformar nada. Corresponde al ítem 2 del backlog.

## Cuándo usar esto

- El usuario pide correr el scraper del paso 2, o volver a correrlo para
  refrescar los datos de la misma zona.
- Antes de correrlo, confirmar que `specs.md` sigue teniendo la URL, el tope
  y el timeout vigentes (por si cambiaron).

## Requisito de red

Este skill necesita una salida a internet real hacia `portalinmobiliario.com`
— no funciona en un entorno con el egreso de red restringido (como una
sesión de Claude Code en la nube con política de red bloqueada, o Cowork en
la nube). Correrlo desde una terminal con internet normal (ej. la
computadora del usuario).

## Cómo correrlo

```
cd .claude/skills/inversion-inmobiliaria
python3 -m venv .venv          # una sola vez
.venv/bin/pip install -r requirements.txt   # una sola vez
.venv/bin/playwright install chromium       # una sola vez, ~550 MB
.venv/bin/python scraper.py
```

Parámetros (todos con default acordado en `specs.md`, se pueden sobreescribir):

| Flag | Default | Significado |
|---|---|---|
| `--url` | URL de Lo Barnechea en `specs.md` | Página de listado de Portal Inmobiliario con la zona ya dibujada |
| `--tope` | 150 | Máximo de propiedades a traer |
| `--timeout-min` | 10 | Minutos máximos de corrida |
| `--out-dir` | `../../../data/scraper` (relativo a este skill; cae en `data/scraper/` del proyecto) | Dónde guardar el snapshot y las páginas crudas |

## Regla de corte

Se detiene por lo primero que ocurra:

1. Una página trae menos de 100 resultados (es la última — el portal
   entrega 100 propiedades por página).
2. Se alcanza el tope de propiedades definido.
3. Se alcanza el timeout definido.

El motivo queda escrito en `snapshot.json`, campo `motivo_corte`.

## Qué guarda

- `data/scraper/raw/pagina_NNN.html` — el HTML crudo de cada página leída,
  sin tocar. Si el parseo tiene un bug, se puede volver a parsear desde acá
  sin volver a scrapear.
- `data/scraper/snapshot.json` — el resultado parseado: metadata de la
  corrida (url de origen, fecha, motivo de corte, páginas leídas, total de
  propiedades) y la lista de propiedades con los campos que trae cada card.

## Estructura de una propiedad en el snapshot

- `id`: identificador de Portal Inmobiliario (`MLC-<número>`), extraído del
  link de la card. Nunca se repite dentro de una corrida — si el scraper
  encuentra un id ya visto, lo descarta y no lo cuenta dos veces.
- `titulo`, `url`: título y link a la ficha individual.
- `es_proyecto`: true si la card trae la etiqueta "PROYECTO" (desarrollo
  nuevo con varias unidades — precio y m² como rango, no como valor único).
- `moneda`: `UF` o `CLP` (algunas propiedades publican en pesos).
- `precio_min`, `precio_max`: iguales si el precio es fijo; distintos si es
  un rango ("Desde X UF").
- `dormitorios_min`, `dormitorios_max`, `banos_min`, `banos_max`,
  `m2_util_min`, `m2_util_max`: iguales entre sí si el dato es fijo. Pueden
  quedar en `null` si la card no trae ese dato (pasó en 2 de cada 100 cards
  observadas, faltó m²).
- `agencia`: nombre de la inmobiliaria/corredora, **solo si la card lo
  muestra** (ocurre en una minoría de casos — el resto se consigue recién en
  el paso 6, entrando a la ficha individual de las propiedades aprobadas).

## Pendiente, no resuelto en este paso

- El filtro de "solo propiedades nuevas" (`supuestos.md`/specs.md) todavía
  no está aplicado en la URL de búsqueda: el portal tiene un filtro de
  antigüedad (`PROPERTY*AGE_0años-0años`) pero no se confirmó su forma
  cuando el filtro queda realmente aplicado (solo se vio la versión
  "unapplied" mientras se armaba). Por ahora el scraper trae todo lo que
  cae en la zona y el precio de la URL dada; filtrar por "nueva" queda para
  decidir en el paso 3 o 4, usando `es_proyecto` como aproximación o
  revisando el dato real de antigüedad en la ficha individual.
