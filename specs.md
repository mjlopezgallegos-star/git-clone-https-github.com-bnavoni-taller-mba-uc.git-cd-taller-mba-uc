# Specs — Agente Airbnb (inversión inmobiliaria)

Diseño general acordado en la entrevista del paso 1 (specs). Este documento es
la fuente de verdad de lo decidido; `CLAUDE.md` trae las reglas de trabajo y
`backlog.md` el desglose accionable paso a paso.

## Propósito general

- **Parte de:** un deseo de invertir ahorros en un departamento para operar
  como Airbnb, sin saber cuál conviene.
- **Termina con:** para hasta 3 propiedades aprobadas por el usuario, un
  mensaje de contacto a la corredora listo para enviar (borrador en Gmail) y
  un bloqueo tentativo en Google Calendar para visitarlas.
- **Forma:** 7 agentes/skills encadenados, cada uno con inicio y fin
  definidos. Notion es la base compartida ("posta") que un paso deja lista
  para que el siguiente la lea sin haber estado presente.

## Zona de búsqueda

- **Comuna:** Lo Barnechea.
- **URL de Portal Inmobiliario (polígono dibujado por el usuario):**
  `https://www.portalinmobiliario.com/venta/departamento/_DisplayType_M_item*location_lat:-33.41047153320048*-33.295617358112594,lon:-70.63295590026856*-70.42095409973145?polygon_location=rkjjEn%7BlmL%7DPj_A%5DpbA%60P%7Ej%40fh%40l%60AxQtHtfA%3FjlBiRjU_NzHrHgErt%40rJvIzY%60%40vRuIZqaA%60a%40%7D%5BtRm%60Af_%40a%5DxQk_AzYa%5DtAg%7E%40wZcjAgy%40_k%40su%40yYwRkSa%7DAzi%40s%7E%40dkAi_%40eBoTzZynAtcA%7DG%7EMfEpGmCcA`
- Guardada tal cual para el paso 2 (scraper). No fue analizada ni decodificada
  en este paso — esa decodificación de la gramática del portal es tarea
  explícita del paso 2.

## Filtros de propiedad (aplican en todo el proceso)

- **Tipologías:** 1D1B, 2D2B. **3D2B queda fuera** (decisión original), y
  **2D1B se cayó del alcance** tras la corrida real del scraper (paso 2):
  sobre 150 propiedades de la zona, ninguna es 2D1B — no existe oferta de
  esa tipología ahí, así que no tiene sentido seguir buscándola.
- **Condición:** solo propiedades **nuevas** (no usadas / segunda mano).
- **Precio tope:** **8.000 UF** (único número de corte en todo el proceso).
  Sobre las 150 propiedades scrapeadas, solo 16 caen dentro de este tope
  (7 × 1D1B, 7 × 2D2B, y 2 de tipologías ya descartadas) — la URL de zona
  no trae un filtro de precio, así que el scraper gasta la mayor parte del
  tope en propiedades fuera de presupuesto. Con 14 propiedades útiles
  (1D1B + 2D2B) alcanza para seguir al paso 4 (ranking).

## Base en Notion (paso 3)

- **Base:** "Propiedades — Agente Airbnb Lo Barnechea" —
  https://app.notion.com/p/237a2210652a467eb84b6194b16914e6
- Contiene las **14 propiedades filtradas** (1D1B/2D2B, ≤ 8.000 UF), no las
  150 del snapshot completo.
- Columnas del sistema: `ID Portal` (título, id único), `Titulo`, `URL`,
  `Tipologia`, `Es proyecto`, `Moneda`, `Precio min/max`,
  `Es rango precio`, `Dormitorios min/max`, `Banos min/max`,
  `M2 util min/max`, `Agencia` (vacía salvo 1 caso, se completa en paso 6).
- Columnas del usuario: `Aprobado evaluador`, `Aprobado visita`, `Notas`.
- Verificado 1 a 1 contra el snapshot filtrado (precio y m²): 14/14 sin
  diferencias.

## Ranking (paso 4)

- Script: `scripts/ranking.py`. Métrica: **UF/m²** = precio_min / m2_util_min,
  agrupado por tipología, sin comparar 1D1B contra 2D2B, sin score
  compuesto con pesos.
- Ambos grupos (1D1B y 2D2B, 7 propiedades cada uno) reportan mediana y
  percentil — ninguno es "grupo chico" (mínimo 5).
- 4 propiedades "proyecto" tienen precio único con rango de m²: el UF/m² se
  calculó emparejando el precio con el **m² mínimo** del rango (lectura más
  razonable de un "Desde X"), marcadas con `Rango m2 = true` en Notion —
  no es un dato 100% cierto, es la interpretación más defendible.
- Columnas nuevas en Notion: `UF por m2`, `Ranking en tipologia`,
  `Percentil en tipologia`, `Grupo chico`, `Rango m2`.

## Cortes y cantidades por paso

| Momento | Parámetro | Valor |
|---|---|---|
| Paso 2 — scraper | tope de propiedades | 150 |
| Paso 2 — scraper | timeout | 10 minutos |
| Paso 2 — scraper | corte por | lo primero que ocurra entre: página con menos resultados que el máximo (última página), tope de 150, o timeout de 10 min. El motivo se escribe en el archivo de snapshot. |
| Paso 4 — ranking | cuántas pasan al evaluador | top 10, dentro del tope de 8.000 UF, agrupadas por tipología |
| Paso 5 — evaluador | cuántas se aprueban para visitar | máximo 3 en total |

## Reglas del ranking (paso 4)

- Agrupar por tipología; nunca comparar una tipología contra otra.
- Grupos con menos de 5 propiedades: no reportar percentil, marcar como
  "grupo chico".
- Sin score compuesto con pesos. El ranking ordena, no elige.
- Cálculo hecho por script de Python, sobre datos observados (UF/m², mediana,
  percentil, y lo que se acuerde adicionalmente) — cero supuestos
  financieros en este paso.

## Reglas del evaluador financiero (paso 5)

- Un solo archivo HTML, sin dependencias externas, abre con doble clic.
- Carga supuestos desde `supuestos.yaml` (tarifa/ocupación por tipología como
  curvas de 12 meses, costos de operación, equipamiento con vida útil,
  parámetros del crédito). Supuestos visibles y editables en pantalla.
- **Excepción al archivo:** el `pie_pct` inicial en pantalla es **10%**, no
  el 20% que trae `supuestos.yaml` — sigue siendo editable ahí mismo.
- Debe mostrar, además de lo ya pedido en el taller (retorno, punto de
  equilibrio, sensibilidad de cuota vs. tasa/pie, composición de la cuota,
  UF actualizada desde el SII, clasificación de renta para acceso a
  crédito, flujo de caja mensual año 1 y anual a todo el plazo, escenario
  de plusvalía/venta con recálculo de ROI y VPN, comparación lado a lado
  entre las propiedades del top 10): una **prueba explícita de
  dividendo-vs-arriendo** — si el arriendo (Airbnb) proyectado cubre el
  dividendo hipotecario, calculado con el pie del 10%.
- **Sin filtro ni corte automático.** El evaluador expone números; la
  decisión de cuáles aprobar para visitar (máx. 3) es 100% del usuario,
  marcada en Notion.

## Reglas de contacto y agenda (paso 6)

- Solo se actúa sobre las propiedades marcadas como aprobadas en Notion
  (máximo 3).
- Por cada una: extraer corredora/teléfono/mail de la ficha individual,
  redactar un mensaje (mail si hay mail, WhatsApp si solo hay teléfono), y
  proponer 3 alternativas de horario según disponibilidad real en Google
  Calendar (L-V 8-10 y 17-19h, sábados 9-13h), usando máximo 7 días hacia
  adelante.
- **No negociable:** nunca se envía nada (ni mail, ni WhatsApp, ni
  invitación) de forma automática. El mail queda como borrador en Gmail. El
  bloqueo de calendario queda como **TENTATIVO**, nunca confirmado. Todo
  queda para que el usuario revise y decida.

## Escalabilidad y programación

- Para esta primera versión, el pipeline corre **manual, on-demand** —no
  programado ni en cron.
- Debe ser **re-ejecutable sin duplicar**: si se vuelve a correr el scraper
  sobre la misma zona, Notion no debe crear filas repetidas de una
  propiedad ya cargada (dedupe por identificador de propiedad).
- Cron y soporte multi-zona quedan como ítems de mejora a evaluar en el
  paso 7 (Supervisar), no se construyen en esta versión.

## Restricciones no negociables (resumen)

- Nunca enviar nada automáticamente (mail, WhatsApp, invitación de
  calendario).
- Bloqueos de calendario siempre TENTATIVOS, nunca confirmados.
- Sin score compuesto con pesos en el ranking.
- Sin filtro ni corte automático en el evaluador financiero.
- Ninguna propiedad repetida, en ningún paso.
- Grupos de menos de 5 propiedades no reportan percentil.
- El motivo de corte del scraper siempre se escribe en el archivo de
  salida.
- Un único tope de precio (8.000 UF) para todo el proceso.

## Puntos de decisión humana (gates)

1. Aprobar el esquema de columnas de Notion antes de crearlo (paso 3).
2. Confirmar que Notion coincide con el snapshot fila por fila antes de
   seguir (paso 3).
3. Aprobar qué análisis adicionales del ranking hacer, además de los
   obligatorios (paso 4).
4. Marcar en Notion cuáles del top 10 se aprueban para el evaluador, y
   cuáles de esas se aprueban para visitar — máx. 3 (paso 5).
5. Revisar y enviar el mail/WhatsApp — el sistema nunca envía (paso 6).
6. Confirmar las visitas — los bloqueos de calendario quedan TENTATIVOS
   (paso 6).

## Qué necesita cada paso para arrancar sin contexto previo

| Paso | Qué necesita | De dónde sale |
|---|---|---|
| 2 · Scraper | URL de zona, tope (150), timeout (10 min), tipologías, precio tope, condición "nuevas" | este `specs.md` |
| 2 · Scraper | gramática actual del portal (URL de listado, paginación, selectores, campos) | se decodifica en vivo abriendo el portal, no se asume |
| 3 · Notion | snapshot crudo | generado por el paso 2 |
| 4 · Ranking | datos ya cargados y verificados | Notion (cargado en paso 3) |
| 5 · Evaluador | top 10 del ranking, `supuestos.yaml`, valor UF actualizado, clasificación de renta | paso 4 + repo + página del SII (en vivo) + input del usuario en pantalla |
| 6 · Contactar/Agendar | propiedades marcadas como aprobadas en Notion, ficha individual de cada una, disponibilidad real en Google Calendar | Notion (marcado en paso 5) + navegación puntual + MCP Calendar |
| 7 · Supervisar | todo el código y los archivos de salida generados en los pasos anteriores | el propio repositorio |

## Éxito unitario y global

- **Paso 2:** el snapshot existe, declara su motivo de corte, y ninguna
  propiedad quedó sin identificador o repetida.
- **Paso 3:** la cantidad de filas y los valores de precio/m² en Notion
  coinciden 1 a 1 contra el snapshot, sin diferencias no explicadas.
- **Paso 4:** entrega el top 10 (≤ 8.000 UF) agrupado por tipología, sin
  comparar tipologías entre sí, marcando "grupo chico" donde corresponda.
- **Paso 5:** muestra retorno, punto de equilibrio y la prueba de
  dividendo-vs-arriendo (pie 10%, editable) para el top 10, sin ningún
  corte automático, y el usuario marcó en Notion cuáles aprueba para
  visitar (máx. 3).
- **Paso 6:** hay un mensaje redactado por cada propiedad aprobada, un
  borrador sin enviar en Gmail, y un bloqueo TENTATIVO en el calendario por
  cada visita.
- **Éxito global:** desde la URL de la zona hasta tener, para hasta 3
  propiedades elegidas por el usuario, un mensaje de contacto listo para
  enviar y una visita tentativamente agendada, con el respaldo financiero
  completo detrás de cada una.

## Harness general (aplica a todos los pasos)

- **MCPs que se usan:** Notion, Gmail, Google Calendar, navegador/Playwright
  para Portal Inmobiliario y SII, filesystem.
- **Lo que ningún paso puede hacer:** enviar mails o mensajes, confirmar
  invitaciones o eventos de calendario, aplicar filtros financieros
  automáticos que descarten una propiedad sin que el usuario lo vea.
- **Validaciones:** ver `backlog.md` (paso 7) y el detalle por paso en las
  tablas de arriba — cada chequeo devuelve verde o rojo, no opina.
