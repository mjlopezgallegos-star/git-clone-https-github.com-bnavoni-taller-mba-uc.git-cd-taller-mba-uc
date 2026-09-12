# Marco de agentes

Entregable del taller · MBA UC · v2

Este documento no te dice qué construir ni cómo. Te dice **qué es lo que estás
construyendo**, para que cuando lo tengas puedas mirarlo y saber si está completo.

---

## Lo que vas a construir

Un **agente** o varios pequeños encadenados, donde cada uno hace un trabajo
que empieza y termina en un lugar definido, y le deja al siguiente algo que el
siguiente puede leer sin haber estado presente.

---

## El mapa de construcción

```
   ┌─────────────────────  L I B E R T A D  ─────────────────────┐
   │  qué le permitís hacer · dónde razona · dónde no            │
   │                                                             │
   │   ┌──────────────────  H A R N E S S  ──────────────────┐   │
   │   │  MCPs — a qué le das acceso y con qué permisos      │   │
   │   │  validaciones internas de cada agente               │   │
   │   │  el humano                                          │   │
   │   │                                                     │   │
   │   │   ┌────────────  C O N T E X T O  ────────────┐     │   │
   │   │   │  los datos — el portal, la base de         │     │   │
   │   │   │  departamentos, el valor de la UF          │     │   │
   │   │   │  los skills                                │     │   │
   │   │   │                                            │     │   │
   │   │   │    ┌────────  S P E C S  ────────┐         │     │   │
   │   │   │    │  propósito                  │         │     │   │
   │   │   │    │  diseño — cuántos agentes,  │         │     │   │
   │   │   │    │  para qué, cómo funcionan   │         │     │   │
   │   │   │    │  preferencias               │         │     │   │
   │   │   │    └─────────────────────────────┘         │     │   │
   │   │   └────────────────────────────────────────────┘     │   │
   │   └─────────────────────────────────────────────────────┘   │
   └─────────────────────────────────────────────────────────────┘

              →  F U N C I O N A L I D A D  →
              el output queda afuera. No se diseña: se obtiene.
              Y tiene que servir de algo.
```

### Specs — el centro

Acá vive el criterio. **Propósito**: de dónde parte y a dónde llega. **Diseño**:
cuántos agentes son, para qué está cada uno, cómo se conectan. **Preferencias**: lo
que querés y lo que no, aunque nadie te lo pida.

Si esto no está escrito, no tenés un sistema: tenés una intención.

### Contexto — lo que ningún modelo trae de fábrica

**Los datos.** El portal, la base de departamentos, el valor de la UF, las tarifas.
El modelo es el mismo para todos; tu contexto no. Esta es la parte que más se olvida
y la que más define el resultado.

**Los skills.** Un skill es un instructivo escrito: los pasos, los criterios, los
casos borde. Es lo que hace que un agente ejecute igual mañana que hoy, y igual en tu
máquina que en la de al lado. Un agente sin skill funciona una vez: la vez que
estabas mirando.

### Harness — la prueba de que se cumplió el criterio

**Los MCPs.** Un MCP es a qué le das acceso y con qué permisos. Escribirlos sirve
para saber qué puede hacer un agente y —sobre todo— **qué no puede**. Un agente sin
MCP de envío no puede enviar nada, y eso no depende de que se porte bien.

**Las validaciones internas.** Código que devuelve verde o rojo: contar filas,
recalcular un número y comparar, verificar que un archivo contiene una palabra. Si tu
chequeo se puede contestar opinando, no es un chequeo.

**El humano.** Vos, en el punto donde el sistema no debe seguir solo.

### Libertad — alrededor de todo

Hay decisiones que querés que tome el agente y decisiones que no. La libertad es esa
frontera, y envuelve a los tres círculos porque los atraviesa a todos: qué specs
puede reinterpretar, qué contexto puede salir a buscar, qué validación puede saltarse.

Cuanto más chica, más confiable y menos útil. Cuanto más grande, más útil y más
difícil de verificar. **Elegirla es tu trabajo, no del modelo.**

---

## Plantilla

Durante la entrevista, se debiera poder definir los siguientes puntos para el sistema:

```
AGENTE: ___________________________________

PROPÓSITO
  parte de:     ______________________________
  termina con:  ______________________________

PREFERENCIAS (como quiero que haga las cosas)
  ___________________________________________

CONTEXTO
  datos que necesita:  _______________________
  de dónde los saca y quién se los provee:   _______________________
  skills que usa:      _______________________

HARNESS
  MCPs — puede tocar:  _______________________
  MCPs — NO puede:     _______________________
  validaciones:        _______________________
  interviene un humano: sí / no · dónde: _____
```

---

## Cómo se ve completada

Esto muestra **la forma** de una respuesta terminada, como un ejemplo de referencia:
```
AGENTE: buscador

PROPÓSITO
  parte de:     un deseo de invertir mis ahorros y no saber cómo elegir la mejor inversión inmobiliaria
  termina con:  un mail y una agenda en el calendario para ir a visitar una propiedad priorizada y analizada previamente


PREFERENCIAS
  ninguna propiedad repetida · Validaciones imparciales . Quiero que el proceso tenga un time out de 10 minutos . Quiero saber si el trabajo solicitado tiene una estimación mayor a 30 minutos y como descomponerlo . Quiero propiedades de 2 y 3 dormitorios

CONTEXTO
  datos que necesita:  la zona, link del sector a analizar
  de dónde los saca:   usuario entrega a partir de su selección en la web
  skills que usa:      portal-inmobiliario-scraper (o nombre similar) ← lo crea el usuario

HARNESS
  MCPs — puede tocar:  un navegador, Chrome MCP, el sistema de archivos
  MCPs — NO puede:     Gmail, Calendario
  validaciones:        cantidad de listados por cantidad de páginas, duplicados, timeout, límite de listado
  interviene un humano: si
```
