# CLAUDE.md — Agente Airbnb (inversión inmobiliaria)

Reglas de trabajo para este proyecto. El detalle del diseño acordado está en
`specs.md`; el desglose paso a paso en `backlog.md`. Este archivo manda sobre
cómo trabajar; no repite los números ya acordados en `specs.md`.

## Regla dura del proceso

No se escribe código de un ítem del backlog sin que el usuario lo haya
confirmado explícitamente. Cuando el usuario pegue un prompt (propio o del
taller) que esté alineado con un ítem de `backlog.md`, avisar cuál ítem es
antes de avanzar, y abrirlo ahí.

## Restricciones no negociables (todo el proyecto)

- Nunca enviar nada de forma automática: ni mail, ni WhatsApp, ni invitación
  de calendario. Todo queda como borrador o archivo para que el usuario
  revise y decida.
- Ningún bloqueo de calendario queda como CONFIRMADO — siempre TENTATIVO.
- Sin score compuesto con pesos en el ranking.
- Sin filtro ni corte automático en el evaluador financiero — el usuario
  decide siempre, comparando los números.
- Ninguna propiedad sin identificador, y ninguna repetida, en ningún paso.
- Grupos de menos de 5 propiedades no reportan percentil (se marcan como
  "grupo chico").
- Todo archivo de salida de un corte (scraper, timeouts, límites) declara
  por qué se detuvo.
- Un único tope de precio para todo el proceso: 8.000 UF (ver `specs.md`).
- Re-ejecutar un paso no debe duplicar datos en Notion.

## Cómo trabajar

- Guardar siempre un snapshot crudo antes de filtrar o transformar datos
  (en particular el scraper del paso 2). Si el parseo tiene un bug, se
  reprocesa el snapshot, no se vuelve a scrapear.
- Los cálculos de ranking y KPIs los hace un script de Python versionado en
  el repo, no un cálculo mental del LLM.
- Antes de escribir cualquier skill nuevo (ej. el scraper del paso 2), no
  asumir la estructura del sitio: verificarla abriendo la página primero.
- Cada paso termina con un chequeo verificable (conteo, comparación de
  valores, presencia de un archivo) — no con una opinión. Ver los
  criterios de éxito por paso en `specs.md` y los chequeos de `backlog.md`
  (ítem 7).
- Los MCPs de Notion, Gmail y Google Calendar se usan solo dentro de lo que
  cada ítem del backlog autoriza explícitamente — nunca para enviar o
  confirmar nada por fuera de lo que `specs.md` permite.

## Documentos de referencia

- `specs.md` — diseño acordado: propósito, zona, filtros, cortes,
  cantidades, reglas por paso, gates, éxito unitario y global.
- `backlog.md` — ítems accionables, uno por paso del pipeline.
- `taller-mba-uc/marco-de-agentes.md` — framework de diseño del taller.
- `taller-mba-uc/supuestos.yaml` — supuestos financieros de referencia para
  el evaluador (paso 5).
