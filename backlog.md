# Backlog — Agente Airbnb (inversión inmobiliaria)

Ítems paso a paso, en el orden en que se construyen. Cada uno es un
agente/skill con inicio y fin propio; Notion es la posta compartida entre
ítems. Detalle completo de cada uno en `specs.md`.

Cuando el usuario pegue un prompt que esté alineado con alguno de estos
ítems, avisar cuál es antes de avanzar.

---

## ✅ 1 · Definir (specs)

**Estado:** cerrado.

Entrevista de diseño general. Definió: arquitectura de 7 pasos, zona (Lo
Barnechea + URL de Portal Inmobiliario), filtros de propiedad (tipologías,
condición, precio tope), cortes y cantidades por paso, reglas del ranking y
del evaluador, reglas de contacto/agenda, escalabilidad, restricciones no
negociables, gates de decisión humana, y criterios de éxito unitario y
global.

**Salida:** `specs.md`, `CLAUDE.md`, este `backlog.md`.

---

## ✅ 2 · Skill del portal (scraper)

**Estado:** cerrado. Corrida real en la máquina de la usuaria (este entorno
y el "Cowork" de escritorio tienen egreso de red bloqueado hacia el portal,
así que se ejecutó desde su Terminal con Python directo, sin necesitar
Claude Code local).

Skill: `inversion-inmobiliaria` (`.claude/skills/inversion-inmobiliaria/`).
Lee la URL de Portal Inmobiliario guardada en `specs.md`, arma la URL de
cada página (gramática decodificada a mano: segmento `_Desde_<N>` para
paginar, 100 resultados por página), parsea cada card
(`li.ui-search-layout__item`) y guarda snapshot crudo antes de filtrar.

**Resultado de la corrida:** motivo de corte = tope de 150 propiedades
alcanzado; 2 páginas leídas; 150 propiedades; 0 duplicados. Snapshot en
`data/scraper/snapshot.json` (no versionado — está en `.gitignore` por ser
output de una corrida, no código fuente).

**Pendiente para el paso 3 (no bloquea el cierre de este ítem):**
- Decidir dónde aplicar el filtro de "solo propiedades nuevas" — el portal
  tiene un filtro de antigüedad (`PROPERTY*AGE_0años-0años`) pero no se
  confirmó su forma ya aplicada; por ahora el snapshot trae todo lo que cae
  en la zona y el precio de la URL dada, sin ese filtro aplicado.

**Éxito:** snapshot generado, motivo de corte declarado, sin propiedades
repetidas ni sin identificador. ✅

---

## ⬜ 3 · Notion (vault)

Diseñar el esquema de la base en Notion a partir de lo que realmente trae
el snapshot del ítem 2 (no antes). Definir qué columnas escribe el sistema
y cuáles el usuario (ej. aprobaciones). Cargar los datos con aprobación
previa del esquema. Chequeo verificable: Notion vs. snapshot, fila por
fila, precio y m².

**Gate:** aprobar el esquema antes de crear la base; confirmar la
comparación fila por fila antes de seguir.

**Éxito:** cantidad de filas y valores coinciden 1 a 1 con el snapshot.

---

## ⬜ 4 · Priorizar (ranking)

Script de Python sobre los datos de Notion: UF/m², mediana, percentil —
agrupado por tipología (1D1B, 2D2B — 2D1B se cayó del alcance, ver
`specs.md`), sin comparar entre tipologías.
Grupos de menos de 5 propiedades se marcan "grupo chico", sin percentil. Sin
score compuesto con pesos. Proponer otros análisis posibles; el usuario
decide cuáles hacer y cuáles quedan para el backlog.

**Salida:** top 10 de propiedades (≤ 8.000 UF), escrito de vuelta en
Notion.

**Gate:** aprobar qué análisis adicionales hacer.

**Éxito:** ranking agrupado y ordenado según lo anterior, sin excepciones.

---

## ⬜ 5 · El modelo (evaluador financiero)

Un solo archivo HTML standalone que carga `supuestos.yaml` (con `pie_pct`
inicial en pantalla de 10%, no el 20% del archivo, editable) y analiza las
propiedades del top 10. Incluye retorno, punto de equilibrio, sensibilidad
de cuota (tasa/pie), composición de cuota, UF actualizada desde el SII,
clasificación de renta, flujo de caja mensual/anual, escenario de
plusvalía/venta con ROI/VPN, comparación lado a lado, y la prueba de
dividendo-vs-arriendo con pie 10%. Sin filtro ni corte automático.

**Gate:** el usuario marca en Notion cuáles del top 10 aprueba para
visitar (máx. 3).

**Éxito:** todos los indicadores visibles para el top 10, decisión
100% del usuario registrada en Notion.

---

## ⬜ 6 · Contactar y agendar

Solo sobre las propiedades marcadas como aprobadas (máx. 3). Entrar a la
ficha individual de cada una, extraer corredora/teléfono/mail, redactar un
mensaje (mail o WhatsApp según el dato disponible), dejar el borrador listo
en Gmail, proponer 3 horarios según disponibilidad real en Calendar (L-V
8-10 y 17-19h, sábados 9-13h, máx. 7 días adelante), y generar un bloqueo
TENTATIVO por visita.

**No negociable:** no se envía nada.

**Éxito:** mensaje redactado por cada aprobada, borrador sin enviar,
bloqueo tentativo por visita.

---

## ⬜ 7 · Supervisar (harness)

Revisión punta a punta del código generado. Mínimo 10 propuestas de mejora
en confiabilidad y eficiencia, clasificadas por impacto. Script de
validación único que corre todos los chequeos del sistema (verde/rojo, sin
opinar), incluyendo como mínimo los listados en `CLAUDE.md`. Las mejoras que
el usuario apruebe se agregan como nuevos ítems de este backlog (por
ejemplo: programar el pipeline con cron, soporte multi-zona).

**Éxito:** script de validación existe y corre; ninguna propuesta aprobada
queda sin su propio ítem de backlog.

---

## Ítems futuros (a agregar cuando se aprueben)

- Programación / cron para re-correr el pipeline automáticamente.
- Soporte para correr sobre más de una zona.
- Cualquier mejora del ítem 7 que el usuario apruebe.
