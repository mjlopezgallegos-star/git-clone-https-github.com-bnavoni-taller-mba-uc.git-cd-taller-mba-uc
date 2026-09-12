# Supervisión (paso 7) — revisión punta a punta

Revisión del código generado en los pasos 2 a 6. El script de validación
(`scripts/validar.py`) corre los chequeos automatizables; esta lista son
propuestas de mejora, no bugs bloqueantes — el usuario decide cuáles
implementar.

## Propuestas de mejora, por impacto

### Alto impacto

1. **El scraper no aplica el filtro de "solo nuevas" en la URL.** Sigue
   pendiente desde el paso 2: `supuestos.md`/`specs.md` piden solo
   propiedades nuevas, pero el scraper trae todo lo que cae en la zona y
   precio de la URL dada. Se descubrió recién mirando los datos (paso 3),
   después de gastar el tope de 150 en propiedades que en su mayoría no
   calificaban por precio. Confirmar la forma del filtro de antigüedad del
   portal y aplicarlo en `build_page_url` o en la URL base.

2. **El emparejamiento precio–m² en propiedades "proyecto" es una
   asunción, no un dato verificado.** Para las 4 propiedades con precio
   único y rango de m² (paso 4), se asumió que el precio "Desde"
   corresponde al m² mínimo del rango — razonable, pero no confirmado con
   la inmobiliaria. Si se visita una de estas, conviene preguntar
   explícitamente qué unidad corresponde al precio publicado antes de
   confiar en el ranking para esa propiedad puntual.

3. **El evaluador financiero tiene las propiedades hardcodeadas.** El
   array `PROPIEDADES` en `evaluador-financiero.html` es un snapshot
   manual tomado al momento de escribir el archivo. Si cambian las
   propiedades aprobadas en Notion (como pasó en esta misma sesión, de 3 a
   2 distintas), el archivo no se entera — hay que regenerarlo a mano.
   Convendría un paso de export Notion → HTML en vez de edición manual.

### Impacto medio

4. **El scraper no tiene reintentos ni checkpoint de reanudación.** Si el
   navegador falla a mitad de una corrida larga (timeout de red, cambio de
   estructura del portal a mitad de páginas), se pierde todo el progreso —
   el snapshot recién se escribe al final de la función `scrape()`, no
   incrementalmente por página.

5. **El seguro del crédito se calcula sobre el principal original, no
   sobre el saldo insoluto.** `seguro_mensual_pct_sobre_principal` se
   aplica como un monto fijo mensual en `evaluador-financiero.html` y en
   `supuestos.yaml`. En la práctica el seguro de desgravamen suele bajar
   con el saldo — esta simplificación puede sobreestimar el costo del
   seguro en los últimos años del crédito.

6. **El botón "Actualizar UF" probablemente falle siempre por CORS,** y hoy
   el archivo no ofrece más alternativa que "revisalo a mano en sii.cl".
   Podría al menos recordar la fecha del valor cargado más visiblemente, o
   sugerir pegar el valor de otra fuente con CORS habilitado.

7. **`supuestos.yaml` y el evaluador HTML son dos fuentes de verdad
   separadas.** El HTML copia a mano los valores de `supuestos.yaml` como
   constantes embebidas (necesario porque es un archivo standalone sin
   dependencias externas), pero si se edita `supuestos.yaml` más adelante,
   el evaluador no se actualiza solo.

8. **El input real de una corrida de ranking no queda versionado.** El
   script `ranking.py` lee un JSON de entrada, pero ese archivo (los datos
   exportados de Notion en el momento de rankear) no se guarda en el repo
   — solo el resultado (`data/ranking/output.json`, que además está en
   `.gitignore`). Dificulta reproducir exactamente una corrida pasada.

### Impacto bajo

9. **El tope de precio no valida la moneda.** El scraper detecta `moneda`
   (UF o CLP) por propiedad, pero nada en el pipeline homologa CLP a UF
   antes de aplicar el filtro de 8.000 UF — si una propiedad viene en CLP
   (pasó 1 de 150 en la corrida real), el filtro de precio la compara mal.

10. **Ningún script registra cuándo se corrió, más allá del snapshot del
    scraper.** `ranking.py` no guarda una fecha de ejecución en
    `output.json`; dificulta saber si un resultado está desactualizado.

11. **`contacto/paso6_contactos.md` es texto libre, no estructurado.** Con
    2-3 propiedades es legible a mano, pero un chequeo automático solo
    puede contarlas por heurística de texto (como hace
    `scripts/validar.py`) — un formato estructurado (JSON/tabla) sería más
    verificable a futuro.

12. **No hay tests automatizados para las funciones puras** (`build_page_url`,
    `parse_price`, `cuotaFrancesa`, etc.) — se verificaron a mano en esta
    sesión contra datos reales, pero no queda una suite que se pueda
    volver a correr sola tras un cambio futuro.

## Chequeos automatizados (`scripts/validar.py`)

Corre: `python3 scripts/validar.py [--notion-export archivo.json]`

| Chequeo | Automatizable sin red/MCP |
|---|---|
| Snapshot declara motivo de corte | Sí |
| Ninguna propiedad sin identificador | Sí |
| Ningún id repetido | Sí |
| Ningún precio nulo o ≤ 0 | Sí |
| Grupos < 5 marcados "grupo chico", sin percentil | Sí |
| KPIs (UF/m²) recalculados == guardados | Sí |
| Mensaje redactado por propiedad aprobada | Sí |
| Notion coincide con snapshot (cantidad y valores) | No — requiere `--notion-export` con un dump de Notion |
| Ningún bloqueo de agenda quedó confirmado | No — requiere revisar Google Calendar en vivo |

Los dos últimos se marcan `OMITIDO`, no `OK` — el script nunca finge un
verde que no verificó.

## Pendiente de decisión del usuario

Ninguna de las 12 propuestas de arriba se implementó todavía — quedan acá
para que el usuario decida cuáles agregar al backlog como ítems nuevos
(ver sección "Ítems futuros" de `backlog.md`).
